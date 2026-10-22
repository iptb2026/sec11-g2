from decimal import Decimal
from typing import Literal
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.core.security import check_password, hash_password
from app.core.db_utils import commit_or_409
from app.models.demo_card import DemoCard
from app.models.account import Account
from app.models.user import User
from app.routers.customer_banking import get_customer, lock_owned_account

router = APIRouter(prefix="/customer/cards", tags=["Simulated cards"])


def card_data(card, account):
    return {"id": card.id, "account_id": account.id, "last_four": account.account_number[-4:], "status": card.status, "spending_limit": card.spending_limit, "pin_set": bool(card.pin_hash)}


def owned_card(card_id, user, db):
    pair = db.query(DemoCard, Account).join(Account, DemoCard.account_id == Account.id).filter(DemoCard.id == card_id, Account.customer_id == user.id).with_for_update().first()
    if not pair:
        raise HTTPException(404, "Card not found")
    return pair


@router.get("/")
def list_cards(user: User = Depends(get_customer), db: Session = Depends(get_db)):
    return [card_data(card, account) for card, account in db.query(DemoCard, Account).join(Account, DemoCard.account_id == Account.id).filter(Account.customer_id == user.id).all()]


class CardCreate(BaseModel):
    account_id: int


@router.post("/", status_code=201)
def create_card(data: CardCreate, user: User = Depends(get_customer), db: Session = Depends(get_db)):
    account = lock_owned_account(db, data.account_id, user.id)
    if db.query(DemoCard).filter(DemoCard.account_id == account.id).first():
        raise HTTPException(409, "This account already has a demo card")
    card = DemoCard(account_id=account.id)
    db.add(card)
    commit_or_409(db, "This account already has a demo card")
    db.refresh(card)
    return card_data(card, account)


class CardUpdate(BaseModel):
    status: Literal["ACTIVE", "FROZEN", "LOST"]
    spending_limit: Decimal = Field(gt=0, max_digits=18, decimal_places=2)


@router.put("/{card_id}")
def update_card(card_id: int, data: CardUpdate, user: User = Depends(get_customer), db: Session = Depends(get_db)):
    card, account = owned_card(card_id, user, db)
    if card.status == "LOST":
        raise HTTPException(409, "A reported lost card cannot be reactivated")
    card.status = data.status
    card.spending_limit = data.spending_limit
    db.commit()
    return card_data(card, account)


class PinInput(BaseModel):
    password: str
    pin: str = Field(pattern=r"^[0-9]{6}$")


@router.post("/{card_id}/pin", status_code=204)
def set_pin(card_id: int, data: PinInput, user: User = Depends(get_customer), db: Session = Depends(get_db)):
    card, account = owned_card(card_id, user, db)
    if card.status == "LOST":
        raise HTTPException(409, "Cannot update a lost card")
    if not check_password(data.password, user.hashed_password):
        raise HTTPException(400, "Current password is incorrect")
    card.pin_hash = hash_password(data.pin)
    db.commit()
