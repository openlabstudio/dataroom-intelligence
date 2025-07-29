"""
DataRoom Intelligence Bot - Google Drive Version
Testing Google Drive + Document Processing (No AI yet)
"""
import os
import threading  # ← CAMBIAR: de asyncio a threading
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from config.settings import config
from handlers.drive_handler import GoogleDriveHandler
from handlers.doc_processor import DocumentProcessor
from utils.logger import get_logger
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize logger
logger = get_logger(__name__)

# Initialize Slack app
app = App(token=config.SLACK_BOT_TOKEN)

# Initialize handlers (no AI yet)
drive_handler = GoogleDriveHandler() if config.google_drive_configured else None
doc_processor = DocumentProcessor()

# Store user sessions
user_sessions = {}

@app.command("/analyze")
def handle_analyze_command(ack, body, client):
    """Handle /analyze command - Google Drive processing only"""
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
            text="🔍 **Document Processing Started**\n\n" +
                 f"📁 Link: *{drive_link}*\n" +
                 f"📥 **Downloading documents from Google Drive...**\n\n" +
                 f"⚠️ Note: AI analysis disabled - testing document processing only"
        )

        # Start background processing
        threading.Thread(
            target=process_dataroom_documents,
            args=(client, channel_id, user_id, drive_link, initial_response['ts']),
            daemon=True
        ).start()

    except Exception as e:
        logger.error(f"❌ Error in analyze command: {e}")
        client.chat_postMessage(
            channel=channel_id,
            text=f"❌ **Analysis Failed**\n\nError: {str(e)}"
        )

def process_dataroom_documents(client, channel_id, user_id, drive_link, message_ts):
    """Process documents without AI analysis"""
    try:
        # Step 1: Download documents
        client.chat_update(
            channel=channel_id,
            ts=message_ts,
            text="🔍 **Document Processing in Progress**\n\n" +
                 f"📁 Link: {drive_link}\n" +
                 f"📥 **Downloading documents from Google Drive...**"
        )

        downloaded_files = drive_handler.download_dataroom(drive_link)

        if not downloaded_files:
            client.chat_update(
                channel=channel_id,
                ts=message_ts,
                text="❌ **Processing Failed**\n\n" +
                     "No supported documents found in the Google Drive folder.\n" +
                     "Supported formats: PDF, Word, TXT"
            )
            return

        # Step 2: Process documents
        client.chat_update(
            channel=channel_id,
            ts=message_ts,
            text="🔍 **Document Processing in Progress**\n\n" +
                 f"📄 Found {len(downloaded_files)} documents\n" +
                 f"📖 **Extracting content from documents...**"
        )

        processed_documents = doc_processor.process_dataroom_documents(downloaded_files)
        document_summary = doc_processor.get_content_summary(processed_documents)

        # Step 3: Generate summary response (no AI)
        response = format_processing_results(processed_documents, document_summary, drive_link)

        client.chat_update(
            channel=channel_id,
            ts=message_ts,
            text=response
        )

        # Store in session for future use
        user_sessions[user_id] = {
            'processed_documents': processed_documents,
            'document_summary': document_summary,
            'drive_link': drive_link
        }

        # Cleanup temporary files
        drive_handler.cleanup_temp_files()

        logger.info(f"✅ Document processing completed for user {user_id}")

    except Exception as e:
        logger.error(f"❌ Document processing failed: {e}")
        client.chat_update(
            channel=channel_id,
            ts=message_ts,
            text=f"❌ **Processing Failed**\n\nError: {str(e)}\n\n" +
                 "Please check the Google Drive link and try again."
        )

def format_processing_results(processed_documents, document_summary, drive_link):
    """Format the processing results without AI analysis"""

    response = "✅ **DOCUMENT PROCESSING COMPLETE**\n\n"

    # Basic stats
    total_docs = document_summary.get('total_documents', 0)
    successful = document_summary.get('successful_processing', 0)
    failed = document_summary.get('failed_processing', 0)

    response += f"📊 **Processing Summary:**\n"
    response += f"• **Total Documents:** {total_docs}\n"
    response += f"• **Successfully Processed:** {successful}\n"
    if failed > 0:
        response += f"• **Failed Processing:** {failed}\n"
    response += "\n"

    # Document types
    doc_types = document_summary.get('document_types', {})
    if doc_types:
        response += "📄 **Document Types Found:**\n"
        for doc_type, count in doc_types.items():
            if doc_type != 'error':
                emoji = get_doc_emoji(doc_type)
                response += f"• {emoji} **{doc_type.title()}:** {count} files\n"
        response += "\n"

    # Content overview
    total_content = document_summary.get('total_content_length', 0)
    if total_content > 0:
        response += f"📏 **Total Content Extracted:** {format_size(total_content)}\n\n"

    # Document details
    response += "📋 **Documents Processed:**\n"
    for doc in processed_documents[:5]:  # Show first 5
        if doc['type'] != 'error':
            emoji = get_doc_emoji(doc['type'])
            content_size = len(doc.get('content', ''))
            response += f"{emoji} **{doc['name']}** - {format_size(content_size)}\n"

    if len(processed_documents) > 5:
        response += f"• *...and {len(processed_documents) - 5} more documents*\n"

    response += "\n"

    # Content samples
    response += "📖 **Content Samples:**\n"
    for doc in processed_documents[:2]:  # Show content from first 2 docs
        if doc['type'] != 'error' and doc.get('content'):
            content_preview = doc['content'][:200].replace('\n', ' ').strip()
            response += f"• **{doc['name']}:** {content_preview}...\n"

    response += "\n"

    # Next steps
    response += "🎯 **Status:** Document extraction successful!\n"
    response += "🤖 **Next Step:** Add AI analysis to generate insights\n\n"
    response += "**Available Commands:**\n"
    response += "• `/health` - Check system status\n"
    response += "• `/reset` - Clear current session"

    return response

