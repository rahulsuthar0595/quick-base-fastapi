from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from database.db_connection import get_db
from src.api.v1.models.user_models.user import User
from src.api.v1.utils.jwt_bearer import JWTAccessTokenValidate
from src.api.v1.utils.user_service import UserService


def get_current_user(
    token_data: dict = Depends(JWTAccessTokenValidate()), db: Session = Depends(get_db)
):
    user_email = token_data.get("email")
    user = UserService().get_user_by_email(user_email, db)
    return user


class ActiveUserCheck:
    def __init__(self):
        pass

    def __call__(self, current_user: User = Depends(get_current_user)):
        if not current_user.is_active:
            raise HTTPException(
                detail="Account is not activated.",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        return True
