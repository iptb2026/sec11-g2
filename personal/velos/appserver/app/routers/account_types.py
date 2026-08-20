from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.db_utils import commit_or_409
from app.database.session import get_db
from app.models.account_type import AccountType
from app.schemas.account_type import AccountTypeCreate, AccountTypeOut

router = APIRouter(prefix="/account-types", tags=["Layer 1 - Account Types"])


@router.post("/", response_model=AccountTypeOut, status_code=status.HTTP_201_CREATED)
def create_account_type(account_type: AccountTypeCreate, db: Session = Depends(get_db)):
    existing = db.query(AccountType).filter(AccountType.type_code == account_type.type_code).first()
    if existing:
        raise HTTPException(status_code=400, detail="type_code already exists")

    new_account_type = AccountType(**account_type.model_dump())
    db.add(new_account_type)
    db.commit()
    db.refresh(new_account_type)
    return new_account_type


@router.get("/", response_model=list[AccountTypeOut])
def list_account_types(db: Session = Depends(get_db)):
    return db.query(AccountType).all()


@router.get("/{account_type_id}", response_model=AccountTypeOut)
def get_account_type(account_type_id: int, db: Session = Depends(get_db)):
    account_type = db.query(AccountType).filter(AccountType.id == account_type_id).first()
    if not account_type:
        raise HTTPException(status_code=404, detail="Account type not found")
    return account_type


@router.put("/{account_type_id}", response_model=AccountTypeOut)
def update_account_type(account_type_id: int, data: AccountTypeCreate, db: Session = Depends(get_db)):
    account_type = db.query(AccountType).filter(AccountType.id == account_type_id).first()
    if not account_type:
        raise HTTPException(status_code=404, detail="Account type not found")

    for field, value in data.model_dump().items():
        setattr(account_type, field, value)

    db.commit()
    db.refresh(account_type)
    return account_type


@router.delete("/{account_type_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_account_type(account_type_id: int, db: Session = Depends(get_db)):
    account_type = db.query(AccountType).filter(AccountType.id == account_type_id).first()
    if not account_type:
        raise HTTPException(status_code=404, detail="Account type not found")

    db.delete(account_type)
    commit_or_409(db, "Cannot delete this account type — one or more accounts still reference it")