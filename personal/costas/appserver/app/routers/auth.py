from datetime import datetime,timedelta
from fastapi import APIRouter,Depends,HTTPException,Request,status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.security import check_password,create_token,oauth2_scheme
from app.database.session import get_db
from app.models.session import UserSession
from app.models.user import User
from app.schemas.auth import Token
router=APIRouter(prefix='/auth',tags=['Layer 2 - Auth'])
@router.post('/login',response_model=Token)
def login(request:Request,form_data:OAuth2PasswordRequestForm=Depends(),db:Session=Depends(get_db)):
    user=db.query(User).filter(User.username==form_data.username).first()
    if not user or not check_password(form_data.password,user.hashed_password): raise HTTPException(401,'Incorrect username or password',headers={'WWW-Authenticate':'Bearer'})
    if user.account_status!='ACTIVE': raise HTTPException(403,'Account is not active')
    token=create_token(user.username); user.last_login_at=datetime.utcnow(); db.add(UserSession(user_id=user.id,jwt_token=token,ip_address=request.client.host if request.client else None,user_agent=request.headers.get('user-agent'),expires_at=datetime.utcnow()+timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))); db.commit(); return Token(access_token=token)
@router.post('/logout',status_code=204)
def logout(token:str=Depends(oauth2_scheme),db:Session=Depends(get_db)):
    session=db.query(UserSession).filter(UserSession.jwt_token==token).first()
    if not session: raise HTTPException(404,'Session not found')
    session.revoked_at=datetime.utcnow(); db.commit()
