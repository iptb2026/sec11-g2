from sqlalchemy import Column, BigInteger, String, DECIMAL, Enum, Date, ForeignKey
from app.database.session import Base

class InterestPolicy(Base):
    __tablename__ = 'interest_policies'
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    account_type_id = Column(BigInteger, ForeignKey('account_types.id'), nullable=False)
    policy_name = Column(String(100), nullable=False)
    annual_rate = Column(DECIMAL(5, 2), nullable=False)
    compounding_frequency = Column(Enum('DAILY', 'MONTHLY', 'QUARTERLY', 'YEARLY'), default='MONTHLY')
    effective_date = Column(Date, nullable=False)
    expiration_date = Column(Date, nullable=True)
