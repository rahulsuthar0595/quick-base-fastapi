import jwt
import requests
import socketio

from fastapi import FastAPI, Request
from fastapi.security import OAuth2PasswordBearer
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

from config.config import settings
from src.api.v1.events.user_event import *  # noqa : Import the event before app called.
from src.api.v1.services.socket_io import SocketIOManager
from src.api.v1.socket.user_chat import websocket_router
from src.api.v1.utils.mongodb import perform_insert_operations, perform_query_operations, perform_modify_operation, \
    perform_GridFS
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


# Uncomment this function, when we have to insert the data

@app.get("/perform-mongodb-operation")
async def perform_mongodb_operation():
    perform_insert_operations()
    perform_query_operations()
    perform_modify_operation()
    perform_GridFS()
    logger.info(f"Successfully run all operations for mongodb.")


@sio_manager.sio.on("connect")
async def connect(sid, environ):
    print(f"on_connect => {sid} - {environ}")


@sio_manager.sio.on("disconnect")
async def on_disconnect(sid):
    print(f"on_disconnect => {sid}")


GOOGLE_CLIENT_ID = "295992062313-d7ej23pt9cv2nlgb9ntfmm1a7nfip4vm.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET = "your-google-client-secret"
GOOGLE_REDIRECT_URI = "https://bedb-180-211-108-109.ngrok-free.app/auth/google"
import os
from fastapi_sso.sso.google import GoogleSSO

CLIENT_ID = "295992062313-d7ej23pt9cv2nlgb9ntfmm1a7nfip4vm.apps.googleusercontent.com"
CLIENT_SECRET = "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"
GOOGLE_REDIRECT_URI = "https://bedb-180-211-108-109.ngrok-free.app/auth/callback"

@app.get("/login/google")
async def login_google():
    return {
        "url": f"https://accounts.google.com/o/oauth2/auth?response_type=code&client_id={GOOGLE_CLIENT_ID}&redirect_uri={GOOGLE_REDIRECT_URI}&scope=openid%20profile%20email&access_type=offline"
    }

@app.get("/auth/google")
async def auth_google(code: str):
    token_url = "https://accounts.google.com/o/oauth2/token"
    data = {
        "code": code,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "grant_type": "authorization_code",
    }
    response = requests.post(token_url, data=data)
    access_token = response.json().get("access_token")
    user_info = requests.get("https://www.googleapis.com/oauth2/v1/userinfo", headers={"Authorization": f"Bearer {access_token}"})
    return user_info.json()

@app.get("/token")
async def get_token(token: str = Depends(oauth2_scheme)):
    return jwt.decode(token, GOOGLE_CLIENT_SECRET, algorithms=["HS256"])


sso = GoogleSSO(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri="https://bedb-180-211-108-109.ngrok-free.app/auth/callback",
    allow_insecure_http=True,
)


@app.get("/auth/login")
async def auth_init():
    """Initialize auth and redirect"""
    async with sso:
        response = await sso.get_login_redirect(params={"prompt": "consent", "access_type": "offline"})
        print("response", response)
        return response.__dict__


@app.get("/auth/callback")
async def auth_callback(request: Request):
    """Verify login"""
    async with sso:
        user = await sso.verify_and_process(request)
    return user