# ==== LAYER 5: Financial Records & Ledger ====
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.account import Account
from app.models.ledger_entry import LedgerEntry
from app.schemas.ledger_entry import LedgerEntryCreate, LedgerEntryOut

router = APIRouter(prefix="/ledger-entries", tags=["Layer 5 - Ledger Entries"])


@router.post("/", response_model=LedgerEntryOut, status_code=status.HTTP_201_CREATED)
def create_ledger_entry(entry: LedgerEntryCreate, db: Session = Depends(get_db)):
    account = db.query(Account).filter(Account.id == entry.account_id).first()
    if not account:
        raise HTTPException(status_code=400, detail="account_id does not exist")

    # In a fully wired system, every deposit/withdrawal/transfer/fee/interest
    # endpoint in Layers 4-5 would call a shared helper to insert its own
    # ledger_entries row automatically, at the exact moment it changes the
    # balance — that's what makes a ledger authoritative. Wiring that up
    # everywhere is a bigger refactor than this project takes on, so here
    # `ledger_entries` is its own simple CRUD table instead: it does NOT
    # apply debit_amount/credit_amount to the account (that already
    # happened via the real transaction endpoint). `balance_after` is a
    # read-only snapshot of the account's current balance at insert time,
    # not something the client can set.
    new_entry = LedgerEntry(**entry.model_dump(), balance_after=account.available_balance)
    db.add(new_entry)
    db.commit()
    db.refresh(new_entry)
    return new_entry


@router.get("/", response_model=list[LedgerEntryOut])
def list_ledger_entries(db: Session = Depends(get_db)):
    return db.query(LedgerEntry).all()


@router.get("/{entry_id}", response_model=LedgerEntryOut)
def get_ledger_entry(entry_id: int, db: Session = Depends(get_db)):
    entry = db.query(LedgerEntry).filter(LedgerEntry.id == entry_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Ledger entry not found")
    return entry


@router.delete("/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ledger_entry(entry_id: int, db: Session = Depends(get_db)):
    entry = db.query(LedgerEntry).filter(LedgerEntry.id == entry_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Ledger entry not found")

    db.delete(entry)
    db.commit()