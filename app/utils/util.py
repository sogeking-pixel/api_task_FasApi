from app.schemas.task import SortModel
from fastapi import Query, Header, HTTPException, status
from typing import Annotated
from pydantic import AfterValidator
from sqlalchemy.orm import Session
from app.core.config import settings

API_KEY: str = settings.API_KEY

def validated_key(key: str):
    if not key.startswith('API GROSSO|'):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Inconrrect Key")
    return  key.replace("API GROSSO|",'')

def check_valid_search(search: str):
    if not len(search.strip())<3:
        raise ValueError('the length of the search string is less than 3')
    return str


async def verify_key(api_key: Annotated[str, Header(), AfterValidator(validated_key)] ):
    if not api_key == API_KEY:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="X-Key header invalid")
    
class CommonQueryParams:
    def __init__(self, search:  Annotated[str | None, Query(max_length=3),AfterValidator(check_valid_search)] = None, sort: SortModel|None = None):
        self.search = search
        self.sort = sort
        
class PaginationParams:
    def __init__(self, page: int = 1, page_size: int = 10):
        self.page = page
        self.page_size = page_size
        self.offset = (page - 1) * page_size
        
def db_create(db: Session, data: any):
    try:
        db.add(data)  
        db.commit()
        db.refresh(data)
       
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Error al crear registro: {str(e)}"
        )
    return data