# ==== LAYER 1: Foundation & Reference Data ====
from sqlalchemy import Column, BigInteger, String, Text, TIMESTAMP
from sqlalchemy.sql import func

from app.database.session import Base


class Role(Base):
    __tablename__ = "roles"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    role_code = Column(String(50), unique=True, nullable=False)
    role_name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())