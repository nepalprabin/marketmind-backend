from typing import Dict, Optional
from authlib.integrations.starlette_client import OAuth
from app.config import settings
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.db.models import User

# Configure OAuth
oauth = OAuth()
oauth.register(
    name="google",
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()

def get_user_by_google_id(db: Session, google_id: str) -> Optional[User]:
    return db.query(User).filter(User.google_id == google_id).first()

def create_user_from_google(db: Session, user_info: Dict) -> User:
    """Create a new user or update existing user with Google information"""
    
    # Check if user exists by email
    user = get_user_by_email(db, user_info.get("email"))
    
    if user:
        # Update existing user with Google info if not already set
        if not user.google_id:
            user.google_id = user_info.get("sub")
            user.picture = user_info.get("picture")
            user.first_name = user_info.get("given_name")
            user.last_name = user_info.get("family_name")
            db.commit()
            db.refresh(user)
        return user
    
    # Create new user
    new_user = User(
        email=user_info.get("email"),
        google_id=user_info.get("sub"),
        first_name=user_info.get("given_name"),
        last_name=user_info.get("family_name"),
        picture=user_info.get("picture")
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user