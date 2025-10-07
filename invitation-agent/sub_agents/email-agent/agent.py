from google.adk.agents.llm_agent import Agent
from .tools import send_mail

root_agent = Agent(
    model='gemini-2.5-flash',
    name='root_agent',
    description='An Email Agent to compose and send emails',
    instruction="""
    Send emails based on user instructions. Use the send_mail function to send emails.
    Compose clear, professional emails based on the user's request.
    """,
    tools=[send_mail],
)
