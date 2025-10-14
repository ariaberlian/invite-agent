import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import List, Optional
from pathlib import Path
from datetime import datetime
from icalendar import Calendar, Event
from google.adk.tools.tool_context import ToolContext

from config import config
from utils.logger import setup_logger
from shared.model import EmailModel

logger = setup_logger(__name__)

# Validate email configuration on import
config.email.validate()

EMAIL_HOST_USER = config.email.EMAIL_HOST_USER
EMAIL_HOST_PASSWORD = config.email.EMAIL_HOST_PASSWORD
SMTP_SERVER = config.email.SMTP_SERVER
SMTP_PORT = config.email.SMTP_PORT

def send_mail(receiver: List[str], subject: str, body: str, attachments: Optional[List[str]] = None) -> str:
    """
    Send an email to one or more recipients.

    Args:
        receiver: List of email addresses to send to
        subject: Email subject line
        body: Email body content
        attachments: Optional list of file paths to attach to the email

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

        # Attach files if provided
        if attachments:
            for file_path in attachments:
                try:
                    path = Path(file_path)
                    if not path.exists():
                        logger.warning(f"Attachment file not found: {file_path}")
                        continue

                    with open(path, 'rb') as file:
                        part = MIMEBase('application', 'octet-stream')
                        part.set_payload(file.read())

                    encoders.encode_base64(part)
                    part.add_header(
                        'Content-Disposition',
                        f'attachment; filename= {path.name}'
                    )
                    msg.attach(part)
                    logger.info(f"Attached file: {path.name}")
                except Exception as attach_error:
                    logger.error(f"Failed to attach file {file_path}: {str(attach_error)}")

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
            server.send_message(msg)

        attachment_info = f" with {len(attachments)} attachment(s)" if attachments else ""
        logger.info(f"Email sent successfully to {', '.join(receiver)}{attachment_info}")
        return f"Email successfully sent to {', '.join(receiver)}{attachment_info}"
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

    tool_context.state["email"] = empty_email.model_dump()

    return {
        "message": f"Successfully reset email"
    }

def create_calendar_invitation(
    summary: str,
    start_time: str,
    end_time: str,
    location: str = "",
    description: str = "",
    attendees: Optional[List[str]] = None,
    organizer_email: Optional[str] = None,
    output_path: str = "invitation.ics"
) -> str:
    """
    Create a calendar invitation file in iCalendar format (.ics).

    Args:
        summary: Event title/summary
        start_time: Event start time in ISO format (e.g., "2025-10-15T14:00:00")
        end_time: Event end time in ISO format (e.g., "2025-10-15T15:00:00")
        location: Event location (optional)
        description: Event description/notes (optional)
        attendees: List of attendee email addresses (optional)
        organizer_email: Organizer email address (defaults to EMAIL_HOST_USER)
        output_path: Path where the .ics file will be saved (default: "invitation.ics")

    Returns:
        Success message with file path or error message
    """
    logger.info(f"--- Tool: create_calendar_invitation called for event '{summary}' ---")

    try:
        # Create calendar
        cal = Calendar()
        cal.add('prodid', '-//Invitation Agent//Calendar Invitation//EN')
        cal.add('version', '2.0')
        cal.add('method', 'REQUEST')

        # Create event
        event = Event()
        event.add('summary', summary)
        event.add('dtstart', datetime.fromisoformat(start_time))
        event.add('dtend', datetime.fromisoformat(end_time))

        if location:
            event.add('location', location)

        if description:
            event.add('description', description)

        # Add organizer
        organizer = organizer_email or EMAIL_HOST_USER
        event.add('organizer', f'mailto:{organizer}')

        # Add attendees
        if attendees:
            for attendee in attendees:
                event.add('attendee', f'mailto:{attendee}', parameters={
                    'CUTYPE': 'INDIVIDUAL',
                    'ROLE': 'REQ-PARTICIPANT',
                    'PARTSTAT': 'NEEDS-ACTION',
                    'RSVP': 'TRUE'
                })

        # Add event to calendar
        cal.add_component(event)

        # Write to file
        output_file = Path(output_path)
        with open(output_file, 'wb') as f:
            f.write(cal.to_ical())

        logger.info(f"Calendar invitation created successfully at {output_file}")
        return f"Calendar invitation created successfully at {output_file.absolute()}"

    except ValueError as ve:
        error_msg = f"Invalid datetime format: {str(ve)}"
        logger.error(error_msg)
        return error_msg
    except Exception as e:
        error_msg = f"Failed to create calendar invitation: {type(e).__name__}: {str(e)}"
        logger.error(error_msg)
        return error_msg

