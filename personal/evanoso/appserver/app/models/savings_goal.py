from sqlalchemy import Column, Integer, BigInteger, String, DECIMAL, ForeignKey
from app.database.session import Base


class SavingsGoal(Base):
    __tablename__ = "savings_goals"
    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(BigInteger, ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String(80), nullable=False)
    target_amount = Column(DECIMAL(18, 2), nullable=False)
    saved_amount = Column(DECIMAL(18, 2), nullable=False, default=0)
