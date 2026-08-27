# ==== LAYER 3: Account Configuration ====
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.db_utils import commit_or_409
from app.core.security import get_current_user_model, require_roles
from app.database.session import get_db
from app.models.account import Account
from app.models.account_type import AccountType
from app.models.role import Role
from app.models.user import User
from app.schemas.account import AccountCreate, AccountUpdate, AccountOut

router = APIRouter(prefix="/accounts", tags=["Layer 3 - Accounts"])


@router.post("/", response_model=AccountOut, status_code=status.HTTP_201_CREATED)
def create_account(
    account: AccountCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN", "STAFF")),
):
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
    # never from the client.
    starting_balance = account_type.opening_deposit

    new_account = Account(
        **account.model_dump(),
        available_balance=starting_balance,
        ledger_balance=starting_balance,
    )
    db.add(new_account)
    db.commit()
    db.refresh(new_account)
    return new_account


@router.get("/", response_model=list[AccountOut])
def list_accounts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_model),
):
    user_role = db.query(Role).filter(Role.id == current_user.role_id).first()
    # Customer can only view their own accounts
    if user_role and user_role.role_code == "CUSTOMER":
        return db.query(Account).filter(Account.customer_id == current_user.id).all()

    # Admin and Staff see all accounts
    return db.query(Account).all()


@router.get("/{account_id}", response_model=AccountOut)
def get_account(
    account_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_model),
):
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    user_role = db.query(Role).filter(Role.id == current_user.role_id).first()
    if user_role and user_role.role_code == "CUSTOMER" and account.customer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: You do not have permission to access another customer's account",
        )

    return account


@router.put("/{account_id}", response_model=AccountOut)
def update_account(
    account_id: int,
    data: AccountUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN", "STAFF")),
):
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    customer = db.query(User).filter(User.id == data.customer_id).first()
    if not customer:
        raise HTTPException(status_code=400, detail="customer_id does not exist")

    account_type = db.query(AccountType).filter(AccountType.id == data.account_type_id).first()
    if not account_type:
        raise HTTPException(status_code=400, detail="account_type_id does not exist")

    if data.status == "CLOSED" and account.status != "CLOSED":
        account.closed_at = datetime.utcnow()

    for field, value in data.model_dump().items():
        setattr(account, field, value)

    db.commit()
    db.refresh(account)
    return account


@router.delete("/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_account(
    account_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN", "STAFF")),
):
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    db.delete(account)
    commit_or_409(db, "Cannot delete this account — related transactions or records still reference it")