def get_doc_emoji(doc_type):
    """Get emoji for document type"""
    emoji_map = {
        'pdf': '📕',
        'word': '📝',
        'text': '📄',
        'csv': '📈',
        'excel': '📊'
    }
    return emoji_map.get(doc_type.lower(), '📄')

def format_size(size):
    """Format content size"""
    if size < 1000:
        return f"{size} chars"
    elif size < 1000000:
        return f"{size//1000}K chars"
    else:
        return f"{size//1000000}M chars"

@app.command("/health")
def handle_health_command(ack, body, client):
    """Handle /health command"""
    ack()

    try:
        channel_id = body['channel_id']

        response = "🏥 **Health Check Status - DRIVE VERSION**\n\n"
        response += f"✅ **Slack:** Connected\n"
        response += f"✅ **Google Drive:** {'OK' if config.google_drive_configured else 'NOT CONFIGURED'}\n"
        response += f"✅ **Document Processing:** Ready\n"
        response += f"⚠️ **AI Analysis:** Disabled (testing mode)\n\n"
        response += f"🌍 **Environment:** {config.ENVIRONMENT}\n"
        response += f"🐛 **Debug Mode:** {config.DEBUG}\n\n"
        response += "**Ready for document processing!**"

        client.chat_postMessage(
            channel=channel_id,
            text=response
        )

    except Exception as e:
        logger.error(f"❌ Error in health command: {e}")

@app.command("/reset")
def handle_reset_command(ack, body, client):
    """Handle /reset command"""
    ack()

    try:
        user_id = body['user_id']
        channel_id = body['channel_id']

        if user_id in user_sessions:
            del user_sessions[user_id]

        if drive_handler:
            drive_handler.cleanup_temp_files()

        client.chat_postMessage(
            channel=channel_id,
            text="🔄 **Session Reset Complete**\n\n" +
                 "✅ Session cleared\n" +
                 "✅ Temporary files cleaned up\n\n" +
                 "Ready for new document processing!"
        )

    except Exception as e:
        logger.error(f"❌ Error in reset command: {e}")

@app.event("app_mention")
def handle_app_mention(event, client):
    """Handle @mentions"""
    try:
        channel_id = event['channel']

        response = "👋 Hi! I'm the DataRoom Intelligence Bot (Drive Testing Mode).\n\n"
        response += "**Available commands:**\n"
        response += "• `/analyze [google-drive-link]` - Process documents from Google Drive\n"
        response += "• `/health` - Check system status\n"
        response += "• `/reset` - Reset current session\n\n"
        response += "🚧 **Current Status:** Document processing ready, AI analysis coming soon!"

        client.chat_postMessage(
            channel=channel_id,
            text=response
        )

    except Exception as e:
        logger.error(f"❌ Error handling mention: {e}")

def main():
    """Main application entry point"""
    try:
        logger.info("🚀 Starting DataRoom Intelligence Bot (Drive Version)...")
        logger.info(f"Environment: {config.ENVIRONMENT}")
        logger.info(f"Debug mode: {config.DEBUG}")

        # Validate configuration
        if not config.slack_configured:
            logger.error("❌ Slack configuration missing")
            return

        if not config.google_drive_configured:
            logger.error("❌ Google Drive configuration missing")
            return

        logger.info("✅ Configuration validated")
        logger.info("🚀 Starting Slack Socket Mode Handler...")

        handler = SocketModeHandler(app, config.SLACK_APP_TOKEN)

        logger.info("✅ DataRoom Intelligence Bot is running (Drive Version)!")
        logger.info("📱 Available commands:")
        logger.info("   • /analyze [google-drive-link]")
        logger.info("   • /health")
        logger.info("   • /reset")
        logger.info("   • @mentions")

        handler.start()

    except KeyboardInterrupt:
        logger.info("🛑 Bot stopped by user")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        raise

if __name__ == "__main__":
    main()
