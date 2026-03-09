from fastapi import APIRouter

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.get("/test")
def auth_test():
    return {"message": "auth route working"}