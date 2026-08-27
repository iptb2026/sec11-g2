# ==== LAYER 4: Transactions ====
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user_model, require_roles
from app.database.session import get_db
from app.models.account import Account
from app.models.role import Role
from app.models.user import User
from app.models.withdrawal import Withdrawal
from app.models.withdrawal_limit import WithdrawalLimit
from app.schemas.withdrawal import WithdrawalCreate, WithdrawalOut

router = APIRouter(prefix="/withdrawals", tags=["Layer 4 - Withdrawals"])


@router.post("/", response_model=WithdrawalOut, status_code=status.HTTP_201_CREATED)
def create_withdrawal(
    withdrawal: WithdrawalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN", "STAFF")),
):
    # Lock the account row for the duration of this transaction — without
    # this, two withdrawals submitted at nearly the same moment could both
    # read the same starting balance and one of their deductions would be
    # silently lost (a "lost update").
    account = db.query(Account).filter(Account.id == withdrawal.account_id).with_for_update().first()
    if not account:
        raise HTTPException(status_code=400, detail="account_id does not exist")

    if withdrawal.approved_by_user_id is not None:
        user = db.query(User).filter(User.id == withdrawal.approved_by_user_id).first()
        if not user:
            raise HTTPException(status_code=400, detail="approved_by_user_id does not exist")

    existing = db.query(Withdrawal).filter(Withdrawal.reference_number == withdrawal.reference_number).first()
    if existing:
        raise HTTPException(status_code=400, detail="reference_number already exists")

    if account.status != "ACTIVE":
        raise HTTPException(status_code=400, detail=f"Account is {account.status}, cannot withdraw")

    if account.available_balance < withdrawal.amount:
        raise HTTPException(status_code=400, detail="Insufficient balance")

    # If this account has a daily withdrawal limit (Layer 3), enforce it.
    limit = db.query(WithdrawalLimit).filter(WithdrawalLimit.account_id == account.id).with_for_update().first()
    if limit and (limit.daily_used_amount + withdrawal.amount) > limit.daily_limit_amount:
        raise HTTPException(status_code=400, detail="This withdrawal would exceed the daily withdrawal limit")

    new_withdrawal = Withdrawal(**withdrawal.model_dump())
    db.add(new_withdrawal)

    account.available_balance -= withdrawal.amount
    account.ledger_balance -= withdrawal.amount
    if limit:
        limit.daily_used_amount += withdrawal.amount

    db.commit()
    db.refresh(new_withdrawal)
    return new_withdrawal


@router.get("/", response_model=list[WithdrawalOut])
def list_withdrawals(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_model),
):
    user_role = db.query(Role).filter(Role.id == current_user.role_id).first()
    if user_role and user_role.role_code == "CUSTOMER":
        user_account_ids = [a.id for a in db.query(Account).filter(Account.customer_id == current_user.id).all()]
        return db.query(Withdrawal).filter(Withdrawal.account_id.in_(user_account_ids)).all()

    return db.query(Withdrawal).all()


@router.get("/{withdrawal_id}", response_model=WithdrawalOut)
def get_withdrawal(
    withdrawal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_model),
):
    withdrawal = db.query(Withdrawal).filter(Withdrawal.id == withdrawal_id).first()
    if not withdrawal:
        raise HTTPException(status_code=404, detail="Withdrawal not found")

    user_role = db.query(Role).filter(Role.id == current_user.role_id).first()
    if user_role and user_role.role_code == "CUSTOMER":
        account = db.query(Account).filter(Account.id == withdrawal.account_id).first()
        if not account or account.customer_id != current_user.id:
            raise HTTPException(status_code=403, detail="Forbidden: You do not have access to this withdrawal")

    return withdrawal


@router.put("/{withdrawal_id}", response_model=WithdrawalOut)
def update_withdrawal(
    withdrawal_id: int,
    data: WithdrawalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN", "STAFF")),
):
    """NOTE: does not re-adjust the account balance or the daily limit usage."""
    withdrawal = db.query(Withdrawal).filter(Withdrawal.id == withdrawal_id).first()
    if not withdrawal:
        raise HTTPException(status_code=404, detail="Withdrawal not found")

    for field, value in data.model_dump().items():
        setattr(withdrawal, field, value)

    db.commit()
    db.refresh(withdrawal)
    return withdrawal


@router.delete("/{withdrawal_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_withdrawal(
    withdrawal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN", "STAFF")),
):
    """NOTE: does not reverse the account balance or the daily limit usage."""
    withdrawal = db.query(Withdrawal).filter(Withdrawal.id == withdrawal_id).first()
    if not withdrawal:
        raise HTTPException(status_code=404, detail="Withdrawal not found")

    db.delete(withdrawal)
    db.commit()