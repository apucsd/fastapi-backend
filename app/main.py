from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_redoc_html
from fastapi.responses import HTMLResponse, JSONResponse
from rich.traceback import install

from app.api.router import api_router
from app.db.base import Base
from app.db.session import engine
from app.utils.exceptions import AppException

install(show_locals=True)

app = FastAPI(title="FastAPI Backend", version="1.0.0", redoc_url=None)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# CREATE DATABASE TABLES
Base.metadata.create_all(bind=engine)

app.include_router(api_router)


@app.get("/")
async def root():
    return {"message": "Welcome to the backend API!"}


@app.get("/redoc", include_in_schema=False, response_class=HTMLResponse)
async def redoc_html():
    return get_redoc_html(
        openapi_url=app.openapi_url,
        title=f"{app.title} - ReDoc",
        redoc_js_url="https://cdn.redoc.ly/redoc/latest/bundles/redoc.standalone.js",
    )


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


@app.api_route(
    "/{full_path:path}",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    include_in_schema=False,
)
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


