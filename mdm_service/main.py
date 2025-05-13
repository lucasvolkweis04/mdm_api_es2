from fastapi import FastAPI, Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session
from . import models, schemas, crud
from database import Base, engine, SessionLocal

Base.metadata.create_all(bind=engine)

app = FastAPI(title="MDM Country Service")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/countries", response_model=schemas.Country)
def create_country(c: schemas.CountryCreate, db: Session = Depends(get_db)):
    if crud.get_country(db, c.cca3):
        raise HTTPException(400, "Country already exists")
    return crud.create_country(db, c)

@app.get("/countries", response_model=List[schemas.Country])
def read_countries(skip: int=0, limit: int=100,
                   region: str=None, name: str=None,
                   db: Session = Depends(get_db)):
    return crud.get_countries(db, skip, limit, region, name)

@app.get("/countries/{cca3}", response_model=schemas.Country)
def read_country(cca3: str, db: Session = Depends(get_db)):
    obj = crud.get_country(db, cca3)
    if not obj:
        raise HTTPException(404, "Country not found")
    return obj

@app.put("/countries/{cca3}", response_model=schemas.Country)
def update_country(cca3: str, c: schemas.CountryUpdate,
                   db: Session = Depends(get_db)):
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