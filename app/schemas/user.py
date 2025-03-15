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
    id: int
    first_name: str
    last_name: str
    dni: str
    username: str
    date_born: date
    type_user : TypeUserModel
    status_account : StatusUserModel = StatusUserModel.activate
    class Config:
        orm_mode = True
        from_attributes = True 
    
    
class UserCreateModel(UserBaseModel):
    password: str
    
class UserResponseModel(UserBaseModel):
    pass
    