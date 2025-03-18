from pydantic import BaseModel, ConfigDict
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
    model_config = ConfigDict(from_attributes=True)

class TaskResponse(TaskBaseModel):
    id: int
    user_id: int

class TaskCreate(TaskBaseModel):
    pass