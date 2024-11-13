from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from config.config import settings
from src.api.v1.socket.user_chat import websocket_router
from src.route.router import v1_router

app = FastAPI(
    docs_url=settings.DOCS_ENDPOINT,
    redoc_url=settings.REDOCS_ENDPOINT,
)

app.include_router(v1_router)
app.include_router(websocket_router)

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")
