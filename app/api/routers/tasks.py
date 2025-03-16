from fastapi import APIRouter, HTTPException, Query,  status, Depends
from typing import List
from app.schemas.task import TaskResponse, TaskCreate, PriorityModel
from app.schemas.user import UserResponse
from typing import Annotated
from app.utils.util import CommonQueryParams, db_create, PaginationParams
from app.utils.token import get_current_active_user, get_only_admin
from sqlalchemy.orm import Session
from app.models.model import Task
from app.core.database import get_db


router = APIRouter()


# dependencies_token = [Depends(verify_token), Depends(verify_key)]
paginationparams  = Annotated[PaginationParams, Depends(PaginationParams)]  
commonsDep = Annotated[CommonQueryParams, Depends(CommonQueryParams)]


# completed!
@router.get('/', status_code=status.HTTP_200_OK)
async def read_task(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_active_user)],
    commons: commonsDep,
    pagination: paginationparams,
    priority: PriorityModel|None = None,
    )-> List[TaskResponse]:
    
    
    query = db.query(Task)
    
    if current_user.type_user == "client":
        query = query.filter(Task.user_id == current_user.id)
    
    if priority:
        query = query.filter(Task.priority == priority)
    
    if commons.search:
        query = query.filter(Task.title.ilike(f'%{commons.search}%'))
    
    if commons.sort:
        query = query.order_by(
            Task.title.desc() if commons.sort == 'desc' 
            else Task.title.asc()
        )
    
    query = query.offset(pagination.offset).limit(pagination.page_size)
    
    return query.all()


@router.post('/', status_code=status.HTTP_201_CREATED)
async def create_task(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_active_user)],
    task: TaskCreate
) -> dict:
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
        
    

@router.get('/{task_id}')
async def get_task(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_only_admin)],
    task_id: int,
    )->TaskResponse:
    if current_user.type_user == "client":
        taks = db.query(Task).filter(Task.id == task_id, current_user.id == Task.user_id).first()
    else:
        taks = db.query(Task).filter(Task.id == task_id ).first()
    return TaskResponse.model_validate(taks)


@router.delete('/{task_id}')
async def delete_task( 
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[UserResponse, 
    Depends(get_current_active_user)],
    task_id: int
)->dict:
    db.query(Task).filter(Task.id == task_id, current_user.id == Task.user_id).delete()
    return {'msg': "deleted!"}


@router.put('/{task_id}')
async def update(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_active_user)],
    task_id: int,
    task: TaskCreate
) -> dict:
    
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


@router.patch('/{task_id}')
async def update_parts(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_active_user)],
    task_id: int, 
    priority: PriorityModel|None = None, 
    title: str|None = Query(default=None, max_length=50), 
    description: str|None = None
)->dict:
    
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
    
   


@router.post('/{task_id}/complete')
async def complete_task(
    db: Annotated[Session, Depends(get_db)], 
    current_user: Annotated[UserResponse, Depends(get_current_active_user)],
    task_id: int
)->dict:
    result = db.query(Task).filter(
    Task.id == task_id,
    Task.user_id == current_user.id
    ).update({'completed': True})

    if result == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found or unauthorized"
        )
    db.commit()
    return {'msg':"completed!"}