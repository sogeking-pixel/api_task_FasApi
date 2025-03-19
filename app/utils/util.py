from app.schemas.task import SortModel
from fastapi import Query, Header, HTTPException, status
from typing import Annotated
from pydantic import AfterValidator
from sqlalchemy.orm import Session
from app.core.config import settings
from urllib.parse import urlencode

API_KEY: str = settings.API_KEY

def validated_key(key: str|None):
    if not key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="The Key is missing")
    if not key.startswith('API GROSSO|'):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Inconrrect Key")
    return  key.replace("API GROSSO|",'')


# async def verify_key(api_key: Annotated[str|None, Header(), AfterValidator(validated_key)]  ):
#     if not api_key == API_KEY:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="X-Key header invalid")
    
async def verify_key(api_key: Annotated[str | None, Header()] = None):
    # First check if the key exists
    if not api_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="The Key is missing")
    
    # Now validate the key format
    if not api_key.startswith('API GROSSO|'):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Inconrrect Key")
    
    # Finally check if the key is correct after stripping the prefix
    cleaned_key = api_key.replace("API GROSSO|", '')
    if cleaned_key != API_KEY:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="X-Key header invalid")
    
    return True
def check_valid_search(search: str):
    if not len(search.strip())<3:
        raise ValueError('the length of the search string is less than 3')
    return str
    
class CommonQueryParams:
    def __init__(self, search:  Annotated[str | None, Query(max_length=3),AfterValidator(check_valid_search)] = None, sort: SortModel|None = None):
        self.search = search
        self.sort = sort
        
class PaginationParams:
    def __init__(self, page: int = 1, page_size: int = 10):
        self.page = page
        self.page_size = page_size
        self.offset = (page - 1) * page_size
        
    def return_link_pagination(self, total_data: int, url_base: str)->list[str|None]:
        next_link = None
        previous_link = None
        
        if self.offset + self.page_size < total_data:
            next_params = {"page": self.page + 1, "page_size": self.page_size}
            next_link = f"{url_base}?{urlencode(next_params)}"
            
        if self.offset > 0:
            prev_params = {"page": max(1, self.page - 1), "page_size": self.page_size}
            previous_link = f"{url_base}?{urlencode(prev_params)}"
        return previous_link, next_link
        
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


    