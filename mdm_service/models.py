from sqlalchemy import Column, String, CHAR, BigInteger, Float, ARRAY
from mdm_service.database import Base

class Country(Base):
    __tablename__ = "country"
    cca3       = Column(CHAR(3), primary_key=True, index=True)
    name       = Column(String, nullable=False)
    region     = Column(String)
    subregion  = Column(String)
    population = Column(BigInteger)
    area       = Column(Float)
    capital    = Column(ARRAY(String))

