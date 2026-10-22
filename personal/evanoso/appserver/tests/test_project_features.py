import unittest
from datetime import date
from decimal import Decimal
import test_bembank as banking
from app.core.project_defaults import ensure_project_defaults
from app.models.account import Account
from app.models.account_type import AccountType
from app.models.bank import Bank
from app.models.user import User

class ProjectTests(unittest.TestCase):
    setUp = banking.BankingTests.setUp
    login = banking.BankingTests.login

    def defaults(self):
        with banking.TestSession() as db:
            ensure_project_defaults(db)
            return db.query(AccountType).filter_by(type_code='FAMILY_SAVINGS').one().id, db.query(Bank).filter_by(bank_code='NORTHSTAR').one().id

    def test_staff_registration_and_no_privilege_escalation(self):
        type_id, _ = self.defaults()
        payload = dict(username='newcustomer', password='Initial-secret-123', first_name='New', last_name='Customer', email='new@example.com', account_type_id=type_id)
        self.assertEqual(self.client.post('/staff/customers/', json=payload).status_code,401)
        self.assertEqual(self.client.post('/staff/customers/',headers=self.alice,json=payload).status_code,403)
        self.assertEqual(self.client.post('/staff/customers/',headers=self.staff,json={**payload,'role_id':3}).status_code,422)
        response=self.client.post('/staff/customers/',headers=self.staff,json=payload)
        self.assertEqual(response.status_code,201,response.text)
        with banking.TestSession() as db:
            user=db.get(User,response.json()['customer_id']); account=db.get(Account,response.json()['account_id'])
            self.assertEqual(user.role_id,1); self.assertNotEqual(user.hashed_password,payload['password']); self.assertEqual(account.ledger_balance,0)
        self.assertEqual(self.client.post('/staff/customers/',headers=self.staff,json=payload).status_code,409)
        self.assertEqual(self.client.post('/auth/login',data={'username':'newcustomer','password':payload['password']}).status_code,200)

    def test_defaults_are_additive_idempotent(self):
        self.defaults(); self.defaults()
        with banking.TestSession() as db:
            self.assertEqual(db.query(AccountType).count(),4)
            self.assertEqual(db.query(Bank).count(),2)

    def test_external_transfer_refund_statement_and_ownership(self):
        _, bank = self.defaults()
        payload=dict(source_account_id=1,target_bank_id=bank,target_account_number='OTHER123',beneficiary_name='Recipient',amount='125.50')
        self.assertEqual(self.client.post('/customer/interbank-transfers/',headers=self.bob,json=payload).status_code,404)
        self.assertEqual(self.client.post('/customer/interbank-transfers/',headers=self.alice,json={**payload,'amount':'0.001'}).status_code,422)
        response=self.client.post('/customer/interbank-transfers/',headers=self.alice,json=payload)
        self.assertEqual(response.status_code,201,response.text)
        self.assertEqual(self.client.get('/customer/interbank-transfers/',headers=self.bob).json(),[])
        today=date.today().isoformat(); report_url=f'/reports/accounts/1/statement?start={today}&end={today}'
        self.assertEqual(self.client.get(report_url,headers=self.bob).status_code,404)
        report=self.client.get(report_url,headers=self.alice)
        self.assertEqual(report.status_code,200,report.text)
        self.assertEqual(Decimal(report.json()['opening_balance']),1000)
        self.assertEqual(Decimal(report.json()['closing_balance']),Decimal('874.50'))
        settle=f"/interbank-transfers/{response.json()['id']}/status"
        self.assertEqual(self.client.put(settle,headers=self.alice,json={'status':'FAILED'}).status_code,403)
        self.assertEqual(self.client.put(settle,headers=self.staff,json={'status':'FAILED'}).status_code,200)
        self.assertEqual(self.client.put(settle,headers=self.staff,json={'status':'FAILED'}).status_code,409)
        report=self.client.get(report_url,headers=self.staff).json()
        self.assertEqual(Decimal(report['closing_balance']),1000)
        self.assertEqual(len(report['rows']),2)
        self.assertEqual(Decimal(report['total_credits']),Decimal('125.50'))

    def test_statement_range_and_ledger_reservations(self):
        today=date.today().isoformat()
        self.client.post('/customer/investments/',headers=self.alice,json={'account_id':1,'plan_code':'SHORT_TERM','amount':'100'})
        r=self.client.get(f'/reports/accounts/1/statement?start={today}&end={today}',headers=self.alice)
        self.assertEqual(r.status_code,200,r.text)
        self.assertEqual(Decimal(r.json()['closing_balance']),1000)
        self.assertEqual(r.json()['rows'],[])
        self.assertEqual(self.client.get('/reports/accounts/1/statement?start=2026-10-15&end=2020-01-01',headers=self.alice).status_code,400)
        self.assertEqual(self.client.get('/reports/accounts/1/statement?start=2020-01-01&end=2099-01-01',headers=self.alice).status_code,400)
