import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List
from google.adk.tools.tool_context import ToolContext

from dotenv import load_dotenv
from utils.logger import setup_logger
from shared.model import EmailModel

load_dotenv()

logger = setup_logger(__name__)


EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
if EMAIL_HOST_USER is None:
    raise ValueError("EMAIL_HOST_USER is not set")

EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
if EMAIL_HOST_PASSWORD is None:
    raise ValueError("EMAIL_HOST_PASSWORD is not set")

SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))

def send_mail(receiver: List[str], subject: str, body: str) -> str:
    """
    Send an email to one or more recipients.

    Args:
        receiver: List of email addresses to send to
        subject: Email subject line
        body: Email body content

    Returns:
        Success or error message
    """
    logger.info(f"--- Tool: send_mail called for sending email to {', '.join(receiver)} - Subject: '{subject}'---")
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_HOST_USER
        msg['To'] = ', '.join(receiver)
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
            server.send_message(msg)

        logger.info(f"Email sent successfully to {', '.join(receiver)}")
        return f"Email successfully sent to {', '.join(receiver)}"
    except Exception as e:
        logger.error(f"Failed to send email: {type(e).__name__}: {str(e)}")
        return f"Failed to send email: {str(e)}"

def update_email_state(email: EmailModel, tool_context: ToolContext):
    """Update email state.

    Args:
        email: 
            subject: Subject line of the email
            body: Body of the email
            recipients: List of valid email address of recipients
        tool_context: Context for accessing and updating session state.

    Returns:
        A confirmation message
    """
    logger.info(f"--- Tool: update_email_state called for {email} ---")
    
    tool_context.state["email"] = email

    return {
        "message": f"Updated email state: {email}"
    }

def reset_email_state(tool_context: ToolContext):
    """Reset email in the state.
    
    Args:
        tool_context: Context for accessing and updating session state.

    Returns:
        A confirmation message
    """
    logger.info(f"--- Tool: reset_email_state called ---")

    empty_email = EmailModel()

    tool_context.state["email"] = empty_email

    return {
        "message": f"Successfully reset email"
    }