"""One-time, additive presentation dataset. All people and transactions are fictional."""
from datetime import datetime, timedelta, date
from decimal import Decimal
from app.core.security import hash_password
from app.models.role import Role
from app.models.user import User
from app.models.account import Account
from app.models.account_type import AccountType
from app.models.bank import Bank
from app.models.fee_type import FeeType
from app.models.interest_policy import InterestPolicy
from app.models.withdrawal_limit import WithdrawalLimit
from app.models.deposit import Deposit
from app.models.withdrawal import Withdrawal
from app.models.transfer import Transfer
from app.models.interbank_transfer import InterbankTransfer
from app.models.fee_record import FeeRecord
from app.models.interest_record import InterestRecord
from app.models.ledger_entry import LedgerEntry
from app.models.audit_log import AuditLog
from app.models.banking_request import BankingRequest, Recipient
from app.models.account_application import AccountApplication
from app.models.demo_card import DemoCard
from app.models.savings_goal import SavingsGoal
from app.models.bill_payment import BillPayment
from app.models.investment import Investment

DEMO_PASSWORD = 'BembankDemo!2026'
MARKER = 'presentation_demo_v1'


def seed_presentation(db):
    """Caller commits once. Re-runs preserve the original data and live edits."""
    if db.query(AuditLog.id).filter(AuditLog.entity_name == MARKER).first():
        return {'created': False, 'message': 'Presentation samples already exist; no records changed.'}
    usernames = ['alex.admin', 'jamie.staff', 'sofia.reyes', 'marco.santos', 'isla.retail']
    if db.query(User.id).filter(User.username.in_(usernames)).first():
        raise ValueError('A reserved username already exists. No existing user will be overwritten.')
    now = datetime.utcnow().replace(microsecond=0)
    when = lambda days: now - timedelta(days=days)
    roles = {}
    for code, label in [('ADMIN','Administrator'),('STAFF','Staff'),('CUSTOMER','Customer')]:
        role = db.query(Role).filter_by(role_code=code).first()
        if not role:
            role=Role(role_code=code, role_name=label);db.add(role);db.flush()
        roles[code]=role
    hashed = hash_password(DEMO_PASSWORD)
    users=[]
    for username, first, last, role, birth in [
        ('alex.admin','Alex','Morgan','ADMIN',date(1990,3,12)),
        ('jamie.staff','Jamie','Cruz','STAFF',date(1995,8,20)),
        ('sofia.reyes','Sofia','Reyes','CUSTOMER',date(1992,5,14)),
        ('marco.santos','Marco','Santos','CUSTOMER',date(1996,9,8)),
        ('isla.retail','Isla','Retail','CUSTOMER',date(1988,11,23))]:
        user=User(username=username, first_name=first, last_name=last, email=username+'@example.com', date_of_birth=birth, role_id=roles[role].id, account_status='ACTIVE', hashed_password=hashed)
        db.add(user);db.flush();users.append(user)
    admin, staff, sofia, marco, business=users
    types=[]
    for code, name in [('FAMILY_SAVINGS','Family savings account'),('EMPLOYEE','Employee account'),('BUSINESS','Business account')]:
        item=db.query(AccountType).filter_by(type_code=code).first()
        if not item:
            item=AccountType(type_code=code,type_name=name,opening_deposit=0,minimum_balance=0,annual_interest_rate=0,daily_withdrawal_limit=10000);db.add(item);db.flush()
        types.append(item)
    banks=[]
    for code,name in [('NORTHSTAR','Northstar Bank'),('HARBOR','Harbor Bank')]:
        bank=db.query(Bank).filter_by(bank_code=code).first()
        if not bank:
            bank=Bank(bank_code=code,bank_name=name,short_name=name,status='ACTIVE');db.add(bank);db.flush()
        banks.append(bank)
    fees=[]
    for code,name,amount in [('BB_SERVICE','service fee','25'),('BB_ATM','ATM fee','15'),('BB_INTERBANK','interbank fee','25')]:
        item=db.query(FeeType).filter_by(fee_code=code).first()
        if not item:
            item=FeeType(fee_code=code,fee_name=name,fee_description='Bank service charge',fixed_amount=Decimal(amount),percentage_rate=0);db.add(item);db.flush()
        fees.append(item)
    accounts=[];policies=[]
    for i,(user,kind,limit) in enumerate(zip([sofia,marco,business],types,[10000,15000,50000]),1):
        account=Account(account_number=f'BEM10000000{i}',customer_id=user.id,account_type_id=kind.id,available_balance=Decimal('0'),ledger_balance=Decimal('0'),currency_code='PHP',status='ACTIVE',opened_at=when(12),branch_code='MAIN')
        db.add(account);db.flush();accounts.append(account)
        db.add(WithdrawalLimit(account_id=account.id,daily_limit_amount=limit,daily_used_amount=0,last_reset_date=now.date()))
        policy=InterestPolicy(account_type_id=kind.id,policy_name=''+kind.type_name,annual_rate=Decimal('1.50'),compounding_frequency='MONTHLY',effective_date=when(30).date(),expiration_date=(now+timedelta(days=365)).date())
        db.add(policy);db.flush();policies.append(policy)
        db.add(DemoCard(account_id=account.id,status='ACTIVE',spending_limit=limit))
    def audit(entity, item, amount, at):
        db.flush()
        db.add(AuditLog(user_id=staff.id,action_type='CREATE',entity_name=entity,entity_id=item.id,new_value={'amount':str(amount),'demo':True},action_timestamp=at))
    def post(account, delta, reference, kind, at):
        delta=Decimal(str(delta));account.available_balance+=delta;account.ledger_balance+=delta
        db.add(LedgerEntry(account_id=account.id,transaction_reference=reference,transaction_type=kind,debit_amount=max(-delta,Decimal('0')),credit_amount=max(delta,Decimal('0')),balance_after=account.ledger_balance,transaction_date=at))
    for i,(account,amount) in enumerate(zip(accounts,[50000,75000,150000]),1):
        ref=f'BB-DEP-{i:03d}';item=Deposit(account_id=account.id,reference_number=ref,amount=amount,deposit_channel='CASH',deposited_by_user_id=staff.id,remarks='Opening deposit',transaction_date=when(10))
        db.add(item);post(account,amount,ref,'DEPOSIT',when(10));audit('deposits',item,amount,when(10))
    for i,(account,amount) in enumerate(zip(accounts,[1500,2500,10000]),1):
        ref=f'BB-WD-{i:03d}';item=Withdrawal(account_id=account.id,reference_number=ref,amount=amount,withdrawal_channel='BRANCH',approved_by_user_id=staff.id,remarks='Branch withdrawal',transaction_date=when(8))
        db.add(item);post(account,-amount,ref,'WITHDRAWAL',when(8));audit('withdrawals',item,amount,when(8))
    a,b,c=accounts
    transfer=Transfer(source_account_id=a.id,destination_account_id=b.id,transfer_reference='BB-TRF-001',amount=2500,transfer_type='INTERNAL',status='SUCCESS',remarks='Shared household expenses',created_at=when(6),completed_at=when(6))
    db.add(transfer);post(a,-2500,'BB-TRF-001','TRANSFER_DEBIT',when(6));post(b,2500,'BB-TRF-001','TRANSFER_CREDIT',when(6));audit('transfers',transfer,2500,when(6))
    for account,bank,amount,fee,ref,status,days in [(b,banks[0],800,25,'BB-EXT-001','SUCCESS',5),(c,banks[1],2500,0,'BB-EXT-002','PROCESSING',1)]:
        item=InterbankTransfer(source_account_id=account.id,target_bank_id=bank.id,target_account_number='9081700001',beneficiary_name='Andrea Flores',reference_number=ref,amount=amount,transfer_fee=fee,status=status,initiated_at=when(days),completed_at=when(days) if status=='SUCCESS' else None)
        db.add(item);post(account,-(amount+fee),ref,'INTERBANK_DEBIT',when(days));audit('interbank_transfers',item,amount+fee,when(days))
    fee=FeeRecord(account_id=a.id,fee_type_id=fees[0].id,transaction_reference='BB-FEE-001',amount_charged=25,charged_at=when(4),remarks='monthly service fee')
    db.add(fee);post(a,-25,'BB-FEE-001','FEE',when(4));audit('fee_records',fee,25,when(4))
    interest=InterestRecord(account_id=a.id,policy_id=policies[0].id,amount_credited=125,balance_before=a.available_balance,balance_after=a.available_balance+125,credited_at=when(3))
    db.add(interest);post(a,125,'BB-INT-001','INTEREST',when(3));audit('interest_records',interest,125,when(3))
    bill=BillPayment(account_id=a.id,biller_name='City Electricity',biller_reference='INV-001',payment_reference='BB-BILL-001',amount=1200,status='COMPLETED',created_at=when(2))
    db.add(bill);post(a,-1200,'BB-BILL-001','WITHDRAWAL',when(2));audit('bill_payments',bill,1200,when(2))
    db.add(Investment(account_id=b.id,plan_code='SHORT_TERM',term_months=3,amount=10000,status='ACTIVE',created_at=when(2)))
    b.available_balance-=Decimal('10000')
    for user,account,name,target,saved in [(sofia,a,'Family emergency fund',100000,25000),(marco,b,'New laptop',60000,18000),(business,c,'Store expansion',300000,90000)]:
        db.add(SavingsGoal(customer_id=user.id,name=name,target_amount=target,saved_amount=saved))
        db.add(BankingRequest(customer_id=user.id,account_id=account.id,kind='DEPOSIT',amount=2000,reference='BB-REQ-'+str(account.id),status='PENDING',note='Deposit awaiting staff approval',created_at=when(1)))
    db.add(BankingRequest(customer_id=sofia.id,account_id=a.id,kind='WITHDRAWAL',amount=500,reference='BB-REQ-REJECTED',status='REJECTED',note='Customer cancelled this request',reviewed_by=staff.id,created_at=when(2)))
    db.add(AccountApplication(customer_id=sofia.id,account_type_id=types[2].id,status='PENDING',created_at=when(1)))
    db.add(Recipient(customer_id=sofia.id,name='Marco Santos',account_number=b.account_number))
    db.add(AuditLog(user_id=admin.id,action_type='CREATE',entity_name=MARKER,new_value={'description':'Fictional presentation dataset','accounts':3},action_timestamp=now))
    db.flush()
    return {'created':True,'users':usernames,'accounts':[a.account_number for a in accounts]}
