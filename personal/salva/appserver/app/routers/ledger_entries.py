# ==== LAYER 5: Financial Records & Ledger ====
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import require_roles
from app.database.session import get_db
from app.models.account import Account
from app.models.ledger_entry import LedgerEntry
from app.models.user import User
from app.schemas.ledger_entry import LedgerEntryCreate, LedgerEntryOut

router = APIRouter(prefix="/ledger-entries", tags=["Layer 5 - Ledger Entries"])


@router.post("/", response_model=LedgerEntryOut, status_code=status.HTTP_201_CREATED)
def create_ledger_entry(
    entry: LedgerEntryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN", "STAFF")),
):
    account = db.query(Account).filter(Account.id == entry.account_id).first()
    if not account:
        raise HTTPException(status_code=400, detail="account_id does not exist")

    new_entry = LedgerEntry(**entry.model_dump(), balance_after=account.available_balance)
    db.add(new_entry)
    db.commit()
    db.refresh(new_entry)
    return new_entry


@router.get("/", response_model=list[LedgerEntryOut])
def list_ledger_entries(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN", "STAFF")),
):
    return db.query(LedgerEntry).all()


@router.get("/{entry_id}", response_model=LedgerEntryOut)
def get_ledger_entry(
    entry_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN", "STAFF")),
):
    entry = db.query(LedgerEntry).filter(LedgerEntry.id == entry_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Ledger entry not found")
    return entry


@router.delete("/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ledger_entry(
    entry_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN", "STAFF")),
):
    entry = db.query(LedgerEntry).filter(LedgerEntry.id == entry_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Ledger entry not found")

    db.delete(entry)
    db.commit()