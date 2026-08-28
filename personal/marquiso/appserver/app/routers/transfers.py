# ==== LAYER 4: Transactions ====
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.core.security import get_current_user_record
from app.models.account import Account
from app.models.transfer import Transfer
from app.models.user import User
from app.schemas.transfer import TransferCreate, TransferOut

router = APIRouter(prefix="/transfers", tags=["Layer 4 - Transfers"])


@router.post("/", response_model=TransferOut, status_code=status.HTTP_201_CREATED)
def create_transfer(transfer: TransferCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_record)):
    if transfer.source_account_id == transfer.destination_account_id:
        raise HTTPException(status_code=400, detail="source and destination accounts must be different")

    # Lock both accounts for the duration of this transaction so a
    # simultaneous transfer touching either one can't read a stale balance.
    # Locking order matters: always lock the lower id first, or two transfers
    # running in opposite directions at the same time (A->B and B->A) could
    # each be waiting on the row the other one is holding — a deadlock.
    first_id, second_id = sorted([transfer.source_account_id, transfer.destination_account_id])
    accounts_by_id = {
        a.id: a
        for a in db.query(Account).filter(Account.id.in_([first_id, second_id])).with_for_update().all()
    }
    source = accounts_by_id.get(transfer.source_account_id)
    destination = accounts_by_id.get(transfer.destination_account_id)

    if not source:
        raise HTTPException(status_code=400, detail="source_account_id does not exist")
    if not destination:
        raise HTTPException(status_code=400, detail="destination_account_id does not exist")
    if current_user.role_id == 3 and source.customer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Customers can only transfer from their own accounts")

    existing = db.query(Transfer).filter(Transfer.transfer_reference == transfer.transfer_reference).first()
    if existing:
        raise HTTPException(status_code=400, detail="transfer_reference already exists")

    if source.status != "ACTIVE":
        raise HTTPException(status_code=400, detail=f"Source account is {source.status}, cannot transfer")

    if source.available_balance < transfer.amount:
        raise HTTPException(status_code=400, detail="Insufficient balance")

    new_transfer = Transfer(
        **transfer.model_dump(),
        status="SUCCESS",
        completed_at=datetime.utcnow(),
    )
    db.add(new_transfer)

    # Move the money: debit source, credit destination — both accounts,
    # same request, same commit.
    source.available_balance -= transfer.amount
    source.ledger_balance -= transfer.amount
    destination.available_balance += transfer.amount
    destination.ledger_balance += transfer.amount

    db.commit()
    db.refresh(new_transfer)
    return new_transfer


@router.get("/", response_model=list[TransferOut])
def list_transfers(db: Session = Depends(get_db), current_user: User = Depends(get_current_user_record)):
    query = db.query(Transfer)
    if current_user.role_id == 3:
        account_ids = [a.id for a in db.query(Account).filter(Account.customer_id == current_user.id).all()]
        query = query.filter((Transfer.source_account_id.in_(account_ids)) | (Transfer.destination_account_id.in_(account_ids)))
    return query.all()


@router.get("/{transfer_id}", response_model=TransferOut)
def get_transfer(transfer_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_record)):
    transfer = db.query(Transfer).filter(Transfer.id == transfer_id).first()
    if not transfer:
        raise HTTPException(status_code=404, detail="Transfer not found")
    if current_user.role_id == 3:
        account_ids = [a.id for a in db.query(Account).filter(Account.customer_id == current_user.id).all()]
        if transfer.source_account_id not in account_ids and transfer.destination_account_id not in account_ids:
            raise HTTPException(status_code=403, detail="Customers can only view their own transfers")
    return transfer


@router.put("/{transfer_id}", response_model=TransferOut)
def update_transfer(transfer_id: int, data: TransferCreate, db: Session = Depends(get_db)):
    """NOTE: does not move any money back — see the Layer 4 guide."""
    transfer = db.query(Transfer).filter(Transfer.id == transfer_id).first()
    if not transfer:
        raise HTTPException(status_code=404, detail="Transfer not found")

    for field, value in data.model_dump().items():
        setattr(transfer, field, value)

    db.commit()
    db.refresh(transfer)
    return transfer


@router.delete("/{transfer_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transfer(transfer_id: int, db: Session = Depends(get_db)):
    """NOTE: does not move any money back — see the Layer 4 guide."""
    transfer = db.query(Transfer).filter(Transfer.id == transfer_id).first()
    if not transfer:
        raise HTTPException(status_code=404, detail="Transfer not found")

    db.delete(transfer)
    db.commit()