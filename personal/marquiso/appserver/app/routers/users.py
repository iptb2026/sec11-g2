# ==== LAYER 2: Identity & Access ====
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.db_utils import commit_or_409
from app.core.security import get_current_user, hash_password
from app.database.session import get_db
from app.models.role import Role
from app.models.user import User
from app.schemas.user import UserCreate, UserOut, UserUpdate

router = APIRouter(prefix="/users", tags=["Layer 2 - Users"])


def require_admin(username: str = Depends(get_current_user), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    role = db.query(Role).filter(Role.id == user.role_id).first() if user else None
    if not role or role.role_code != "ADMIN":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return user


@router.post("/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_db), _admin: User = Depends(require_admin)):
    # role_id is a foreign key — the referenced role must already exist.
    role = db.query(Role).filter(Role.id == user.role_id).first()
    if not role:
        raise HTTPException(status_code=400, detail="role_id does not exist")

    existing = db.query(User).filter(
        (User.username == user.username) | (User.email == user.email)
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="username or email already in use")

    data = user.model_dump(exclude={"password"})
    try:
        hashed_password = hash_password(user.password)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error))

    new_user = User(**data, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.get("/", response_model=list[UserOut])
def list_users(db: Session = Depends(get_db)):
    return db.query(User).all()


@router.get("/{user_id}", response_model=UserOut)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/{user_id}", response_model=UserOut)
def update_user(user_id: int, user_data: UserUpdate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    role = db.query(Role).filter(Role.id == user_data.role_id).first()
    if not role:
        raise HTTPException(status_code=400, detail="role_id does not exist")

    data = user_data.model_dump(exclude={"password"}, exclude_unset=True)
    for field, value in data.items():
        setattr(user, field, value)
    if user_data.password:
        user.hashed_password = hash_password(user_data.password)

    db.commit()
    db.refresh(user)
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    commit_or_409(db, "Cannot delete this user — related sessions, accounts, or audit logs still reference it")