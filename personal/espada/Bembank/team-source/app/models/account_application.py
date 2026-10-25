from sqlalchemy import Column, Integer, BigInteger, String, ForeignKey, DateTime
from datetime import datetime
from app.database.session import Base


class AccountApplication(Base):
    __tablename__ = "account_applications"
    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(BigInteger, ForeignKey("users.id"), nullable=False, index=True)
    account_type_id = Column(BigInteger, ForeignKey("account_types.id"), nullable=False)
    status = Column(String(16), nullable=False, default="PENDING")
    account_number = Column(String(30), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
