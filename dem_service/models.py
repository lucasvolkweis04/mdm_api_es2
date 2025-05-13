import enum
from sqlalchemy import (
    Column, Integer, String, Enum, Text,
    TIMESTAMP, func
)
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class ETLStatus(enum.Enum):
    pending = "pending"
    running = "running"
    success = "success"
    failure = "failure"

class ETLTransaction(Base):
    __tablename__ = "etl_transaction"
    id         = Column(Integer, primary_key=True, index=True)
    type       = Column(String, nullable=False)          # extract/transform/load
    status     = Column(Enum(ETLStatus), default=ETLStatus.pending)
    logs       = Column(Text)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )