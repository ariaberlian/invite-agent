"""
Centralized configuration module for Invitation Agent.
All environment variables and configuration settings are managed here.
"""

import os
from typing import Optional
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file in project root
BASE_DIR = Path(__file__).resolve().parent
ENV_FILE = BASE_DIR / ".env"

# Load .env file if it exists
if ENV_FILE.exists():
    load_dotenv(ENV_FILE)
else:
    # Try to load from default location
    load_dotenv()


class DatabaseConfig:
    """Database configuration settings"""
    DB_URL: str = os.getenv("DB_URL", "postgresql://localhost:5432/invitation_agent")


class EmailConfig:
    """Email configuration settings"""
    EMAIL_HOST_USER: str = os.getenv("EMAIL_HOST_USER", "")
    EMAIL_HOST_PASSWORD: str = os.getenv("EMAIL_HOST_PASSWORD", "")
    SMTP_SERVER: str = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))

    @classmethod
    def validate(cls):
        """Validate required email configuration"""
        if not cls.EMAIL_HOST_USER:
            raise ValueError("EMAIL_HOST_USER is not set in environment variables")
        if not cls.EMAIL_HOST_PASSWORD:
            raise ValueError("EMAIL_HOST_PASSWORD is not set in environment variables")


class AuthConfig:
    """Authentication and security configuration"""
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))


class BackendConfig:
    """Backend API configuration"""
    APP_NAME: str = os.getenv("APP_NAME", "Invitation Assistant")
    HOST: str = os.getenv("BACKEND_HOST", "0.0.0.0")
    PORT: int = int(os.getenv("BACKEND_PORT", "8000"))


class FrontendConfig:
    """Frontend UI configuration"""
    BACKEND_URL: str = os.getenv("BACKEND_URL", "http://localhost:8000")
    HOST: str = os.getenv("FRONTEND_HOST", "0.0.0.0")
    PORT: int = int(os.getenv("FRONTEND_PORT", "8001"))
    SHARE: bool = os.getenv("FRONTEND_SHARE", "false").lower() == "true"


class Config:
    """Main configuration class that aggregates all config sections"""
    database = DatabaseConfig
    email = EmailConfig
    auth = AuthConfig
    backend = BackendConfig
    frontend = FrontendConfig

    # Direct access to commonly used values
    DB_URL = DatabaseConfig.DB_URL
    SECRET_KEY = AuthConfig.SECRET_KEY
    APP_NAME = BackendConfig.APP_NAME


# Create a singleton instance for easy import
config = Config()


# Validation function to be called at startup
def validate_config():
    """Validate all required configuration settings"""
    errors = []

    # Validate database
    if not config.DB_URL:
        errors.append("DB_URL is not set")

    # Validate email (only if email features are being used)
    try:
        EmailConfig.validate()
    except ValueError as e:
        errors.append(str(e))

    # Validate auth
    if config.SECRET_KEY == "your-secret-key-change-this-in-production":
        errors.append("WARNING: SECRET_KEY is using default value. Please set a secure SECRET_KEY in production!")

    if errors:
        error_msg = "Configuration validation failed:\n" + "\n".join(f"  - {e}" for e in errors)
        raise ValueError(error_msg)


if __name__ == "__main__":
    # Test configuration loading
    print("Configuration loaded successfully!")
    print(f"Database URL: {config.DB_URL}")
    print(f"App Name: {config.APP_NAME}")
    print(f"Backend: {config.backend.HOST}:{config.backend.PORT}")
    print(f"Frontend: {config.frontend.HOST}:{config.frontend.PORT}")
    print(f"Email Server: {config.email.SMTP_SERVER}:{config.email.SMTP_PORT}")

    # Validate
    try:
        validate_config()
        print("\nAll configuration validated successfully!")
    except ValueError as e:
        print(f"\nConfiguration validation errors:\n{e}")
