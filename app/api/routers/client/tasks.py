from fastapi import APIRouter, HTTPException, Query,  status, Depends, Request
from app.schemas.task import TaskResponse, TaskCreate, PriorityModel, PaginationTaskResponse
from app.schemas.user import UserResponse
from typing import Annotated
from app.utils.util import CommonQueryParams, db_create, PaginationParams
from app.utils.token import get_current_active_user
from sqlalchemy.orm import Session
from app.models.model import Task
from app.core.database import get_db


router = APIRouter()

commonparams  =  Annotated[CommonQueryParams, Depends(CommonQueryParams)]
paginationparams  = Annotated[PaginationParams, Depends(PaginationParams)]

@router.get('/{user_id}/tasks', response_model=PaginationTaskResponse, name="user_get_tasks")
async def read_user_tasks(
    request: Request,
    user_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_active_user)], 
    common: commonparams, 
    pagination: paginationparams,
    priority: PriorityModel|None = None,    
) -> PaginationTaskResponse:
    
    if current_user.type_user == "client" and user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Task unauthorized"
        )
    
    if current_user.type_user == "client" :
        query = query.filter(Task.user_id == current_user.id)
        
    query = db.query(Task).filter(Task.user_id == user_id)
    
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
    url_base = request.url_for("get_tasks", user_id = user_id )
    
    previous_link, next_link = pagination.return_link_pagination(total_data, url_base)
    
    tasks = query.offset(pagination.offset).limit(pagination.page_size).all()
    
    return  PaginationTaskResponse(
        count=total_data,
        next_link=next_link,
        previous_link=previous_link,
        data=[TaskResponse.model_validate(task) for task in tasks]
    )


@router.post('/{user_id}/tasks', status_code=status.HTTP_201_CREATED)
async def create_task(
    user_id:int, 
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_active_user)],
    task: TaskCreate
) -> dict:
    if user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="created unauthorized"
        )
    data_taks = task.model_dump()
    data_taks['user_id'] = current_user.id
    
    db_task = db_create(db, Task(**data_taks))
    
    if not db_task:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create task"
        )

    return {
        'status': 'success',
        'message': 'Task created successfully',
        'data': TaskResponse.model_validate(db_task)
    }
        
    

@router.get('/{user_id}/tasks/{task_id}')
async def get_task(
    user_id:int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_active_user)],
    task_id: int,
    )->TaskResponse:
    if current_user.type_user == "client" and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Task unauthorized"
        )
    
    if current_user.type_user == "client":
        taks = db.query(Task).filter(Task.id == task_id, current_user.id == Task.user_id).first()
    else:
        taks = db.query(Task).filter(Task.id == task_id ).first()
    return TaskResponse.model_validate(taks)


@router.delete('/{user_id}/tasks/{task_id}')
async def delete_task(
    user_id: int, 
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[UserResponse, 
    Depends(get_current_active_user)],
    task_id: int
)->dict:
    
    if user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="delete unauthorized"
        )
        
    db.query(Task).filter(Task.id == task_id, current_user.id == Task.user_id).delete()
    return {'msg': "deleted!"}


@router.put('/{user_id}/tasks/{task_id}')
async def update_task(
    user_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_active_user)],
    task_id: int,
    task: TaskCreate
) -> dict:
    
    if user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="put unauthorized"
        )
        
    existing_task = db.query(Task).filter(
        Task.id == task_id,
        Task.user_id == current_user.id
    ).first()

    if not existing_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found or unauthorized"
        )
    
    update_data = task.model_dump(exclude_unset=True)
    
    db.query(Task).filter(Task.id == task_id).update(update_data)
    db.commit()
    db.refresh(existing_task)

    return {'msg': 'updated!', 'task': existing_task}


@router.patch('/{user_id}/tasks/{task_id}')
async def update_parts_task(
    user_id:int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_active_user)],
    task_id: int, 
    priority: PriorityModel|None = None, 
    title: str|None = Query(default=None, max_length=50), 
    description: str|None = None
)->dict:
    if user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="put unauthorized"
        )
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.user_id == current_user.id
    ).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found or unauthorized"
        )
    
    update_data = {}
    if priority is not None:
        update_data['priority'] = priority
    if title is not None:
        update_data['title'] = title 
    if description is not None:
        update_data['description'] = description

    if not update_data:
        return {'msg': 'updated!', 'task': task}
        
        
    result = db.query(Task).filter(
        Task.id == task_id,
        Task.user_id == current_user.id
    ).update(update_data)
    
    if result == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found or unauthorized"
        )
    db.commit()
    task = db.query(Task).filter(Task.id == task_id).first()    
    return {'msg': 'updated!', 'task':TaskResponse.model_validate(task) }
      

@router.post('/{user_id}/{task_id}/complete')
async def complete_task(
    user_id : int,
    db: Annotated[Session, Depends(get_db)], 
    current_user: Annotated[UserResponse, Depends(get_current_active_user)],
    task_id : int
)->dict:
    result = db.query(Task).filter(
    Task.id == task_id,
    Task.user_id == current_user.id
    ).update({'completed': True})
    
    if user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="put unauthorized"
        )
        
    if result == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found or unauthorized"
        )
    db.commit()
    return {'msg':"completed!"}