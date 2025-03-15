from fastapi import APIRouter, HTTPException, Query, Path,  status, Depends
from typing import List
from app.schemas.task import TaskModel, PriorityModel
from app.schemas.user import UserResponseModel
from typing import Annotated
from app.utils.util import CommonQueryParams, verify_token, verify_key, validate_len
from app.utils.token import get_current_active_user, get_only_admin
from app.models.list import tasks


router = APIRouter()


dependencies_token = [Depends(verify_token), Depends(verify_key)]
    
commonsDep = Annotated[CommonQueryParams, Depends(CommonQueryParams)]

def not_authorized_client(user: UserResponseModel, task_id: int)->bool:
    return user.type_user == "client" and user.username != tasks[task_id].user_username

@router.get('/', status_code=status.HTTP_200_OK)
async def read_task(
    current_user: Annotated[UserResponseModel, Depends(get_current_active_user)],
    commons: commonsDep,
    priority: PriorityModel|None = None,
   
    )-> List[TaskModel]:
    
    if current_user.type_user == "client":
        list_taks = [task for task in tasks if task.user_username == current_user.username]
    else:
        list_taks = tasks.copy()
    
    if priority:
        list_taks = list(filter(lambda i: i.priority == priority, list_taks))
    
    if commons.search:
        list_taks = list(filter(lambda i: commons.search in i.title or (i.description and commons.search in i.description), list_taks))
    
    if commons.sort:
        list_taks.sort(key=lambda x: x.title, reverse=(commons.sort=='desc'))

    return list_taks


@router.post('/',status_code=status.HTTP_201_CREATED)
async def create_task( current_user: Annotated[UserResponseModel, Depends(get_current_active_user)],task : TaskModel)->dict:
    task.user_username = current_user.username
    tasks.append(task)
    return {'msg': 'create!'}


@router.get('/{task_id}')
async def get_task(
    current_user: Annotated[UserResponseModel, Depends(get_current_active_user)],
    task_id: int,
    )->TaskModel:
    
    if validate_len(task_id, tasks):
        raise HTTPException(status_code=404)
    if not_authorized_client(current_user, task_id) :
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return tasks[task_id]


@router.delete('/{task_id}')
async def delete_task( current_user: Annotated[UserResponseModel, Depends(get_current_active_user)],task_id:  Annotated[int, Path(title="The ID of the item to get", ge=0, le=200)])->dict:
    if validate_len(task_id, tasks):
        raise HTTPException(status_code=404)
    if not_authorized_client(current_user, task_id) :
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    tasks.pop(task_id)
    return {'msg': "deleted!"}


@router.put('/{task_id}')
async def update( current_user: Annotated[UserResponseModel, Depends(get_current_active_user)],task_id: int, task_new: TaskModel)->dict:
    if validate_len(task_id):
        raise HTTPException(status_code=404)
    if not_authorized_client(current_user, task_id) :
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    tasks[task_id] = task_new
    return {'msg':'updated!', 'task': tasks[task_id]}   


@router.patch('/{task_id}')
async def update_parts(
    current_user: Annotated[UserResponseModel, Depends(get_current_active_user)],
    task_id: int, 
    priority: PriorityModel|None = None, 
    title: str| None = Query(default=None, max_length=50), 
    description: str|None = None
    )->dict:
    
    if validate_len(task_id, tasks):
        raise HTTPException(status_code=404)
    if not_authorized_client(current_user, task_id) :
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    
    task = tasks[task_id]
    
    if priority:
        task.priority = priority
    if title:
        task.title = title
    if description:
        task.description = description
    
    return {'msg':'updated!', 'task': tasks[task_id]}    


@router.post('/{task_id}/complete')
async def complete_task( current_user: Annotated[UserResponseModel, Depends(get_current_active_user)],task_id: int)->dict:
    
    if validate_len(task_id, tasks):
        raise HTTPException(status_code=404)
    if not_authorized_client(current_user, task_id) :
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    task = tasks[task_id]
    task.completed = True
    return {'msg':"completed!"}