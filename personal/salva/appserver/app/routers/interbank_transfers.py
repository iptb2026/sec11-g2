# ==== LAYER 4: Transactions ====
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user_model, require_roles
from app.database.session import get_db
from app.models.account import Account
from app.models.bank import Bank
from app.models.interbank_transfer import InterbankTransfer
from app.models.role import Role
from app.models.user import User
from app.schemas.interbank_transfer import (
    InterbankTransferCreate,
    InterbankTransferStatusUpdate,
    InterbankTransferOut,
)

router = APIRouter(prefix="/interbank-transfers", tags=["Layer 4 - Interbank Transfers"])


@router.post("/", response_model=InterbankTransferOut, status_code=status.HTTP_201_CREATED)
def create_interbank_transfer(
    transfer: InterbankTransferCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_model),
):
    source = db.query(Account).filter(Account.id == transfer.source_account_id).with_for_update().first()
    if not source:
        raise HTTPException(status_code=400, detail="source_account_id does not exist")

    # Customer can only transfer out of their own account
    user_role = db.query(Role).filter(Role.id == current_user.role_id).first()
    if user_role and user_role.role_code == "CUSTOMER" and source.customer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: You can only transfer funds from your own account",
        )

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

    new_transfer = InterbankTransfer(**transfer.model_dump(), status="PROCESSING")
    db.add(new_transfer)

    source.available_balance -= total_debit
    source.ledger_balance -= total_debit

    db.commit()
    db.refresh(new_transfer)
    return new_transfer


@router.get("/", response_model=list[InterbankTransferOut])
def list_interbank_transfers(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_model),
):
    user_role = db.query(Role).filter(Role.id == current_user.role_id).first()
    if user_role and user_role.role_code == "CUSTOMER":
        user_account_ids = [a.id for a in db.query(Account).filter(Account.customer_id == current_user.id).all()]
        return db.query(InterbankTransfer).filter(InterbankTransfer.source_account_id.in_(user_account_ids)).all()

    return db.query(InterbankTransfer).all()


@router.get("/{transfer_id}", response_model=InterbankTransferOut)
def get_interbank_transfer(
    transfer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_model),
):
    transfer = db.query(InterbankTransfer).filter(InterbankTransfer.id == transfer_id).first()
    if not transfer:
        raise HTTPException(status_code=404, detail="Interbank transfer not found")

    user_role = db.query(Role).filter(Role.id == current_user.role_id).first()
    if user_role and user_role.role_code == "CUSTOMER":
        account = db.query(Account).filter(Account.id == transfer.source_account_id).first()
        if not account or account.customer_id != current_user.id:
            raise HTTPException(status_code=403, detail="Forbidden: You do not have access to this transfer")

    return transfer


@router.put("/{transfer_id}/status", response_model=InterbankTransferOut)
def update_interbank_transfer_status(
    transfer_id: int,
    data: InterbankTransferStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN", "STAFF")),
):
    """Moves a PROCESSING transfer to its final settlement status (SUCCESS/FAILED/REVERSED)."""
    transfer = db.query(InterbankTransfer).filter(InterbankTransfer.id == transfer_id).first()
    if not transfer:
        raise HTTPException(status_code=404, detail="Interbank transfer not found")

    transfer.status = data.status
    if data.status in ("SUCCESS", "FAILED", "REVERSED"):
        transfer.completed_at = datetime.utcnow()

    db.commit()
    db.refresh(transfer)
    return transfer


@router.delete("/{transfer_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_interbank_transfer(
    transfer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN", "STAFF")),
):
    """NOTE: does not move any money back."""
    transfer = db.query(InterbankTransfer).filter(InterbankTransfer.id == transfer_id).first()
    if not transfer:
        raise HTTPException(status_code=404, detail="Interbank transfer not found")

    db.delete(transfer)
    db.commit()