"""Run once to add the final-presentation examples; safe to run again."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from app.main import app  # Register all models and initialize missing reference tables.
from app.database.session import SessionLocal
from app.core.presentation_demo import seed_presentation

if __name__ == '__main__':
    with SessionLocal() as db:
        try:
            result=seed_presentation(db)
            db.commit()
            print(result)
        except Exception:
            db.rollback()
            raise
