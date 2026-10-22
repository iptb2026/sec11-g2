"""Disposable browser-test API. Uses a temporary SQLite database, never bank data."""
import os
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from cryptography.fernet import Fernet
os.environ['BEMBANK_OTP_ENCRYPTION_KEY'] = Fernet.generate_key().decode()
from test_bembank import BankingTests, app, database, TestSession
from sqlalchemy import create_engine
from tempfile import TemporaryDirectory

if __name__ == '__main__':
    # Separate pooled connections are needed for parallel browser API requests.
    directory = TemporaryDirectory(prefix='bembank-browser-')
    database.engine = create_engine('sqlite:///' + str(Path(directory.name) / 'bank.sqlite'), connect_args={'check_same_thread': False})
    TestSession.configure(bind=database.engine)
    fixture = BankingTests()
    fixture.setUp()
    from app.core.project_defaults import ensure_project_defaults
    with TestSession() as db:
        ensure_project_defaults(db)
    import uvicorn
    uvicorn.run(app, host='127.0.0.1', port=5012, log_level='warning')
