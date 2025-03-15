from fastapi import APIRouter, HTTPException, Body, status, Depends
from typing import Annotated 
from app.schemas.user import UserCreateModel, UserResponseModel
from app.schemas.token import TokenModel
from app.utils.util import verify_key, db_create
from app.utils.token import create_access_token, get_password_hash, authenticate_user

from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.model import User, Token
from app.core.database import get_db

router = APIRouter()


@router.post('/sign-up', status_code=201, dependencies= [Depends(verify_key)])
async def sign_up(user: UserCreateModel, db: Annotated[Session, Depends(get_db)])->dict:
    
    user.first_name = user.first_name.lower()
    user.last_name = user.first_name.lower()
    user.username =  user.username.lower()
    
    user_exists  = db.query(User).filter(User.username == user.username).first()
    if user_exists:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,  detail="Username is existed",)
    
    user.password = get_password_hash(user.password)
    db_user = db_create(db, User( **user ))
    return {'msg': 'create!', 'user': UserResponseModel(db_user)}



@router.post('/login')
async def login(db: Annotated[Session, Depends(get_db)],username: Annotated[str, Body()], password: Annotated[str, Body()])->dict:
    
    user = authenticate_user(db, username, password)
    
    if not user:
        raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Could not validate credentials")
    
    token_str, date_now, date_expire = create_access_token(user)
   
    token = TokenModel(token_type="bear", access_token=token_str, created_date=date_now, expiration_date=date_expire, user_id=user.id)
    
    db_token = db_create(db, Token(**token))
    
    return {'msg': 'logeado!', 'token': db_token.access_token}
