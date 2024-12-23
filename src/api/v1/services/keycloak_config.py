import json
from typing import List

from fastapi import HTTPException
from keycloak import KeycloakOpenID, KeycloakAdmin, KeycloakAuthenticationError, KeycloakOpenIDConnection, \
    KeycloakPostError
from keycloak.exceptions import KeycloakGetError

from config.config import settings

"""
STEPS TO BE FOLLOW FOR GOOGLE SOCIAL AUTH:

# Assumed, you have already configured Keycloak and logged in with a realm.

1. Click on Identity providers -> Google.
2. There will be a redirect_url as fixed, you need to copy and create token in google cloud console 
   with this as redirect url. Set alias, display name and client ID and client Secret from google 
   cloud console. Additionally, set prompt as `consent` for each time permission on social login.
3. Click on Authorization, make a duplicate of browser. Now add step, with `Identify Provider Redirector Google,
   make Default Identity Provider value as google and save. Then make that as Required.
4. Now click on the client you have created, add a new Valid redirect URIs with the endpoint of callback for google.
5. Click on Advanced, at the last, change the Browser flow to the duplicate Authorization, you have created.
6. In the Service account roles, you may have to click on Assign role and add view-clients and manage-users in case you get errors in API.
"""


class KeycloakService:
    def __init__(self):
        keycloak_connection = KeycloakOpenIDConnection(
            server_url=settings.KEYCLOAK_SERVER_URL,
            realm_name=settings.KEYCLOAK_REALM_NAME,
            client_id=settings.KEYCLOAK_CLIENT_ID,
            user_realm_name=settings.KEYCLOAK_REALM_NAME,
            client_secret_key=settings.KEYCLOAK_CLIENT_SECRET,
            verify=True
        )
        # For OpenID (Authentication and Authorization)
        self.keycloak_openid = KeycloakOpenID(
            server_url=settings.KEYCLOAK_SERVER_URL,
            client_id=settings.KEYCLOAK_CLIENT_ID,
            realm_name=settings.KEYCLOAK_REALM_NAME,
            client_secret_key=settings.KEYCLOAK_CLIENT_SECRET,
        )
        # For Admin Operations (Creating Users, Groups, etc.)
        self.keycloak_admin = KeycloakAdmin(
            connection=keycloak_connection
        )

    def sign_up(self, first_name: str, last_name: str, email: str, password: str, phone_number: int):
        try:
            user_data = {
                "username": email,
                "email": email,
                "enabled": True,
                "credentials": [{"value": password, "type": "password"}],
                "firstName": first_name,
                "lastName": last_name,
                "emailVerified": False,
                "attributes": {
                    "phonenumber": phone_number
                },
            }
            user = self.keycloak_admin.create_user(user_data)
            return {"message": "User created successfully", "user_id": user}
        except KeycloakPostError as e:
            error = json.loads(e.response_body.decode())
            raise HTTPException(status_code=400, detail=error)

    def login(self, username: str, password: str):
        """Normal Login via Username/Password (OAuth2 Password Grant)"""
        try:
            token = self.keycloak_openid.token(
                username=username,
                password=password,
                client_secret_key=settings.KEYCLOAK_CLIENT_SECRET,
            )
            return token
        except KeycloakAuthenticationError:
            raise HTTPException(status_code=400, detail="Invalid credentials")

    def social_login_url(self):
        """Social Login - Generates URL for Google OAuth (or any other provider)"""
        auth_url = self.keycloak_openid.auth_url(
            redirect_uri=settings.KEYCLOAK_REDIRECT_URI,
            scope="openid email profile"
        )
        auth_url += "&kc_idp_hint=google"  # Redirect to Google directly
        return auth_url

    def handle_social_callback(self, code: str):
        """Handle Social Login Callback (Exchanges the Authorization Code for Tokens)"""
        try:
            token = self.keycloak_openid.token(
                grant_type="authorization_code",
                code=code,
                redirect_uri=settings.KEYCLOAK_REDIRECT_URI
            )
            access_token = token["access_token"]
            id_token = token["id_token"]
            try:
                user_info = self.keycloak_openid.userinfo(access_token)
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Failed to fetch user info: {str(e)}")

            user_info.update({"access_token": access_token, "id_token": id_token})
            return user_info
        except KeycloakGetError as e:
            raise HTTPException(status_code=400, detail=f"Failed to fetch token: {str(e)}")
        except KeycloakPostError as e:
            raise HTTPException(status_code=400, detail="Code not valid")

    def add_user_to_group(self, user_id: str, group_id: str):
        """Admin function to add a user to a group"""
        try:
            self.keycloak_admin.group_user_add(user_id=user_id, group_id=group_id)
            return {"message": f"User {user_id} added to group"}
        except KeycloakGetError:
            raise HTTPException(status_code=400, detail="Failed to add user to group")

    def remove_user_from_group(self, user_id: str, group_id: str):
        """Admin function to remove a user from a group"""
        try:
            self.keycloak_admin.group_user_remove(user_id=user_id, group_id=group_id)
            return {"message": f"User {user_id} removed from group"}
        except KeycloakGetError:
            raise HTTPException(status_code=400, detail="Failed to remove user from group")

    def create_group(self, group_name: str):
        """Admin function to create a new group"""
        try:
            group = self.keycloak_admin.create_group({"name": group_name}, skip_exists=True)
            return {"message": f"Group {group_name} created successfully", "group_id": group}
        except Exception:
            raise HTTPException(status_code=400, detail="Failed to create group")

    def get_groups(self) -> List[dict]:
        """Admin function to get all groups"""
        try:
            groups = self.keycloak_admin.get_groups()
            return groups
        except KeycloakGetError:
            raise HTTPException(status_code=400, detail="Failed to fetch groups")

    def delete_group(self, group_id: str):
        """Admin function to delete a group"""
        try:
            self.keycloak_admin.delete_group(group_id)
            return {"message": f"Group {group_id} deleted successfully"}
        except KeycloakGetError:
            raise HTTPException(status_code=400, detail="Failed to delete group")
