from google.adk.agents.llm_agent import Agent
from .tools import get_curent_datetime
from .sub_agents.email_agent import email_agent
from ..utils.logger import setup_logger

logger = setup_logger(__name__)

invitation_agent = Agent(
    model='gemini-2.5-flash',
    name='invitation_agent',
    description='A helpfull agent to create, send, and manage invitation',
    instruction="""
    You are an Invitation Agent.
    Your task is to create invitation to users agenda.
    
    *You need to know*:
    - Agenda's Name,
    - Location,
    - Date and Time,
    - Notes,
    - Recipients,
    - Tone.

    # GUIDELINES:
    - If user dont give explicit information you need to know, give your best to guess.
    - Confirm your guess to user.
    - You can use get_current_datetime tools to know current time.
    - If you can't get information you need, you may ask user.
    - If all information already confirmed by user, you may delegate to email_agent along with the data.
    
""",
    tools=[get_curent_datetime],
    sub_agents=[email_agent],
)