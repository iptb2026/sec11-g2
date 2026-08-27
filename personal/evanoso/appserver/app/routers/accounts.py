from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.db_utils import commit_or_409
from app.database.session import get_db
from app.models.account import Account
from app.models.account_type import AccountType
from app.models.user import User
from app.schemas.account import AccountCreate, AccountUpdate, AccountOut

router = APIRouter(prefix="/accounts", tags=["Layer 3 - Accounts"])


@router.post("/", response_model=AccountOut, status_code=status.HTTP_201_CREATED)
def create_account(account: AccountCreate, db: Session = Depends(get_db)):
    customer = db.query(User).filter(User.id == account.customer_id).first()
    if not customer:
        raise HTTPException(status_code=400, detail="customer_id does not exist")

    account_type = db.query(AccountType).filter(
        AccountType.id == account.account_type_id
    ).first()
    if not account_type:
        raise HTTPException(status_code=400, detail="account_type_id does not exist")

    existing = db.query(Account).filter(
        Account.account_number == account.account_number
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="account_number already exists")

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


from typing import Optional
from app.core.security import get_current_user

@router.get("/", response_model=list[AccountOut])
def list_accounts(customer_id: Optional[int] = None, db: Session = Depends(get_db)):
    query = db.query(Account)
    if customer_id is not None:
        query = query.filter(Account.customer_id == customer_id)
    return query.all()


@router.get("/my", response_model=list[AccountOut])
def get_my_accounts(
    username: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return db.query(Account).filter(Account.customer_id == user.id).all()


@router.get("/{account_id}", response_model=AccountOut)
def get_account(account_id: int, db: Session = Depends(get_db)):
    account = db.query(Account).filter(Account.id == account_id).first()

    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    return account


@router.put("/{account_id}", response_model=AccountOut)
def update_account(
    account_id: int,
    data: AccountUpdate,
    db: Session = Depends(get_db)
):
    account = db.query(Account).filter(Account.id == account_id).first()

    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    customer = db.query(User).filter(User.id == data.customer_id).first()
    if not customer:
        raise HTTPException(status_code=400, detail="customer_id does not exist")

    account_type = db.query(AccountType).filter(
        AccountType.id == data.account_type_id
    ).first()
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
def delete_account(account_id: int, db: Session = Depends(get_db)):
    account = db.query(Account).filter(Account.id == account_id).first()

    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    db.delete(account)

    commit_or_409(
        db,
        "Cannot delete this account — related transactions or records still reference it"
    )
