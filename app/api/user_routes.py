from fastapi import APIRouter

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/test")
def user_test():
    return {"message": "user route working"}