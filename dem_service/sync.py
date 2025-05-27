from dem_service.transform import clean_countries_full
import os, json, requests
from datetime import datetime
from sqlalchemy.orm import Session
from dem_service import crud, models
from dotenv import load_dotenv
from types import SimpleNamespace

load_dotenv()
MDM_URL = os.getenv("MDM_URL")

BASE_STORAGE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "storage"))
RAW_DIR = os.path.join(BASE_STORAGE, "raw")
PROCESSED_DIR = os.path.join(BASE_STORAGE, "processed")

os.makedirs(RAW_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)


def transform(data):
    result = []
    rejected = []
    seen_cca3 = set()

    for country in data:
        try:
            cca3 = country.get("cca3")
            name = country.get("name", {}).get("common")

            if not cca3 or not name or cca3 in seen_cca3:
                rejected.append(country)
                continue

            capital = country.get("capital", [])
            if isinstance(capital, str):
                capital = [capital]
            elif capital is None:
                capital = []

            result.append({
                "cca3": cca3,
                "name": name,
                "region": country.get("region"),
                "subregion": country.get("subregion"),
                "population": country.get("population", 0),
                "area": country.get("area", 0.0),
                "capital": capital
            })

            seen_cca3.add(cca3)
        except Exception:
            rejected.append(country)

    return result, rejected


def sync_all_providers(db: Session):
    providers = crud.get_providers(db)

    for p in providers:
        try:
            resp = requests.get(p.url, timeout=10)
            resp.raise_for_status()
            original_data = json.loads(resp.text)

            timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
            raw_path = os.path.join(RAW_DIR, f"{p.name}_{timestamp}_raw.json")
            with open(raw_path, "w", encoding="utf-8") as f:
                f.write(resp.text)

            processed_data, rejected_data = transform(original_data)

            processed_path = os.path.join(PROCESSED_DIR, f"{p.name}_{timestamp}_processed.json")
            with open(processed_path, "w", encoding="utf-8") as f:
                json.dump(processed_data, f, indent=2, ensure_ascii=False)

            inserted = 0
            already_exists = 0
            failed = 0

            for item in processed_data:
                try:
                    res = requests.post(f"{MDM_URL}/countries", json=item)

                    if res.status_code == 400:
                        if "already exists" in res.text:
                            print(f"[-] País já existe: {item.get('cca3')}")
                            already_exists += 1
                        else:
                            print(f"[!] 400 ao enviar país {item.get('cca3')} | Resposta: {res.text}")
                            print("Payload enviado:\n", json.dumps(item, indent=2, ensure_ascii=False))
                            failed += 1
                        continue

                    res.raise_for_status()
                    inserted += 1

                except Exception as e:
                    print(f"[!] Erro ao enviar país {item.get('cca3')}: {e}")
                    print("Payload com erro:\n", json.dumps(item, indent=2, ensure_ascii=False))
                    failed += 1

            crud.create_metadata(
                db,
                provider=p,
                status="success",
                raw_path=raw_path,
                processed_path=processed_path,
                processed_count=len(processed_data),
                rejected_count=len(rejected_data),
                rejected_samples=[r.get("cca3") for r in rejected_data[:5]]
            )

            print("\n[RESUMO] Provedor:", p.name)
            print(" - Inseridos com sucesso:", inserted)
            print(" - Já existiam:", already_exists)
            print(" - Falharam na inserção:", failed)
            print(" - Rejeitados na transformação:", len(rejected_data), "\n")

        except Exception as e:
            print(f"[ERRO] Falha com provedor {p.name}: {e}")
            crud.create_metadata(
                db,
                provider=p,
                status="fail",
                raw_path="none",
                processed_path="none",
                processed_count=0,
                rejected_count=0,
                rejected_samples=[]
            )



def run_dynamic_extract(name: str, url: str, db):
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        original_data = json.loads(resp.text)

        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        raw_path = os.path.join(RAW_DIR, f"{name}_{timestamp}_raw.json")
        with open(raw_path, "w", encoding="utf-8") as f:
            f.write(resp.text)

        processed_data, rejected_data = transform(original_data)

        processed_path = os.path.join(PROCESSED_DIR, f"{name}_{timestamp}_processed.json")
        with open(processed_path, "w", encoding="utf-8") as f:
            json.dump(processed_data, f, indent=2, ensure_ascii=False)

        inserted = 0
        for item in processed_data:
            try:
                res = requests.post(f"{MDM_URL}/countries", json=item)
                if res.status_code == 400:
                    if "already exists" in res.text:
                        print(f"[-] País já existe: {item.get('cca3')}")
                    else:
                        print(f"[!] 400 ao enviar país {item.get('cca3')} | Resposta: {res.text}")
                        print("Payload enviado:\n", json.dumps(item, indent=2, ensure_ascii=False))
                    continue
                res.raise_for_status()
                inserted += 1
            except Exception as e:
                print(f"[!] Erro ao enviar país {item.get('cca3')}: {e}")

        crud.create_metadata(
            db,
            provider=SimpleNamespace(id=0, name=name),
            status="success",
            raw_path=raw_path,
            processed_path=processed_path,
            processed_count=len(processed_data),
            rejected_count=len(rejected_data),
            rejected_samples=[r.get("cca3") for r in rejected_data[:5]]
        )

        return {
            "detail": f"{inserted} países enviados, {len(rejected_data)} rejeitados.",
            "raw_path": raw_path,
            "processed_path": processed_path
        }

    except Exception as e:
        return {"error": str(e)}
