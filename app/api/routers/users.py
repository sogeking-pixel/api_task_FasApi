from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Annotated
from app.schemas.user import TypeUserModel, StatusUserModel, UserCreateModel, UserResponseModel
from app.utils.util import validate_len, verify_key, verify_token, CommonQueryParams
from app.utils.token import get_only_admin, get_only_super_admin, get_current_active_user
from app.models.list import users

router = APIRouter()

dependencies_token = [Depends(verify_token), Depends(verify_key)]
commonparams  =  Annotated[CommonQueryParams, Depends(CommonQueryParams)]

@router.get('/', response_model=list[UserResponseModel])
async def read_users(
    current_user: Annotated[UserResponseModel, Depends(get_only_admin)], 
    common : commonparams, 
    type_user: TypeUserModel| None = None, 
    status_user: StatusUserModel|None = None
    )->List[UserResponseModel]:
    
    if users:
        return []
    
    list_users = users.copy()
    
    if type_user:
        list_users = list(filter(lambda user: user.type_user  == type_user, list_users))
        
    if status_user:
        list_users = list(filter(lambda user: user.status_account == status_user, list_users))
    
    if common.search:
        list_users = list(filter(lambda user: common.search in (user.first_name or  user.last_name), list_users))
    
    if common.sort:
        list_users.sort(key=lambda user: user.first_name, reverse=(common.sort=='desc'))
        
    return list_users


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
