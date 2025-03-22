from fastapi import APIRouter, Body, Depends, HTTPException, status
from typing import Annotated
from app.schemas.user import UserResponse
from app.utils.token import  get_current_active_user
from app.schemas.user import UserResponse
from app.utils.util import CommonQueryParams, PaginationParams
from app.models.model import User, RevokedToken, Token
from app.utils.token import get_db, get_password_hash
from sqlalchemy.orm import Session


router = APIRouter()

commonparams  =  Annotated[CommonQueryParams, Depends(CommonQueryParams)]
paginationparams  = Annotated[PaginationParams, Depends(PaginationParams)]

@router.get('/me')
async def get_user( 
    current_user: Annotated[UserResponse, Depends(get_current_active_user)]
)->UserResponse:    
    return current_user



@router.patch('/{user_id}/password')
async def change_password(
    user_id: int, 
    current_user: Annotated[UserResponse, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)],
    new_password: Annotated[str, Body()]
) -> dict:
    
    if current_user.type_user == 'client' and current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
        detail="Could not access")
    
    user: User = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
        detail="Could not found")
     
    if current_user.type_user == 'admin' and user.type_user != 'client':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
        detail="Could not access")  
    
    # Store all existing tokens in RevokedToken
    tokens :list[Token] = db.query(Token).filter(Token.user_id == user_id).all()
    for token in tokens:
        revoked_token = RevokedToken(token=token.access_token)
        db.add(revoked_token)
        db.delete(token)
    
    user.password = get_password_hash(new_password)  
    db.commit()
    
    return {'msg': "Password updated successfully!"}
    
