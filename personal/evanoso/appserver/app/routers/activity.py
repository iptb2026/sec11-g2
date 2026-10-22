from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.activity_read import ActivityRead
from app.models.banking_request import BankingRequest
from app.models.account_application import AccountApplication
from app.models.user import User
from app.routers.customer_banking import get_customer, list_my_transactions
from app.core.db_utils import commit_or_409

router = APIRouter(prefix="/customer/alerts", tags=["Account activity"])


def events(user, db):
    result = [{"id": "transaction-" + row["id"], "title": row["transaction_type"].replace("_", " ").title(), "amount": row["amount"], "status": row["status"], "date": row["transaction_date"], "reference": row["reference"], "to": "/my-transactions"} for row in list_my_transactions(user, db)]
    for item in db.query(BankingRequest).filter(BankingRequest.customer_id == user.id).all():
        result.append({"id": f"request-{item.id}-{item.status}", "title": item.kind.title() + " request", "amount": item.amount, "status": item.status, "date": item.created_at, "reference": item.reference, "to": "/requests"})
    for item in db.query(AccountApplication).filter(AccountApplication.customer_id == user.id).all():
        result.append({"id": f"application-{item.id}-{item.status}", "title": "Account application", "amount": None, "status": item.status, "date": item.created_at, "reference": item.account_number or f"Application #{item.id}", "to": "/my-account"})
    result.sort(key=lambda row: row["date"] or datetime.min, reverse=True)
    return result[:100]


@router.get("/")
def list_alerts(user: User = Depends(get_customer), db: Session = Depends(get_db)):
    seen = {row.event_key for row in db.query(ActivityRead).filter(ActivityRead.user_id == user.id).all()}
    return [{**row, "read": row["id"] in seen} for row in events(user, db)]


class ReadInput(BaseModel):
    ids: list[str] = Field(min_length=1, max_length=100)


@router.post("/read", status_code=204)
def mark_read(data: ReadInput, user: User = Depends(get_customer), db: Session = Depends(get_db)):
    db.query(User).filter(User.id == user.id).with_for_update().first()
    valid = {row["id"] for row in events(user, db)}
    if not set(data.ids).issubset(valid):
        raise HTTPException(400, "One or more alerts are no longer available. Refresh and try again.")
    seen = {row.event_key for row in db.query(ActivityRead).filter(ActivityRead.user_id == user.id).all()}
    for key in set(data.ids) - seen:
        db.add(ActivityRead(user_id=user.id, event_key=key))
    commit_or_409(db, "Could not update activity alerts. Please retry.")
