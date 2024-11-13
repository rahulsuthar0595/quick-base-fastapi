from datetime import datetime

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import InvalidTokenError
from pydantic import ValidationError
from sqlalchemy.orm import Session

from database.db_connection import get_db
from src.api.v1.utils.auth import decode_token
from src.api.v1.utils.user_service import UserService


class JWTBearer(HTTPBearer):
    credentials_exception = HTTPException(
        detail="Invalid Credentials.",
        status_code=status.HTTP_401_UNAUTHORIZED,
        headers={"WWW-Authenticate": "Bearer"},
    )

    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request, db: Session = Depends(get_db)):
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)
        if credentials:
            if credentials.scheme != "Bearer":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Invalid Token Schema.",
                )

            token = credentials.credentials
            token_data = decode_token(token)
            if token_data is None:
                raise self.credentials_exception

            self.validate_token_data(token_data, db)
            return token_data
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid authorization code."
        )

    def validate_token_data(self, token_data: dict, db: Session = Depends(get_db)):
        try:
            email = token_data.get("email")
            expiration = datetime.fromtimestamp(token_data.get("exp"))
            if not email:
                raise self.credentials_exception

            if expiration <= datetime.now():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail=f"Token expired."
                )
        except (InvalidTokenError, ValidationError):
            raise self.credentials_exception

        if not UserService().get_user_by_email(email, db):
            raise self.credentials_exception


class JWTAccessTokenValidate(JWTBearer):
    def validate_token_data(self, token_data, db: Session = Depends(get_db)):
        if token_data and token_data.get("refresh"):
            raise HTTPException(
                detail="Access token required in header",
                status_code=status.HTTP_401_UNAUTHORIZED,
                headers={"WWW-Authenticate": "Bearer"},
            )
        return super().validate_token_data(token_data, db)


class JWTRefreshTokenValidate(JWTBearer):
    def validate_token_data(self, token_data, db: Session = Depends(get_db)):
        if token_data and not token_data.get("refresh"):
            raise HTTPException(
                detail="Refresh token required in header",
                status_code=status.HTTP_401_UNAUTHORIZED,
                headers={"WWW-Authenticate": "Bearer"},
            )
