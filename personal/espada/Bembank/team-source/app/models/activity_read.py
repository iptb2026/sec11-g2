from sqlalchemy import Column, BigInteger, String, ForeignKey
from app.database.session import Base


class ActivityRead(Base):
    __tablename__ = "activity_reads"
    user_id = Column(BigInteger, ForeignKey("users.id"), primary_key=True)
    event_key = Column(String(128), primary_key=True)
