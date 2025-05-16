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

            processed_data = transform(data)

            processed_path = os.path.join(PROCESSED_DIR, f"{p.name}_{timestamp}.json")
            with open(processed_path, "w") as f:
                json.dump(processed_data, f)

            for item in processed_data:
                requests.post(f"{MDM_URL}/countries", json=item)

            crud.create_metadata(db, p.id, "success", raw_path, processed_path)
        except Exception as e:
            crud.create_metadata(db, p.id, "fail", "none", "none")
            print(f"Erro com provedor {p.name}: {e}")

def transform(data):
    result = []
    seen_cca3 = set()

    for country in data:
        try:
            cca3 = country.get("cca3")
            if not cca3 or cca3 in seen_cca3:
                continue  # ignora duplicados e sem código

            name = country.get("name", {}).get("common")
            if not name:
                continue  # ignora sem nome

            region = country.get("region")
            subregion = country.get("subregion")
            population = country.get("population", 0)
            area = country.get("area", 0.0)
            capital = country.get("capital", [])

            # força capital como lista de string
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

def run_dynamic_extract(name: str, url: str, db):
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        raw_path = os.path.join(RAW_DIR, f"{name}_{timestamp}.json")
        with open(raw_path, "w") as f:
            json.dump(data, f)

        processed, rejected = clean_countries_full(data)

        processed_path = os.path.join(PROCESSED_DIR, f"{name}_{timestamp}.json")
        with open(processed_path, "w") as f:
            json.dump(processed, f)

        for item in processed:
            requests.post(f"{MDM_URL}/countries", json=item)

        crud.create_metadata(
            db,
            provider=SimpleNamespace(id=0, name=name),
            status="success",
            raw_path=raw_path,
            processed_path=processed_path,
            processed_count=len(processed),
            rejected_count=len(rejected),
            rejected_samples=rejected
        )

        return {
            "detail": f"{len(processed)} países enviados, {len(rejected)} rejeitados.",
            "raw_path": raw_path,
            "processed_path": processed_path
        }

    except Exception as e:
        return {"error": str(e)}

    return result
