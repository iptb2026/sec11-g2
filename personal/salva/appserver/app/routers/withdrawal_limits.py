# ==== LAYER 3: Account Configuration ====
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user_model, require_roles
from app.database.session import get_db
from app.models.account import Account
from app.models.user import User
from app.models.withdrawal_limit import WithdrawalLimit
from app.schemas.withdrawal_limit import WithdrawalLimitCreate, WithdrawalLimitUpdate, WithdrawalLimitOut

router = APIRouter(prefix="/withdrawal-limits", tags=["Layer 3 - Withdrawal Limits"])


@router.post("/", response_model=WithdrawalLimitOut, status_code=status.HTTP_201_CREATED)
def create_withdrawal_limit(
    data: WithdrawalLimitCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN", "STAFF")),
):
    account = db.query(Account).filter(Account.id == data.account_id).first()
    if not account:
        raise HTTPException(status_code=400, detail="account_id does not exist")

    # account_id is UNIQUE on this table — one account has at most one withdrawal_limits row.
    existing = db.query(WithdrawalLimit).filter(WithdrawalLimit.account_id == data.account_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="This account already has a withdrawal limit")

    new_limit = WithdrawalLimit(**data.model_dump())
    db.add(new_limit)
    db.commit()
    db.refresh(new_limit)
    return new_limit


@router.get("/", response_model=list[WithdrawalLimitOut])
def list_withdrawal_limits(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_model),
):
    return db.query(WithdrawalLimit).all()


@router.get("/{limit_id}", response_model=WithdrawalLimitOut)
def get_withdrawal_limit(
    limit_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_model),
):
    limit = db.query(WithdrawalLimit).filter(WithdrawalLimit.id == limit_id).first()
    if not limit:
        raise HTTPException(status_code=404, detail="Withdrawal limit not found")
    return limit


@router.put("/{limit_id}", response_model=WithdrawalLimitOut)
def update_withdrawal_limit(
    limit_id: int,
    data: WithdrawalLimitUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN", "STAFF")),
):
    limit = db.query(WithdrawalLimit).filter(WithdrawalLimit.id == limit_id).first()
    if not limit:
        raise HTTPException(status_code=404, detail="Withdrawal limit not found")

    limit.daily_limit_amount = data.daily_limit_amount
    limit.last_reset_date = data.last_reset_date

    db.commit()
    db.refresh(limit)
    return limit


@router.delete("/{limit_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_withdrawal_limit(
    limit_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN", "STAFF")),
):
    limit = db.query(WithdrawalLimit).filter(WithdrawalLimit.id == limit_id).first()
    if not limit:
        raise HTTPException(status_code=404, detail="Withdrawal limit not found")

    db.delete(limit)
    db.commit()