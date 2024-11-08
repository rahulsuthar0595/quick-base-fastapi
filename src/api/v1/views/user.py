from typing import List

from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session

from database.db_connection import get_db
from src.api.v1.models.user_models.user import User
from src.api.v1.schemas.user import UserResponse

router = APIRouter(prefix="/user-auth")


@router.get("/user-list", response_model=List[UserResponse])
async def get_user_list(request: Request, db: Session = Depends(get_db), limit: int = 10):
    return db.query(User).limit(limit).all()
