from fastapi import APIRouter, Request
from starlette.responses import RedirectResponse, JSONResponse

from src.api.v1.schemas.user import UserBase, KeyCloakUserSignUp
from src.api.v1.services.keycloak_config import KeycloakService

router = APIRouter(prefix="/keycloak")

keycloak_service = KeycloakService()


@router.post("/login")
async def login(login_req: UserBase):
    response = keycloak_service.login(
        username=str(login_req.email),
        password=login_req.password,
    )
    return response


@router.post("/sign-up")
async def sign_up(data: KeyCloakUserSignUp):
    response = keycloak_service.sign_up(
        first_name=data.first_name,
        last_name=data.last_name,
        email=str(data.email),
        password=data.password,
        phone_number=data.phone_number
    )
    return response


@router.post("/add-group")
async def add_group(group_name: str):
    response = keycloak_service.create_group(
        group_name
    )
    return response


@router.get("/get-groups")
async def get_groups():
    response = keycloak_service.get_groups()
    return response


@router.delete("/delete-group")
async def delete_group(group_id: str):
    response = keycloak_service.delete_group(group_id)
    return response


@router.get("/google-auth")
async def google_auth_login():
    response = keycloak_service.social_login_url()
    return RedirectResponse(url=response)


@router.get("/google-auth-callback")
async def google_auth_login(request: Request):
    code = request.query_params.get("code")
    if not code:
        return JSONResponse({"error": "Authorization code not found"}, status_code=400)

    response = keycloak_service.handle_social_callback(code)
    return response


@router.post("/assign-user-group")
async def assign_user_group(user_id: str, group_id: str):
    response = keycloak_service.add_user_to_group(user_id, group_id)
    return response
