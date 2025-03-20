from fastapi import APIRouter, Depends, HTTPException, status, Request
from typing import Annotated
from app.schemas.user import TypeUserModel, StatusUserModel, UserResponse, UserCreate, PaginationUserResponse
from app.utils.util import CommonQueryParams, PaginationParams, db_create
from app.utils.token import get_only_admin, get_only_super_admin,get_password_hash

from sqlalchemy.orm import Session
from app.models.model import User
from app.core.database import get_db

router = APIRouter()

# dependencies_token = [Depends(verify_token), Depends(verify_key)]

commonparams  =  Annotated[CommonQueryParams, Depends(CommonQueryParams)]
paginationparams  = Annotated[PaginationParams, Depends(PaginationParams)]

@router.get('/users', response_model=PaginationUserResponse, name="admin.get_users")
async def read_users(
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_only_admin)], 
    common: commonparams, 
    pagination: paginationparams,
    type_user: TypeUserModel | None = None, 
    status_user: StatusUserModel | None = None,
) -> PaginationUserResponse:
    
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
        
    total_data = query.count()
    url_base = request.url_for("admin.get_users")
    
    previous_link, next_link = pagination.return_link_pagination(total_data, url_base)
    
    users = query.offset(pagination.offset).limit(pagination.page_size).all()
    
    return PaginationUserResponse(
        count=total_data,
        next_link=next_link,
        previous_link=previous_link,
        data=[UserResponse.model_validate(user) for user in users]
    )


@router.post('/create_admin', status_code=201)
async def create_admin(current_user: Annotated[UserResponse, Depends(get_only_super_admin)], user: UserCreate, db: Annotated[Session, Depends(get_db)])->dict:
    
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
    return {'msg': 'create!', 'user': UserResponse.model_validate(db_user)}



@router.get('/users/{user_id}', status_code=201, response_model=UserResponse)
async def get_user( 
    current_user: Annotated[UserResponse, Depends(get_only_admin)], 
    user_id: int,
    db: Annotated[Session, Depends(get_db)]
)->UserResponse:
     
    user = db.query(User).filter(User.id == user_id).first()
    
    return user
        
    
@router.delete('/users/{user_id}')
async def delete_user(
    user_id: int, 
    current_user: Annotated[UserResponse, Depends(get_only_super_admin)],
    db: Annotated[Session, Depends(get_db)]
)->dict:
    db.query(User).filter(User.id == user_id).delete()
    return  {'msg': "deleted!"}


@router.patch('/users/{user_id}/status')
async def patch_user(
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

