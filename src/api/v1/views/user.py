import time
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database.db_connection import get_db
from logger.logger import logger
from src.api.v1.events.user_event import generate_bulk_users, elastic_search_client
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


@router.post("/bulk-generate-users")
async def bulk_generate_users(db: Session = Depends(get_db), count: int = 100):
    await generate_bulk_users(count, db)
    return True


@router.get("/fetch-from-db", response_model=list[UserResponse])
async def get_users_from_db(db: Session = Depends(get_db), limit: int = 100):
    start_time = time.perf_counter()
    users = db.query(User).limit(limit).all()
    logger.info(f"{limit} records fetched from database in time - {time.perf_counter() - start_time}")
    return users


@router.get("/fetch-from-elastic-search", response_model=list[UserResponse])
async def get_users_from_elastic_search(db: Session = Depends(get_db), limit: int = 100):
    start_time = time.perf_counter()
    users = await elastic_search_client.fetch_all_users(limit)
    logger.info(f"{limit} records fetched from elastic search in time - {time.perf_counter() - start_time}")
    return users
