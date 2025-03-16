
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends,  HTTPException, status
from app.schemas.user import UserResponse, UserResponseWithPassword
from app.schemas.token import TokenData
import jwt
from jwt.exceptions import InvalidTokenError
from datetime import datetime, timedelta, timezone
from typing import Annotated
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.model import User
from app.core.database import get_db
from app.models.model import  RevokedToken

SECRET_KEY: str = settings.SECRETE_KEY
ALGORITHM: str = settings.ALGORITHM_TOKEN
ACCESS_TOKEN_EXPIRE_MINUTES: str = settings.ACCESS_TOKEN_EXPIRE_MINUTES


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
credentials_expires = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZE,
        detail="Token expired",
        headers={"WWW-Authenticate": "Bearer"},
    )


def verify_password(plain_password, hashed_password)-> CryptContext:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password)-> CryptContext:
    return pwd_context.hash(password)


def get_user(db: Session,  username: str)-> UserResponseWithPassword | None:
    user = db.query(User).filter(User.username == username).first()
    return user


def authenticate_user(db: Session, username: str, password: str) -> UserResponse | None:
    user = get_user(db, username)
    if not user:
        return None
    if not verify_password(password, user.password):
        return None
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> tuple[str, datetime, datetime]:
    to_encode = data.copy()
    now_time = datetime.now(timezone.utc)
    if expires_delta:
        expire = now_time + expires_delta
    else:
        expire = now_time+ timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt, expire


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: Annotated[Session, Depends(get_db)]) -> UserResponse:
    
    try:
        revoked_token_exist = db.query(RevokedToken).filter(RevokedToken.token == token).first()
        
        if revoked_token_exist:
            raise credentials_exception
        
        payload = get_playload(token)
        now_time = datetime.now(timezone.utc)
        
        
        username = payload.get("sub")        
        date_expires =  payload.get("exp")
        
        if date_expires > now_time or not date_expires:
            raise credentials_expires
        
        if username is None:
            raise credentials_exception
        
        token_data = TokenData(username=username)
        
    except InvalidTokenError:
        raise credentials_exception
    
    user = get_user(db, token_data.username)
    
    if user is None:
        raise credentials_exception
    
    return user
    
    
async def get_current_active_user(
    current_user: Annotated[UserResponse, Depends(get_current_user)],
):
    if current_user.status_account ==  'suspense' :
        raise HTTPException(status_code=400, detail="suspense user")
    if current_user.status_account ==  'banned' :
        raise HTTPException(status_code=400, detail="banned user")
    return current_user



async def get_only_admin( current_user: Annotated[UserResponse, Depends(get_current_active_user)],
):
    if current_user.type_user == "client":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not admin" )
    
    return current_user


async def get_only_super_admin(current_user: Annotated[UserResponse, Depends(get_current_active_user)]):
    if not current_user.type_user == "super_admin":
        raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not super admin")
    return current_user

def get_playload(token: str):
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    return payload
    