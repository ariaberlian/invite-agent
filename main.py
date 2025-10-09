import asyncio
import logging
from dotenv import load_dotenv
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from invitation_agent.agent import invitation_agent

from shared.model import EmailModel, InvitationInfo 
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

async def main_async():
    logger.info("Starting invite-agent application")

    new_session =await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        state=initial_state,
    )
    SESSION_ID = new_session.id
    logger.info(f"Created new session: {SESSION_ID}")

    runner = Runner(
        agent=invitation_agent,
        app_name=APP_NAME,
        session_service=session_service,
    )

    print("\nWelcome to Invitation Assistant Chat!")
    print("Type 'exit' or 'quit' to end the conversation.\n")

    while True:
        user_input = input("You:  ")

        if user_input.lower() in ["exit", "quit"]:
            print("Ending conversation. Goodbye!")
            break

        await call_agent_async(runner=runner,
                               user_id=USER_ID,
                               session_id=SESSION_ID,
                               query=user_input)

def main():
    asyncio.run(main_async())

if __name__ == "__main__":
    main()
