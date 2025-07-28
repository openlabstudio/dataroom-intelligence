"""
DataRoom Intelligence Bot - Minimal Version for Testing
Testing basic Slack connectivity without heavy imports
"""

import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from config.settings import config
from utils.logger import get_logger
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize logger
logger = get_logger(__name__)

# Initialize Slack app
app = App(token=config.SLACK_BOT_TOKEN)

@app.command("/health")
def handle_health_command(ack, body, client):
    """Handle /health command - System health check"""
    ack()

    try:
        channel_id = body['channel_id']

        response = "🏥 **Health Check Status - MINIMAL VERSION**\n\n"
        response += f"✅ **Slack:** Connected\n"
        response += f"✅ **Bot:** Running\n"
        response += f"🌍 **Environment:** {config.ENVIRONMENT}\n"
        response += f"🐛 **Debug Mode:** {config.DEBUG}\n\n"
        response += "**Note:** This is a minimal version for testing basic connectivity.\n"
        response += "Full analysis features are being loaded..."

        client.chat_postMessage(
            channel=channel_id,
            text=response
        )

    except Exception as e:
        logger.error(f"❌ Error in health command: {e}")
        client.chat_postMessage(
            channel=channel_id,
            text=f"❌ Health check failed: {str(e)}"
        )

@app.command("/analyze")
def handle_analyze_command(ack, body, client):
    """Handle /analyze command - Placeholder"""
    ack()

    try:
        channel_id = body['channel_id']
        drive_link = body.get('text', '').strip()

        response = "🔍 **Analysis Request Received**\n\n"
        response += f"📁 Link: {drive_link}\n"
        response += "⚠️ **Status:** Running in minimal mode\n\n"
        response += "**Next Steps:**\n"
        response += "1. ✅ Slack connectivity confirmed\n"
        response += "2. 🔄 Loading full analysis capabilities...\n"
        response += "3. 🚧 Full implementation in progress"

        client.chat_postMessage(
            channel=channel_id,
            text=response
        )

    except Exception as e:
        logger.error(f"❌ Error in analyze command: {e}")

@app.event("app_mention")
def handle_app_mention(event, client):
    """Handle @mentions of the bot"""
    try:
        channel_id = event['channel']

        response = "👋 Hi! I'm the DataRoom Intelligence Bot (Minimal Mode).\n\n"
        response += "**Available commands:**\n"
        response += "• `/health` - Check system status\n"
        response += "• `/analyze [link]` - Test command recognition\n\n"
        response += "🚧 Full analysis features are being loaded..."

        client.chat_postMessage(
            channel=channel_id,
            text=response
        )

    except Exception as e:
        logger.error(f"❌ Error handling mention: {e}")

def main():
    """Main application entry point - Minimal Version"""
    try:
        logger.info("🚀 Starting DataRoom Intelligence Bot (Minimal Mode)...")
        logger.info(f"Environment: {config.ENVIRONMENT}")
        logger.info(f"Debug mode: {config.DEBUG}")

        # Basic validation
        if not config.slack_configured:
            logger.error("❌ Slack configuration missing")
            return

        logger.info("✅ Basic configuration validated")
        logger.info("🚀 Starting Slack Socket Mode Handler...")

        handler = SocketModeHandler(app, config.SLACK_APP_TOKEN)

        logger.info("✅ DataRoom Intelligence Bot is running (Minimal Mode)!")
        logger.info("📱 Available commands:")
        logger.info("   • /health")
        logger.info("   • /analyze [test]")
        logger.info("   • @mentions")

        handler.start()

    except KeyboardInterrupt:
        logger.info("🛑 Bot stopped by user")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        raise

if __name__ == "__main__":
    main()
