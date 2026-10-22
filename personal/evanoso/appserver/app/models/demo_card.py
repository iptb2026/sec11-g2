from sqlalchemy import Column, Integer, BigInteger, String, DECIMAL, ForeignKey
from app.database.session import Base


class DemoCard(Base):
    __tablename__ = "demo_cards"
    id = Column(Integer, primary_key=True, autoincrement=True)
    account_id = Column(BigInteger, ForeignKey("accounts.id"), nullable=False, unique=True)
    status = Column(String(12), nullable=False, default="ACTIVE")
    spending_limit = Column(DECIMAL(18, 2), nullable=False, default=10000)
    pin_hash = Column(String(255), nullable=True)
