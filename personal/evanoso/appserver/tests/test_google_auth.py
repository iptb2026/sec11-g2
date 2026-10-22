import os
import unittest
from unittest.mock import patch
from datetime import datetime, timedelta
import test_bembank as banking
from app.core.project_defaults import ensure_project_defaults
from app.core.otp import digest
from app.models.google_identity import GoogleIdentity, GoogleChallenge
from app.models.user import User
from app.models.account import Account
from app.models.otp import OtpCredential

class GoogleTests(unittest.TestCase):
    setUpBank = banking.BankingTests.setUp
    login = banking.BankingTests.login

    def setUp(self):
        self.setUpBank()
        self.env = patch.dict(os.environ, {'GOOGLE_CLIENT_ID': 'test.apps.googleusercontent.com'})
        self.env.start(); self.addCleanup(self.env.stop)
        with banking.TestSession() as db:
            ensure_project_defaults(db)
        self.claims = {'sub': 'google-subject', 'email': 'google@example.com', 'email_verified': True, 'given_name': 'Google', 'family_name': 'Customer'}
        self.verifier = patch('app.routers.google_auth.verify_google_token', side_effect=lambda *_: dict(self.claims))
        self.verifier.start(); self.addCleanup(self.verifier.stop)

    def start(self):
        response = self.client.get('/auth/google/config')
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.headers['cache-control'], 'no-store')
        self.claims['nonce'] = response.json()['nonce']
        return {'nonce': self.claims['nonce'], 'credential': 'test-google-credential-value'}

    def test_signup_returning_user_and_pin(self):
        data = self.start()
        response = self.client.post('/auth/google/verify', json=data)
        self.assertEqual(response.status_code, 200, response.text)
        self.assertTrue(response.json()['pin_setup_required'])
        self.assertNotIn('access_token', response.json())
        with banking.TestSession() as db:
            identity = db.get(GoogleIdentity, self.claims['sub'])
            user = db.get(User, identity.user_id)
            self.assertEqual(user.role_id, 1)
            self.assertEqual(db.query(Account).filter_by(customer_id=user.id).one().available_balance, 0)
        pin = self.client.post('/auth/pin/verify', json={'challenge_token': response.json()['challenge_token'], 'pin': '012345', 'confirm_pin': '012345'})
        self.assertEqual(pin.status_code, 200, pin.text)
        self.assertEqual(self.client.post('/auth/google/verify', json=data).status_code, 400)
        # Google subject, not a mutable email address, identifies returning users.
        self.claims['email'] = 'changed@example.com'
        response = self.client.post('/auth/google/verify', json=self.start())
        self.assertFalse(response.json()['pin_setup_required'])
        with banking.TestSession() as db:
            self.assertEqual(db.query(GoogleIdentity).count(), 1)

    def test_existing_account_requires_password_and_preserves_otp(self):
        with banking.TestSession() as db:
            db.get(User, 1).email = self.claims['email']
            db.add(OtpCredential(user_id=1, enabled=True, encrypted_secret='test-secret'))
            db.commit()
        data = self.start()
        self.assertTrue(self.client.post('/auth/google/verify', json=data).json()['password_required'])
        self.assertEqual(self.client.post('/auth/google/verify', json={**data, 'password': 'wrong'}).status_code, 400)
        response = self.client.post('/auth/google/verify', json={**data, 'password': 'test-password-123'})
        self.assertTrue(response.json()['otp_required'])
        self.assertNotIn('access_token', response.json())

    def test_invalid_nonce_unverified_expired_and_disabled(self):
        data = self.start()
        self.claims['nonce'] = 'wrong'
        self.assertEqual(self.client.post('/auth/google/verify', json=data).status_code, 400)
        self.claims['nonce'] = data['nonce']; self.claims['email_verified'] = False
        self.assertEqual(self.client.post('/auth/google/verify', json=data).status_code, 400)
        self.claims['email_verified'] = True
        with banking.TestSession() as db:
            db.get(GoogleChallenge, digest(data['nonce'])).expires_at = datetime.utcnow() - timedelta(seconds=1)
            db.commit()
        self.assertEqual(self.client.post('/auth/google/verify', json=data).status_code, 400)
        data = self.start()
        with banking.TestSession() as db:
            user = db.get(User, 1); user.email = self.claims['email']; user.account_status = 'LOCKED'; db.commit()
        self.assertEqual(self.client.post('/auth/google/verify', json=data).status_code, 403)

    def test_missing_config_and_invalid_token_fail_closed(self):
        with patch.dict(os.environ, {'GOOGLE_CLIENT_ID': ''}):
            self.assertEqual(self.client.get('/auth/google/config').status_code, 503)
        data = self.start()
        self.verifier.stop()
        # Stub only the key-fetch transport; real verifier rejects malformed JWT.
        with patch('google.auth.transport.requests.Request') as request:
            request.return_value.return_value.status = 200
            request.return_value.return_value.data = b'{}'
            response = self.client.post('/auth/google/verify', json=data)
            self.assertEqual(response.status_code, 400, response.text)
