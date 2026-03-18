from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi import Depends
from jose import JWTError, jwt
from app.db.session import get_db
from sqlalchemy.orm import Session
from app.core.security import decode_access_token
from app.utils.exceptions import AppException
from app.models.user import User

bearer_schema = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_schema),
    db: Session = Depends(get_db),
):


    token = credentials.credentials
    try:
        payload = decode_access_token(token)

        user_id = payload.get("sub")
        if not user_id:
            raise AppException(status_code=401, message="Your provided a invalid token")
    except JWTError:
        raise AppException(status_code=401, message="Your provided a invalid token")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise AppException(status_code=401, message="User not found")

    return user


def require_role(*roles):
    def checker(current_user: User = Depends(get_current_user)):
        if current_user.role.value not in roles:
            raise AppException(
                status_code=403, message="You are not authorized to perform this action"
            )
        return current_user

    return checker
