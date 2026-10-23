# ==== LAYER 2: Identity & Access ====
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.db_utils import commit_or_409
from app.database.session import get_db
from app.models.session import UserSession
from app.models.user import User
from app.schemas.session import SessionCreate, SessionOut

router = APIRouter(prefix="/sessions", tags=["Layer 2 - Sessions"])


@router.post("/", response_model=SessionOut, status_code=status.HTTP_201_CREATED)
def create_session(session_data: SessionCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == session_data.user_id).first()
    if not user:
        raise HTTPException(status_code=400, detail="user_id does not exist")

    new_session = UserSession(**session_data.model_dump())
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    return new_session


@router.get("/", response_model=list[SessionOut])
def list_sessions(db: Session = Depends(get_db)):
    return db.query(UserSession).all()


@router.get("/{session_id}", response_model=SessionOut)
def get_session(session_id: int, db: Session = Depends(get_db)):
    session = db.query(UserSession).filter(UserSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@router.put("/{session_id}/revoke", response_model=SessionOut)
def revoke_session(session_id: int, db: Session = Depends(get_db)):
    """Convenience action endpoint: marks a session revoked instead of replacing the whole row."""
    session = db.query(UserSession).filter(UserSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    session.revoked_at = datetime.utcnow()
    db.commit()
    db.refresh(session)
    return session


@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_session(session_id: int, db: Session = Depends(get_db)):
    session = db.query(UserSession).filter(UserSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    db.delete(session)
    commit_or_409(db, "Cannot delete this session — it is still referenced elsewhere")