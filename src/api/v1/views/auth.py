from datetime import datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from config.config import settings
from database.db_connection import get_db
from src.api.v1.constants.messages import (INCORRECT_EMAIL_OR_PASSWORD,
                                           USER_EMAIL_ALREADY_EXISTS,
                                           USER_NOT_FOUND, EMAIL_VERIFICATION_SUCCESS, EMAIL_NOT_VERIFIED)
from src.api.v1.models.user_models.user import User
from src.api.v1.schemas.user import UserBase, UserCreate, UserResponse
from src.api.v1.utils import auth as auth_utils
from src.api.v1.utils.auth import (create_access_token, create_url_safe_token,
                                   decode_url_safe_token)
from src.api.v1.utils.jwt_bearer import JWTRefreshTokenValidate
from src.api.v1.utils.user_service import UserService
from src.api.v1.utils.tasks import send_account_activation_mail

router = APIRouter(prefix="/auth")

CommonDB = Annotated[Session, Depends(get_db)]


@router.post("/registration", response_model=UserResponse)
async def user_registration(
        user_data: UserCreate, background_tasks: BackgroundTasks, db: CommonDB
):
    if db.query(User).filter(User.email.ilike(f"%{user_data.email}%")).first():
        raise HTTPException(
            detail=USER_EMAIL_ALREADY_EXISTS, status_code=status.HTTP_400_BAD_REQUEST
        )

    user = UserService().create_user(user_data, db)
    token = create_url_safe_token({"email": user.email})
    verify_email_link = f"{settings.BACKEND_DOMAIN}/api/v1/auth/verify-email/{token}"
    send_account_activation_mail(
        background_tasks,
        email=user.email,
        data={"verify_email_link": verify_email_link, "email": user.email},
    )
    return user


@router.post("/login")
async def user_login(data: UserBase, db: CommonDB):
    user = UserService().get_user_by_email(data.email, db)
    if not user:
        raise HTTPException(
            detail=USER_NOT_FOUND, status_code=status.HTTP_404_NOT_FOUND
        )

    if not user.is_active:
        raise HTTPException(
            detail=EMAIL_NOT_VERIFIED, status_code=status.HTTP_400_BAD_REQUEST
        )

    if not auth_utils.verify_password(data.password, user.password):
        raise HTTPException(
            detail=INCORRECT_EMAIL_OR_PASSWORD, status_code=status.HTTP_400_BAD_REQUEST
        )

    access_token = auth_utils.create_access_token(user.email)
    refresh_token = auth_utils.create_access_token(
        email=user.email,
        refresh=True,
        expiry=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_LIMIT),
    )
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user_data": {"full_name": user.full_name, "email": user.email},
    }


@router.get("/verify-email/{token}", response_class=JSONResponse)
async def user_email_verify(token: str, db: CommonDB):
    token_data = decode_url_safe_token(token)
    user_email = token_data.get("email")
    if user_email:
        user = UserService().get_user_by_email(user_email, db)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=USER_NOT_FOUND
            )

        UserService().update_user(user, {"is_active": True}, db)
        return {"message": EMAIL_VERIFICATION_SUCCESS}

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token."
    )


@router.get("/refresh_token", response_class=JSONResponse)
async def get_new_access_token(token_details: dict = Depends(JWTRefreshTokenValidate())):
    expiry_timestamp = token_details["exp"]

    if datetime.fromtimestamp(expiry_timestamp) > datetime.now():
        new_access_token = create_access_token(email=token_details["email"])
        return JSONResponse(content={"access_token": new_access_token})

    raise HTTPException(
        detail="Invalid Token.", status_code=status.HTTP_401_UNAUTHORIZED
    )
