import uuid
from datetime import datetime, timedelta

import jwt
from itsdangerous import URLSafeTimedSerializer
from passlib.context import CryptContext

from config.config import settings
from logger.logger import logger

pwd_context = CryptContext(schemes=["bcrypt"])

url_safe_timed_serializer = URLSafeTimedSerializer(secret_key=settings.SECRET_KEY)


def get_hashed_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(email: str, expiry: timedelta = None, refresh: bool = False):
    to_encode = {
        "email": email,
        "exp": datetime.now()
        + (
            expiry
            if expiry is not None
            else timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_LIMIT)
        ),
        "jti": str(uuid.uuid4()),
        "refresh": refresh,
    }
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def decode_token(token: str):
    try:
        return jwt.decode(
            jwt=token, key=settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
    except jwt.PyJWTError as e:
        logger.error(f"Exception while decode token for '{token}': {str(e)}")
        return None


def create_url_safe_token(data: dict):
    return url_safe_timed_serializer.dumps(data)


def decode_url_safe_token(token: str):
    try:
        return url_safe_timed_serializer.loads(token, max_age=3600)
    except Exception as e:
        logger.exception(
            f"Exception while decode url safe token for '{token}': {str(e)}"
        )
        return None
