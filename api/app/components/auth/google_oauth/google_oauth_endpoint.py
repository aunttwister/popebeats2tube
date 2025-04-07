from fastapi import APIRouter, Depends, Request
from requests import Session
from app.db.db import get_db_session
from app.components.auth.google_oauth.google_oauth_schema  import AuthRequestDto
from app.components.auth.google_oauth.google_oauth_service import handle_google_auth, handle_google_callback, handle_token_refresh
 
google_oauth_router = APIRouter()

@google_oauth_router.post("/login")
async def google_auth(auth_request: AuthRequestDto, db: Session = Depends(get_db_session)):
    return await handle_google_auth(auth_request, db)

@google_oauth_router.post("/login-callback")
async def google_callback(request: Request, db: Session = Depends(get_db_session)):
    request_body = await request.json()    
    return await handle_google_callback(request_body, db)

@google_oauth_router.post("/token-refresh")
async def refresh_auth_token(request: Request, db: Session = Depends(get_db_session)):
    request_body = await request.json()
    user_id = str(request_body.get("user_id"))
    return await handle_token_refresh(user_id, db)