from fastapi import FastAPI
from app.db.session import engine
from app.api.router import api_router
from app.db.base import Base

app = FastAPI(
    title="FastAPI Backend",
    version="1.0.0"
)

# CREATE DATABASE TABLES
Base.metadata.create_all(bind=engine)

app.include_router(api_router)


@app.get("/")
def root():
    return {"message": "Welcome to the backend API!"}