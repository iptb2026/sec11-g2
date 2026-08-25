# ==== LAYER 5: Financial Records & Ledger ====
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.account import Account
from app.models.ledger_entry import LedgerEntry
from app.schemas.ledger_entry import LedgerEntryCreate, LedgerEntryOut


router = APIRouter(
    prefix="/ledger-entries",
    tags=["Layer 5 - Ledger Entries"],
)


@router.post(
    "/",
    response_model=LedgerEntryOut,
    status_code=status.HTTP_201_CREATED,
)
def create_ledger_entry(
    entry: LedgerEntryCreate,
    db: Session = Depends(get_db),
):
    account = (
        db.query(Account)
        .filter(Account.id == entry.account_id)
        .with_for_update()
        .first()
    )

    if not account:
        raise HTTPException(status_code=400, detail="account_id does not exist")

    if entry.debit_amount < 0 or entry.credit_amount < 0:
        raise HTTPException(status_code=400, detail="debit_amount and credit_amount cannot be negative")

    if entry.debit_amount > 0 and entry.credit_amount > 0:
        raise HTTPException(status_code=400, detail="An entry cannot have both debit and credit amounts")

    balance_after = account.available_balance

    new_entry = LedgerEntry(
        **entry.model_dump(),
        balance_after=balance_after,
    )

    db.add(new_entry)
    db.commit()
    db.refresh(new_entry)
    return new_entry


@router.get("/", response_model=list[LedgerEntryOut])
def list_ledger_entries(db: Session = Depends(get_db)):
    return db.query(LedgerEntry).order_by(LedgerEntry.id).all()


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

