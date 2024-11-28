import socketio
from fastapi import FastAPI


class SocketIOManager:

    def __init__(
        self, app: FastAPI, mount_location: str = "/socket.io", async_mode: str = "asgi",
        cors_allowed_origins: list['str'] | str = "*", **kwargs
    ):
        self.sio = socketio.AsyncServer(
            async_mode=async_mode,
            cors_allowed_origins=cors_allowed_origins,
            **kwargs
        )
        self.sio_app = socketio.ASGIApp(self.sio)
        app.mount(mount_location, self.sio_app)

        self.sio.on("connect", self.on_connect)
        self.sio.on("disconnect", self.on_disconnect)
        self.sio.on("room_chat", self.room_chat)

    @staticmethod
    def on_connect(sid, environ):
        print(f"on_connect => {sid} - {environ}")

    @staticmethod
    async def on_disconnect(sid, data):
        print(f"on_disconnect => {sid} - {data}")

    async def room_chat(self, sid, data):
        print(f"room_chat => {sid} - {data}")
        await self.sio.emit("return_chat", {"message": f"Server send: hello everyone"}, to=sid)
        # await self.sio.emit("room_chat", "hello everyone")