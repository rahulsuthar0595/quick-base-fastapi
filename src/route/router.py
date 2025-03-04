from fastapi import APIRouter

from src.api.v1.views import user, auth

v1_router = APIRouter(prefix="/api/v1")

v1_router.include_router(auth.router, tags=["Auth"])
v1_router.include_router(user.router, tags=["User"])
