from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.user import User
from app.models.role import Role
from app.schemas.user import UserCreate, UserOut, UserUpdate
from app.core.security import hash_password, check_password, get_current_user
from app.core.db_utils import commit_or_409

router = APIRouter(prefix="/users", tags=["Users"])


def require_admin(db: Session, current_email: str):
    user = db.query(User).filter(User.email == current_email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unknown user")
    role = db.query(Role).filter(Role.id == user.role_id).first()
    if not role or role.role_code != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return user


@router.get("/", response_model=list[UserOut])
def list_users(db: Session = Depends(get_db), current: str = Depends(get_current_user)):
    require_admin(db, current)
    users = db.query(User).all()
    out = []
    for u in users:
        role = db.query(Role).filter(Role.id == u.role_id).first()
        out.append({
            "id": u.id,
            "full_name": u.full_name,
            "email": u.email,
            "role_code": role.role_code if role else "",
            "is_active": u.is_active,
            "created_at": u.created_at,
        })
    return out


@router.get("/me", response_model=UserOut)
def get_me(db: Session = Depends(get_db), current: str = Depends(get_current_user)):
    u = db.query(User).filter(User.email == current).first()
    if not u:
        raise HTTPException(status_code=404, detail="User not found")
    role = db.query(Role).filter(Role.id == u.role_id).first()
    return {
        "id": u.id,
        "full_name": u.full_name,
        "email": u.email,
        "role_code": role.role_code if role else "",
        "is_active": u.is_active,
        "created_at": u.created_at,
    }


@router.get("/customers", response_model=list[UserOut])
def list_customers(db: Session = Depends(get_db), current: str = Depends(get_current_user)):
    user = db.query(User).filter(User.email == current).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unknown user")

    role = db.query(Role).filter(Role.id == user.role_id).first()
    if not role or role.role_code not in ("staff", "admin"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Staff access required")

    customers = (
        db.query(User)
        .join(Role, Role.id == User.role_id)
        .filter(Role.role_code == "customer")
        .all()
    )
    return [
        {
            "id": customer.id,
            "full_name": customer.full_name,
            "email": customer.email,
            "role_code": "customer",
            "is_active": customer.is_active,
            "created_at": customer.created_at,
        }
        for customer in customers
    ]



@router.put("/me", response_model=UserOut)
def update_me(payload: UserUpdate, db: Session = Depends(get_db), current: str = Depends(get_current_user)):
    u = db.query(User).filter(User.email == current).first()
    if not u:
        raise HTTPException(status_code=404, detail="User not found")

    if payload.full_name:
        u.full_name = payload.full_name
    if payload.email:
        u.email = payload.email
    if payload.password:
        u.hashed_password = hash_password(payload.password)

    db.commit()
    db.refresh(u)
    role = db.query(Role).filter(Role.id == u.role_id).first()
    return {
        "id": u.id,
        "full_name": u.full_name,
        "email": u.email,
        "role_code": role.role_code if role else "",
        "is_active": u.is_active,
        "created_at": u.created_at,
    }


@router.post("/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreate, db: Session = Depends(get_db), current: str = Depends(get_current_user)):
    require_admin(db, current)

    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="email already exists")

    role = db.query(Role).filter(Role.role_code == payload.role_code).first()
    if not role:
        raise HTTPException(status_code=400, detail="invalid role_code")

    new_user = User(
        full_name=payload.full_name,
        email=payload.email,
        hashed_password=hash_password(payload.password),
        role_id=role.id,
        is_active=True,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "id": new_user.id,
        "full_name": new_user.full_name,
        "email": new_user.email,
        "role_code": role.role_code,
        "is_active": new_user.is_active,
        "created_at": new_user.created_at,
    }


@router.put("/{user_id}", response_model=UserOut)
def update_user(user_id: int, payload: UserUpdate, db: Session = Depends(get_db), current: str = Depends(get_current_user)):
    require_admin(db, current)
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if payload.full_name:
        user.full_name = payload.full_name
    if payload.email:
        user.email = payload.email
    if payload.password:
        user.hashed_password = hash_password(payload.password)
    if payload.role_code:
        role = db.query(Role).filter(Role.role_code == payload.role_code).first()
        if not role:
            raise HTTPException(status_code=400, detail="invalid role_code")
        user.role_id = role.id
    if payload.is_active is not None:
        user.is_active = payload.is_active

    db.commit()
    db.refresh(user)
    role = db.query(Role).filter(Role.id == user.role_id).first()
    return {
        "id": user.id,
        "full_name": user.full_name,
        "email": user.email,
        "role_code": role.role_code if role else "",
        "is_active": user.is_active,
        "created_at": user.created_at,
    }


@router.post("/{user_id}/deactivate", status_code=status.HTTP_200_OK)
def deactivate_user(user_id: int, db: Session = Depends(get_db), current: str = Depends(get_current_user)):
    require_admin(db, current)
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_active = False
    db.commit()
    return {"status": "deactivated"}


@router.post("/{user_id}/activate", status_code=status.HTTP_200_OK)
def activate_user(user_id: int, db: Session = Depends(get_db), current: str = Depends(get_current_user)):
    require_admin(db, current)
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_active = True
    db.commit()
    return {"status": "activated"}


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db), current: str = Depends(get_current_user)):
    require_admin(db, current)
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    commit_or_409(db, "Cannot delete this user — an integrity constraint was triggered")
