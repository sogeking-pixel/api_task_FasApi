from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Annotated
from app.schemas.user import TypeUserModel, StatusUserModel, UserCreateModel, UserResponseModel
from app.schemas.task import TaskModel, PriorityModel
from app.utils.util import validate_len, verify_key, verify_token, CommonQueryParams, PaginationParams, db_create
from app.utils.token import get_only_admin, get_only_super_admin, get_current_active_user

from sqlalchemy.orm import Session
from app.models.model import Task
from app.core.database import get_db

router = APIRouter()

dependencies_token = [Depends(verify_token), Depends(verify_key)]
commonparams  =  Annotated[CommonQueryParams, Depends(CommonQueryParams)]
paginationparams  = Annotated[PaginationParams, Depends(PaginationParams)]

@router.get('/user/{user_id}/tasks', response_model=list[TaskModel])
async def read_user_tasks(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[UserResponseModel, Depends(get_only_admin)], 
    common: commonparams, 
    pagination: paginationparams,
    priority: PriorityModel|None = None,    
) -> List[TaskModel]:
    
    query = db.query(Task).filter(Task.user_id == current_user.id)
    
    if priority:
        query = query.filter(Task.priority == priority)
    
    if common.search:
        query = query.filter(Task.title.ilike(f'%{common.search}%'))
    
    if common.sort:
        query = query.order_by(
            Task.title.desc() if common.sort == 'desc' 
            else Task.title.asc()
        )
    
    query = query.offset(pagination.offset).limit(pagination.page_size)
    
    return query.all()

