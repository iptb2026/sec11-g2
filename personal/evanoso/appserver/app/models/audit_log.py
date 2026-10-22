# ==== LAYER 2: Identity & Access ====
from sqlalchemy import Column, BigInteger, String, Text, JSON, TIMESTAMP, ForeignKey
from sqlalchemy.sql import func

from app.database.session import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=True)
    action_type = Column(String(100), nullable=False)
    entity_name = Column(String(100), nullable=False)
    entity_id = Column(BigInteger, nullable=True)
    old_value = Column(JSON, nullable=True)
    new_value = Column(JSON, nullable=True)
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(Text, nullable=True)
    action_timestamp = Column(TIMESTAMP, server_default=func.now())