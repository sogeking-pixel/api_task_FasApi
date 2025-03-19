from fastapi import APIRouter
from app.api.routers import auth
from app.api.routers.admin import tasks as admin_tasks, users as admin_users
from app.api.routers.client import tasks as client_tasks, users as client_users

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(admin_users.router, prefix="/admin", tags=["Admin Users"])
api_router.include_router(admin_tasks.router, prefix="/admin", tags=["Admin Tasks"])
api_router.include_router(client_users.router, prefix="/users", tags=["Client Users"])
api_router.include_router(client_tasks.router, prefix="/users", tags=["Client Tasks"])