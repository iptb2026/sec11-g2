from sqlalchemy import Column, BigInteger, String, DECIMAL, Enum, SmallInteger, TIMESTAMP, DateTime, ForeignKey
from sqlalchemy.sql import func

from app.database.session import Base


class Investment(Base):
    __tablename__ = "investments"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    account_id = Column(BigInteger, ForeignKey("accounts.id"), nullable=False)
    plan_code = Column(Enum("SHORT_TERM", "MEDIUM_TERM", "LONG_TERM"), nullable=False)
    term_months = Column(SmallInteger, nullable=False)
    amount = Column(DECIMAL(18, 2), nullable=False)
    status = Column(Enum("ACTIVE", "REDEEMED"), nullable=False, default="ACTIVE")
    created_at = Column(TIMESTAMP, server_default=func.now())
    redeemed_at = Column(DateTime, nullable=True)