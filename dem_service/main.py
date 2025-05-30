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
    provider = crud.create_provider(db, p)
    # 1. Baixar o JSON da URL do provider
    try:
        response = requests.get(provider.url, timeout=10)
        response.raise_for_status()
        countries_raw = response.json()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro ao baixar JSON do provider: {e}")

    # 2. Salvar JSON bruto
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    safe_name = safe_filename(provider.name)
    raw_path = os.path.join(RAW_DIR, f"{safe_name}_{timestamp}_raw.json")
    with open(raw_path, "w", encoding="utf-8") as f:
        json.dump(countries_raw, f, ensure_ascii=False, indent=2)

    # 3. Transformar e salvar JSON processado
    countries, _ = transform(countries_raw)
    processed_path = os.path.join(PROCESSED_DIR, f"{safe_name}_{timestamp}_processed.json")
    with open(processed_path, "w", encoding="utf-8") as f:
        json.dump(countries, f, ensure_ascii=False, indent=2)

    # 4. Inserir/atualizar countries no banco
    for country in countries:
        obj = db.query(models.Country).filter(models.Country.cca3 == country["cca3"]).first()
        if obj:
            for k, v in country.items():
                setattr(obj, k, v)
        else:
            obj = models.Country(**country)
            db.add(obj)
    db.commit()
    return provider


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




