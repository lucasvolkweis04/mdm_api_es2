import os
import json
from datetime import datetime
import requests
from fastapi import FastAPI, Depends, HTTPException, Body
from typing import List
from sqlalchemy.orm import Session
from mdm_service import models, schemas, crud
from mdm_service.database import Base, engine, SessionLocal

DEM_URL = os.getenv("DEM_URL")

Base.metadata.create_all(bind=engine)

app = FastAPI(title="MDM Country Service")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/countries", response_model=schemas.Country)
def upsert_country(c: schemas.CountryCreate, db: Session = Depends(get_db)):
    return crud.upsert_country(db, c)

@app.get("/countries", response_model=List[schemas.Country])
def read_countries(skip: int = 0, limit: int = 100,
                   region: str = None, name: str = None,
                   db: Session = Depends(get_db)):
    return crud.get_countries(db, skip, limit, region, name)

@app.post("/sync-from-dem")
def sync_from_dem(db: Session = Depends(get_db)):
    import requests
    import os

    dem_url = os.getenv("DEM_URL", "http://localhost:8002")  # ou defina DEM_URL no .env
    endpoint = f"{dem_url}/countries/processed-latest"

    try:
        response = requests.get(endpoint, timeout=10)
        response.raise_for_status()
        countries = response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar dados do DEM: {e}")

    inserted = []
    for country in countries:
        try:
            schema = schemas.CountryCreate(**country)
            country_obj = crud.upsert_country(db, schema)
            inserted.append(country_obj.cca3)
        except Exception as e:
            print(f"Erro ao inserir país {country.get('cca3')}: {e}")

    return {
        "message": f"{len(inserted)} países sincronizados com sucesso via API.",
        "países": inserted
    }

@app.get("/countries/{cca3}", response_model=schemas.Country)
def read_country(cca3: str, db: Session = Depends(get_db)):
    obj = crud.get_country(db, cca3)
    if not obj:
        raise HTTPException(404, "Country not found")
    return obj

@app.put("/countries/{cca3}", response_model=schemas.Country)
def update_country(cca3: str, c: schemas.CountryUpdate, db: Session = Depends(get_db)):
    obj = crud.update_country(db, cca3, c)
    if not obj:
        raise HTTPException(404, "Country not found")
    return obj

@app.delete("/countries/{cca3}")
def delete_country(cca3: str, db: Session = Depends(get_db)):
    obj = crud.delete_country(db, cca3)
    if not obj:
        raise HTTPException(404, "Country not found")
    return {"detail": "Deleted"}

@app.delete("/reset-countries")
def reset_countries(db: Session = Depends(get_db)):
    deleted = db.query(models.Country).delete()
    db.commit()
    return {"detail": f"{deleted} países apagados"}

