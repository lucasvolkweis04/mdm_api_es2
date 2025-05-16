from pydantic import BaseModel
from typing import List, Optional

class CountryBase(BaseModel):
    name: str
    region: Optional[str]
    subregion: Optional[str]
    population: Optional[int]
    area: Optional[float]
    capital: Optional[List[str]]

class CountryCreate(CountryBase):
    cca3: str

class CountryUpdate(CountryBase):
    pass

class Country(CountryBase):
    cca3: str
    class Config:
        from_attributes = True  # para compatibilidade com Pydantic v2
