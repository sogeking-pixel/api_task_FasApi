from pydantic import BaseModel, ConfigDict
from enum import Enum
from datetime import date
from app.schemas.response_pagination import PaginationBaseModel


class TypeUserModel(str, Enum):
    super_admin = "super_admin"
    admin = "admin"
    client = "client"
    
class StatusUserModel(str, Enum):
    banned = 'banned'
    suspense = 'suspense'
    activate = 'activate'
    
class UserBaseModel(BaseModel):
    first_name: str
    last_name: str
    dni: str
    username: str
    date_born: date
    model_config = ConfigDict(from_attributes=True) 
    
    
class UserCreate(UserBaseModel):
    password: str
    
class UserResponse(UserBaseModel):
    id: int
    type_user : TypeUserModel
    status_account : StatusUserModel

class UserResponseWithPassword(UserResponse):
    password: str

class PaginationTaskResponse(PaginationBaseModel):
    data : list[UserResponse]
    