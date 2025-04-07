from app.components.auth.jwt_mgmt.jwt_mgmt_service import create_jwt

def generate_jwt_response(user_id: str, returned_user_id: str = None) -> dict:
    jwt = create_jwt(user_id)
    return {
        "jwt": jwt["token"],
        "expires_in": jwt["expires_in"],
        "user_id": returned_user_id or user_id
    }