from fastapi import APIRouter, status, Depends, Request, HTTPException
from app.schemas.task import TaskResponse, TaskCreate, PriorityModel, PaginationTaskResponse
from app.schemas.user import UserResponse
from typing import Annotated
from app.utils.util import CommonQueryParams, PaginationParams
from app.utils.token import get_only_admin
from sqlalchemy.orm import Session
from app.models.model import Task, User
from app.core.database import get_db


router = APIRouter()


# dependencies_token = [Depends(verify_token), Depends(verify_key)]
paginationparams  = Annotated[PaginationParams, Depends(PaginationParams)]  
commonparams = Annotated[CommonQueryParams, Depends(CommonQueryParams)]

@router.get('/tasks', response_model=PaginationTaskResponse, name="admin_get_tasks")
async def read_tasks(
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_only_admin)], 
    common: commonparams, 
    pagination: paginationparams,
    priority: PriorityModel|None = None,    
) -> PaginationTaskResponse:
    
    if current_user.type_user == 'admin':    
        query = db.query(Task).join(User).filter(User.type_user == 'client' or (User.type_user == 'admin' and User.id == current_user.id))
    else:
        query = db.query(Task).join(User).filter(
            (User.type_user != 'super_admin') | 
            ((User.type_user == 'super_admin') & (User.id == current_user.id))
        )

    if priority:
        query = query.filter(Task.priority == priority)
    
    if common.search:
        query = query.filter(Task.title.ilike(f'%{common.search}%'))
    
    if common.sort:
        query = query.order_by(
            Task.title.desc() if common.sort == 'desc' 
            else Task.title.asc()
        )
    total_data = query.count()
    url_base = request.url_for("admin_get_tasks" )
    
    previous_link, next_link = pagination.return_link_pagination(total_data, url_base)
    
    tasks = query.offset(pagination.offset).limit(pagination.page_size).all()
    
    return  PaginationTaskResponse(
        count=total_data,
        next_link=next_link,
        previous_link=previous_link,
        data=[TaskResponse.model_validate(task) for task in tasks]
    )