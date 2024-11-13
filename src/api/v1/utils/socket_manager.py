from fastapi.websockets import WebSocket


class ConnectionManager:

    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket, protocol: str | None):
        await websocket.accept(protocol)
        self.active_connections.append(websocket)

    async def disconnect(self, websocket: WebSocket, code: int = 1000, reason: str = ""):
        await websocket.close(code, reason)
        self.active_connections.remove(websocket)

    @staticmethod
    async def send_message(message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast_message(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


connection_manager = ConnectionManager()