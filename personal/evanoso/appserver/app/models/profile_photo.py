from sqlalchemy import Column, BigInteger, ForeignKey, LargeBinary
from app.database.session import Base


class ProfilePhoto(Base):
    __tablename__ = "profile_photos"
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    image = Column(LargeBinary, nullable=False)
