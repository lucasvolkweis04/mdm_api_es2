import os
import subprocess
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from database import Base, engine, SessionLocal
from .models import ETLTransaction, ETLStatus

# cria tabela de transações ETL
Base.metadata.create_all(bind=engine)

app = FastAPI(title="DEM Service")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/etl/extract")
def extract(db: Session = Depends(get_db)):
    tx = ETLTransaction(type="extract", status=ETLStatus.running, logs="")
    db.add(tx); db.commit(); db.refresh(tx)
    try:
        result = subprocess.run(
            ["python", "load_countries.py"],
            cwd=os.path.dirname(__file__),
            capture_output=True, text=True
        )
        tx.status = ETLStatus.success if result.returncode == 0 else ETLStatus.failure
        tx.logs   = result.stdout if result.returncode == 0 else result.stderr
    except Exception as e:
        tx.status = ETLStatus.failure
        tx.logs   = str(e)
    db.commit()
    return {"id": tx.id, "status": tx.status.value, "logs": tx.logs}

@app.post("/etl/transform")
def transform(db: Session = Depends(get_db)):
    tx = ETLTransaction(type="transform", status=ETLStatus.running, logs="")
    db.add(tx); db.commit(); db.refresh(tx)
    # Aqui você colocaria sua lógica de transformação
    tx.status = ETLStatus.success
    tx.logs   = "Transform completed."
    db.commit()
    return {"id": tx.id, "status": tx.status.value, "logs": tx.logs}

@app.post("/etl/load")
def load(db: Session = Depends(get_db)):
    tx = ETLTransaction(type="load", status=ETLStatus.running, logs="")
    db.add(tx); db.commit(); db.refresh(tx)
    # Se tiver lógica de “load” separada, vai aqui
    tx.status = ETLStatus.success
    tx.logs   = "Load completed."
    db.commit()
    return {"id": tx.id, "status": tx.status.value, "logs": tx.logs}

@app.get("/etl/transactions")
def list_transactions(db: Session = Depends(get_db)):
    txs = db.query(ETLTransaction).order_by(ETLTransaction.id.desc()).all()
    return [
        {
            "id": t.id,
            "type": t.type,
            "status": t.status.value,
            "created_at": t.created_at,
            "updated_at": t.updated_at
        }
        for t in txs
    ]

@app.get("/etl/transactions/{tx_id}")
def get_transaction(tx_id: int, db: Session = Depends(get_db)):
    t = db.query(ETLTransaction).filter(ETLTransaction.id == tx_id).first()
    if not t:
        raise HTTPException(404, "Transaction not found")
    return {
        "id": t.id,
        "type": t.type,
        "status": t.status.value,
        "logs": t.logs,
        "created_at": t.created_at,
        "updated_at": t.updated_at
    }