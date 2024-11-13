import pytest
from fastapi.websockets import WebSocketDisconnect


class TestUserChatWebSocket:

    def setup_method(self):
        self.login_url = "/api/v1/auth/login"
        self.user_chat_url = "/ws/user_chat"

    @staticmethod
    def set_active_user(user, db_session):
        user.is_active = True
        db_session.commit()

    def test_connection_close_without_sub_protocol(self, test_client):
        with pytest.raises(WebSocketDisconnect):
            with test_client.websocket_connect(self.user_chat_url) as websocket:
                websocket.receive_text()

    def test_connection_close_with_invalid_token(self, test_client):
        try:
            with test_client.websocket_connect(
                self.user_chat_url, subprotocols=["access_token", "Invalid-Token"]
            ) as websocket:
                websocket.receive_text()
        except WebSocketDisconnect as err:
            assert err.code == 3000
            assert err.reason == "Invalid Access token."

    def test_connection_success_with_valid_token(
        self, test_client, db_session, create_user
    ):
        self.set_active_user(create_user, db_session)
        response = test_client.post(
            self.login_url, json={"email": "admin@gmail.com", "password": "Admin@123"}
        )
        access_token = response.json().get("access_token")

        with test_client.websocket_connect(
            self.user_chat_url, subprotocols=["access_token", access_token]
        ) as websocket:
            websocket.send_text("Hello")
            received_text = websocket.receive_text()
            assert "Hello" in received_text
