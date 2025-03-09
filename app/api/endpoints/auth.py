from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from app.deps import get_current_user
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.core.auth import oauth, create_user_from_google
from app.core.security import create_access_token
from app.config import settings
from app.schemas.user import Token, UserResponse

router = APIRouter()

@router.get("/login/google")
async def login_google(request: Request):
    """Redirect to Google OAuth login page"""
    redirect_uri = settings.GOOGLE_REDIRECT_URI
    return await oauth.google.authorize_redirect(request, redirect_uri)

@router.get("/callback")
async def auth_callback(request: Request, db: Session = Depends(get_db)):
    """Handle the OAuth callback from Google"""
    token = await oauth.google.authorize_access_token(request)
    user_info = token.get("userinfo")

    if not user_info:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not fetch user info from Google"
        )
    
    # Get state from the session
    state_from_session = request.session.get("state")

    if state_from_session != token.get("state"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CSRF Token Mismatch"
        )
    
    # Clear state after successful login
    request.session.pop("state", None)
    
    # Create or update user in database
    user = create_user_from_google(db, user_info)
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=user.id, expires_delta=access_token_expires
    )
    
    # Create token response
    token_data = {
        "access_token": access_token,
        "token_type": "bearer"
    }
    return token_data

@router.get("/me", response_model=UserResponse)
async def read_users_me(
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """Get current user information"""
    return current_user