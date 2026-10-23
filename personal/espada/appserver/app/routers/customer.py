from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.security import get_current_admin, get_current_user
from app.database.session import get_db
from app.models.account import Account
from app.models.ledger_entry import LedgerEntry
from app.models.user import User
from app.schemas.account import AccountOut
from app.schemas.ledger_entry import LedgerEntryOut
from app.schemas.user import UserOut

router = APIRouter(prefix="/customer", tags=["Customer Mobile"])


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return user


@router.get("/accounts", response_model=list[AccountOut])
def my_accounts(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return db.query(Account).filter(Account.customer_id == user.id).all()


@router.get("/transactions", response_model=list[LedgerEntryOut])
def my_transactions(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    account_ids = db.query(Account.id).filter(Account.customer_id == user.id)
    return (
        db.query(LedgerEntry)
        .filter(LedgerEntry.account_id.in_(account_ids))
        .order_by(LedgerEntry.transaction_date.desc())
        .all()
    )


@router.get("/admin/accounts")
def admin_accounts(
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    rows = (
        db.query(Account, User)
        .join(User, Account.customer_id == User.id)
        .order_by(User.last_name, User.first_name)
        .all()
    )
    return [
        {
            "id": account.id,
            "account_number": account.account_number,
            "customer_name": f"{customer.first_name} {customer.last_name}",
            "available_balance": account.available_balance,
            "status": account.status,
        }
        for account, customer in rows
    ]
