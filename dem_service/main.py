from fastapi import FastAPI, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from typing import List
from dem_service import models, schemas, crud, sync
from dem_service.database import SessionLocal, Base, engine
from dem_service.sync import run_dynamic_extract

# ✅ 1. Cria o app primeiro!
app = FastAPI(title="DEM ETL Service")

# ✅ 2. Cria as tabelas
Base.metadata.create_all(bind=engine)

# ✅ 3. Dependência do banco
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ✅ 4. Endpoints
@app.post("/providers", response_model=schemas.Provider)
def create_provider(p: schemas.ProviderCreate, db: Session = Depends(get_db)):
    return crud.create_provider(db, p)

@app.get("/providers", response_model=List[schemas.Provider])
def list_providers(db: Session = Depends(get_db)):
    return crud.get_providers(db)

@app.post("/sync")
def run_sync(db: Session = Depends(get_db)):
    sync.sync_all_providers(db)
    return {"detail": "Sync initiated"}

@app.get("/metadata", response_model=List[schemas.ETLMetadata])
def get_metadata(db: Session = Depends(get_db)):
    return crud.get_metadata(db)

# ✅ 5. Novo endpoint dinâmico
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
