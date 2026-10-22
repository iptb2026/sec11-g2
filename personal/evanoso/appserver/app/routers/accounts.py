# ==== LAYER 3: Account Configuration ====
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.audit import record_audit_event
from app.core.db_utils import commit_or_409
from app.database.session import get_db
from app.models.account import Account
from app.models.account_type import AccountType
from app.models.user import User
from app.schemas.account import AccountCreate, AccountUpdate, AccountOut

router = APIRouter(prefix="/accounts", tags=["Layer 3 - Accounts"])


@router.post("/", response_model=AccountOut, status_code=status.HTTP_201_CREATED)
def create_account(account: AccountCreate, request: Request, db: Session = Depends(get_db)):
    customer = db.query(User).filter(User.id == account.customer_id).first()
    if not customer:
        raise HTTPException(status_code=400, detail="customer_id does not exist")

    account_type = db.query(AccountType).filter(AccountType.id == account.account_type_id).first()
    if not account_type:
        raise HTTPException(status_code=400, detail="account_type_id does not exist")

    existing = db.query(Account).filter(Account.account_number == account.account_number).first()
    if existing:
        raise HTTPException(status_code=400, detail="account_number already exists")

    # The starting balance comes from the account type's opening_deposit —
    # never from the client. This is the same "don't trust the client with
    # money fields" lesson from AccountCreate in the old single-table version.
    starting_balance = account_type.opening_deposit

    new_account = Account(
        **account.model_dump(),
        available_balance=starting_balance,
        ledger_balance=starting_balance,
    )
    db.add(new_account)
    db.flush()
    record_audit_event(
        db,
        request,
        "CREATE",
        "accounts",
        new_account.id,
        new_value={
            "account_number": new_account.account_number,
            "customer_id": new_account.customer_id,
            "account_type_id": new_account.account_type_id,
            "opening_balance": str(starting_balance),
        },
    )
    commit_or_409(db, "Account conflicts with an existing record")
    db.refresh(new_account)
    return new_account


@router.get("/", response_model=list[AccountOut])
def list_accounts(db: Session = Depends(get_db)):
    return db.query(Account).all()


@router.get("/{account_id}", response_model=AccountOut)
def get_account(account_id: int, db: Session = Depends(get_db)):
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return account


@router.put("/{account_id}", response_model=AccountOut)
def update_account(account_id: int, data: AccountUpdate, request: Request, db: Session = Depends(get_db)):
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    customer = db.query(User).filter(User.id == data.customer_id).first()
    if not customer:
        raise HTTPException(status_code=400, detail="customer_id does not exist")

    account_type = db.query(AccountType).filter(AccountType.id == data.account_type_id).first()
    if not account_type:
        raise HTTPException(status_code=400, detail="account_type_id does not exist")

    old_value = {
        "account_number": account.account_number,
        "customer_id": account.customer_id,
        "account_type_id": account.account_type_id,
        "status": account.status,
    }
    if data.status == "CLOSED" and account.status != "CLOSED":
        account.closed_at = datetime.utcnow()

    for field, value in data.model_dump().items():
        setattr(account, field, value)

    record_audit_event(
        db,
        request,
        "UPDATE",
        "accounts",
        account.id,
        old_value=old_value,
        new_value={
            "account_number": account.account_number,
            "customer_id": account.customer_id,
            "account_type_id": account.account_type_id,
            "status": account.status,
        },
    )
    commit_or_409(db, "Account update conflicts with an existing record")
    db.refresh(account)
    return account


@router.delete("/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_account(account_id: int, request: Request, db: Session = Depends(get_db)):
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    old_value = {
        "account_number": account.account_number,
        "customer_id": account.customer_id,
        "status": account.status,
        "available_balance": str(account.available_balance),
    }
    db.delete(account)
    record_audit_event(db, request, "DELETE", "accounts", account_id, old_value=old_value)
    commit_or_409(db, "Cannot delete this account — related transactions or records still reference it")