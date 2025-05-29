from sqlalchemy import Column, Integer, String, DateTime, Text, JSON
from datetime import datetime
from dem_service.database import Base


class Provider(Base):
    __tablename__ = "providers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    url = Column(String, nullable=False)

class ETLMetadata(Base):
    __tablename__ = "etl_metadata"

    id = Column(Integer, primary_key=True, index=True)
    provider_id = Column(Integer, nullable=True)
    provider_name = Column(String, nullable=False)
    status = Column(String, nullable=False)
    raw_path = Column(Text, nullable=True)
    processed_path = Column(Text, nullable=True)
    rejected_count = Column(Integer, nullable=False)
    processed_count = Column(Integer, nullable=False)
    rejected_samples = Column(JSON, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    