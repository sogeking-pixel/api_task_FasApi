from fastapi import APIRouter,  Depends
from typing import List, Annotated
from app.schemas.user import UserResponse
from app.schemas.task import TaskResponse, PriorityModel
from app.utils.util import  CommonQueryParams, PaginationParams
from app.utils.token import get_only_admin
from sqlalchemy.orm import Session
from app.models.model import Task
from app.core.database import get_db

router = APIRouter()

# dependencies_token = [Depends(verify_token), Depends(verify_key)]
commonparams  =  Annotated[CommonQueryParams, Depends(CommonQueryParams)]
paginationparams  = Annotated[PaginationParams, Depends(PaginationParams)]

@router.get('/user/{user_id}/tasks', response_model=list[TaskResponse])
async def read_user_tasks(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_only_admin)], 
    common: commonparams, 
    pagination: paginationparams,
    priority: PriorityModel|None = None,    
) -> List[TaskResponse]:
    
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

