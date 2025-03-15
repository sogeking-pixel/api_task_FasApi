from fastapi import FastAPI, HTTPException, Depends
from typing import List, Optional, Annotated
from app.core.config import settings
from app.api.router import api_router
from fastapi.security import OAuth2PasswordBearer


app = FastAPI(
    title = settings.PROJECT_NAME,
    description = settings.PROJECT_DESCRIPTION,
    version = settings.VERSION,
    debug = settings.DEBUG
)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app.include_router(api_router, prefix=settings.API_PREFIX)


# @app.get("/items/")
# async def read_items(token: Annotated[str, Depends(oauth2_scheme)]):
#     return {"token": token}

# @app.get('/')
# async def read_root():
#     return {"Hello": "World"}



