from sqlalchemy import Column, Integer, String, CHAR, BigInteger, Float, ARRAY, DateTime, Text, JSON
from dem_service.database import Base
from datetime import datetime

class Provider(Base):
    __tablename__ = "providers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    url = Column(String, nullable=False)

class ETLMetadata(Base):
    __tablename__ = "etl_metadata"
    id = Column(Integer, primary_key=True, index=True)
    provider_id = Column(Integer)
    provider_name = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    status = Column(String)
    raw_path = Column(Text)
    processed_path = Column(Text)
    rejected_count = Column(Integer)
    processed_count = Column(Integer)
    rejected_samples = Column(JSON)  # salva até 5 exemplos de rejeitados

class Country(Base):
    __tablename__ = "country"
    cca3       = Column(CHAR(3), primary_key=True, index=True)
    name       = Column(String, nullable=False)
    region     = Column(String)
    subregion  = Column(String)
    population = Column(BigInteger)
    area       = Column(Float)
    capital    = Column(ARRAY(String))