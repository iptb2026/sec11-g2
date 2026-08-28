from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.database.session import Base, engine, SessionLocal
from app.core.security import hash_password
from app.models.role import Role
from app.models.user import User
from app.core.security import require_roles

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

db = SessionLocal()
for username, password, role_code, first_name, last_name in [
    ("staff1", "StaffPass123!", "STAFF", "Bank", "Staff"),
    ("manager1", "ManagerPass123!", "MANAGER", "Bank", "Manager"),
]:
    role = db.query(Role).filter(Role.role_code == role_code).first()
    if role and not db.query(User).filter(User.username == username).first():
        db.add(User(
            username=username,
            hashed_password=hash_password(password),
            first_name=first_name,
            last_name=last_name,
            role_id=role.id,
            account_status="ACTIVE",
        ))
db.commit()
db.close()

app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION)

# Allows the Quasar frontend to call this API from the browser.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:9000",
        "http://127.0.0.1:9000",
        "http://172.17.100.14:9000",
        "http://172.17.0.2:9000",
        "http://localhost:9001",
        "http://127.0.0.1:9001",
        "http://172.17.100.14:9001",
        "http://172.17.0.2:9001",
        "http://localhost:8080",
        "http://127.0.0.1:8080",
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==== LAYER 1: Foundation & Reference Data ====
app.include_router(roles.router, dependencies=[Depends(require_roles("ADMIN"))])
app.include_router(account_types.router, dependencies=[Depends(require_roles("ADMIN", "MANAGER"))])
app.include_router(banks.router, dependencies=[Depends(require_roles("ADMIN", "MANAGER"))])
app.include_router(fee_types.router, dependencies=[Depends(require_roles("ADMIN", "MANAGER"))])

# ==== LAYER 2: Identity & Access ====
app.include_router(users.router, dependencies=[Depends(require_roles("ADMIN"))])
app.include_router(auth.router)
app.include_router(sessions.router, dependencies=[Depends(require_roles("ADMIN", "MANAGER"))])
app.include_router(audit_logs.router, dependencies=[Depends(require_roles("ADMIN", "MANAGER", "AUDITOR"))])

# ==== LAYER 3: Account Configuration ====
app.include_router(accounts.router, dependencies=[Depends(require_roles("ADMIN", "MANAGER", "STAFF", "CUSTOMER"))])
app.include_router(withdrawal_limits.router, dependencies=[Depends(require_roles("ADMIN", "MANAGER"))])
app.include_router(interest_policies.router, dependencies=[Depends(require_roles("ADMIN", "MANAGER"))])

# ==== LAYER 4: Transactions ====
app.include_router(deposits.router, dependencies=[Depends(require_roles("ADMIN", "MANAGER", "STAFF", "CUSTOMER"))])
app.include_router(withdrawals.router, dependencies=[Depends(require_roles("ADMIN", "MANAGER", "STAFF", "CUSTOMER"))])
app.include_router(transfers.router, dependencies=[Depends(require_roles("ADMIN", "MANAGER", "STAFF", "CUSTOMER"))])
app.include_router(interbank_transfers.router, dependencies=[Depends(require_roles("ADMIN", "MANAGER", "STAFF"))])

# ==== LAYER 5: Financial Records & Ledger ====
app.include_router(fee_records.router, dependencies=[Depends(require_roles("ADMIN", "MANAGER"))])
app.include_router(interest_records.router, dependencies=[Depends(require_roles("ADMIN", "MANAGER"))])
app.include_router(ledger_entries.router, dependencies=[Depends(require_roles("ADMIN", "MANAGER"))])


@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "app": settings.APP_NAME}