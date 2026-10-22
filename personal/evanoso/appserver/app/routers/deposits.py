# ==== LAYER 4: Transactions ====
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.audit import record_audit_event
from app.core.db_utils import commit_or_409
from app.database.session import get_db
from app.models.account import Account
from app.models.deposit import Deposit
from app.models.user import User
from app.schemas.deposit import DepositCreate, DepositOut

router = APIRouter(prefix="/deposits", tags=["Layer 4 - Deposits"])


@router.post("/", response_model=DepositOut, status_code=status.HTTP_201_CREATED)
def create_deposit(deposit: DepositCreate, request: Request, db: Session = Depends(get_db)):
    # .with_for_update() locks this account row until the commit below, so a
    # second request touching the same account has to wait its turn instead
    # of reading a stale balance and silently overwriting this change.
    account = db.query(Account).filter(Account.id == deposit.account_id).with_for_update().first()
    if not account:
        raise HTTPException(status_code=400, detail="account_id does not exist")

    if deposit.deposited_by_user_id is not None:
        user = db.query(User).filter(User.id == deposit.deposited_by_user_id).first()
        if not user:
            raise HTTPException(status_code=400, detail="deposited_by_user_id does not exist")

    existing = db.query(Deposit).filter(Deposit.reference_number == deposit.reference_number).first()
    if existing:
        raise HTTPException(status_code=400, detail="reference_number already exists")

    new_deposit = Deposit(**deposit.model_dump())
    db.add(new_deposit)

    # This is the actual point of a deposit: money enters the account.
    account.available_balance += deposit.amount
    account.ledger_balance += deposit.amount

    db.flush()
    record_audit_event(
        db,
        request,
        "CREATE",
        "deposits",
        new_deposit.id,
        new_value={
            "account_id": deposit.account_id,
            "reference_number": deposit.reference_number,
            "amount": str(deposit.amount),
            "deposit_channel": deposit.deposit_channel,
        },
    )
    commit_or_409(db, "Deposit conflicts with an existing record")
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
def update_deposit(deposit_id: int, data: DepositCreate, db: Session = Depends(get_db)):
    if not db.query(Deposit.id).filter(Deposit.id == deposit_id).first():
        raise HTTPException(status_code=404, detail="Deposit not found")
    raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail="Posted deposits cannot be edited; create a correcting transaction",
    )


@router.delete("/{deposit_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_deposit(deposit_id: int, db: Session = Depends(get_db)):
    if not db.query(Deposit.id).filter(Deposit.id == deposit_id).first():
        raise HTTPException(status_code=404, detail="Deposit not found")
    raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail="Posted deposits cannot be deleted; create a correcting withdrawal",
    )