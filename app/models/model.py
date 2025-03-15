from app.core.database import Base
from sqlalchemy import Column, Integer, String, Boolean, Date, DateTime, ForeignKey
from sqlalchemy import Enum as SQLAEnum
from app.schemas.user import TypeUserModel, StatusUserModel
from app.schemas.task import PriorityModel
from sqlalchemy.sql import func

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    dni = Column(String, unique=True, nullable=False, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    password = Column(String, nullable=False)
    date_born = Column(Date) 
    type_user = Column(SQLAEnum(TypeUserModel), default=TypeUserModel.client, nullable=False) 
    status_account = Column(SQLAEnum(StatusUserModel), nullable=False, default=StatusUserModel.activate) 
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())  
      

class Token(Base):
    __tablename__ = "tokens"

    id = Column(Integer, primary_key=True, nullable=False)
    access_token = Column(String, nullable=False, unique=True)
    user_id = Column(Integer, ForeignKey('users.id')) 
    created_at = Column(DateTime, nullable=False)
    expires_at = Column(DateTime, nullable=False) 


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    priority = Column(SQLAEnum(PriorityModel), nullable=False, default=PriorityModel.medium)
    completed = Column(Boolean, default=False)
    user_id = Column(Integer, ForeignKey('users.id')) 
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
