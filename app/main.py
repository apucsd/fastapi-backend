from fastapi import FastAPI, Request
from app.db.session import engine
from app.api.router import api_router
from app.db.base import Base
from rich.traceback import install
install(show_locals=True)
from fastapi.responses import JSONResponse



app = FastAPI(
    title="FastAPI Backend",
    version="1.0.0"
)

# CREATE DATABASE TABLES
Base.metadata.create_all(bind=engine)

app.include_router(api_router)


@app.get("/")
async def root():
    return {"message": "Welcome to the backend API!"}

@app.exception_handler(Exception)
async def human_readable_error_handler(request: Request, exc: Exception):
    # Print a clean, 1-line error to your terminal!
    print(f"❌ ERROR in {request.url.path}: {str(exc)}")
    
    return JSONResponse(
        status_code=500,
        content={"message": "Something went wrong! Check the terminal for details.", "error": str(exc)},
    )