"""
DataRoom Intelligence Bot - Main Application
Basic Slack bot implementation for K Fund MVP
"""

import os
import logging
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from config.settings import config

# ==========================================
# LOGGING CONFIGURATION
# ==========================================

logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('temp/bot.log') if config.temp_dir.exists() else logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# ==========================================
# SLACK APP INITIALIZATION
# ==========================================

# Initialize Slack app with bot token
app = App(
    token=config.SLACK_BOT_TOKEN,
    signing_secret=config.SLACK_SIGNING_SECRET
)

# ==========================================
# EVENT HANDLERS
# ==========================================

@app.event("app_mention")
def handle_app_mention(event, say, logger):
    """Handle when bot is mentioned in a channel"""
    user = event.get('user')
    text = event.get('text', '')

    logger.info(f"Bot mentioned by user {user}: {text}")

    # Simple response for now
    say(f"Hello <@{user}>! 👋 I'm the DataRoom Intelligence Bot. I'm ready to help analyze data rooms!")

@app.event("message")
def handle_direct_message(event, say, logger):
    """Handle direct messages to the bot"""
    # Only respond to direct messages (not channel messages)
    if event.get('channel_type') == 'im':
        user = event.get('user')
        text = event.get('text', '')

        logger.info(f"Direct message from user {user}: {text}")

        # Simple response
        say(f"Hi there! 👋 I received your message: '{text}'\n\nI'm the DataRoom Intelligence Bot and I'm currently in development. Soon I'll be able to analyze data rooms for you!")

# ==========================================
# SLASH COMMANDS
# ==========================================

@app.command("/analyze")
def handle_analyze_command(ack, body, respond, logger):
    """Handle /analyze slash command - main functionality"""
    # Acknowledge the command immediately
    ack()

    user_id = body['user_id']
    text = body.get('text', '').strip()

    logger.info(f"User {user_id} executed /analyze with text: {text}")

    # For now, just acknowledge the command
    if not text:
        respond({
            "response_type": "ephemeral",  # Only visible to user
            "text": "🔍 *DataRoom Analysis Command*\n\n" +
                   "Usage: `/analyze [google-drive-link]`\n\n" +
                   "Example: `/analyze https://drive.google.com/drive/folders/abc123`\n\n" +
                   "⚠️ *Currently in development mode* - Full functionality coming soon!"
        })
    else:
        respond({
            "response_type": "ephemeral",
            "text": f"🔍 *Analysis Request Received*\n\n" +
                   f"📁 Link: `{text}`\n\n" +
                   f"⏳ Starting analysis... (Development mode)\n\n" +
                   f"🚧 *Note:* Full analysis functionality is under development. " +
                   f"This is a placeholder response to confirm the bot is working!"
        })

@app.command("/ask")
def handle_ask_command(ack, body, respond, logger):
    """Handle /ask slash command - Q&A functionality"""
    ack()

    user_id = body['user_id']
    text = body.get('text', '').strip()

    logger.info(f"User {user_id} executed /ask with text: {text}")

    if not text:
        respond({
            "response_type": "ephemeral",
            "text": "💭 *Ask Question Command*\n\n" +
                   "Usage: `/ask [your question]`\n\n" +
                   "Example: `/ask What is the company's runway?`\n\n" +
                   "⚠️ *Currently in development mode*"
        })
    else:
        respond({
            "response_type": "ephemeral",
            "text": f"💭 *Question Received*\n\n" +
                   f"❓ Question: `{text}`\n\n" +
                   f"🤖 I would answer this question based on the last analyzed data room.\n\n" +
                   f"🚧 *Development mode:* Full Q&A functionality coming soon!"
        })

@app.command("/scoring")
def handle_scoring_command(ack, body, respond, logger):
    """Handle /scoring slash command"""
    ack()

    user_id = body['user_id']
    logger.info(f"User {user_id} executed /scoring")

    respond({
        "response_type": "ephemeral",
        "text": "📊 *Detailed Scoring Breakdown*\n\n" +
               "🏢 Team & Management: 8/10\n" +
               "💼 Business Model: 7/10\n" +
               "💰 Financials & Traction: 6/10\n" +
               "🎯 Market & Competition: 7/10\n" +
               "🔧 Technology/Product: 8/10\n" +
               "⚖️ Legal & Compliance: 5/10\n\n" +
               "📈 *Overall Score: 6.8/10*\n\n" +
               "🚧 *Development mode:* This is sample data. Real scoring will be based on actual data room analysis."
    })

@app.command("/memo")
def handle_memo_command(ack, body, respond, logger):
    """Handle /memo slash command"""
    ack()

    user_id = body['user_id']
    logger.info(f"User {user_id} executed /memo")

    respond({
        "response_type": "ephemeral",
        "text": "📄 *Investment Memo Generation*\n\n" +
               "🔄 Generating comprehensive investment memo...\n\n" +
               "📋 *Would include:*\n" +
               "• Executive Summary\n" +
               "• Investment Thesis\n" +
               "• Key Strengths & Risks\n" +
               "• Financial Analysis\n" +
               "• Recommendation\n\n" +
               "🚧 *Development mode:* Full memo generation coming soon!"
    })

