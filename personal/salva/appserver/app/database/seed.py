"""
Seed script for Salva Banking System.
Populates standard reference data, roles, test accounts, demo banking records, and transactions.
"""

from datetime import date, datetime
import sys
import os

# Ensure app package is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from app.core.security import hash_password
from app.database.session import Base, SessionLocal, engine
from app.models.account import Account
from app.models.account_type import AccountType
from app.models.audit_log import AuditLog
from app.models.bank import Bank
from app.models.deposit import Deposit
from app.models.fee_record import FeeRecord
from app.models.fee_type import FeeType
from app.models.interbank_transfer import InterbankTransfer
from app.models.interest_policy import InterestPolicy
from app.models.interest_record import InterestRecord
from app.models.ledger_entry import LedgerEntry
from app.models.role import Role
from app.models.session import UserSession
from app.models.transfer import Transfer
from app.models.user import User
from app.models.withdrawal import Withdrawal
from app.models.withdrawal_limit import WithdrawalLimit


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        print("--- Seeding Salva Banking System Database ---")

        # 1. ROLES
        roles_data = [
            ("ADMIN", "System Administrator", "Full administrative access to configuration and banking operations"),
            ("STAFF", "Bank Staff", "Day-to-day banking operations, account maintenance, and transaction processing"),
            ("CUSTOMER", "Bank Customer", "Self-service banking access to own accounts and transaction history"),
        ]
        role_map = {}
        for code, name, desc in roles_data:
            role = db.query(Role).filter(Role.role_code == code).first()
            if not role:
                role = Role(role_code=code, role_name=name, description=desc)
                db.add(role)
                db.commit()
                db.refresh(role)
                print(f"Created Role: {code}")
            role_map[code] = role

        # 2. ACCOUNT TYPES
        actypes_data = [
            ("SAVINGS", "Regular Savings", 500.00, 1000.00, 0.0250, 50000.00),
            ("CHECKING", "Standard Checking", 1000.00, 5000.00, 0.0100, 100000.00),
            ("TIME_DEPOSIT", "Time Deposit (1 Year)", 10000.00, 10000.00, 0.0450, 200000.00),
        ]
        actype_map = {}
        for code, name, min_bal, open_dep, rate, limit in actypes_data:
            actype = db.query(AccountType).filter(AccountType.type_code == code).first()
            if not actype:
                actype = AccountType(
                    type_code=code,
                    type_name=name,
                    minimum_balance=min_bal,
                    opening_deposit=open_dep,
                    annual_interest_rate=rate,
                    daily_withdrawal_limit=limit,
                )
                db.add(actype)
                db.commit()
                db.refresh(actype)
                print(f"Created Account Type: {code}")
            actype_map[code] = actype

        # 3. BANKS
        banks_data = [
            ("BDO", "Banco de Oro Universal Bank", "BNORPHMMXXX", "BDO", "ACTIVE"),
            ("BPI", "Bank of the Philippine Islands", "BOPIPHMMXXX", "BPI", "ACTIVE"),
            ("MBTC", "Metropolitan Bank and Trust Company", "MBTCPHMMXXX", "Metrobank", "ACTIVE"),
            ("LBP", "Land Bank of the Philippines", "TLBPPHMMXXX", "LandBank", "ACTIVE"),
        ]
        bank_map = {}
        for code, name, swift, short, status in banks_data:
            bank = db.query(Bank).filter(Bank.bank_code == code).first()
            if not bank:
                bank = Bank(
                    bank_code=code,
                    bank_name=name,
                    swift_code=swift,
                    short_name=short,
                    status=status,
                )
                db.add(bank)
                db.commit()
                db.refresh(bank)
                print(f"Created Bank: {code}")
            bank_map[code] = bank

        # 4. FEE TYPES
        fee_types_data = [
            ("MAINTENANCE", "Monthly Maintenance Fee", "Below minimum balance service charge", 50.00, 0.00),
            ("OVERDRAFT", "Overdraft Protection Fee", "Assessed when balance exceeds limit", 200.00, 0.00),
            ("TRANSFER_FEE", "Interbank Transfer Fee", "InstaPay / PESONet processing fee", 25.00, 0.00),
            ("ATM_WITHDRAWAL", "Other Bank ATM Fee", "Fee for transactions via BancNet partner ATMs", 18.00, 0.00),
        ]
        fee_type_map = {}
        for code, name, desc, fixed, pct in fee_types_data:
            ft = db.query(FeeType).filter(FeeType.fee_code == code).first()
            if not ft:
                ft = FeeType(
                    fee_code=code,
                    fee_name=name,
                    fee_description=desc,
                    fixed_amount=fixed,
                    percentage_rate=pct,
                )
                db.add(ft)
                db.commit()
                db.refresh(ft)
                print(f"Created Fee Type: {code}")
            fee_type_map[code] = ft

        # 5. USERS
        users_data = [
            ("admin", "admin@salva.bank", "09171000001", "System", None, "Administrator", date(1990, 1, 1), role_map["ADMIN"].id),
            ("mgarcia", "mgarcia@salva.bank", "09171000002", "Maria", "Santos", "Garcia", date(1993, 5, 12), role_map["STAFF"].id),
            ("jdelacruz", "jdelacruz@gmail.com", "09171000003", "Juan", "Protacio", "Dela Cruz", date(1998, 6, 19), role_map["CUSTOMER"].id),
            ("asoriano", "asoriano@gmail.com", "09171000004", "Ana", "Marie", "Soriano", date(2000, 11, 23), role_map["CUSTOMER"].id),
        ]
        user_map = {}
        for uname, email, mobile, first, mid, last, dob, r_id in users_data:
            user = db.query(User).filter(User.username == uname).first()
            if not user:
                user = User(
                    username=uname,
                    hashed_password=hash_password("1234"),
                    email=email,
                    mobile_number=mobile,
                    first_name=first,
                    middle_name=mid,
                    last_name=last,
                    date_of_birth=dob,
                    role_id=r_id,
                    account_status="ACTIVE",
                )
                db.add(user)
                db.commit()
                db.refresh(user)
                print(f"Created User: {uname} (Password: 1234)")
            user_map[uname] = user

        # 6. ACCOUNTS
        accounts_data = [
            ("SA-1001-001", user_map["jdelacruz"].id, actype_map["SAVINGS"].id, 18500.00, 18500.00, "BR-MNL-01"),
            ("CA-1001-002", user_map["jdelacruz"].id, actype_map["CHECKING"].id, 28000.00, 28000.00, "BR-MNL-01"),
            ("SA-1002-001", user_map["asoriano"].id, actype_map["SAVINGS"].id, 12000.00, 12000.00, "BR-CEB-01"),
        ]
        account_map = {}
        for acc_num, cust_id, act_id, avail, ledger, branch in accounts_data:
            acc = db.query(Account).filter(Account.account_number == acc_num).first()
            if not acc:
                acc = Account(
                    account_number=acc_num,
                    customer_id=cust_id,
                    account_type_id=act_id,
                    available_balance=avail,
                    ledger_balance=ledger,
                    currency_code="PHP",
                    status="ACTIVE",
                    branch_code=branch,
                )
                db.add(acc)
                db.commit()
                db.refresh(acc)
                print(f"Created Account: {acc_num}")
            account_map[acc_num] = acc

        # 7. WITHDRAWAL LIMITS
        for acc_num in ["SA-1001-001", "CA-1001-002", "SA-1002-001"]:
            acc = account_map[acc_num]
            w_limit = db.query(WithdrawalLimit).filter(WithdrawalLimit.account_id == acc.id).first()
            if not w_limit:
                daily_limit = 50000.00 if "SA" in acc_num else 100000.00
                w_limit = WithdrawalLimit(
                    account_id=acc.id,
                    daily_limit_amount=daily_limit,
                    daily_used_amount=0.00,
                    last_reset_date=date.today(),
                )
                db.add(w_limit)
                db.commit()
                print(f"Created Withdrawal Limit for: {acc_num}")

        # 8. INTEREST POLICIES
        policies_data = [
            (actype_map["SAVINGS"].id, "Standard Savings 2.5% Policy", 0.0250, "MONTHLY", date(2026, 1, 1)),
            (actype_map["TIME_DEPOSIT"].id, "Time Deposit 4.5% Policy", 0.0450, "YEARLY", date(2026, 1, 1)),
        ]
        for act_id, name, rate, comp_freq, eff_date in policies_data:
            pol = db.query(InterestPolicy).filter(InterestPolicy.account_type_id == act_id).first()
            if not pol:
                pol = InterestPolicy(
                    account_type_id=act_id,
                    policy_name=name,
                    annual_rate=rate,
                    compounding_frequency=comp_freq,
                    effective_date=eff_date,
                )
                db.add(pol)
                db.commit()
                print(f"Created Interest Policy: {name}")

        # 9. TRANSACTIONS FOR JUAN DELA CRUZ
        j_savings = account_map["SA-1001-001"]
        j_checking = account_map["CA-1001-002"]

        # Deposit
        if not db.query(Deposit).filter(Deposit.reference_number == "DEP-2026-0001").first():
            dep = Deposit(
                account_id=j_savings.id,
                reference_number="DEP-2026-0001",
                amount=10000.00,
                deposit_channel="CASH",
                deposited_by_user_id=user_map["mgarcia"].id,
                remarks="Initial Payroll Deposit",
                transaction_date=datetime.utcnow(),
            )
            db.add(dep)
            print("Created Demo Deposit: DEP-2026-0001")

        # Withdrawal
        if not db.query(Withdrawal).filter(Withdrawal.reference_number == "WTH-2026-0001").first():
            wth = Withdrawal(
                account_id=j_savings.id,
                reference_number="WTH-2026-0001",
                amount=2000.00,
                withdrawal_channel="ATM",
                approved_by_user_id=user_map["mgarcia"].id,
                remarks="ATM Cash Withdrawal",
                transaction_date=datetime.utcnow(),
            )
            db.add(wth)
            print("Created Demo Withdrawal: WTH-2026-0001")

        # Transfer
        if not db.query(Transfer).filter(Transfer.transfer_reference == "TRF-2026-0001").first():
            trf = Transfer(
                source_account_id=j_savings.id,
                destination_account_id=j_checking.id,
                transfer_reference="TRF-2026-0001",
                amount=3000.00,
                status="SUCCESS",
                remarks="Savings to Checking Transfer",
                completed_at=datetime.utcnow(),
            )
            db.add(trf)
            print("Created Demo Transfer: TRF-2026-0001")

        # Interbank Transfer
        if not db.query(InterbankTransfer).filter(InterbankTransfer.reference_number == "IBT-2026-0001").first():
            ibt = InterbankTransfer(
                source_account_id=j_savings.id,
                target_bank_id=bank_map["BPI"].id,
                target_account_number="1234567890",
                beneficiary_name="Pedro Penduko",
                reference_number="IBT-2026-0001",
                amount=1500.00,
                transfer_fee=25.00,
                status="SUCCESS",
                completed_at=datetime.utcnow(),
            )
            db.add(ibt)
            print("Created Demo Interbank Transfer: IBT-2026-0001")

        # Audit Log
        if not db.query(AuditLog).first():
            log = AuditLog(
                user_id=user_map["admin"].id,
                action_type="SYSTEM_INIT",
                entity_name="SYSTEM",
                entity_id=1,
                ip_address="127.0.0.1",
            )
            db.add(log)
            print("Created Initial Audit Log")

        db.commit()
        print("--- Database Seeding Completed Successfully ---")

    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
