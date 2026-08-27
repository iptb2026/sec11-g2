# ==== LAYER 1: Foundation & Reference Data ====
from sqlalchemy import Column, Integer, String, Enum, TIMESTAMP
from sqlalchemy.sql import func

from app.database.session import Base


class Bank(Base):
    __tablename__ = "banks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    bank_code = Column(String(50), unique=True, nullable=False)
    swift_code = Column(String(50), nullable=True)
    bank_name = Column(String(150), nullable=False)
    short_name = Column(String(100), nullable=True)
    api_endpoint = Column(String(255), nullable=True)
    contact_email = Column(String(150), nullable=True)
    status = Column(Enum("ACTIVE", "INACTIVE"), default="ACTIVE")
    created_at = Column(TIMESTAMP, server_default=func.now())

    