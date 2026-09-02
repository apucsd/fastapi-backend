from fastapi import APIRouter

router = APIRouter(prefix="/todos", tags=["Todo"])


@router.get("/test")
async def test_todo():
    return {"message": "Todo API is working"}