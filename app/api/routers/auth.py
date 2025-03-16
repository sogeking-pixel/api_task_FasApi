from fastapi import APIRouter, HTTPException, Body, status, Depends
from typing import Annotated 
from app.schemas.user import UserCreate, UserResponse
from app.schemas.token import TokenCreate
from app.utils.util import verify_key, db_create
from app.utils.token import create_access_token, get_password_hash, authenticate_user, oauth2_scheme, get_playload

from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.model import User, Token, RevokedToken
from app.core.database import get_db
from jwt.exceptions import InvalidTokenError

from datetime import datetime, timezone
router = APIRouter()


@router.post('/sign-up', status_code=201, dependencies= [Depends(verify_key)])
async def sign_up(user: UserCreate, db: Annotated[Session, Depends(get_db)])->dict:
    
    user.first_name = user.first_name.lower()
    user.last_name = user.last_name.lower()
    user.username =  user.username.lower()
    
    user_exists  = db.query(User).filter(User.username == user.username).first()
    if user_exists:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,  detail="Username is existed",)
    
    user.password = get_password_hash(user.password)
    db_user = db_create(db, User( **user.model_dump() ))
    return {'msg': 'create!', 'user': UserResponse(db_user)}



@router.post('/login')
async def login(db: Annotated[Session, Depends(get_db)],username: Annotated[str, Body()], password: Annotated[str, Body()])->dict:
    
    user = authenticate_user(db, username, password)
    
    if not user:
        raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Could not validate credentials")
    
    token_str, date_expire = create_access_token(user)
   
    token = TokenCreate(token_type="bear", access_token=token_str, expires_at=date_expire, user_id=user.id)
    
    db_token = db_create(db, Token(**token.model_dump()))
    
    return {'msg': 'logeado!', 'token': db_token.access_token}


@router.post('/logout')
async def logout(token: Annotated[str, Depends(oauth2_scheme)], db: Annotated[Session, Depends(get_db)]):
    try:
        
        payload  = get_playload(db, token)
        exp_timestamp = payload.get("exp")
        
        expires_at = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)
        
        existing_token = db.query(RevokedToken).filter(RevokedToken.token == token).first()
        if existing_token:
            return {"message": "Token already revoked"}
        
        revoked_token = RevokedToken(
            token=token,
            expires_at=expires_at
        )
        
        db.add(revoked_token)
        db.commit()
        
        return {"message": "Successfully logged out"}
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

