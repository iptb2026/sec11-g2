# ==== LAYER 4: Transactions ====
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.core.security import get_current_user_record
from app.models.account import Account
from app.models.deposit import Deposit
from app.models.user import User
from app.schemas.deposit import DepositCreate, DepositOut

router = APIRouter(prefix="/deposits", tags=["Layer 4 - Deposits"])


@router.post("/", response_model=DepositOut, status_code=status.HTTP_201_CREATED)
def create_deposit(deposit: DepositCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_record)):
    # .with_for_update() locks this account row until the commit below, so a
    # second request touching the same account has to wait its turn instead
    # of reading a stale balance and silently overwriting this change.
    account = db.query(Account).filter(Account.id == deposit.account_id).with_for_update().first()
    if not account:
        raise HTTPException(status_code=400, detail="account_id does not exist")
    if current_user.role_id == 3 and account.customer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Customers can only deposit into their own accounts")

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

    db.commit()
    db.refresh(new_deposit)
    return new_deposit


@router.get("/", response_model=list[DepositOut])
def list_deposits(db: Session = Depends(get_db), current_user: User = Depends(get_current_user_record)):
    query = db.query(Deposit)
    if current_user.role_id == 3:
        query = query.join(Account).filter(Account.customer_id == current_user.id)
    return query.all()


@router.get("/{deposit_id}", response_model=DepositOut)
def get_deposit(deposit_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_record)):
    deposit = db.query(Deposit).filter(Deposit.id == deposit_id).first()
    if not deposit:
        raise HTTPException(status_code=404, detail="Deposit not found")
    if current_user.role_id == 3 and deposit.account_id not in [a.id for a in db.query(Account).filter(Account.customer_id == current_user.id).all()]:
        raise HTTPException(status_code=403, detail="Customers can only view their own deposits")
    return deposit


@router.put("/{deposit_id}", response_model=DepositOut)
def update_deposit(deposit_id: int, data: DepositCreate, db: Session = Depends(get_db)):
    """
    NOTE: this only edits the deposit record itself (e.g. fixing a typo in
    `remarks`). It does NOT re-adjust the account balance for the amount
    difference. Real banking systems never edit a posted transaction for
    exactly this reason — see the Layer 4 guide for why.
    """
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
    """NOTE: does not reverse the account balance change either — see the Layer 4 guide."""
    deposit = db.query(Deposit).filter(Deposit.id == deposit_id).first()
    if not deposit:
        raise HTTPException(status_code=404, detail="Deposit not found")

    db.delete(deposit)
    db.commit()