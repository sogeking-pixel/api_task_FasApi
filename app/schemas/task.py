from pydantic import BaseModel
from enum import Enum


class SortModel(str, Enum):
    asc = 'asc'
    desc = 'desc'

class PriorityModel(str, Enum):
    low = "low"
    medium  = "medium"
    high = "high"

class TaskBaseModel(BaseModel):
    title: str
    description: str | None = None
    priority: PriorityModel = PriorityModel.medium
    completed: bool = False
    user_id: int
    class Config:
        orm_mode = True

class TaskResponse(TaskBaseModel):
    id: int

class TaskCreate(TaskBaseModel):
    pass