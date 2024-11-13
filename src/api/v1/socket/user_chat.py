from datetime import datetime

from fastapi import APIRouter, Depends
from fastapi.websockets import WebSocket
from jwt import InvalidTokenError
from pydantic import ValidationError
from sqlalchemy.orm import Session

from database.db_connection import get_db
from logger.logger import logger
from src.api.v1.utils.auth import decode_token
from src.api.v1.utils.dependencies import ActiveUserCheck
from src.api.v1.utils.socket_manager import connection_manager
from src.api.v1.utils.user_service import UserService

websocket_router = APIRouter(tags=["Websocket"], prefix="/ws")

active_user_check = Depends(ActiveUserCheck)


@websocket_router.websocket("/user_chat")
async def user_chat_websocket(websocket: WebSocket, db: Session = Depends(get_db)):
    await connection_manager.connect(websocket, "access_token")

    sub_protocols = websocket.scope.get("subprotocols")
    if not sub_protocols or len(sub_protocols) != 2:
        await connection_manager.disconnect(websocket, code=3000,
                                            reason="Must pass access token in sub-protocol.")  # Unauthorized
        return

    token_data = decode_token(sub_protocols[1])
    if token_data is None:
        await connection_manager.disconnect(websocket, code=3000, reason="Invalid Access token.")
        return

    try:
        email = token_data.get("email")
        expiration = datetime.fromtimestamp(token_data.get("exp"))
        if not email or expiration <= datetime.now():
            await connection_manager.disconnect(websocket, code=3000, reason="Invalid Access token.")
            return

    except (InvalidTokenError, ValidationError):
        await connection_manager.disconnect(websocket, code=3000, reason="Invalid Access token.")
        return

    if user := UserService().get_user_by_email(email, db):
        logger.info(f"User '{user.email}' is connected to chat.")
        while True:
            data = await websocket.receive_text()
            # sending message to broadcast connections
            await connection_manager.broadcast_message(message=f"Message From {user.full_name} : {data}")

    else:
        await connection_manager.disconnect(websocket, code=3000, reason="Invalid Access token.")
        return
