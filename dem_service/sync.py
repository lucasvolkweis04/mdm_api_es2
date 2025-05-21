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

def sync_all_providers(db: Session):
    providers = crud.get_providers(db)
    for p in providers:
        try:
            resp = requests.get(p.url, timeout=10)
            resp.raise_for_status()
            data = resp.json()

            timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
            raw_path = os.path.join(RAW_DIR, f"{p.name}_{timestamp}.json")
            with open(raw_path, "w") as f:
                json.dump(data, f)

            processed, rejected = clean_countries_full(data)

            processed_path = os.path.join(PROCESSED_DIR, f"{p.name}_{timestamp}.json")
            with open(processed_path, "w") as f:
                json.dump(processed, f)

            for item in processed:
                try:
                    requests.post(f"{MDM_URL}/countries", json=item)
                except Exception as e:
                    print(f"[!] Erro ao enviar país {item.get('cca3')}: {e}")

            crud.create_metadata(
                db,
                provider=p,
                status="success",
                raw_path=raw_path,
                processed_path=processed_path,
                processed_count=len(processed),
                rejected_count=len(rejected),
                rejected_samples=rejected
            )

        except Exception as e:
            crud.create_metadata(
                db,
                provider=p,
                status="fail",
                raw_path="none",
                processed_path="none",
                processed_count=0,
                rejected_count=0,
                rejected_samples=[str(e)]
            )
            print(f"Erro com provedor {p.name}: {e}")


def transform(data):
    result = []
    seen_cca3 = set()

    for country in data:
        try:
            cca3 = country.get("cca3")
            name = country.get("name", {}).get("common")
            if not cca3 or not name:
                continue
            if cca3 in seen_cca3:
                continue

            region = country.get("region")
            subregion = country.get("subregion")
            population = country.get("population", 0)
            area = country.get("area", 0.0)
            capital = country.get("capital", [])

            # Padroniza capital como lista
            if isinstance(capital, str):
                capital = [capital]
            elif capital is None:
                capital = []

            result.append({
                "cca3": cca3,
                "name": name,
                "region": region,
                "subregion": subregion,
                "population": population,
                "area": area,
                "capital": capital
            })

            seen_cca3.add(cca3)

        except Exception as e:
            print(f"Erro ao processar país: {e}")
            continue

    return result

def run_dynamic_extract(name: str, url: str, db):
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        raw_path = os.path.join(RAW_DIR, f"{name}_{timestamp}.json")
        with open(raw_path, "w") as f:
            json.dump(data, f, indent=2)

        processed_data = transform(data)

        processed_path = os.path.join(PROCESSED_DIR, f"{name}_{timestamp}.json")
        with open(processed_path, "w") as f:
            json.dump(processed_data, f, indent=2)

        for item in processed_data:
            requests.post(f"{MDM_URL}/countries", json=item)

        crud.create_metadata(
            db,
            provider=SimpleNamespace(id=0, name=name),
            status="success",
            raw_path=raw_path,
            processed_path=processed_path,
            processed_count=len(processed_data),
            rejected_count=len(data) - len(processed_data),
            rejected_samples=[c.get("cca3") for c in data if c.get("cca3") not in {x["cca3"] for x in processed_data}]
        )

        return {
            "detail": f"{len(processed_data)} países enviados, {len(data) - len(processed_data)} rejeitados.",
            "raw_path": raw_path,
            "processed_path": processed_path
        }

    except Exception as e:
        return {"error": str(e)}

