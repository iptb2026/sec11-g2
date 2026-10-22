import os
import time
import unittest
from datetime import datetime, timedelta
from unittest.mock import patch
import pyotp
from cryptography.fernet import Fernet
import test_bembank as banking
TestSession = banking.TestSession
from app.models.otp import OtpCredential, OtpChallenge
from app.models.session import UserSession
from app.core.otp import digest


class OtpTests(unittest.TestCase):
    login = banking.BankingTests.login

    def setUp(self):
        key_patch = patch.dict(os.environ, {"BEMBANK_OTP_ENCRYPTION_KEY": Fernet.generate_key().decode()})
        key_patch.start()
        self.addCleanup(key_patch.stop)
        self.now = int(time.time()) // 30 * 30
        clock = patch('app.core.otp.time.time', return_value=self.now)
        self.clock = clock.start()
        self.addCleanup(clock.stop)
        banking.BankingTests.setUp(self)

    def enroll(self):
        response = self.client.post('/auth/otp/setup', headers=self.alice, json={"password": "test-password-123"})
        self.assertEqual(response.status_code, 200, response.text)
        self.secret = response.json()['secret']
        self.assertIn('otpauth://totp/Bembank', response.json()['provisioning_uri'])
        self.assertEqual(response.headers['cache-control'], 'no-store')
        with TestSession() as db:
            self.assertNotEqual(db.get(OtpCredential, 1).encrypted_secret, self.secret)
        response = self.client.post('/auth/otp/confirm', headers=self.alice, json={"code": pyotp.TOTP(self.secret).at(self.now)})
        self.assertEqual(response.status_code, 200, response.text)
        self.codes = response.json()['recovery_codes']
        self.assertEqual(len(self.codes), 8)
        self.clock.return_value = self.now + 30
        return self.codes

    def challenge(self):
        result = self.client.post('/auth/login', data={"username": "alice", "password": "test-password-123"})
        self.assertEqual(result.status_code, 200, result.text)
        self.assertTrue(result.json()['otp_required'])
        self.assertNotIn('access_token', result.json())
        return result.json()['challenge_token']

    def verify(self, challenge, code=None):
        return self.client.post('/auth/otp/verify', json={"challenge_token": challenge, "code": code or pyotp.TOTP(self.secret).at(self.clock.return_value)})

    def test_enrollment_login_and_secret_privacy(self):
        self.enroll()
        status = self.client.get('/auth/otp/status', headers=self.alice).json()
        self.assertEqual(status, {"enabled": True, "recovery_codes_remaining": 8})
        challenge = self.challenge()
        self.assertEqual(self.client.get('/auth/me', headers={"Authorization": 'Bearer ' + challenge}).status_code, 401)
        response = self.verify(challenge)
        self.assertEqual(response.status_code, 200, response.text)
        self.assertTrue(response.json()['pin_required'])
        self.assertNotIn('access_token', response.json())
        response = self.client.post('/auth/pin/verify', json={'challenge_token': response.json()['challenge_token'], 'pin': '012345'})
        headers = {"Authorization": 'Bearer ' + response.json()['access_token']}
        self.assertEqual(self.client.get('/auth/me', headers=headers).json()['username'], 'alice')

    def test_code_and_challenge_cannot_be_replayed(self):
        self.enroll()
        challenge = self.challenge()
        self.assertEqual(self.verify(challenge).status_code, 200)
        self.assertEqual(self.verify(challenge).status_code, 400)
        self.assertEqual(self.verify(self.challenge()).status_code, 400)

    def test_recovery_codes_are_single_use_and_hashed(self):
        codes = self.enroll()
        self.assertEqual(self.verify(self.challenge(), codes[0]).status_code, 200)
        self.assertEqual(self.verify(self.challenge(), codes[0]).status_code, 400)
        with TestSession() as db:
            hashes = db.get(OtpCredential, 1).recovery_hashes
            self.assertEqual(len(hashes), 7)
            self.assertNotIn(codes[1], hashes)

    def test_failed_codes_lock_account_across_challenges(self):
        self.enroll()
        challenge = self.challenge()
        # Non-numeric, non-recovery value guarantees a wrong code.
        for _ in range(5):
            self.assertEqual(self.verify(challenge, 'BADCODE').status_code, 400)
        self.assertEqual(self.verify(challenge).status_code, 429)
        self.assertEqual(self.client.post('/auth/login', data={"username": "alice", "password": "test-password-123"}).status_code, 429)

    def test_challenges_expire_without_creating_session(self):
        self.enroll()
        challenge = self.challenge()
        with TestSession() as db:
            count = db.query(UserSession).count()
            db.get(OtpChallenge, digest(challenge)).expires_at = datetime.utcnow() - timedelta(seconds=1)
            db.commit()
        self.assertEqual(self.verify(challenge).status_code, 400)
        with TestSession() as db:
            self.assertEqual(db.query(UserSession).count(), count)

    def test_setup_requires_password_and_confirmation(self):
        self.assertEqual(self.client.post('/auth/otp/setup', headers=self.alice, json={"password": "wrong"}).status_code, 400)
        self.assertEqual(self.client.get('/auth/otp/status', headers=self.bob).json()['enabled'], False)
        self.enroll()
        self.assertEqual(self.client.post('/auth/otp/setup', headers=self.alice, json={"password": "test-password-123"}).status_code, 409)

    def test_enable_revokes_other_sessions(self):
        other = self.login('alice')
        self.enroll()
        self.assertEqual(self.client.get('/auth/me', headers=other).status_code, 401)
        self.assertEqual(self.client.get('/auth/me', headers=self.alice).status_code, 200)

    def test_disable_requires_password_and_fresh_code(self):
        self.enroll()
        bad = self.client.post('/auth/otp/disable', headers=self.alice, json={"password": "wrong", "code": self.codes[0]})
        self.assertEqual(bad.status_code, 400)
        response = self.client.post('/auth/otp/disable', headers=self.alice, json={"password": "test-password-123", "code": self.codes[0]})
        self.assertEqual(response.status_code, 204, response.text)
        self.assertFalse(self.client.get('/auth/otp/status', headers=self.alice).json()['enabled'])
        self.assertIn('Authorization', self.login('alice'))

    def test_password_change_invalidates_pending_challenge(self):
        self.enroll()
        challenge = self.challenge()
        response = self.client.post('/auth/password', headers=self.alice, json={"current_password": "test-password-123", "new_password": "Another-safe-password-456"})
        self.assertEqual(response.status_code, 204, response.text)
        self.assertEqual(self.verify(challenge).status_code, 400)

    def test_password_attempts_are_limited(self):
        for _ in range(10):
            self.assertEqual(self.client.post('/auth/login', data={"username": "unknown", "password": "wrong"}).status_code, 401)
        self.assertEqual(self.client.post('/auth/login', data={"username": "unknown", "password": "wrong"}).status_code, 429)


if __name__ == '__main__':
    unittest.main()
