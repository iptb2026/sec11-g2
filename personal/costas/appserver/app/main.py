from fastapi import FastAPI

from app.core.config import settings
from app.database.session import Base, engine

# ==== LAYER 1: Foundation & Reference Data ====
from app.routers import roles, account_types, banks, fee_types

# Creates tables if they don't already exist
Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION)

# ==== LAYER 1: Foundation & Reference Data ====
app.include_router(roles.router)
app.include_router(account_types.router)
app.include_router(banks.router)
app.include_router(fee_types.router)


@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "app": settings.APP_NAME}