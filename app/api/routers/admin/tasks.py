from fastapi import APIRouter, status, Depends, Request
from app.schemas.task import TaskResponse, TaskCreate, PriorityModel, PaginationTaskResponse
from app.schemas.user import UserResponse
from typing import Annotated
from app.utils.util import CommonQueryParams, PaginationParams
from app.utils.token import get_only_admin
from sqlalchemy.orm import Session
from app.models.model import Task
from app.core.database import get_db


router = APIRouter()


# dependencies_token = [Depends(verify_token), Depends(verify_key)]
paginationparams  = Annotated[PaginationParams, Depends(PaginationParams)]  
commonsDep = Annotated[CommonQueryParams, Depends(CommonQueryParams)]


# completed!
