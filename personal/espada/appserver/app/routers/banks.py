# ==== LAYER 1: Foundation & Reference Data ====
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.db_utils import commit_or_409
from app.database.session import get_db
from app.models.bank import Bank
from app.schemas.bank import BankCreate, BankOut

router = APIRouter(prefix="/banks", tags=["Layer 1 - Banks"])


@router.post("/", response_model=BankOut, status_code=status.HTTP_201_CREATED)
def create_bank(bank: BankCreate, db: Session = Depends(get_db)):
    existing = db.query(Bank).filter(Bank.bank_code == bank.bank_code).first()
    if existing:
        raise HTTPException(status_code=400, detail="bank_code already exists")

    new_bank = Bank(**bank.model_dump())
    db.add(new_bank)
    db.commit()
    db.refresh(new_bank)
    return new_bank


@router.get("/", response_model=list[BankOut])
def list_banks(db: Session = Depends(get_db)):
    return db.query(Bank).all()


@router.get("/{bank_id}", response_model=BankOut)
def get_bank(bank_id: int, db: Session = Depends(get_db)):
    bank = db.query(Bank).filter(Bank.id == bank_id).first()
    if not bank:
        raise HTTPException(status_code=404, detail="Bank not found")
    return bank


@router.put("/{bank_id}", response_model=BankOut)
def update_bank(bank_id: int, data: BankCreate, db: Session = Depends(get_db)):
    bank = db.query(Bank).filter(Bank.id == bank_id).first()
    if not bank:
        raise HTTPException(status_code=404, detail="Bank not found")

    for field, value in data.model_dump().items():
        setattr(bank, field, value)

    db.commit()
    db.refresh(bank)
    return bank


@router.delete("/{bank_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_bank(bank_id: int, db: Session = Depends(get_db)):
    bank = db.query(Bank).filter(Bank.id == bank_id).first()
    if not bank:
        raise HTTPException(status_code=404, detail="Bank not found")

    db.delete(bank)
    commit_or_409(db, "Cannot delete this bank — one or more interbank transfers still reference it")