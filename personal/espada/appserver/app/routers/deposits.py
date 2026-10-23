# ==== LAYER 4: Transactions ====
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.core.security import get_current_admin
from app.models.account import Account
from app.models.deposit import Deposit
from app.models.ledger_entry import LedgerEntry
from app.models.user import User
from app.schemas.deposit import DepositCreate, DepositOut

router = APIRouter(prefix="/deposits", tags=["Layer 4 - Deposits"])


@router.post("/", response_model=DepositOut, status_code=status.HTTP_201_CREATED)
def create_deposit(
    deposit: DepositCreate,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    account = (
        db.query(Account)
        .filter(Account.id == deposit.account_id)
        .with_for_update()
        .first()
    )

    if not account:
        raise HTTPException(status_code=400, detail="account_id does not exist")

    if deposit.deposited_by_user_id is not None:
        user = db.query(User).filter(User.id == deposit.deposited_by_user_id).first()
        if not user:
            raise HTTPException(
                status_code=400,
                detail="deposited_by_user_id does not exist",
            )

    existing = (
        db.query(Deposit)
        .filter(Deposit.reference_number == deposit.reference_number)
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=400,
            detail="reference_number already exists",
        )

    new_deposit = Deposit(**deposit.model_dump(exclude={"deposited_by_user_id"}), deposited_by_user_id=admin.id)
    db.add(new_deposit)

    account.available_balance += deposit.amount
    account.ledger_balance += deposit.amount
    db.add(LedgerEntry(
        account_id=account.id,
        transaction_reference=deposit.reference_number,
        transaction_type="DEPOSIT",
        credit_amount=deposit.amount,
        debit_amount=0,
        balance_after=account.available_balance,
        transaction_date=deposit.transaction_date,
    ))

    db.commit()
    db.refresh(new_deposit)

    return new_deposit


@router.get("/", response_model=list[DepositOut])
def list_deposits(db: Session = Depends(get_db)):
    return db.query(Deposit).all()


@router.get("/{deposit_id}", response_model=DepositOut)
def get_deposit(deposit_id: int, db: Session = Depends(get_db)):
    deposit = db.query(Deposit).filter(Deposit.id == deposit_id).first()

    if not deposit:
        raise HTTPException(status_code=404, detail="Deposit not found")

    return deposit


@router.put("/{deposit_id}", response_model=DepositOut)
def update_deposit(
    deposit_id: int,
    data: DepositCreate,
    db: Session = Depends(get_db),
):
    deposit = db.query(Deposit).filter(Deposit.id == deposit_id).first()

    if not deposit:
        raise HTTPException(status_code=404, detail="Deposit not found")

    for field, value in data.model_dump().items():
        setattr(deposit, field, value)

    db.commit()
    db.refresh(deposit)

    return deposit


@router.delete("/{deposit_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_deposit(deposit_id: int, db: Session = Depends(get_db)):
    deposit = db.query(Deposit).filter(Deposit.id == deposit_id).first()

    if not deposit:
        raise HTTPException(status_code=404, detail="Deposit not found")

    db.delete(deposit)
    db.commit()
