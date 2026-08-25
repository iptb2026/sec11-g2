# ==== LAYER 5: Financial Records & Ledger ====
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.account import Account
from app.models.interest_policy import InterestPolicy
from app.models.interest_record import InterestRecord
from app.schemas.interest_record import InterestRecordCreate, InterestRecordOut

router = APIRouter(prefix="/interest-records", tags=["Layer 5 - Interest Records"])


@router.post("/", response_model=InterestRecordOut, status_code=status.HTTP_201_CREATED)
def create_interest_record(record: InterestRecordCreate, db: Session = Depends(get_db)):
    account = db.query(Account).filter(Account.id == record.account_id).with_for_update().first()
    if not account:
        raise HTTPException(status_code=400, detail="account_id does not exist")

    policy = db.query(InterestPolicy).filter(InterestPolicy.id == record.policy_id).first()
    if not policy:
        raise HTTPException(status_code=400, detail="policy_id does not exist")

    # Snapshot the balance before and after crediting.
    balance_before = account.available_balance
    account.available_balance += record.amount_credited
    account.ledger_balance += record.amount_credited
    balance_after = account.available_balance

    new_record = InterestRecord(
        **record.model_dump(),
        balance_before=balance_before,
        balance_after=balance_after,
    )
    db.add(new_record)

    db.commit()
    db.refresh(new_record)
    return new_record


@router.get("/", response_model=list[InterestRecordOut])
def list_interest_records(db: Session = Depends(get_db)):
    return db.query(InterestRecord).all()


@router.get("/{record_id}", response_model=InterestRecordOut)
def get_interest_record(record_id: int, db: Session = Depends(get_db)):
    record = db.query(InterestRecord).filter(InterestRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Interest record not found")
    return record


@router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_interest_record(record_id: int, db: Session = Depends(get_db)):
    """NOTE: does not reverse the account balance change."""
    record = db.query(InterestRecord).filter(InterestRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Interest record not found")

    db.delete(record)
    db.commit()
