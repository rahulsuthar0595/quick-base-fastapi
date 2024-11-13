from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from database.db_connection import get_db
from src.api.v1.models.user_models.user import User
from src.api.v1.schemas.user import UserCreate
from src.api.v1.utils.auth import get_hashed_password

CommonDB = Annotated[Session, Depends(get_db)]


class UserService:

    @staticmethod
    def get_user_by_email(email: str, db: CommonDB):
        user = db.query(User).filter(User.email.ilike(f"%{email}%")).first()
        return user

    def is_user_exists(self, email: str, db: CommonDB):
        user = self.get_user_by_email(email, db)
        return True if user is not None else False

    @staticmethod
    def create_user(user_data: UserCreate, db: CommonDB):
        user_data_dict = user_data.model_dump()
        user_data_dict["password"] = get_hashed_password(user_data_dict.get("password"))
        user = User(**user_data_dict)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def update_user(user: User, user_data: dict, db: CommonDB):
        for key, val in user_data.items():
            setattr(user, key, val)

        db.commit()
        db.refresh(user)
        return user