@app.command("/gaps")
def handle_gaps_command(ack, body, respond, logger):
    """Handle /gaps slash command"""
    ack()

    user_id = body['user_id']
    logger.info(f"User {user_id} executed /gaps")

    respond({
        "response_type": "ephemeral",
        "text": "❓ *Missing Information Analysis*\n\n" +
               "🔍 *Critical gaps identified:*\n" +
               "• Detailed competitive analysis\n" +
               "• Customer contracts and pipeline\n" +
               "• IP protection documentation\n" +
               "• Team equity distribution\n" +
               "• Regulatory compliance status\n\n" +
               "📊 *Completeness Score: 65%*\n\n" +
               "🚧 *Development mode:* Real gap analysis will be based on actual data room content."
    })

@app.command("/reset")
def handle_reset_command(ack, body, respond, logger):
    """Handle /reset slash command"""
    ack()

    user_id = body['user_id']
    logger.info(f"User {user_id} executed /reset")

    respond({
        "response_type": "ephemeral",
        "text": "🔄 *Session Reset*\n\n" +
               "✅ Current analysis context cleared\n" +
               "✅ Ready for new data room analysis\n\n" +
               "💡 Use `/analyze [google-drive-link]` to start a new analysis"
    })

# ==========================================
# ERROR HANDLING
# ==========================================

@app.error
def global_error_handler(error, body, logger):
    """Global error handler for unhandled exceptions"""
    logger.exception(f"Error: {error}")
    logger.info(f"Request body: {body}")

    # Could send notification to admin channel in production
    return "Sorry, something went wrong. Please try again later."

# ==========================================
# HEALTH CHECK
# ==========================================

@app.command("/health")
def handle_health_command(ack, body, respond, logger):
    """Health check command for monitoring"""
    ack()

    user_id = body['user_id']
    logger.info(f"Health check requested by user {user_id}")

    # Check configuration status
    status = config.validate_configuration()

    status_text = "🏥 *Health Check Status*\n\n"

    for component, is_ok in status.items():
        emoji = "✅" if is_ok else "❌"
        status_text += f"{emoji} {component.replace('_', ' ').title()}\n"

    status_text += f"\n🌍 Environment: {config.ENVIRONMENT}"
    status_text += f"\n🐛 Debug Mode: {config.DEBUG}"

    respond({
        "response_type": "ephemeral",
        "text": status_text
    })

# ==========================================
# STARTUP VALIDATION
# ==========================================

def validate_startup_configuration():
    """Validate configuration before starting the bot"""
    logger.info("Starting DataRoom Intelligence Bot...")
    logger.info(f"Environment: {config.ENVIRONMENT}")
    logger.info(f"Debug mode: {config.DEBUG}")

    # Check critical configuration
    status = config.validate_configuration()

    if not status.get('slack'):
        logger.error("❌ Slack configuration missing!")
        logger.error("Required: SLACK_BOT_TOKEN, SLACK_SIGNING_SECRET")
        return False

    if not status.get('openai'):
        logger.warning("⚠️ OpenAI configuration missing - AI features will be disabled")

    if not status.get('google_drive'):
        logger.warning("⚠️ Google Drive configuration missing - Document processing will be disabled")

    logger.info("✅ Bot configuration validated successfully")
    return True

# ==========================================
# MAIN APPLICATION
# ==========================================

def main():
    """Main application entry point"""

    # Validate configuration before starting
    if not validate_startup_configuration():
        logger.error("❌ Configuration validation failed. Exiting.")
        return

    # Start the bot
    try:
        logger.info("🚀 Starting Slack Socket Mode Handler...")

        # Use Socket Mode for development (easier than ngrok)
        handler = SocketModeHandler(app, config.SLACK_APP_TOKEN)

        logger.info("✅ DataRoom Intelligence Bot is running!")
        logger.info("📱 The bot will respond to:")
        logger.info("   • /analyze [google-drive-link]")
        logger.info("   • /ask [question]")
        logger.info("   • /scoring")
        logger.info("   • /memo")
        logger.info("   • /gaps")
        logger.info("   • /reset")
        logger.info("   • /health")
        logger.info("   • Direct messages")
        logger.info("   • @mentions in channels")

        # Start the handler (this blocks)
        handler.start()

    except KeyboardInterrupt:
        logger.info("👋 Bot stopped by user")
    except Exception as e:
        logger.exception(f"❌ Unexpected error: {e}")
    finally:
        logger.info("🛑 DataRoom Intelligence Bot shutdown complete")

if __name__ == "__main__":
    main()
