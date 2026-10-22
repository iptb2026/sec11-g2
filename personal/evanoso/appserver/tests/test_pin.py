import unittest
from datetime import datetime, timedelta
import test_bembank as banking
from app.models.pin import PinCredential, PinChallenge
from app.models.user import User
from app.models.session import UserSession
from app.core.otp import digest
from app.core.security import hash_password


class PinTests(unittest.TestCase):
    setUp = banking.BankingTests.setUp
    login = banking.BankingTests.login

    def challenge(self, username="alice"):
        response = self.client.post('/auth/login', data={"username": username, "password": "test-password-123"})
        self.assertEqual(response.status_code, 200, response.text)
        self.assertNotIn('access_token', response.json())
        return response.json()

    def verify(self, challenge, pin="012345", **extra):
        return self.client.post('/auth/pin/verify', json={"challenge_token": challenge['challenge_token'], "pin": pin, **extra})

    def test_setup_confirmation_hashing_and_leading_zero(self):
        challenge = self.challenge('admin')
        self.assertTrue(challenge['pin_setup_required'])
        self.assertEqual(self.verify(challenge).status_code, 400)
        self.assertEqual(self.verify(challenge, confirm_pin='999999').status_code, 400)
        response = self.verify(challenge, confirm_pin='012345')
        self.assertEqual(response.status_code, 200, response.text)
        with banking.TestSession() as db:
            self.assertNotEqual(db.get(PinCredential, 4).hashed_pin, '012345')
        self.assertFalse(self.challenge('admin')['pin_setup_required'])

    def test_invalid_pin_never_creates_session_and_challenge_is_single_use(self):
        challenge = self.challenge()
        with banking.TestSession() as db:
            count = db.query(UserSession).count()
        for pin in ['12345', '1234567', 'abcdef', '１２３４５６']:
            self.assertEqual(self.verify(challenge, pin).status_code, 422)
        self.assertEqual(self.verify(challenge, '999999').status_code, 400)
        with banking.TestSession() as db:
            self.assertEqual(db.query(UserSession).count(), count)
        self.assertEqual(self.verify(challenge).status_code, 200)
        self.assertEqual(self.verify(challenge).status_code, 400)

    def test_expiry_password_change_and_inactive_user(self):
        challenge = self.challenge()
        with banking.TestSession() as db:
            db.get(PinChallenge, digest(challenge['challenge_token'])).expires_at = datetime.utcnow() - timedelta(seconds=1)
            db.commit()
        self.assertEqual(self.verify(challenge).status_code, 400)
        challenge = self.challenge()
        with banking.TestSession() as db:
            db.get(User, 1).account_status = 'LOCKED'
            db.commit()
        self.assertEqual(self.verify(challenge).status_code, 403)
        with banking.TestSession() as db:
            db.get(User, 1).account_status = 'ACTIVE'
            db.get(User, 1).hashed_password = hash_password('changed-password')
            db.commit()
        self.assertEqual(self.verify(challenge).status_code, 400)

    def test_attempt_limit_across_challenges(self):
        first, second = self.challenge(), self.challenge()
        # Initial fixture sign-in already consumed one PIN attempt.
        for i in range(9):
            self.assertEqual(self.verify(first if i % 2 else second, '999999').status_code, 400)
        self.assertEqual(self.verify(second).status_code, 429)
