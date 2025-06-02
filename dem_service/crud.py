from sqlalchemy.orm import Session
from dem_service import models, schemas

def create_provider(db: Session, data: schemas.ProviderCreate):
    obj = models.Provider(**data.dict())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

def get_providers(db: Session):
    return db.query(models.Provider).all()

def get_provider(db: Session, provider_id: int):
    return db.query(models.Provider).filter(models.Provider.id == provider_id).first()

def create_metadata(db: Session, provider, status, raw_path, processed_path, processed_count, rejected_count, rejected_samples):
    meta = models.ETLMetadata(
        provider_id=provider.id,
        provider_name=provider.name,
        status=status,
        raw_path=raw_path,
        processed_path=processed_path,
        processed_count=processed_count,
        rejected_count=rejected_count,
        rejected_samples=rejected_samples[:5]  # limitar
    )
    db.add(meta)
    db.commit()
    db.refresh(meta)
    return meta


def get_metadata(db: Session):
    return db.query(models.ETLMetadata).all()

def get_provider_by_id(db: Session, provider_id: int):
    return db.query(models.Provider).filter(models.Provider.id == provider_id).first()

def delete_provider(db: Session, provider_id: int):
    db.query(models.Provider).filter(models.Provider.id == provider_id).delete()
    db.commit()


