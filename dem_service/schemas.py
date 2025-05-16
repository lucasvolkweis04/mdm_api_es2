from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ProviderBase(BaseModel):
    name: str
    url: str

class ProviderCreate(ProviderBase):
    pass

class Provider(ProviderBase):
    id: int
    class Config:
        orm_mode = True

class ETLMetadata(BaseModel):
    id: int
    provider_id: int
    timestamp: datetime
    status: str
    raw_path: str
    processed_path: str
    class Config:
        orm_mode = True
