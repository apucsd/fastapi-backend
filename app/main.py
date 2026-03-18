from app.utils.exceptions import AppException
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.db.session import engine
from app.api.router import api_router
from app.db.base import Base
from rich.traceback import install

install(show_locals=True)


app = FastAPI(title="FastAPI Backend", version="1.0.0")

# CREATE DATABASE TABLES
Base.metadata.create_all(bind=engine)

app.include_router(api_router)


@app.get("/")
async def root():
    return {"message": "Welcome to the backend API!"}


@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "statusCode": exc.status_code,
            "message": exc.message,
            "data": None,
        },
    )


@app.api_route("/{full_path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def not_found_handler(request: Request, full_path: str):
    return JSONResponse(
        status_code=404,
        content={
            "success": False,
            "statusCode": 404,
            "message": "API NOT FOUND!",
            "error": {
                "path": request.url.path,
                "message": "Your requested path is not found!",
            },
        },
    )
