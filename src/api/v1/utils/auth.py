from datetime import datetime, timedelta, timezone

import jwt
from fastapi import HTTPException, status
from fastapi.params import Depends
from jwt import InvalidTokenError
from passlib.context import CryptContext
from pydantic import ValidationError
from sqlalchemy.orm import Session

from config.config import settings
from database.db_connection import get_db
from src.api.v1.models.user_models.user import User
from src.api.v1.schemas.user import UserCreate
from src.api.v1.utils.jwt_bearer import JWTBearer

pwd_context = CryptContext(schemes=["bcrypt"])
jwt_bearer = JWTBearer()


def get_hashed_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(email: str):
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_LIMIT)
    to_encode = {"sub": email, "exp": datetime.now(timezone.utc) + access_token_expires}
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def create_user(db: Session, user_data: UserCreate) -> User:
    user = User(
        full_name=user_data.full_name,
        email=user_data.email,
        password=get_hashed_password(user_data.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_current_active_user(
    token: str = Depends(jwt_bearer), db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        detail="Invalid Credentials.",
        status_code=status.HTTP_401_UNAUTHORIZED,
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        email = payload.get("sub")
        expiration = datetime.fromtimestamp(payload.get("exp"))
        if not email:
            raise credentials_exception

        if expiration <= datetime.now():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=f"Token expired."
            )
    except (InvalidTokenError, ValidationError):
        raise credentials_exception

    user = (
        db.query(User)
        .filter(User.email.ilike(f"%{email}%"), User.is_active == True)
        .first()
    )
    if not user:
        raise credentials_exception
    return user
