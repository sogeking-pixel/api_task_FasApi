from pydantic import BaseModel
from enum import Enum


class SortModel(str, Enum):
    asc = 'asc'
    desc = 'desc'

class PriorityModel(str, Enum):
    low = "low"
    medium  = "medium"
    high = "high"

class TaskModel(BaseModel):
    id: int
    title: str
    description: str | None = None
    priority: PriorityModel = PriorityModel.medium
    completed: bool = False
    user_id: int
    
    class Config:
        orm_mode = True