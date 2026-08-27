from sqlalchemy import Column, BigInteger, String, DECIMAL, Enum, DateTime, TIMESTAMP, ForeignKey
from sqlalchemy.sql import func
from app.database.session import Base
class LedgerEntry(Base):
    __tablename__='ledger_entries'
    id=Column(BigInteger,primary_key=True,autoincrement=True); account_id=Column(BigInteger,ForeignKey('accounts.id'),nullable=False); transaction_reference=Column(String(100),nullable=False); transaction_type=Column(Enum('DEPOSIT','WITHDRAWAL','TRANSFER_DEBIT','TRANSFER_CREDIT','FEE','INTEREST','INTERBANK_DEBIT','INTERBANK_CREDIT','REVERSAL'),nullable=False); debit_amount=Column(DECIMAL(18,2),default=0.00); credit_amount=Column(DECIMAL(18,2),default=0.00); balance_after=Column(DECIMAL(18,2),nullable=False); transaction_date=Column(DateTime,nullable=False); created_at=Column(TIMESTAMP,server_default=func.now())
