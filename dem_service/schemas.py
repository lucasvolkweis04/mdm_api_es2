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
    provider_id: Optional[int]
    provider_name: str
    status: str
    raw_path: Optional[str]
    processed_path: Optional[str]
    processed_count: int
    rejected_count: int
    rejected_samples: List[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True