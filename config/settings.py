"""
DataRoom Intelligence Bot - Configuration Settings
Centralized configuration management for the application
"""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Base directory of the project
BASE_DIR = Path(__file__).parent.parent

class Config:
    """
    Configuration class for DataRoom Intelligence Bot
    All settings loaded from environment variables with sensible defaults
    """

    # ==========================================
    # SLACK CONFIGURATION
    # ==========================================

    # K Fund specific Slack tokens
    SLACK_BOT_TOKEN: str = os.getenv("KFUND_SLACK_BOT_TOKEN", "")
    SLACK_SIGNING_SECRET: str = os.getenv("SLACK_SIGNING_SECRET", "")
    SLACK_APP_TOKEN: str = os.getenv("SLACK_APP_TOKEN", "")

    # Validate Slack configuration
    @property
    def slack_configured(self) -> bool:
        return bool(self.SLACK_BOT_TOKEN and self.SLACK_SIGNING_SECRET)

    # ==========================================
    # OPENAI CONFIGURATION
    # ==========================================

    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4")
    OPENAI_TEMPERATURE: float = float(os.getenv("OPENAI_TEMPERATURE", "0.3"))
    OPENAI_MAX_TOKENS: int = int(os.getenv("OPENAI_MAX_TOKENS", "2000"))

    @property
    def openai_configured(self) -> bool:
        return bool(self.OPENAI_API_KEY)

    # ==========================================
    # GOOGLE DRIVE CONFIGURATION
    # ==========================================

    GOOGLE_SERVICE_ACCOUNT_PATH = "config/kfund_creds.json"

    GOOGLE_CREDENTIALS_PATH: str = os.getenv(
        "GOOGLE_CREDENTIALS_PATH",
        str(BASE_DIR / "config" / "kfund_creds.json")
    )

    @property
    def google_drive_configured(self) -> bool:
        return Path(self.GOOGLE_CREDENTIALS_PATH).exists()

    # ==========================================
    # APPLICATION SETTINGS
    # ==========================================

    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # Server configuration
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "3000"))

    @property
    def is_development(self) -> bool:
        return self.ENVIRONMENT == "development"

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"


     # Processing Limits  ← AÑADIR ESTA SECCIÓN
    TIMEOUT_SECONDS = int(os.getenv("TIMEOUT_SECONDS", "300"))
    MAX_FILES_PER_DATAROOM = int(os.getenv("MAX_FILES", "20"))

    # Storage Configuration  ← AÑADIR ESTA SECCIÓN
    TEMP_STORAGE_PATH = os.getenv("TEMP_STORAGE_PATH", "temp")

    # ==========================================
    # PROCESSING SETTINGS
    # ==========================================

    # Temporary storage
    TEMP_STORAGE_PATH: str = os.getenv("TEMP_STORAGE_PATH", "./temp")
    MAX_FILE_SIZE_MB: int = int(os.getenv("MAX_FILE_SIZE_MB", "50"))
    ANALYSIS_TIMEOUT_SECONDS: int = int(os.getenv("ANALYSIS_TIMEOUT_SECONDS", "300"))

    # Document processing limits
    MAX_DOCUMENTS_PER_DATAROOM: int = int(os.getenv("MAX_DOCUMENTS_PER_DATAROOM", "20"))
    MAX_PAGES_PER_PDF: int = int(os.getenv("MAX_PAGES_PER_PDF", "100"))

    # Ensure temp directory exists
    @property
    def temp_dir(self) -> Path:
        temp_path = Path(self.TEMP_STORAGE_PATH)
        temp_path.mkdir(exist_ok=True)
        return temp_path

    # ==========================================
    # K FUND SPECIFIC SETTINGS
    # ==========================================

    # K Fund workspace identification
    KFUND_SLACK_TEAM_ID: str = os.getenv("KFUND_SLACK_TEAM_ID", "")
    KFUND_COMPANY_NAME: str = "K Fund"

    # Analysis preferences for K Fund
    KFUND_PREFERRED_LANGUAGE: str = "en"
    KFUND_ANALYSIS_STYLE: str = "detailed"
    KFUND_SCORING_CATEGORIES: list = [
        "Team & Management",
        "Business Model",
        "Financials & Traction",
        "Market & Competition",
        "Technology/Product",
        "Legal & Compliance"
    ]

    # ==========================================
    # VALIDATION AND HEALTH CHECK
    # ==========================================

    def validate_configuration(self) -> dict:
        """
        Validate all configuration settings and return status
        """
        status = {
            "slack": self.slack_configured,
            "openai": self.openai_configured,
            "google_drive": self.google_drive_configured,
            "temp_storage": self.temp_dir.exists(),
        }

        status["all_configured"] = all(status.values())
        return status

    def get_missing_configuration(self) -> list:
        """
        Return list of missing configuration items
        """
        missing = []

        if not self.slack_configured:
            missing.append("Slack tokens (SLACK_BOT_TOKEN, SLACK_SIGNING_SECRET)")

        if not self.openai_configured:
            missing.append("OpenAI API key (OPENAI_API_KEY)")

        if not self.google_drive_configured:
            missing.append(f"Google Drive credentials ({self.GOOGLE_CREDENTIALS_PATH})")

        return missing

# ==========================================
# GLOBAL CONFIGURATION INSTANCE
# ==========================================

# Create global configuration instance
config = Config()

# ==========================================
# HELPER FUNCTIONS
# ==========================================

def get_config() -> Config:
    """Get the global configuration instance"""
    return config

def is_configured() -> bool:
    """Check if application is fully configured"""
    return config.validate_configuration()["all_configured"]

def get_configuration_status() -> dict:
    """Get detailed configuration status"""
    return config.validate_configuration()

# ==========================================
# DEVELOPMENT HELPERS
# ==========================================

if __name__ == "__main__":
    # Quick configuration check for development
    print("DataRoom Intelligence Bot - Configuration Check")
    print("=" * 50)

    status = config.validate_configuration()

    for component, configured in status.items():
        emoji = "✅" if configured else "❌"
        print(f"{emoji} {component}: {'OK' if configured else 'NOT CONFIGURED'}")

    if not status["all_configured"]:
        print("\nMissing configuration:")
        for item in config.get_missing_configuration():
            print(f"  - {item}")

    print(f"\nEnvironment: {config.ENVIRONMENT}")
    print(f"Debug mode: {config.DEBUG}")
    print(f"Temp directory: {config.temp_dir}")
