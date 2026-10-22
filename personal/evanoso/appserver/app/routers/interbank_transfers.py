# ==== LAYER 4: Transactions ====
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.audit import record_audit_event
from app.core.db_utils import commit_or_409
from app.database.session import get_db
from app.models.account import Account
from app.models.bank import Bank
from app.models.interbank_transfer import InterbankTransfer
from app.schemas.interbank_transfer import (
    InterbankTransferCreate,
    InterbankTransferStatusUpdate,
    InterbankTransferOut,
)

router = APIRouter(prefix="/interbank-transfers", tags=["Layer 4 - Interbank Transfers"])


@router.post("/", response_model=InterbankTransferOut, status_code=status.HTTP_201_CREATED)
def create_interbank_transfer(
    transfer: InterbankTransferCreate, request: Request, db: Session = Depends(get_db)
):
    # Lock the source account row for the duration of this transaction — see
    # the same note in deposits.py / withdrawals.py.
    source = db.query(Account).filter(Account.id == transfer.source_account_id).with_for_update().first()
    if not source:
        raise HTTPException(status_code=400, detail="source_account_id does not exist")

    bank = db.query(Bank).filter(Bank.id == transfer.target_bank_id).first()
    if not bank:
        raise HTTPException(status_code=400, detail="target_bank_id does not exist")

    existing = db.query(InterbankTransfer).filter(
        InterbankTransfer.reference_number == transfer.reference_number
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="reference_number already exists")

    if source.status != "ACTIVE":
        raise HTTPException(status_code=400, detail=f"Source account is {source.status}, cannot transfer")

    total_debit = transfer.amount + transfer.transfer_fee
    if source.available_balance < total_debit:
        raise HTTPException(status_code=400, detail="Insufficient balance to cover amount + transfer fee")

    # Unlike an internal `transfer`, the destination bank is external — we
    # can only debit our own side. The transfer starts PROCESSING (not
    # SUCCESS) because settlement with the other bank isn't instant; use
    # PUT /interbank-transfers/{id}/status to move it to SUCCESS/FAILED later.
    new_transfer = InterbankTransfer(**transfer.model_dump(), status="PROCESSING")
    db.add(new_transfer)

    source.available_balance -= total_debit
    source.ledger_balance -= total_debit

    db.flush()
    record_audit_event(
        db,
        request,
        "CREATE",
        "interbank_transfers",
        new_transfer.id,
        new_value={
            "source_account_id": transfer.source_account_id,
            "target_bank_id": transfer.target_bank_id,
            "reference_number": transfer.reference_number,
            "amount": str(transfer.amount),
            "transfer_fee": str(transfer.transfer_fee),
            "status": new_transfer.status,
        },
    )
    commit_or_409(db, "Interbank transfer conflicts with an existing record")
    db.refresh(new_transfer)
    return new_transfer


@router.get("/", response_model=list[InterbankTransferOut])
def list_interbank_transfers(db: Session = Depends(get_db)):
    return db.query(InterbankTransfer).all()


@router.get("/{transfer_id}", response_model=InterbankTransferOut)
def get_interbank_transfer(transfer_id: int, db: Session = Depends(get_db)):
    transfer = db.query(InterbankTransfer).filter(InterbankTransfer.id == transfer_id).with_for_update().first()
    if not transfer:
        raise HTTPException(status_code=404, detail="Interbank transfer not found")
    return transfer


@router.put("/{transfer_id}/status", response_model=InterbankTransferOut)
def update_interbank_transfer_status(
    transfer_id: int,
    data: InterbankTransferStatusUpdate,
    request: Request,
    db: Session = Depends(get_db),
):
    """Settle a transfer or reverse a previously successful transfer."""
    transfer = db.query(InterbankTransfer).filter(InterbankTransfer.id == transfer_id).with_for_update().first()
    if not transfer:
        raise HTTPException(status_code=404, detail="Interbank transfer not found")

    old_status = transfer.status
    allowed_transitions = {
        "PROCESSING": {"SUCCESS", "FAILED"},
        "SUCCESS": {"REVERSED"},
    }
    if data.status not in allowed_transitions.get(old_status, set()):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Cannot change interbank transfer from {old_status} to {data.status}",
        )

    if data.status in ("FAILED", "REVERSED"):
        source = db.query(Account).filter(Account.id == transfer.source_account_id).with_for_update().first()
        if not source:
            raise HTTPException(status_code=409, detail="Source account no longer exists")
        refund = transfer.amount + transfer.transfer_fee
        source.available_balance += refund
        source.ledger_balance += refund

    transfer.status = data.status
    if data.status in ("SUCCESS", "FAILED", "REVERSED"):
        transfer.completed_at = datetime.utcnow()

    record_audit_event(
        db,
        request,
        "UPDATE",
        "interbank_transfers",
        transfer.id,
        old_value={"status": old_status},
        new_value={"status": transfer.status},
    )
    commit_or_409(db, "Interbank transfer status conflicts with an existing record")
    db.refresh(transfer)
    return transfer


@router.delete("/{transfer_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_interbank_transfer(transfer_id: int, db: Session = Depends(get_db)):
    if not db.query(InterbankTransfer.id).filter(InterbankTransfer.id == transfer_id).with_for_update().first():
        raise HTTPException(status_code=404, detail="Interbank transfer not found")
    raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail="Interbank transfers cannot be deleted; use a valid settlement or reversal status",
    )