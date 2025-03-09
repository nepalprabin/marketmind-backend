import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from app.api.endpoints import auth, users
from app.core.auth import oauth
from app.config import settings

app = FastAPI(title=settings.PROJECT_NAME)

# Add SessionMiddleware for OAuth
app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, you should specify the allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])
app.include_router(users.router, prefix=f"{settings.API_V1_STR}/users", tags=["users"])

@app.on_event("startup")
async def startup():
    # Initialize OAuth
    oauth.google.client_id = settings.GOOGLE_CLIENT_ID
    oauth.google.client_secret = settings.GOOGLE_CLIENT_SECRET

@app.get("/")
def read_root():
    return {"message": "Welcome to FastAPI Google Authentication API"}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)