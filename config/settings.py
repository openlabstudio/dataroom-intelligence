# config/settings.py - Updated for cloud deployment
"""
DataRoom Intelligence Bot - Configuration Settings
Cloud-ready configuration management for Railway deployment
"""

import os
import json
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
    Cloud-ready with Railway deployment support
    """

    # ==========================================
    # SLACK CONFIGURATION
    # ==========================================

    # Support both K Fund and OpenLab tokens
    SLACK_BOT_TOKEN: str = os.getenv("SLACK_BOT_TOKEN") or os.getenv("KFUND_SLACK_BOT_TOKEN", "")
    SLACK_SIGNING_SECRET: str = os.getenv("SLACK_SIGNING_SECRET", "")
    SLACK_APP_TOKEN: str = os.getenv("SLACK_APP_TOKEN", "")

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
    # AI ANALYSIS FEATURE FLAGS
    # ==========================================

    # Strict extraction mode - only use facts from documents, no inferences
    STRICT_EXTRACTION: bool = os.getenv("STRICT_EXTRACTION", "True").lower() == "true"

    # Enable AI inferences when data is missing
    ENABLE_INFERENCE: bool = os.getenv("ENABLE_INFERENCE", "False").lower() == "true"

    # ==========================================
    # GOOGLE DRIVE CONFIGURATION - CLOUD READY
    # ==========================================

    @property
    def google_credentials_json(self) -> Optional[dict]:
        """Get Google credentials from environment variable or file"""
        # First try environment variable (Railway deployment)
        creds_json = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
        if creds_json:
            try:
                return json.loads(creds_json)
            except json.JSONDecodeError as e:
                print(f"❌ Invalid JSON in GOOGLE_SERVICE_ACCOUNT_JSON: {e}")
                return None

        # Fallback to file (local development)
        file_paths = [
            "config/openlab_creds.json",  # OpenLab corporate
            "config/kfund_creds.json",    # K Fund specific
            "config/service_account.json" # Generic
        ]

        for file_path in file_paths:
            full_path = BASE_DIR / file_path
            if full_path.exists():
                try:
                    with open(full_path, 'r') as f:
                        return json.load(f)
                except Exception as e:
                    print(f"❌ Failed to load {file_path}: {e}")
                    continue

        return None

    @property
    def google_drive_configured(self) -> bool:
        return self.google_credentials_json is not None

    # ==========================================
    # CLOUD DEPLOYMENT SETTINGS
    # ==========================================

    # Railway/cloud detection
    IS_RAILWAY = bool(os.getenv("RAILWAY_ENVIRONMENT"))
    IS_RENDER = bool(os.getenv("RENDER"))
    IS_HEROKU = bool(os.getenv("DYNO"))

    @property
    def is_cloud_deployment(self) -> bool:
        return self.IS_RAILWAY or self.IS_RENDER or self.IS_HEROKU

    # Environment detection - Fix the self reference
    @property
    def environment(self) -> str:
        return os.getenv("ENVIRONMENT", "production" if self.is_cloud_deployment else "development")

    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # Server configuration
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "3000"))

    # ==========================================
    # STORAGE CONFIGURATION - CLOUD READY
    # ==========================================

    @property
    def temp_storage_path(self) -> str:
        """Get appropriate temp storage path for cloud deployment"""
        if self.is_cloud_deployment:
            # Use /tmp in cloud environments
            return "/tmp/dataroom_temp"
        else:
            # Use local temp directory for development
            return os.getenv("TEMP_STORAGE_PATH", "./temp")

    @property
    def temp_dir(self) -> Path:
        temp_path = Path(self.temp_storage_path)
        temp_path.mkdir(parents=True, exist_ok=True)
        return temp_path

    # Processing limits
    TIMEOUT_SECONDS = int(os.getenv("TIMEOUT_SECONDS", "300"))
    MAX_FILES_PER_DATAROOM = int(os.getenv("MAX_FILES", "20"))
    MAX_FILE_SIZE_MB: int = int(os.getenv("MAX_FILE_SIZE_MB", "50"))
    ANALYSIS_TIMEOUT_SECONDS: int = int(os.getenv("ANALYSIS_TIMEOUT_SECONDS", "300"))
    MAX_DOCUMENTS_PER_DATAROOM: int = int(os.getenv("MAX_DOCUMENTS_PER_DATAROOM", "20"))
    MAX_PAGES_PER_PDF: int = int(os.getenv("MAX_PAGES_PER_PDF", "100"))

    # ==========================================
    # COMPANY SETTINGS (OpenLab + K Fund)
    # ==========================================

    COMPANY_NAME: str = os.getenv("COMPANY_NAME", "OpenLab")
    ANALYSIS_STYLE: str = "detailed"
    PREFERRED_LANGUAGE: str = "en"
    SCORING_CATEGORIES: list = [
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
        """Validate all configuration settings and return status"""
        status = {
            "slack": self.slack_configured,
            "openai": self.openai_configured,
            "google_drive": self.google_drive_configured,
            "temp_storage": self.temp_dir.exists(),
            "cloud_deployment": self.is_cloud_deployment
        }

        status["all_configured"] = all([
            status["slack"],
            status["openai"],
            status["google_drive"]
        ])
        return status

    def get_missing_configuration(self) -> list:
        """Return list of missing configuration items"""
        missing = []

        if not self.slack_configured:
            missing.append("Slack tokens (SLACK_BOT_TOKEN, SLACK_SIGNING_SECRET)")

        if not self.openai_configured:
            missing.append("OpenAI API key (OPENAI_API_KEY)")

        if not self.google_drive_configured:
            missing.append("Google Drive service account (GOOGLE_SERVICE_ACCOUNT_JSON or file)")

        return missing

    def deployment_info(self) -> dict:
        """Get deployment environment information"""
        return {
            "environment": self.ENVIRONMENT,
            "is_cloud": self.is_cloud_deployment,
            "platform": (
                "Railway" if self.IS_RAILWAY else
                "Render" if self.IS_RENDER else
                "Heroku" if self.IS_HEROKU else
                "Local"
            ),
            "temp_storage": str(self.temp_dir),
            "debug_mode": self.DEBUG
        }

# ==========================================
# GLOBAL CONFIGURATION INSTANCE
# ==========================================

# Create global configuration instance
config = Config()

# ==========================================
# CLOUD DEPLOYMENT HELPERS
# ==========================================

def get_deployment_info():
    """Get deployment information for debugging"""
    info = config.deployment_info()
    print("🚀 DataRoom Intelligence Bot - Deployment Info")
    print("=" * 50)
    print(f"Platform: {info['platform']}")
    print(f"Environment: {info['environment']}")
    print(f"Cloud deployment: {info['is_cloud']}")
    print(f"Temp storage: {info['temp_storage']}")
    print(f"Debug mode: {info['debug_mode']}")
    return info

if __name__ == "__main__":
    get_deployment_info()

    # Configuration validation
    status = config.validate_configuration()
    print("\n📋 Configuration Status:")
    for component, configured in status.items():
        emoji = "✅" if configured else "❌"
        print(f"{emoji} {component}: {'OK' if configured else 'NOT CONFIGURED'}")

    if not status["all_configured"]:
        print("\n❌ Missing configuration:")
        for item in config.get_missing_configuration():
            print(f"  - {item}")
