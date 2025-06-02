import os
import json
import re
import requests
from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from dem_service import models, schemas, crud
from dem_service.database import SessionLocal, Base, engine

app = FastAPI(title="DEM ETL Service")

Base.metadata.create_all(bind=engine)

BASE_STORAGE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "storage"))
RAW_DIR = os.path.join(BASE_STORAGE, "raw")
PROCESSED_DIR = os.path.join(BASE_STORAGE, "processed")
os.makedirs(RAW_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

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

def safe_filename(name):
    return re.sub(r'[^a-zA-Z0-9_-]', '_', name)

@app.post("/providers")
def create_provider(p: schemas.ProviderCreate, db: Session = Depends(get_db)):
    import time
    from dem_service.transform import clean_countries_full

    # Cria e salva o provider no banco
    provider = crud.create_provider(db, p)

    # 1. Baixar o JSON da URL do provider
    try:
        response = requests.get(provider.url, timeout=10)
        response.raise_for_status()
        countries_raw = response.json()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro ao baixar JSON do provider: {e}")

    # 2. Gerar nome de arquivo com timestamp
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    raw_filename = f"{provider.name}_{timestamp}.json"
    processed_filename = f"{provider.name}_{timestamp}.json"

    raw_path = os.path.join(RAW_DIR, raw_filename)
    processed_path = os.path.join(PROCESSED_DIR, processed_filename)

    # 3. Salvar JSON BRUTO na pasta raw
    with open(raw_path, "w", encoding="utf-8") as f:
        f.write(response.text)  # <-- mantém exatamente como veio da API

    # 4. Processar e salvar na pasta processed
    processed_data, _ = clean_countries_full(countries_raw)
    with open(processed_path, "w", encoding="utf-8") as f:
        json.dump(processed_data, f, ensure_ascii=False, indent=2)

    return {"message": "Provider criado e dados salvos em raw e processed com sucesso."}

@app.get("/providers", response_model=List[schemas.Provider])
def list_providers(db: Session = Depends(get_db)):
    return crud.get_providers(db)

@app.get("/countries")
def get_countries(db: Session = Depends(get_db)):
    return db.query(models.Country).all()


@app.get("/metadata", response_model=List[schemas.ETLMetadata])
def get_metadata(db: Session = Depends(get_db)):
    return crud.get_metadata(db)

@app.delete("/providers/{provider_id}", status_code=204)
def delete_provider(provider_id: int, db: Session = Depends(get_db)):
    db_provider = crud.get_provider_by_id(db, provider_id)
    if not db_provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    crud.delete_provider(db, provider_id)
    return

@app.get("/countries/processed-latest")
def get_latest_processed_countries():
    import json

    processed_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "storage", "processed"))

    json_files = [f for f in os.listdir(processed_dir) if f.endswith(".json")]
    if not json_files:
        raise HTTPException(status_code=404, detail="Nenhum arquivo processado encontrado.")

    latest_file = max(json_files, key=lambda f: os.path.getmtime(os.path.join(processed_dir, f)))
    latest_path = os.path.join(processed_dir, latest_file)

    try:
        with open(latest_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao carregar JSON: {e}")