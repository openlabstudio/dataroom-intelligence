"""
DataRoom Intelligence Bot - Main Application
A Slack bot that analyzes data rooms for venture capital investment decisions using AI
"""

import os
import asyncio
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from config.settings import config
from handlers.drive_handler import GoogleDriveHandler
from handlers.doc_processor import DocumentProcessor
from handlers.ai_analyzer import AIAnalyzer
from utils.slack_formatter import format_analysis_response, format_health_response, format_error_response
from utils.logger import get_logger
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize logger
logger = get_logger(__name__)

# Initialize Slack app
app = App(token=config.SLACK_BOT_TOKEN)

# Initialize handlers
drive_handler = GoogleDriveHandler() if config.google_drive_configured else None
doc_processor = DocumentProcessor()
ai_analyzer = AIAnalyzer()

# Store user sessions (in production, use a database)
user_sessions = {}

@app.command("/analyze")
def handle_analyze_command(ack, body, client):
    """Handle /analyze command - Main data room analysis"""
    ack()

    try:
        user_id = body['user_id']
        channel_id = body['channel_id']
        drive_link = body.get('text', '').strip()

        if not drive_link:
            client.chat_postMessage(
                channel=channel_id,
                text="❌ Please provide a Google Drive folder link.\n\nUsage: `/analyze [google-drive-link]`"
            )
            return

        if not config.google_drive_configured:
            client.chat_postMessage(
                channel=channel_id,
                text="❌ Google Drive is not configured. Please contact the administrator."
            )
            return

        # Send initial response
        initial_response = client.chat_postMessage(
            channel=channel_id,
            text="🔍 **Analysis Request Received**\n\n" +
                 f"📁 Link: *{drive_link}*\n" +
                 f"⏳ Starting analysis... (Development mode)\n\n" +
                 f"🚧 Note: Full analysis functionality is now being processed!"
        )

        # Start async analysis
        asyncio.create_task(perform_dataroom_analysis(
            client, channel_id, user_id, drive_link, initial_response['ts']
        ))

    except Exception as e:
        logger.error(f"❌ Error in analyze command: {e}")
        client.chat_postMessage(
            channel=channel_id,
            text=format_error_response("analyze", str(e))
        )

async def perform_dataroom_analysis(client, channel_id, user_id, drive_link, message_ts):
    """Perform the actual data room analysis asynchronously"""
    try:
        # Update status: Downloading
        client.chat_update(
            channel=channel_id,
            ts=message_ts,
            text="🔍 **Analysis in Progress**\n\n" +
                 f"📁 Link: {drive_link}\n" +
                 f"📥 **Downloading documents from Google Drive...**"
        )

        # Step 1: Download documents
        downloaded_files = drive_handler.download_dataroom(drive_link)

        if not downloaded_files:
            client.chat_update(
                channel=channel_id,
                ts=message_ts,
                text="❌ **Analysis Failed**\n\n" +
                     "No supported documents found in the Google Drive folder.\n" +
                     "Supported formats: PDF, Excel, Word, CSV, TXT"
            )
            return

        # Update status: Processing
        client.chat_update(
            channel=channel_id,
            ts=message_ts,
            text="🔍 **Analysis in Progress**\n\n" +
                 f"📁 Found {len(downloaded_files)} documents\n" +
                 f"📄 **Processing document contents...**"
        )

        # Step 2: Process documents
        processed_documents = doc_processor.process_dataroom_documents(downloaded_files)
        document_summary = doc_processor.get_content_summary(processed_documents)

        # Update status: AI Analysis
        client.chat_update(
            channel=channel_id,
            ts=message_ts,
            text="🔍 **Analysis in Progress**\n\n" +
                 f"📄 Processed {document_summary['successful_processing']} documents\n" +
                 f"🧠 **Analyzing with AI (GPT-4)...**"
        )

        # Step 3: AI Analysis
        analysis_result = ai_analyzer.analyze_dataroom(processed_documents, document_summary)

        # Step 4: Format and send final response
        formatted_response = format_analysis_response(analysis_result, document_summary)

        client.chat_update(
            channel=channel_id,
            ts=message_ts,
            text=formatted_response
        )

        # Store analysis in user session
        user_sessions[user_id] = {
            'analysis_result': analysis_result,
            'document_summary': document_summary,
            'drive_link': drive_link
        }

        # Cleanup temporary files
        drive_handler.cleanup_temp_files()

        logger.info(f"✅ Analysis completed for user {user_id}")

    except Exception as e:
        logger.error(f"❌ Analysis failed: {e}")
        client.chat_update(
            channel=channel_id,
            ts=message_ts,
            text=format_error_response("analysis", str(e))
        )

