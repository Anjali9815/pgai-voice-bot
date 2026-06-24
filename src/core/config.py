"""
config.py - Configuration Management
One place for all settings. Clean and organized.
"""

import os
from dotenv import load_dotenv


class Config:
    """
    Loads and validates all environment variables.
    
    OOP Concept: Encapsulation
    - All config logic is INSIDE this class
    - Outside code just does: config.groq_key
    - Nobody needs to know HOW we load it
    """

    def __init__(self):
        load_dotenv()
        self._validate()

    def _validate(self):
        """
        Private method -- only this class calls this.
        Checks all required keys are present.
        """
        missing = []
        if not self.groq_api_key:
            missing.append("GROQ_API_KEY")
        if missing:
            raise EnvironmentError(
                f"Missing required variables: {', '.join(missing)}\n"
                f"Please check your .env file."
            )
        print("[Config] All environment variables loaded successfully")

    # Groq Settings

    @property
    def groq_api_key(self) -> str:
        return os.getenv("GROQ_API_KEY", "")

    @property
    def groq_model(self) -> str:
        return os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

    # Twilio Settings (Mode 2 later)

    @property
    def twilio_account_sid(self) -> str:
        return os.getenv("TWILIO_ACCOUNT_SID", "")

    @property
    def twilio_auth_token(self) -> str:
        return os.getenv("TWILIO_AUTH_TOKEN", "")

    @property
    def twilio_phone_number(self) -> str:
        return os.getenv("TWILIO_PHONE_NUMBER", "")

    @property
    def target_phone_number(self) -> str:
        return os.getenv("TARGET_PHONE_NUMBER", "+18054398008")

    # Directories

    @property
    def transcripts_dir(self) -> str:
        return os.getenv("TRANSCRIPTS_DIR", "transcripts")

    @property
    def recordings_dir(self) -> str:
        return os.getenv("RECORDINGS_DIR", "recordings")

    @property
    def logs_dir(self) -> str:
        return os.getenv("LOGS_DIR", "logs")

    def __repr__(self):
        return (
            f"Config("
            f"model={self.groq_model}, "
            f"twilio={'configured' if self.twilio_account_sid else 'not set'}"
            f")"
        )


# Single shared instance
config = Config()