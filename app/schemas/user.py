from pydantic import BaseModel
from enum import Enum
from datetime import date

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
    class Config:
        orm_mode = True
        from_attributes = True 
    
    
class UserCreate(UserBaseModel):
    password: str
    
class UserResponse(UserBaseModel):
    id: int
    type_user : TypeUserModel
    status_account : StatusUserModel

class UserResponseWithPassword(UserResponse):
    password: str
    
    