"""
Database engine, session factory, and declarative base.
"""

from sqlalchemy import BigInteger, create_engine
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import settings

@compiles(BigInteger, 'sqlite')
def sqlite_bigint(element, compiler, **kwargs):
    return 'INTEGER'


database_url = settings.DATABASE_URL
engine = create_engine(database_url, pool_pre_ping=True, connect_args={'check_same_thread': False} if database_url.startswith('sqlite:') else {})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """FastAPI dependency that yields a DB session and closes it afterwards."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
