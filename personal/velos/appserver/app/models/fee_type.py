# ==== LAYER 1: Foundation & Reference Data ====
from sqlalchemy import Column, BigInteger, String, Text, DECIMAL, TIMESTAMP
from sqlalchemy.sql import func

from app.database.session import Base


class FeeType(Base):
    __tablename__ = "fee_types"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    fee_code = Column(String(50), unique=True, nullable=False)
    fee_name = Column(String(100), nullable=False)
    fee_description = Column(Text, nullable=True)
    fixed_amount = Column(DECIMAL(18, 2), default=0.00)
    percentage_rate = Column(DECIMAL(5, 2), default=0.00)
    created_at = Column(TIMESTAMP, server_default=func.now())