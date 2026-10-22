import unittest
from decimal import Decimal
from datetime import date, timedelta
import test_bembank as banking
from app.core.presentation_demo import seed_presentation, DEMO_PASSWORD
from app.models.account import Account
from app.models.user import User
from app.models.ledger_entry import LedgerEntry
from app.models.interest_policy import InterestPolicy
from app.models.withdrawal_limit import WithdrawalLimit
from app.models.audit_log import AuditLog

class PresentationTests(unittest.TestCase):
    setUp=banking.BankingTests.setUp
    login=banking.BankingTests.login

    def test_samples_balance_and_rerun_preserves_edits(self):
        with banking.TestSession() as db:
            original={a.id:(a.available_balance,a.ledger_balance) for a in db.query(Account).all()}
            result=seed_presentation(db);db.commit()
            self.assertTrue(result['created'])
            self.assertEqual({a.id:(a.available_balance,a.ledger_balance) for a in db.query(Account).filter(Account.id.in_(original)).all()},original)
            accounts=db.query(Account).filter(Account.account_number.like('BEM10000000%')).order_by(Account.account_number).all()
            self.assertEqual([a.ledger_balance for a in accounts],list(map(Decimal,['44900','74175','137500'])))
            self.assertEqual(accounts[1].available_balance,Decimal('64175'))
            for account in accounts:
                running=Decimal('0')
                for item in db.query(LedgerEntry).filter_by(account_id=account.id).order_by(LedgerEntry.transaction_date,LedgerEntry.id):
                    running+=item.credit_amount-item.debit_amount
                    self.assertEqual(item.balance_after,running)
                self.assertEqual(running,account.ledger_balance)
            self.assertEqual(db.query(InterestPolicy).count(),3)
            self.assertEqual(db.query(WithdrawalLimit).count(),3)
            counts=(db.query(User).count(),db.query(LedgerEntry).count(),db.query(AuditLog).count())
            accounts[0].status='FROZEN';db.commit()
            self.assertFalse(seed_presentation(db)['created']);db.commit()
            self.assertEqual(db.get(Account,accounts[0].id).status,'FROZEN')
            self.assertEqual(counts,(db.query(User).count(),db.query(LedgerEntry).count(),db.query(AuditLog).count()))

    def test_demo_login_and_statement_reconcile(self):
        with banking.TestSession() as db:
            seed_presentation(db);db.commit()
        result=self.client.post('/auth/login',data={'username':'sofia.reyes','password':DEMO_PASSWORD})
        self.assertEqual(result.status_code,200,result.text)
        result=self.client.post('/auth/pin/verify',json={'challenge_token':result.json()['challenge_token'],'pin':'012345','confirm_pin':'012345'})
        self.assertEqual(result.status_code,200,result.text)
        headers={'Authorization':'Bearer '+result.json()['access_token']}
        accounts=self.client.get('/customer/accounts/',headers=headers).json()
        end=date.today();start=end-timedelta(days=20)
        response=self.client.get(f"/reports/accounts/{accounts[0]['id']}/statement?start={start}&end={end}",headers=headers)
        self.assertEqual(response.status_code,200,response.text)
        self.assertEqual(Decimal(response.json()['opening_balance']),0)
        self.assertEqual(Decimal(response.json()['closing_balance']),Decimal('44900'))
        self.assertEqual(len(self.client.get('/customer/requests/',headers=headers).json()),2)
        self.assertEqual(len(self.client.get('/customer/cards/',headers=headers).json()),1)
