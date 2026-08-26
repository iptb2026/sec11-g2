from fastapi import FastAPI

from app.core.config import settings
from app.database.session import Base, engine

# ==== LAYER 1: Foundation & Reference Data ====
from app.routers import roles, account_types, banks, fee_types

# ==== LAYER 2: Identity & Access ====
from app.routers import users, auth, sessions, audit_logs

# ==== LAYER 3: Account Configuration ====
from app.routers import accounts, withdrawal_limits, interest_policies

# ==== LAYER 4: Transactions ====
from app.routers import deposits, withdrawals, transfers, interbank_transfers

# ==== LAYER 5: Financial Records & Ledger ====
from app.routers import fee_records, interest_records, ledger_entries

# Creates tables if they don't already exist
Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION)

# ==== LAYER 1: Foundation & Reference Data ====
app.include_router(roles.router)
app.include_router(account_types.router)
app.include_router(banks.router)
app.include_router(fee_types.router)

# ==== LAYER 2: Identity & Access ====
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(sessions.router)
app.include_router(audit_logs.router)

# ==== LAYER 3: Account Configuration ====
app.include_router(accounts.router)
app.include_router(withdrawal_limits.router)
app.include_router(interest_policies.router)

# ==== LAYER 4: Transactions ====
app.include_router(deposits.router)
app.include_router(withdrawals.router)
app.include_router(transfers.router)
app.include_router(interbank_transfers.router)

# ==== LAYER 5: Financial Records & Ledger ====
from app.routers import fee_records, interest_records, ledger_entries
app.include_router(fee_records.router)
app.include_router(interest_records.router)
app.include_router(ledger_entries.router)

@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "app": settings.APP_NAME}
