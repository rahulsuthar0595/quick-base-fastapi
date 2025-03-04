from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database.db_connection import get_db
from src.api.v1.models.user_models.user import User
from src.api.v1.schemas.user import UserResponse
from src.api.v1.utils.dependencies import ActiveUserCheck, get_current_user

router = APIRouter(prefix="/user")

active_user_check = Depends(ActiveUserCheck)


@router.get("/user-list", response_model=List[UserResponse])
async def get_user_list(db: Session = Depends(get_db), limit: int = 10):
    return db.query(User).limit(limit).all()


@router.get("/me", response_model=UserResponse, dependencies=[active_user_check])
async def get_user_profile(current_user: User = Depends(get_current_user)):
    return current_user
