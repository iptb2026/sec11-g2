"""Rename only the known presentation dataset; preserve money and audit history."""
import sys
from pathlib import Path
from datetime import datetime
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from app.main import app
from app.database.session import SessionLocal
from app.models.user import User
from app.models.account import Account
from app.models.session import UserSession
from app.models.bank import Bank
from app.models.fee_type import FeeType
from app.models.interest_policy import InterestPolicy
from app.models.deposit import Deposit
from app.models.withdrawal import Withdrawal
from app.models.transfer import Transfer
from app.models.interbank_transfer import InterbankTransfer
from app.models.fee_record import FeeRecord
from app.models.ledger_entry import LedgerEntry
from app.models.banking_request import BankingRequest, Recipient
from app.models.bill_payment import BillPayment
from app.models.audit_log import AuditLog

NAMES={'demo.admin':('alex.admin','Morgan'),'demo.staff':('jamie.staff','Cruz'),'demo.sofia':('sofia.reyes','Reyes'),'demo.marco':('marco.santos','Santos'),'demo.business':('isla.retail','Retail')}
REFS={**{f'DEMO-DEP-{i:03d}':f'BB-DEP-{i:03d}' for i in range(1,4)},**{f'DEMO-WD-{i:03d}':f'BB-WD-{i:03d}' for i in range(1,4)},'DEMO-TRF-001':'BB-TRF-001','DEMO-EXT-001':'BB-EXT-001','DEMO-EXT-002':'BB-EXT-002','DEMO-FEE-001':'BB-FEE-001','DEMO-INT-001':'BB-INT-001','DEMO-BILL-001':'BB-BILL-001'}

def rename(db):
    if not db.query(AuditLog.id).filter_by(entity_name='presentation_demo_v1').first():
        raise ValueError('Presentation seed marker missing; no changes made')
    users=db.query(User).filter(User.username.in_(NAMES)).all()
    if not users:return 'Presentation names already updated.'
    assert len(users)==5, 'Expected all five presentation users'
    ids=[u.id for u in users];customers=[u.id for u in users if u.username in ['demo.sofia','demo.marco','demo.business']]
    accounts=db.query(Account).filter(Account.customer_id.in_(customers),Account.account_number.in_(['BEM-DEMO-0001','BEM-DEMO-0002','BEM-DEMO-0003'])).all()
    assert len(accounts)==3
    account_ids=[a.id for a in accounts]
    before={a.id:(a.available_balance,a.ledger_balance) for a in db.query(Account)}
    for u in users:
        new,last=NAMES[u.username]
        assert not db.query(User.id).filter(User.username==new).first(), 'Username conflict'
        old=u.username;u.username=new;u.last_name=last
        if u.email==old+'@example.com':u.email=new+'@example.com'
    account_map={f'BEM-DEMO-{i:04d}':f'BEM10000000{i}' for i in range(1,4)}
    for a in accounts:
        new=account_map[a.account_number]
        assert not db.query(Account.id).filter(Account.account_number==new).first(), 'Account number conflict'
        a.account_number=new
        if a.branch_code=='DEMO-MAIN':a.branch_code='MAIN'
    for code,name in [('DEMO_A','Northstar Bank'),('DEMO_B','Harbor Bank')]:
        bank=db.query(Bank).filter_by(bank_code=code).first()
        if bank and bank.bank_name in ['Demo Bank A','Demo Bank B']:
            bank.bank_name=name;bank.short_name=name
    for fee in db.query(FeeType).filter(FeeType.fee_code.in_(['DEMO_SERVICE','DEMO_ATM','DEMO_INTERBANK'])):
        fee.fee_name=fee.fee_name.removeprefix('Demo ')
        if fee.fee_description=='Fictional presentation fee':fee.fee_description='Bank service charge'
        fee.fee_code=fee.fee_code.replace('DEMO_','BB_',1)
    for policy in db.query(InterestPolicy).filter(InterestPolicy.account_type_id.in_([a.account_type_id for a in accounts]),InterestPolicy.policy_name.in_(['Demo Family savings account','Demo Employee account','Demo Business account'])):
        policy.policy_name=policy.policy_name.removeprefix('Demo ')
    for model,field,owner in [(Deposit,'reference_number','account_id'),(Withdrawal,'reference_number','account_id'),(Transfer,'transfer_reference','source_account_id'),(InterbankTransfer,'reference_number','source_account_id'),(FeeRecord,'transaction_reference','account_id'),(LedgerEntry,'transaction_reference','account_id'),(BillPayment,'payment_reference','account_id')]:
        for row in db.query(model).filter(getattr(model,owner).in_(account_ids),getattr(model,field).in_(REFS)):
            setattr(row,field,REFS[getattr(row,field)])
            if model is Deposit and row.remarks=='Presentation opening deposit':row.remarks='Opening deposit'
            if model is Withdrawal and row.remarks=='Presentation withdrawal':row.remarks='Branch withdrawal'
            if model is InterbankTransfer:
                if row.target_account_number=='DEMO-RECIPIENT-001':row.target_account_number='9081700001'
                if row.beneficiary_name=='Fictional demo recipient':row.beneficiary_name='Andrea Flores'
            if model is FeeRecord and row.remarks=='Demo monthly service fee':row.remarks='Monthly service fee'
            if model is BillPayment:
                if row.biller_name=='Demo Electricity':row.biller_name='City Electricity'
                if row.biller_reference=='DEMO-INVOICE-001':row.biller_reference='INV-001'
    refs=[f'DEMO-REQ-{i}' for i in account_ids]+['DEMO-REQ-REJECTED']
    for row in db.query(BankingRequest).filter(BankingRequest.account_id.in_(account_ids),BankingRequest.reference.in_(refs)):
        row.reference=row.reference.replace('DEMO-','BB-',1)
        if row.note=='Presentation request awaiting staff approval':row.note='Deposit awaiting staff approval'
        if row.note=='Demo: customer cancelled this request':row.note='Customer cancelled this request'
    for row in db.query(Recipient).filter(Recipient.customer_id.in_(customers),Recipient.account_number.in_(account_map)):
        row.account_number=account_map[row.account_number];row.name=row.name.removesuffix(' (demo)')
    db.query(UserSession).filter(UserSession.user_id.in_(ids),UserSession.revoked_at.is_(None)).update({'revoked_at':datetime.utcnow()},synchronize_session=False)
    db.flush()
    assert before=={a.id:(a.available_balance,a.ledger_balance) for a in db.query(Account)}
    return 'Renamed the five presentation users and three accounts, plus their seeded references. Balances, passwords, and audit history preserved.'

if __name__=='__main__':
    with SessionLocal() as db:
        try:
            result=rename(db);db.commit();print(result)
        except Exception:
            db.rollback();raise
