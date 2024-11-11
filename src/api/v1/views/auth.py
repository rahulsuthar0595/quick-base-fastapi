from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database.db_connection import get_db
from src.api.v1.constants.messages import (INCORRECT_EMAIL_OR_PASSWORD,
                                           USER_EMAIL_ALREADY_EXISTS,
                                           USER_NOT_FOUND)
from src.api.v1.models.user_models.user import User
from src.api.v1.schemas.user import UserBase, UserCreate, UserResponse
from src.api.v1.utils import auth as auth_utils

router = APIRouter(prefix="/auth")


@router.post("/registration", response_model=UserResponse)
async def user_registration(user_data: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email.ilike(f"%{user_data.email}%")).first():
        raise HTTPException(
            detail=USER_EMAIL_ALREADY_EXISTS, status_code=status.HTTP_400_BAD_REQUEST
        )

    return auth_utils.create_user(db, user_data)


@router.post("/login")
async def user_login(data: UserBase = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email.ilike(f"%{data.email}%")).first()
    if not user:
        raise HTTPException(
            detail=USER_NOT_FOUND, status_code=status.HTTP_404_NOT_FOUND
        )

    if not auth_utils.verify_password(data.password, user.password):
        raise HTTPException(
            detail=INCORRECT_EMAIL_OR_PASSWORD, status_code=status.HTTP_400_BAD_REQUEST
        )

    access_token = auth_utils.create_access_token(user.email)
    user.is_active = True   # Activate when verify account
    db.commit()
    db.refresh(user)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_data": {"full_name": user.full_name, "email": user.email},
    }


