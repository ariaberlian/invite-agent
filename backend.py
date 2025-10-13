import os
import logging
import uvicorn
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Depends, status
from google.adk.runners import Runner
from google.adk.sessions import DatabaseSessionService
from invitation_agent.agent import invitation_agent

from shared.model import EmailModel, InvitationInfo, ChatRequest, ChatResponse, UserContext
from utils.logger import setup_logger
from utils.utils import call_agent_async
from auth.models import UserCreate, UserLogin, Token, User
from auth.database import UserDatabase
from auth.security import create_access_token
from auth.dependencies import get_current_user
from datetime import timedelta

logger = setup_logger(__name__, logging.INFO)

load_dotenv()

DB_URL = os.getenv("DB_URL", "")

session_service = DatabaseSessionService(db_url=DB_URL)
user_db = UserDatabase(db_url=DB_URL)

APP_NAME = "Invitation Assistant"

def create_initial_state(user_context: UserContext) -> dict:
    """Create initial state with user context"""
    invitation_info_init = InvitationInfo()
    email_init = EmailModel()

    return {
        "user_context": user_context.model_dump(),
        "invitation_info": invitation_info_init.model_dump(),
        "email": email_init.model_dump(),
    }

# Store runner globally
runner = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize runner and user database
    global runner
    logger.info("Starting invite-agent application")

    # Initialize user database
    await user_db.initialize()
    logger.info("User database initialized")

    runner = Runner(
        agent=invitation_agent,
        app_name=APP_NAME,
        session_service=session_service,
    )

    yield

    # Shutdown
    logger.info("Shutting down invite-agent application")
    await user_db.close()

app = FastAPI(title="Invitation Assistant API", lifespan=lifespan)

@app.post("/auth/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate):
    """
    Register a new user
    """
    try:
        # Check if user already exists
        existing_user = await user_db.get_user_by_username(user.username)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )

        # Create new user
        new_user = await user_db.create_user(user)
        logger.info(f"New user registered: {new_user.username}")
        return new_user

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error registering user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error registering user: {str(e)}"
        )

@app.post("/auth/login", response_model=Token)
async def login(user_login: UserLogin):
    """
    Login and receive access token
    """
    try:
        # Authenticate user
        user = await user_db.authenticate_user(user_login.username, user_login.password)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Create access token
        access_token = create_access_token(
            data={"sub": user.username},
            expires_delta=timedelta(minutes=30)
        )

        logger.info(f"User logged in: {user.username}")
        return Token(access_token=access_token, token_type="bearer")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during login: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error during login: {str(e)}"
        )

@app.get("/auth/me", response_model=User)
async def get_current_user_info(current_user: str = Depends(get_current_user)):
    """
    Get current authenticated user information
    """
    try:
        user_data = await user_db.get_user_by_username(current_user)
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        return User(
            id=user_data['id'],
            username=user_data['username'],
            full_name=user_data['full_name'],
            email=user_data['email']
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching user info: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching user info: {str(e)}"
        )

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, current_user: str = Depends(get_current_user)):
    """
    Chat endpoint to interact with the invitation agent (protected)
    Requires authentication token
    """
    if not runner:
        raise HTTPException(status_code=503, detail="Service not initialized")

    try:
        # Use authenticated username as user_id
        user_id = current_user

        # Get user information from database
        user_data = await user_db.get_user_by_username(user_id)
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )

        # Determine session: use provided session_id or create new
        session_id = request.session_id

        if session_id:
            # Verify session exists
            try:
                await session_service.get_session(
                    app_name=APP_NAME,
                    user_id=user_id,
                    session_id=session_id
                )
                logger.info(f"Using session: {session_id} for user: {user_id}")
            except:
                # Invalid session, create new
                logger.warning(f"Session {session_id} not found, creating new")
                session_id = None

        if not session_id:
            # Create user context with authenticated user information
            user_context = UserContext(
                username=user_data['username'],
                full_name=user_data['full_name'],
                user_id=user_data['id']
            )

            # Create new session with user context in state
            initial_state = create_initial_state(user_context)
            new_session = await session_service.create_session(
                app_name=APP_NAME,
                user_id=user_id,
                state=initial_state,
            )
            session_id = new_session.id
            logger.info(f"Created session: {session_id} for user: {user_id}")

        # Call agent
        response = await call_agent_async(
            runner=runner,
            user_id=user_id,
            session_id=session_id,
            query=request.message
        )

        return ChatResponse(
            response=response if response else "No response from agent",
            session_id=session_id
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing chat request: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

@app.get("/health")
async def health():
    """
    Health check endpoint
    """
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run("backend:app", host="0.0.0.0", port=8000)