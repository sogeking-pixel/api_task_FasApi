from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Annotated
from app.schemas.user import TypeUserModel, StatusUserModel, UserResponse, UserCreate
from app.utils.util import CommonQueryParams, PaginationParams, db_create
from app.utils.token import get_only_admin, get_only_super_admin, get_current_active_user, get_password_hash

from sqlalchemy.orm import Session
from app.models.model import User
from app.core.database import get_db

router = APIRouter()

# dependencies_token = [Depends(verify_token), Depends(verify_key)]

commonparams  =  Annotated[CommonQueryParams, Depends(CommonQueryParams)]
paginationparams  = Annotated[PaginationParams, Depends(PaginationParams)]

@router.get('/', response_model=list[UserResponse])
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

@router.post('/create_admin', status_code=201)
async def sign_up(current_user: Annotated[UserResponse, Depends(get_only_super_admin)], user: UserCreate, db: Annotated[Session, Depends(get_db)])->dict:
    
    user.first_name = user.first_name.lower()
    user.last_name = user.last_name.lower()
    user.username =  user.username.lower()
    
    user_exists  = db.query(User).filter(User.username == user.username).first()
    if user_exists:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,  detail="Username is existed",)
    user.password = get_password_hash(user.password)
    userdata = user.model_dump()
    userdata["type_user"] = "admin"
    db_user = db_create(db, User( **userdata ))
    return {'msg': 'create!', 'user': UserResponse(db_user)}

@router.get('/me')
async def get_user( 
    current_user: Annotated[UserResponse, Depends(get_current_active_user)]
)->UserResponse:    
    return current_user


@router.get('/{user_id}', status_code=201, response_model=UserResponse)
async def get_user( 
    current_user: Annotated[UserResponse, Depends(get_only_admin)], 
    user_id: int,
    db: Annotated[Session, Depends(get_db)]
)->UserResponse:
     
    user = db.query(User).filter(User.id == user_id).first()
    
    return user
        
    
@router.delete('/{user_id}')
async def get_user(
    user_id: int, 
    current_user: Annotated[UserResponse, Depends(get_only_super_admin)],
    db: Annotated[Session, Depends(get_db)]
)->dict:
    db.query(User).filter(User.id == user_id).delete()
    return  {'msg': "deleted!"}


@router.patch('/{user_id}/status')
async def get_user(
    user_id: int, 
    current_user: Annotated[UserResponse, Depends(get_only_admin)],
    db: Annotated[Session, Depends(get_db)],
    status: str
)->dict:
    
    if current_user.type_user == 'admin':
        db.query(User).filter(User.id == user_id and User.type_user == 'client').update({'status_account': status})
    else:
        db.query(User).filter(User.id == user_id and User.type_user != 'super_admin').update({'status_account': status})
    return  {'msg': "update status user!"}
