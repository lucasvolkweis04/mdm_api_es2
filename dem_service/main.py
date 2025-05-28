from fastapi import FastAPI, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from typing import List
from dem_service import models, schemas, crud, sync
from dem_service.database import SessionLocal, Base, engine
from dem_service.sync import run_dynamic_extract
from dem_service.schemas import ProviderCreate
from dem_service import models


app = FastAPI(title="DEM ETL Service")

models.Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/providers")
def create_provider(p: ProviderCreate, db: Session = Depends(get_db)):
    return crud.create_provider(db, p)

@app.get("/providers", response_model=List[schemas.Provider])
def list_providers(db: Session = Depends(get_db)):
    return crud.get_providers(db)

@app.post("/sync")
def run_sync(db: Session = Depends(get_db)):
    sync.sync_all_providers(db)
    return {"detail": "Sync initiated"}

@app.get("/transactions", response_model=List[schemas.ETLMetadata])
def get_metadata(db: Session = Depends(get_db)):
    return crud.get_metadata(db)

@app.post("/run-extract")
def run_extract(payload: dict = Body(...), db: Session = Depends(get_db)):
    """
    Executa extração de uma nova fonte externa sem cadastrar permanentemente.
    """
    name = payload.get("name")
    url = payload.get("url")
    if not name or not url:
        raise HTTPException(400, "Campos 'name' e 'url' são obrigatórios.")
    
    return run_dynamic_extract(name, url, db)

@app.delete("/providers/{provider_id}", status_code=204)
def delete_provider(provider_id: int, db: Session = Depends(get_db)):
    db_provider = crud.get_provider_by_id(db, provider_id)
    if not db_provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    crud.delete_provider(db, provider_id)
    return




