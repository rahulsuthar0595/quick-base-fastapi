from fastapi import FastAPI

from config.config import settings
from src.route.router import v1_router

app = FastAPI(
    docs_url=settings.DOCS_ENDPOINT,
    redoc_url=settings.REDOCS_ENDPOINT
)


app.include_router(v1_router)