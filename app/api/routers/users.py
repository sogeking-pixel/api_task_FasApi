from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Annotated
from app.schemas.user import TypeUserModel, StatusUserModel, UserCreateModel, UserResponseModel
from app.utils.util import validate_len, verify_key, verify_token, CommonQueryParams, PaginationParams
from app.utils.token import get_only_admin, get_only_super_admin, get_current_active_user

from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.model import User, Token
from app.core.database import get_db

router = APIRouter()

dependencies_token = [Depends(verify_token), Depends(verify_key)]
commonparams  =  Annotated[CommonQueryParams, Depends(CommonQueryParams)]
paginationparams  = Annotated[PaginationParams, Depends(PaginationParams)]

@router.get('/', response_model=list[UserResponseModel])
async def read_users(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[UserResponseModel, Depends(get_only_admin)], 
    common: commonparams, 
    pagination: paginationparams,
    type_user: TypeUserModel | None = None, 
    status_user: StatusUserModel | None = None,
   
) -> List[UserResponseModel]:
    
    query = db.query(User)
    
    if type_user:
        query = query.filter(User.type_user == type_user)
    
    if status_user:
        query = query.filter(User.status_account == status_user)
    
    if common.search:
        query = query.filter(
            (User.first_name.ilike(f'%{common.search}%')) |
            (User.last_name.ilike(f'%{common.search}%'))
        )
    
    if common.sort:
        query = query.order_by(
            User.first_name.desc() if common.sort == 'desc' 
            else User.first_name.asc()
        )
    
    query = query.offset(pagination.offset).limit(pagination.page_size)
    
    return query.all()


@router.get('/{user_id}', status_code=201, response_model=list[UserResponseModel])
async def get_user( current_user: Annotated[UserResponseModel, Depends(get_current_active_user)], user_id: int)->UserResponseModel:
    if not validate_len(user_id, users):
        raise HTTPException(status_code=404)
    if current_user.type_user == "client" and current_user.username != users[user_id].username :
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return users[id]
    
    
@router.delete('/{user_id}')
async def get_user(user_id: int, current_user: Annotated[UserResponseModel, Depends(get_only_super_admin)])->dict:
    if not validate_len(user_id, users):
        raise HTTPException(status_code=404)
    users.pop(user_id)
    return  {'msg': "deleted!"}
