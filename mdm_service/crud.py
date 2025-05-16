from sqlalchemy.orm import Session
from mdm_service import models, schemas

def get_country(db: Session, cca3: str):
    return db.query(models.Country).filter(models.Country.cca3 == cca3).first()

def get_countries(db: Session, skip: int = 0, limit: int = 100, region: str = None, name: str = None):
    q = db.query(models.Country)
    if region:
        q = q.filter(models.Country.region == region)
    if name:
        q = q.filter(models.Country.name.ilike(f"%{name}%"))
    return q.offset(skip).limit(limit).all()

def create_country(db: Session, data: schemas.CountryCreate):
    obj = models.Country(**data.dict())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

def update_country(db: Session, cca3: str, data: schemas.CountryUpdate):
    obj = get_country(db, cca3)
    if not obj:
        return None
    for k, v in data.dict(exclude_unset=True).items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return obj

def delete_country(db: Session, cca3: str):
    obj = get_country(db, cca3)
    if not obj:
        return None
    db.delete(obj)
    db.commit()
    return obj
