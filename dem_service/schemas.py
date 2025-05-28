from pydantic import BaseModel
from typing import List, Optional
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
    provider_name: str
    status: str
    processed_count: int
    rejected_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
     from_attributes = True
     arbitrary_types_allowed = True
