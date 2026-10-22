from datetime import datetime
from decimal import Decimal
from typing import Literal
from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field, ConfigDict
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.core.security import require_roles, hash_password, check_password
from app.core.password_policy import StrongPassword
from app.core.otp import throttle
from app.core.audit import record_audit_event
from app.core.db_utils import commit_or_409
from app.models.concept_features import MobileLoad, SupportTicket
from app.models.account import Account
from app.models.user import User
from app.models.role import Role
from app.models.session import UserSession
from app.models.otp import OtpChallenge
from app.routers.customer_banking import get_customer, lock_owned_account

router = APIRouter(tags=['Customer conveniences'])

class RecipientLookup(BaseModel):
    account_number: str = Field(min_length=1,max_length=30)

@router.post('/customer/recipient-lookup')
def recipient_lookup(data: RecipientLookup, user=Depends(get_customer), db: Session=Depends(get_db)):
    account=db.query(Account).filter(Account.account_number==data.account_number,Account.status=='ACTIVE').first()
    if not account:
        raise HTTPException(404,'No active Bembank account matches this number')
    owner=db.get(User,account.customer_id)
    if not owner or owner.account_status!='ACTIVE':
        raise HTTPException(404,'Recipient is not available')
    return {'account_number':account.account_number,'name':f'{owner.first_name} {owner.last_name}'}

class LoadInput(BaseModel):
    model_config=ConfigDict(extra='forbid')
    account_id: int
    network: Literal['Globe','Smart','DITO']
    mobile_number: str = Field(pattern=r'^09[0-9]{9}$')
    amount: Decimal = Field(gt=0,max_digits=18,decimal_places=2)
    request_key: str = Field(min_length=32,max_length=40,pattern=r'^[a-zA-Z0-9-]+$')

@router.post('/customer/mobile-load/',status_code=201)
def buy_load(data: LoadInput, request: Request, user=Depends(get_customer), db: Session=Depends(get_db)):
    if data.amount not in [25,50,100,200,300,500,1000]:
        raise HTTPException(400,'Choose one of the available load amounts')
    account=lock_owned_account(db,data.account_id,user.id)
    existing=db.query(MobileLoad).filter(MobileLoad.request_key==data.request_key).first()
    if existing:
        if existing.customer_id!=user.id or any(getattr(existing,k)!=v for k,v in data.model_dump().items()):
            raise HTTPException(409,'Request reference already used with different details')
        return existing
    if account.available_balance<data.amount:
        raise HTTPException(400,'Insufficient available balance')
    item=MobileLoad(**data.model_dump(),customer_id=user.id,reference='LOAD-'+uuid4().hex[:24].upper())
    db.add(item)
    account.available_balance-=data.amount;account.ledger_balance-=data.amount
    record_audit_event(db,request,'CREATE','mobile_loads',None,new_value={'account_id':account.id,'amount':str(data.amount),'reference':item.reference})
    commit_or_409(db,'This request was already submitted. Refresh your load history before retrying.')
    db.refresh(item)
    return item

@router.get('/customer/mobile-load/')
def load_history(user=Depends(get_customer),db: Session=Depends(get_db)):
    return db.query(MobileLoad).filter(MobileLoad.customer_id==user.id).order_by(MobileLoad.id.desc()).all()

class TicketInput(BaseModel):
    model_config=ConfigDict(str_strip_whitespace=True)
    subject: str = Field(min_length=3,max_length=100)
    message: str = Field(min_length=10,max_length=2000)

@router.post('/support/tickets/',status_code=201)
def create_ticket(data: TicketInput,user=Depends(require_roles('CUSTOMER','STAFF','ADMIN')),db: Session=Depends(get_db)):
    ticket=SupportTicket(customer_id=user.id,**data.model_dump())
    db.add(ticket);db.commit();db.refresh(ticket);return ticket

@router.get('/support/tickets/')
def tickets(user=Depends(require_roles('CUSTOMER','STAFF','ADMIN')),db: Session=Depends(get_db)):
    query=db.query(SupportTicket)
    if db.get(Role,user.role_id).role_code=='CUSTOMER':query=query.filter(SupportTicket.customer_id==user.id)
    return query.order_by(SupportTicket.id.desc()).all()

class ReplyInput(BaseModel):
    reply: str = Field(min_length=3,max_length=2000,pattern=r'\S')

@router.post('/support/tickets/{ticket_id}/resolve')
def resolve(ticket_id:int,data:ReplyInput,user=Depends(require_roles('STAFF','ADMIN')),db:Session=Depends(get_db)):
    ticket=db.query(SupportTicket).filter(SupportTicket.id==ticket_id).with_for_update().first()
    if not ticket:raise HTTPException(404,'Request not found')
    if ticket.status!='OPEN':raise HTTPException(409,'Request already resolved')
    ticket.reply=data.reply;ticket.status='RESOLVED';ticket.resolved_at=datetime.utcnow();db.commit();return ticket

@router.get('/staff/customer-access/')
def customer_access(user=Depends(require_roles('STAFF','ADMIN')),db:Session=Depends(get_db)):
    return [{'id':u.id,'username':u.username,'name':f'{u.first_name} {u.last_name}'} for u in db.query(User).join(Role,Role.id==User.role_id).filter(Role.role_code=='CUSTOMER').order_by(User.username)]

class ResetInput(BaseModel):
    staff_password: str
    new_password: StrongPassword
    identity_confirmed: Literal[True]

@router.post('/staff/customer-access/{customer_id}/password',status_code=204)
def reset_password(customer_id:int,data:ResetInput,request:Request,actor=Depends(require_roles('STAFF','ADMIN')),db:Session=Depends(get_db)):
    throttle(db,'reauth:'+actor.username)
    if not check_password(data.staff_password,actor.hashed_password):raise HTTPException(400,'Your current password is incorrect')
    customer=db.query(User).join(Role,Role.id==User.role_id).filter(User.id==customer_id,Role.role_code=='CUSTOMER').with_for_update().first()
    if not customer:raise HTTPException(404,'Customer not found')
    customer.hashed_password=hash_password(data.new_password)
    now=datetime.utcnow()
    db.query(UserSession).filter(UserSession.user_id==customer.id,UserSession.revoked_at.is_(None)).update({'revoked_at':now})
    db.query(OtpChallenge).filter(OtpChallenge.user_id==customer.id,OtpChallenge.used_at.is_(None)).update({'used_at':now})
    record_audit_event(db,request,'UPDATE','users',customer.id,new_value={'password_reset':True})
    db.commit()

@router.get('/customer/recent-recipients/')
def recent_recipients(user=Depends(get_customer),db:Session=Depends(get_db)):
    from app.models.transfer import Transfer
    source_ids=[a.id for a in db.query(Account).filter(Account.customer_id==user.id)]
    result=[];seen=set()
    for transfer in db.query(Transfer).filter(Transfer.source_account_id.in_(source_ids),Transfer.status=='SUCCESS').order_by(Transfer.id.desc()).limit(100):
        if transfer.destination_account_id in seen:continue
        target=db.get(Account,transfer.destination_account_id)
        if not target or target.status!='ACTIVE':continue
        owner=db.get(User,target.customer_id)
        if not owner or owner.account_status!='ACTIVE':continue
        seen.add(target.id);result.append({'account_number':target.account_number,'name':f'{owner.first_name} {owner.last_name}'})
        if len(result)==10:break
    return result
