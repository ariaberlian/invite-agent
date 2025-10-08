import logging
import sys
from pathlib import Path

def setup_logger(name: str = None, level: int = logging.INFO) -> logging.Logger:
    """
    Setup and configure a centralized logger for the invitation-agent project.

    Args:
        name: Logger name (typically __name__ from the calling module)
        level: Logging level (default: INFO)

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name or "invitation-agent")

    # Avoid adding handlers multiple times
    if logger.handlers:
        return logger

    logger.setLevel(level)

    # Console handler with formatting
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)

    # Detailed formatter
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)

    logger.addHandler(console_handler)

    # Prevent propagation to root logger to avoid duplicate logs
    logger.propagate = False

    return logger


def setup_file_logger(name: str = None, level: int = logging.INFO, log_file: str = "invitation-agent.log") -> logging.Logger:
    """
    Setup logger with both console and file output.

    Args:
        name: Logger name (typically __name__ from the calling module)
        level: Logging level (default: INFO)
        log_file: Path to log file (default: invitation-agent.log)

    Returns:
        Configured logger instance with file handler
    """
    logger = setup_logger(name, level)

    # Check if file handler already exists
    has_file_handler = any(isinstance(h, logging.FileHandler) for h in logger.handlers)
    if has_file_handler:
        return logger

    # File handler
    log_path = Path(log_file)
    file_handler = logging.FileHandler(log_path, encoding='utf-8')
    file_handler.setLevel(level)

    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)

    return logger


# Create a default logger instance for the package
default_logger = setup_logger("invitation-agent")
