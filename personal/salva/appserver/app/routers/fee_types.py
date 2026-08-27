# ==== LAYER 1: Foundation & Reference Data ====
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.db_utils import commit_or_409
from app.core.security import get_current_user_model, require_roles
from app.database.session import get_db
from app.models.fee_type import FeeType
from app.models.user import User
from app.schemas.fee_type import FeeTypeCreate, FeeTypeOut

router = APIRouter(prefix="/fee-types", tags=["Layer 1 - Fee Types"])


@router.post("/", response_model=FeeTypeOut, status_code=status.HTTP_201_CREATED)
def create_fee_type(
    fee_type: FeeTypeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN")),
):
    existing = db.query(FeeType).filter(FeeType.fee_code == fee_type.fee_code).first()
    if existing:
        raise HTTPException(status_code=400, detail="fee_code already exists")

    new_fee_type = FeeType(**fee_type.model_dump())
    db.add(new_fee_type)
    db.commit()
    db.refresh(new_fee_type)
    return new_fee_type


@router.get("/", response_model=list[FeeTypeOut])
def list_fee_types(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_model),
):
    return db.query(FeeType).all()


@router.get("/{fee_type_id}", response_model=FeeTypeOut)
def get_fee_type(
    fee_type_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_model),
):
    fee_type = db.query(FeeType).filter(FeeType.id == fee_type_id).first()
    if not fee_type:
        raise HTTPException(status_code=404, detail="Fee type not found")
    return fee_type


@router.put("/{fee_type_id}", response_model=FeeTypeOut)
def update_fee_type(
    fee_type_id: int,
    data: FeeTypeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN")),
):
    fee_type = db.query(FeeType).filter(FeeType.id == fee_type_id).first()
    if not fee_type:
        raise HTTPException(status_code=404, detail="Fee type not found")

    for field, value in data.model_dump().items():
        setattr(fee_type, field, value)

    db.commit()
    db.refresh(fee_type)
    return fee_type


@router.delete("/{fee_type_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_fee_type(
    fee_type_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN")),
):
    fee_type = db.query(FeeType).filter(FeeType.id == fee_type_id).first()
    if not fee_type:
        raise HTTPException(status_code=404, detail="Fee type not found")

    db.delete(fee_type)
    commit_or_409(db, "Cannot delete this fee type — one or more fee records still reference it")