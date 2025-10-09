from datetime import datetime

from google.genai import types

from utils.logger import setup_logger

logger = setup_logger(__name__)

# TODO: define display state
# def display_state(
#     session_service, app_name, user_id, session_id, label="Current State"
# ):
#     """Display the current session state in a formatted way."""
#     try:
#         session = session_service.get_session(
#             app_name=app_name, user_id=user_id, session_id=session_id
#         )

#         # Format the output with clear sections
#         print(f"\n{'-' * 10} {label} {'-' * 10}")

#         # Handle the user name
#         user_name = session.state.get("user_name", "Unknown")
#         print(f"👤 User: {user_name}")

#         # Handle reminders
#         reminders = session.state.get("reminders", [])
#         if reminders:
#             print("📝 Reminders:")
#             for idx, reminder in enumerate(reminders, 1):
#                 print(f"  {idx}. {reminder}")
#         else:
#             print("📝 Reminders: None")

#         print("-" * (22 + len(label)))
#     except Exception as e:
#         print(f"Error displaying state: {e}")


async def process_agent_response(event):
    """Process and display agent response events."""
    logger.info(f"Event ID: {event.id}, Author: {event.author}")

    # Check for specific parts first
    has_specific_part = False
    if event.content and event.content.parts:
        for part in event.content.parts:
            if hasattr(part, "text") and part.text and not part.text.isspace():
                logger.debug(f"---Specific Parts Text: '{part.text.strip()}' ---")

            elif hasattr(part, "tool_response") and part.tool_response:
                # Print tool response information
                logger.debug(f"--- Tool Response: {part.tool_response.output} ---")
                has_specific_part = True        
    
    # Check for final response after specific parts
    final_response = None
    if not has_specific_part and event.is_final_response():
        if (
            event.content
            and event.content.parts
            and hasattr(event.content.parts[0], "text")
            and event.content.parts[0].text
        ):
            final_response = event.content.parts[0].text.strip()

            logger.debug(f"Agent Response: {final_response}")
        else:
            logger.debug(f"Final Agent Response: [No text content in final event]")
    return final_response


async def call_agent_async(runner, user_id, session_id, query):
    """Call the agent asynchronously with the user's query"""

    content = types.Content(role="user", parts=[types.Part(text=query)])
    logger.info(f"Running Query: {query}")

    final_respoonse_text = None

    try:
        async for event in runner.run_async(
            user_id=user_id, session_id=session_id,
            new_message=content
        ):
            response = await process_agent_response(event)
            if response:
                final_respoonse_text = response
            
            logger.info(f"Agent Response: {response}")
    except Exception as e:
        logger.error(f"ERROR during agent run: {e}")
    
    return final_respoonse_text
    