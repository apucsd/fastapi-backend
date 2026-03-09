from fastapi import FastAPI
from app.api.router import api_router

app = FastAPI(
    title="FastAPI Backend",
    version="1.0.0"
)

app.include_router(api_router)


@app.get("/")
def root():
    return {"message": "Welcome to the backend API!"}