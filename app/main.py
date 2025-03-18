from fastapi import FastAPI
from app.core.config import settings
from app.api.router import api_router
from fastapi.security import OAuth2PasswordBearer
from app.core.database import Base, engine
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    print(settings.POSTGRESQL_URL)  
    print("🔧 Creando tablas si no existen...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tablas creadas o ya existen.")
    yield 


app = FastAPI(
    title = settings.PROJECT_NAME,
    description = settings.PROJECT_DESCRIPTION,
    version = settings.VERSION,
    debug = settings.DEBUG,
    lifespan=lifespan
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app.include_router(api_router, prefix=settings.API_PREFIX)




# @app.get("/items/")
# async def read_items(token: Annotated[str, Depends(oauth2_scheme)]):
#     return {"token": token}

@app.get('/')
async def read_root():
    return {"Hello": "World"}



