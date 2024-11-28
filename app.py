from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from config.config import settings
from src.api.v1.events.user_event import *  # noqa : Import the event before app called.
from src.api.v1.services.socket_io import SocketIOManager
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

sio_manager = SocketIOManager(app=app)


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse(
        request=request, name="socket_io.html", context={}
    )
