from datetime import datetime
from utils.logger import setup_logger
from google.adk.tools.tool_context import ToolContext
from shared.model import InvitationInfo

logger = setup_logger(__name__)

def get_curent_datetime():
    """Function to get current date time.

    Args:
        None

    Returns:
        current datetime
    """
    logger.info("--- Tool: get_current_datetime called ---")
    current_time = datetime.now()
    logger.debug(f"Current datetime: {current_time}")
    return current_time

def update_invitation_info(invitation_info: InvitationInfo, tool_context: ToolContext):
    """Update invitation info based on information from user.
    
    Args:
        invitation_info: The information to be update, made of:
            user_name: Name of user,
            agenda_name: Name of agenda,
            location: Agenda's location,
            scheduled_at: Agenda's date and time,
            notes: Agenda's note,
            recipients: List of recipients email,
            tone: Tone to use when create email.
        tool_context: Context for accessing and updating session state.

    Returns:
        A confirmation message
    """
    logger.info(f"--- Tool: update_invitation_info called for {invitation_info} ---")
    
    tool_context.state["invitation_info"] = invitation_info

    return {
        "message": f"Updated invitation_info: {invitation_info}"
    }



def reset_invitation_info(tool_context: ToolContext):
    """Reset invitation_info in the state.
    
    Args:
        tool_context: Context for accessing and updating session state.

    Returns:
        A confirmation message
    """
    logger.info(f"--- Tool: reset_invitation_info called ---")

    empty_invitation_info = InvitationInfo()

    tool_context.state["invitation_info"] = empty_invitation_info

    return {
        "message": f"Successfully reset invitation info"
    }