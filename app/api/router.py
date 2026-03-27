from fastapi import APIRouter
from app.api.auth_routes import router as auth_router
from app.api.user_routes import router as user_router
from app.api.file_routes import router as file_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth_router)
api_router.include_router(user_router)
api_router.include_router(file_router)
