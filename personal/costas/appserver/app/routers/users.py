from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.db_utils import commit_or_409
from app.core.security import hash_password
from app.database.session import get_db
from app.models.role import Role
from app.models.user import User
from app.schemas.user import UserCreate, UserOut
router=APIRouter(prefix='/users',tags=['Layer 2 - Users'])
@router.post('/',response_model=UserOut,status_code=201)
def create_user(user:UserCreate,db:Session=Depends(get_db)):
    if not db.query(Role).filter(Role.id==user.role_id).first(): raise HTTPException(400,'role_id does not exist')
    if db.query(User).filter((User.username==user.username)|(User.email==user.email)).first(): raise HTTPException(400,'username or email already in use')
    data=user.model_dump(exclude={'password'}); obj=User(**data,hashed_password=hash_password(user.password)); db.add(obj); db.commit(); db.refresh(obj); return obj
@router.get('/',response_model=list[UserOut])
def list_users(db:Session=Depends(get_db)): return db.query(User).all()
@router.get('/{user_id}',response_model=UserOut)
def get_user(user_id:int,db:Session=Depends(get_db)):
    obj=db.query(User).filter(User.id==user_id).first()
    if not obj: raise HTTPException(404,'User not found')
    return obj
@router.put('/{user_id}',response_model=UserOut)
def update_user(user_id:int,data:UserCreate,db:Session=Depends(get_db)):
    obj=db.query(User).filter(User.id==user_id).first()
    if not obj: raise HTTPException(404,'User not found')
    if not db.query(Role).filter(Role.id==data.role_id).first(): raise HTTPException(400,'role_id does not exist')
    for field,value in data.model_dump(exclude={'password'}).items(): setattr(obj,field,value)
    obj.hashed_password=hash_password(data.password); db.commit(); db.refresh(obj); return obj
@router.delete('/{user_id}',status_code=204)
def delete_user(user_id:int,db:Session=Depends(get_db)):
    obj=db.query(User).filter(User.id==user_id).first()
    if not obj: raise HTTPException(404,'User not found')
    db.delete(obj); commit_or_409(db,'Cannot delete this user — related sessions, accounts, or audit logs still reference it')
