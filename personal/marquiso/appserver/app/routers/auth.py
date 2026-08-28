# ==== LAYER 2: Identity & Access ====
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import check_password, create_token, get_current_user_record, hash_password, oauth2_scheme
from app.database.session import get_db
from app.models.session import UserSession
from app.models.role import Role
from app.models.user import User
from app.models.account import Account
from app.models.account_type import AccountType
from app.schemas.auth import Token
from app.schemas.user import UserCreate, UserOut

router = APIRouter(prefix="/auth", tags=["Layer 2 - Auth"])


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register_customer(user: UserCreate, db: Session = Depends(get_db)):
    customer_role = db.query(Role).filter(Role.role_code == "CUSTOMER").first()
    if not customer_role:
        raise HTTPException(status_code=500, detail="Customer role is not configured")

    existing = db.query(User).filter(
        (User.username == user.username) | (User.email == user.email)
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username or email already in use")

    data = user.model_dump(exclude={"password", "role_id", "account_status"})
    new_user = User(
        **data,
        hashed_password=hash_password(user.password),
        role_id=customer_role.id,
        account_status="ACTIVE",
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    savings_type = db.query(AccountType).filter(AccountType.id == 1).first()
    if savings_type:
        db.add(Account(
            account_number=f"SAV-{new_user.id}",
            customer_id=new_user.id,
            account_type_id=savings_type.id,
            currency_code="PHP",
            available_balance=savings_type.opening_deposit,
            ledger_balance=savings_type.opening_deposit,
        ))
        db.commit()
    return new_user


@router.post("/login", response_model=Token)
def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not check_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if user.account_status != "ACTIVE":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is not active")

    token = create_token(user.username)
    expires_at = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    # Every successful login is recorded as a row in `sessions` (Layer 2 table).
    new_session = UserSession(
        user_id=user.id,
        jwt_token=token,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        expires_at=expires_at,
    )
    db.add(new_session)

    user.last_login_at = datetime.utcnow()

    db.commit()
    return Token(access_token=token)


@router.get("/me")
def current_user(current_user: User = Depends(get_current_user_record), db: Session = Depends(get_db)):
    role = db.query(Role).filter(Role.id == current_user.role_id).first()
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "role_id": current_user.role_id,
        "role_code": role.role_code if role else None,
        "role_name": role.role_name if role else None,
    }


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    session = db.query(UserSession).filter(UserSession.jwt_token == token).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    session.revoked_at = datetime.utcnow()
    db.commit()