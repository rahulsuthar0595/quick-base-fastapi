from unittest import mock

from fastapi import status

from src.api.v1.constants.messages import (EMAIL_NOT_VERIFIED,
                                           INCORRECT_EMAIL_OR_PASSWORD,
                                           USER_EMAIL_ALREADY_EXISTS,
                                           USER_NOT_FOUND)
from src.api.v1.models.user_models.user import User
from src.api.v1.schemas.user import UserCreate, UserResponse
from src.api.v1.utils.user_service import UserService


class TestRegistrationAPI:

    def setup_method(self):
        self.url = "/api/v1/auth/registration"

    def test_api_without_payload(self, test_client):
        response = test_client.post(self.url, json={})
        assert response.json() == {
            "detail": [
                {
                    "type": "missing",
                    "loc": ["body", "email"],
                    "msg": "Field required",
                    "input": {},
                },
                {
                    "type": "missing",
                    "loc": ["body", "password"],
                    "msg": "Field required",
                    "input": {},
                },
                {
                    "type": "missing",
                    "loc": ["body", "full_name"],
                    "msg": "Field required",
                    "input": {},
                },
            ]
        }

    def test_api_with_invalid_email_address(self, test_client):
        response = test_client.post(
            self.url,
            json={
                "email": "invalid-email",  # without @ and .
                "full_name": "Adam",
                "password": "Adam@123",
            },
        )
        assert response.json() == {
            "detail": [
                {
                    "type": "value_error",
                    "loc": ["body", "email"],
                    "msg": "value is not a valid email address: An email address must have an @-sign.",
                    "input": "invalid-email",
                    "ctx": {"reason": "An email address must have an @-sign."},
                }
            ]
        }

    def test_api_with_weak_password(self, test_client):
        response = test_client.post(
            self.url,
            json={"email": "adam@gmail.com", "full_name": "Adam", "password": "adam"},
        )
        assert response.json() == {
            "detail": [
                {
                    "type": "value_error",
                    "loc": ["body", "password"],
                    "msg": "Value error, Password must be at least 8 characters long, contain at least one uppercase letter, one lowercase letter, one digit, and one special character.",
                    "input": "adam",
                    "ctx": {"error": {}},
                }
            ]
        }

    @mock.patch("src.utils.tasks.FastMail.send_message")
    def test_api_with_successfully_registration(
        self, mock_fast_mail, test_client, db_session
    ):
        response = test_client.post(
            self.url,
            json={
                "email": "adam@gmail.com",
                "full_name": "Adam",
                "password": "Adam@123",
            },
        )
        mock_fast_mail.assert_called_once()
        instance = (
            db_session.query(User).filter(User.email.ilike(f"%adam@gmail.com%")).one()
        )
        assert response.status_code == status.HTTP_200_OK
        assert instance is not None
        assert (
            UserResponse.model_validate(instance).model_dump(mode="json")
            == response.json()
        )

    @mock.patch("src.utils.tasks.FastMail.send_message")
    def test_api_with_user_email_already_exists(
        self, mock_fast_mail, test_client, db_session
    ):
        payload = {
            "email": "adam@gmail.com",
            "password": "Adam@123",
            "full_name": "Adam",
        }
        test_client.post(self.url, json=payload)
        mock_fast_mail.assert_called_once()

        response = test_client.post(self.url, json=payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {"detail": USER_EMAIL_ALREADY_EXISTS}


class TestLoginAPI:

    def setup_method(self):
        self.url = "/api/v1/auth/login"

    @staticmethod
    def set_active_user(user, db_session):
        user.is_active = True
        db_session.commit()

    @staticmethod
    def create_user(db_session, is_active=False):
        user = UserService().create_user(
            UserCreate(
                full_name="Admin", email="admin@gmail.com", password="Admin@123"
            ),
            db_session,
        )
        # If this flag set to True, then update user is active status to True.
        if is_active:
            user.is_active = True
            db_session.commit()
        return user

    def test_api_without_payload(self, test_client, db_session):
        response = test_client.post(self.url, json={})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert response.json() == {
            "detail": [
                {
                    "type": "missing",
                    "loc": ["body", "email"],
                    "msg": "Field required",
                    "input": {},
                },
                {
                    "type": "missing",
                    "loc": ["body", "password"],
                    "msg": "Field required",
                    "input": {},
                },
            ]
        }

    def test_api_with_non_exists_user_credentials(self, test_client):
        response = test_client.post(
            self.url,
            json={"email": "non.exist.user@gmail.com", "password": "fake-password"},
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {"detail": USER_NOT_FOUND}

    def test_api_with_inactive_user_account(self, test_client, db_session, create_user):
        response = test_client.post(
            self.url, json={"email": "admin@gmail.com", "password": "Admin@123"}
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {"detail": EMAIL_NOT_VERIFIED}

    def test_api_with_invalid_password(self, test_client, db_session, create_user):
        self.set_active_user(create_user, db_session)

        response = test_client.post(
            self.url, json={"email": "admin@gmail.com", "password": "Admin"}
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {"detail": INCORRECT_EMAIL_OR_PASSWORD}

    def test_api_with_correct_credentials(self, test_client, db_session, create_user):
        self.set_active_user(create_user, db_session)

        response = test_client.post(
            self.url, json={"email": "admin@gmail.com", "password": "Admin@123"}
        )
        assert response.status_code == status.HTTP_200_OK
        # check if all the keys are present in response.
        assert all(
            [
                key in ["access_token", "refresh_token", "token_type", "user_data"]
                for key in response.json().keys()
            ]
        )