@app.command("/ask")
def handle_ask_command(ack, body, client):
    """Handle /ask command - Q&A about analyzed data room"""
    ack()

    try:
        user_id = body['user_id']
        channel_id = body['channel_id']
        question = body.get('text', '').strip()

        if not question:
            client.chat_postMessage(
                channel=channel_id,
                text="❓ Please provide a question.\n\nUsage: `/ask [your question]`"
            )
            return

        if user_id not in user_sessions:
            client.chat_postMessage(
                channel=channel_id,
                text="❌ No data room analysis found. Please run `/analyze [google-drive-link]` first."
            )
            return

        # Get answer from AI
        answer = ai_analyzer.answer_question(question)

        response = f"💡 **Question:** {question}\n\n" +\
                  f"**Answer:**\n{answer}\n\n" +\
                  f"📎 *Based on analyzed data room*"

        client.chat_postMessage(
            channel=channel_id,
            text=response
        )

    except Exception as e:
        logger.error(f"❌ Error in ask command: {e}")
        client.chat_postMessage(
            channel=channel_id,
            text=format_error_response("ask", str(e))
        )

@app.command("/scoring")
def handle_scoring_command(ack, body, client):
    """Handle /scoring command - Detailed scoring breakdown"""
    ack()

    try:
        user_id = body['user_id']
        channel_id = body['channel_id']

        if user_id not in user_sessions:
            client.chat_postMessage(
                channel=channel_id,
                text="❌ No data room analysis found. Please run `/analyze [google-drive-link]` first."
            )
            return

        scoring_data = ai_analyzer.get_detailed_scoring()

        if 'error' in scoring_data:
            client.chat_postMessage(
                channel=channel_id,
                text=f"❌ {scoring_data['error']}"
            )
            return

        # Format scoring response
        response = "📊 **DETAILED SCORING BREAKDOWN**\n\n"
        response += f"🎯 **Overall Score: {scoring_data['overall_score']}/10**\n\n"

        response += "**Category Scores:**\n"
        for category, data in scoring_data['category_scores'].items():
            category_name = category.replace('_', ' ').title()
            score = data.get('score', 0)
            justification = data.get('justification', 'No justification available')
            response += f"• **{category_name}:** {score}/10 - {justification}\n"

        response += f"\n🎯 **Recommendation:** {scoring_data['recommendation']}\n"

        client.chat_postMessage(
            channel=channel_id,
            text=response
        )

    except Exception as e:
        logger.error(f"❌ Error in scoring command: {e}")
        client.chat_postMessage(
            channel=channel_id,
            text=format_error_response("scoring", str(e))
        )

@app.command("/memo")
def handle_memo_command(ack, body, client):
    """Handle /memo command - Generate investment memo"""
    ack()

    try:
        user_id = body['user_id']
        channel_id = body['channel_id']

        if user_id not in user_sessions:
            client.chat_postMessage(
                channel=channel_id,
                text="❌ No data room analysis found. Please run `/analyze [google-drive-link]` first."
            )
            return

        memo = ai_analyzer.generate_investment_memo()

        response = "📄 **INVESTMENT MEMO**\n\n" + memo

        client.chat_postMessage(
            channel=channel_id,
            text=response
        )

    except Exception as e:
        logger.error(f"❌ Error in memo command: {e}")
        client.chat_postMessage(
            channel=channel_id,
            text=format_error_response("memo", str(e))
        )

