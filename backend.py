import logging
import uvicorn
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from invitation_agent.agent import invitation_agent

from shared.model import EmailModel, InvitationInfo, ChatRequest, ChatResponse
from utils.logger import setup_logger
from utils.utils import call_agent_async

logger = setup_logger(__name__, logging.INFO)

load_dotenv()

session_service = InMemorySessionService()

APP_NAME = "Invitation Assistant"
USER_ID = "budigalaksi123"

invitation_info_init = InvitationInfo()
email_init = EmailModel()

initial_state = {
    "invitation_info": invitation_info_init,
    "email" : email_init,
}

# Store runner globally
runner = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize runner only
    global runner
    logger.info("Starting invite-agent application")

    runner = Runner(
        agent=invitation_agent,
        app_name=APP_NAME,
        session_service=session_service,
    )

    yield

    # Shutdown
    logger.info("Shutting down invite-agent application")

app = FastAPI(title="Invitation Assistant API", lifespan=lifespan)

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat endpoint to interact with the invitation agent
    """
    if not runner:
        raise HTTPException(status_code=503, detail="Service not initialized")

    try:
        # Determine session: use provided session_id or create new
        session_id = request.session_id

        if session_id:
            # Verify session exists
            try:
                await session_service.get_session(
                    app_name=APP_NAME,
                    user_id=request.user_id,
                    session_id=session_id
                )
                logger.info(f"Using session: {session_id}")
            except:
                # Invalid session, create new
                logger.warning(f"Session {session_id} not found, creating new")
                session_id = None

        if not session_id:
            # Create new session
            new_session = await session_service.create_session(
                app_name=APP_NAME,
                user_id=request.user_id,
                state=initial_state,
            )
            session_id = new_session.id
            logger.info(f"Created session: {session_id}")

        # Call agent
        response = await call_agent_async(
            runner=runner,
            user_id=request.user_id,
            session_id=session_id,
            query=request.message
        )

        return ChatResponse(
            response=response if response else "No response from agent",
            session_id=session_id
        )
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
    uvicorn.run("backend:app", host="0.0.0.0", port=8000, reload=True)