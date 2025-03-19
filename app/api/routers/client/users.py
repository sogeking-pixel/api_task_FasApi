from fastapi import APIRouter, Depends
from typing import Annotated
from app.schemas.user import UserResponse
from app.utils.token import  get_current_active_user
from app.schemas.user import UserResponse
from app.utils.util import CommonQueryParams, PaginationParams


router = APIRouter()

commonparams  =  Annotated[CommonQueryParams, Depends(CommonQueryParams)]
paginationparams  = Annotated[PaginationParams, Depends(PaginationParams)]

@router.get('/me')
async def get_user( 
    current_user: Annotated[UserResponse, Depends(get_current_active_user)]
)->UserResponse:    
    return current_user



# @router.patch('/{user_id}/status')
# async def get_user(
#     user_id: int, 
#     current_user: Annotated[UserResponse, Depends(get_only_admin)],
#     db: Annotated[Session, Depends(get_db)],
#     status: str
# )->dict:
    
#     if current_user.type_user == 'admin':
#         db.query(User).filter(User.id == user_id and User.type_user == 'client').update({'status_account': status})
#     else:
#         db.query(User).filter(User.id == user_id and User.type_user != 'super_admin').update({'status_account': status})
#     return  {'msg': "update status user!"}