@app.command("/gaps")
def handle_gaps_command(ack, body, client):
    """Handle /gaps command - Analyze information gaps"""
    ack()

    try:
        user_id = body['user_id']
        channel_id = body['channel_id']

        if user_id not in user_sessions:
            client.chat_postMessage(
                channel=channel_id,
                text="❌ No data room analysis found. Please run `/analyze [google-drive-link]` first."
            )
            return

        gaps_analysis = ai_analyzer.analyze_gaps()

        response = "🔍 **INFORMATION GAPS ANALYSIS**\n\n" + gaps_analysis

        client.chat_postMessage(
            channel=channel_id,
            text=response
        )

    except Exception as e:
        logger.error(f"❌ Error in gaps command: {e}")
        client.chat_postMessage(
            channel=channel_id,
            text=format_error_response("gaps", str(e))
        )

@app.command("/reset")
def handle_reset_command(ack, body, client):
    """Handle /reset command - Reset analysis session"""
    ack()

    try:
        user_id = body['user_id']
        channel_id = body['channel_id']

        # Clear user session
        if user_id in user_sessions:
            del user_sessions[user_id]

        # Reset AI analyzer
        ai_analyzer.reset_analysis()

        # Cleanup temp files
        if drive_handler:
            drive_handler.cleanup_temp_files()

        client.chat_postMessage(
            channel=channel_id,
            text="🔄 **Session Reset Complete**\n\n" +
                 "✅ Analysis context cleared\n" +
                 "✅ Temporary files cleaned up\n" +
                 "✅ Ready for new data room analysis\n\n" +
                 "Use `/analyze [google-drive-link]` to start a new analysis."
        )

    except Exception as e:
        logger.error(f"❌ Error in reset command: {e}")
        client.chat_postMessage(
            channel=channel_id,
            text=format_error_response("reset", str(e))
        )

@app.command("/health")
def handle_health_command(ack, body, client):
    """Handle /health command - System health check"""
    ack()

    try:
        channel_id = body['channel_id']
        health_response = format_health_response()

        client.chat_postMessage(
            channel=channel_id,
            text=health_response
        )

    except Exception as e:
        logger.error(f"❌ Error in health command: {e}")
        client.chat_postMessage(
            channel=channel_id,
            text=format_error_response("health", str(e))
        )

@app.event("app_mention")
def handle_app_mention(event, client):
    """Handle @mentions of the bot"""
    try:
        channel_id = event['channel']
        text = event.get('text', '')

        response = "👋 Hi! I'm the DataRoom Intelligence Bot.\n\n" +\
                  "**Available commands:**\n" +\
                  "• `/analyze [google-drive-link]` - Analyze a data room\n" +\
                  "• `/ask [question]` - Ask questions about analyzed data room\n" +\
                  "• `/scoring` - Get detailed scoring breakdown\n" +\
                  "• `/memo` - Generate investment memo\n" +\
                  "• `/gaps` - Analyze missing information\n" +\
                  "• `/reset` - Reset current session\n" +\
                  "• `/health` - Check system status\n\n" +\
                  "Start by analyzing a data room with `/analyze`!"

        client.chat_postMessage(
            channel=channel_id,
            text=response
        )

    except Exception as e:
        logger.error(f"❌ Error handling mention: {e}")

def main():
    """Main application entry point"""
    try:
        logger.info("Starting DataRoom Intelligence Bot...")
        logger.info(f"Environment: {config.ENVIRONMENT}")
        logger.info(f"Debug mode: {config.DEBUG}")

        # Validate configuration
        if not config.slack_configured:
            logger.error("❌ Slack configuration missing")
            return

        if not config.openai_configured:
            logger.error("❌ OpenAI configuration missing")
            return

        if not config.google_drive_configured:
            logger.warning("⚠️ Google Drive configuration missing - Document processing will be disabled")

        logger.info("✅ Bot configuration validated successfully")

        # Start the bot
        logger.info("🚀 Starting Slack Socket Mode Handler...")
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

        handler.start()

    except KeyboardInterrupt:
        logger.info("🛑 Bot stopped by user")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        raise

if __name__ == "__main__":
    main()
