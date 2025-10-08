from datetime import datetime
from ..utils.logger import setup_logger

logger = setup_logger(__name__)

def get_curent_datetime():
    """Function to get current date time.

    Args:
        None

    Returns:
        datetime
    """
    logger.info("--- Tool Call: get_current_datetime() ---")
    current_time = datetime.now()
    logger.debug(f"Current datetime: {current_time}")
    return current_time