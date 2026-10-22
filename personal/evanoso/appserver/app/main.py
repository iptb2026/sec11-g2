from fastapi import FastAPI, Depends
from app.core.security import require_roles, reference_access
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.database.session import Base, engine

# ==== LAYER 1: Foundation & Reference Data ====
from app.routers import roles, account_types, banks, fee_types

# ==== LAYER 2: Identity & Access ====
from app.routers import google_auth, users, auth, sessions, audit_logs, customer_banking, banking_requests, cards, account_applications, otp, activity

# ==== LAYER 3: Account Configuration ====
from app.routers import accounts, withdrawal_limits, interest_policies, project_features, concept_features

# ==== LAYER 4: Transactions ====
from app.routers import deposits, withdrawals, transfers, interbank_transfers

# ==== LAYER 5: Financial Records & Ledger ====
from app.routers import fee_records, interest_records, ledger_entries

# Creates tables if they don't already exist
Base.metadata.create_all(bind=engine)
from sqlalchemy.orm import Session
from app.core.project_defaults import ensure_project_defaults
with Session(engine) as reference_db:
    ensure_project_defaults(reference_db)

app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION)

# Allows the Quasar frontend (a different origin/port, e.g. http://localhost:9000)
# to call this API from the browser. Wide open here since this is a learning
# project with no real users; a production app would restrict allow_origins.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==== LAYER 1: Foundation & Reference Data ====
admin_access = [Depends(require_roles("ADMIN"))]
operations_access = [Depends(require_roles("ADMIN", "STAFF"))]
app.include_router(roles.router, dependencies=admin_access)
app.include_router(account_types.router, dependencies=[Depends(reference_access)])
app.include_router(banks.router, dependencies=[Depends(reference_access)])
app.include_router(fee_types.router, dependencies=[Depends(reference_access)])

# ==== LAYER 2: Identity & Access ====
app.include_router(users.router, dependencies=operations_access)
app.include_router(auth.router)
app.include_router(google_auth.router)
app.include_router(otp.router)
app.include_router(activity.router)
app.include_router(sessions.router, dependencies=admin_access)
app.include_router(audit_logs.router, dependencies=admin_access)
app.include_router(customer_banking.router)
app.include_router(project_features.router)
app.include_router(concept_features.router)
app.include_router(banking_requests.router)
app.include_router(cards.router)
app.include_router(account_applications.router)

# ==== LAYER 3: Account Configuration ====
app.include_router(accounts.router, dependencies=operations_access)
app.include_router(withdrawal_limits.router, dependencies=operations_access)
app.include_router(interest_policies.router, dependencies=operations_access)

# ==== LAYER 4: Transactions ====
app.include_router(deposits.router, dependencies=operations_access)
app.include_router(withdrawals.router, dependencies=operations_access)
app.include_router(transfers.router, dependencies=operations_access)
app.include_router(interbank_transfers.router, dependencies=operations_access)

# ==== LAYER 5: Financial Records & Ledger ====
app.include_router(fee_records.router, dependencies=operations_access)
app.include_router(interest_records.router, dependencies=operations_access)
app.include_router(ledger_entries.router, dependencies=operations_access)


@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "app": settings.APP_NAME}
