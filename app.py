"""
DataRoom Intelligence Bot - Railway-Compatible Version
A Slack bot that analyzes data rooms for venture capital investment decisions using AI
Combines robust document processing with full AI analysis capabilities + Flask server for Railway
"""

import os
import threading
from datetime import datetime
from flask import Flask, jsonify
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from config.settings import config
from handlers.drive_handler import GoogleDriveHandler
from handlers.doc_processor import DocumentProcessor
from handlers.ai_analyzer import AIAnalyzer
# NEW: Import market research system (not used yet)
from agents import MarketResearchOrchestrator
from utils.slack_formatter import format_analysis_response, format_health_response, format_error_response
from utils.logger import get_logger
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize logger
logger = get_logger(__name__)

# ==========================================
# FLASK APP FOR RAILWAY HEALTH CHECKS
# ==========================================

flask_app = Flask(__name__)

@flask_app.route('/health')
def health_check():
    """Health check endpoint for Railway"""
    try:
        # Check all system components
        health_status = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "service": "DataRoom Intelligence Bot",
            "components": {
                "slack": config.slack_configured,
                "openai": config.openai_configured,
                "google_drive": config.google_drive_configured,
                "temp_storage": config.temp_dir.exists()
            }
        }

        # Overall health
        all_healthy = all(health_status["components"].values())
        health_status["overall"] = "healthy" if all_healthy else "degraded"

        logger.info(f"Health check: {health_status['overall']}")

        # Always return 200 for Railway (even if degraded, bot can still work partially)
        return jsonify(health_status), 200

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 200

@flask_app.route('/')
def root():
    """Root endpoint"""
    return jsonify({
        "service": "DataRoom Intelligence Bot",
        "status": "running",
        "version": "1.0.0",
        "platform": "Railway",
        "endpoints": ["/health", "/status"]
    })

@flask_app.route('/status')
def status():
    """Detailed status endpoint"""
    try:
        return jsonify({
            "service": "DataRoom Intelligence Bot",
            "timestamp": datetime.now().isoformat(),
            "deployment": config.deployment_info(),
            "active_sessions": len(user_sessions),
            "configuration_status": config.validate_configuration()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ==========================================
# SLACK BOT INITIALIZATION
# ==========================================

# Initialize Slack app
app = App(token=config.SLACK_BOT_TOKEN)

# Initialize handlers
drive_handler = GoogleDriveHandler() if config.google_drive_configured else None
doc_processor = DocumentProcessor()
ai_analyzer = AIAnalyzer()

# NEW: Initialize market research orchestrator (not used yet)
market_research_orchestrator = MarketResearchOrchestrator() if config.openai_configured else None

# Log initialization status
logger.info(f"🔧 AI Analyzer initialized: {ai_analyzer is not None}")
logger.info(f"🔧 Market Research Orchestrator initialized: {market_research_orchestrator is not None}")
logger.info(f"🔧 OpenAI configured: {config.openai_configured}")

# Store user sessions (in production, use a database)
user_sessions = {}

# ==========================================
# SLACK BOT COMMANDS - COMPLETE SET
# ==========================================

@app.command("/analyze")
def handle_analyze_command(ack, body, client):
    """Handle /analyze command - Complete data room analysis with AI"""
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
                 f"⏳ Starting comprehensive data room analysis...\n\n" +
                 f"🚧 Processing documents and generating AI insights..."
        )

        # Start background processing using threading (proven to work)
        threading.Thread(
            target=perform_dataroom_analysis,
            args=(client, channel_id, user_id, drive_link, initial_response['ts']),
            daemon=True
        ).start()

    except Exception as e:
        logger.error(f"❌ Error in analyze command: {e}")
        client.chat_postMessage(
            channel=channel_id,
            text=format_error_response("analyze", str(e))
        )

def perform_dataroom_analysis(client, channel_id, user_id, drive_link, message_ts):
    """Perform the complete data room analysis with AI"""
    try:
        # Step 1: Download documents
        client.chat_update(
            channel=channel_id,
            ts=message_ts,
            text="🔍 **Analysis in Progress**\n\n" +
                 f"📁 Link: {drive_link}\n" +
                 f"📥 **Downloading documents from Google Drive...**"
        )

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

        # Step 2: Process documents
        client.chat_update(
            channel=channel_id,
            ts=message_ts,
            text="🔍 **Analysis in Progress**\n\n" +
                 f"📄 Found {len(downloaded_files)} documents\n" +
                 f"📖 **Processing document contents...**"
        )

        processed_documents = doc_processor.process_dataroom_documents(downloaded_files)
        document_summary = doc_processor.get_content_summary(processed_documents)

        # Step 3: AI Analysis (if configured)
        if ai_analyzer and config.openai_configured:
            client.chat_update(
                channel=channel_id,
                ts=message_ts,
                text="🔍 **Analysis in Progress**\n\n" +
                     f"📄 Processed {document_summary['successful_processing']} documents\n" +
                     f"🧠 **Analyzing with AI (GPT-4)...**"
            )

            analysis_result = ai_analyzer.analyze_dataroom(processed_documents, document_summary)

            # Format and send AI analysis response
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
                'processed_documents': processed_documents,
                'drive_link': drive_link
            }

        else:
            # Fallback: Document processing only
            client.chat_update(
                channel=channel_id,
                ts=message_ts,
                text="🔍 **Analysis in Progress**\n\n" +
                     f"📄 Processed {document_summary['successful_processing']} documents\n" +
                     f"⚠️ **AI analysis disabled** - showing document processing results"
            )

            response = format_processing_results(processed_documents, document_summary, drive_link)

            client.chat_update(
                channel=channel_id,
                ts=message_ts,
                text=response
            )

            # Store documents in user session (for future AI activation)
            user_sessions[user_id] = {
                'processed_documents': processed_documents,
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

def format_processing_results(processed_documents, document_summary, drive_link):
    """Format the processing results when AI is not available"""
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
    if config.openai_configured:
        response += "🎯 **Status:** Documents processed, ready for AI analysis!\n"
        response += "🤖 **Next:** Use commands below for AI insights\n\n"
        response += "**Available AI Commands:**\n"
        response += "• `/ask [question]` - Ask questions about the documents\n"
        response += "• `/scoring` - Get detailed VC scoring\n"
        response += "• `/memo` - Generate investment memo\n"
        response += "• `/gaps` - Analyze missing information\n"
    else:
        response += "🎯 **Status:** Document extraction successful!\n"
        response += "🤖 **Note:** AI analysis requires OpenAI configuration\n\n"

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

@app.command("/asktest")
def handle_asktest_command(ack, body, client):
    """Simple test version of ask command"""
    ack()
    logger.info("🧪 /asktest command received!")

    client.chat_postMessage(
        channel=body['channel_id'],
        text="✅ asktest command is working!"
    )

@app.command("/ask")
def handle_ask_command(ack, body, client):
    """Handle /ask command - Q&A about analyzed data room"""
    ack()

    logger.info("🔍 /ask command received")

    try:
        user_id = body['user_id']
        channel_id = body['channel_id']
        question = body.get('text', '').strip()

        logger.info(f"🔍 User: {user_id}, Question: {question}")

        if not question:
            logger.info("❌ No question provided")
            client.chat_postMessage(
                channel=channel_id,
                text="❓ Please provide a question.\n\nUsage: `/ask [your question]`"
            )
            return

        if user_id not in user_sessions:
            logger.info(f"❌ No session found for user {user_id}")
            logger.info(f"📊 Active sessions: {list(user_sessions.keys())}")
            client.chat_postMessage(
                channel=channel_id,
                text="❌ No data room analysis found. Please run `/analyze [google-drive-link]` first."
            )
            return

        if not ai_analyzer or not config.openai_configured:
            logger.info("❌ AI not configured")
            client.chat_postMessage(
                channel=channel_id,
                text="❌ AI analysis is not configured. Please configure OpenAI API key."
            )
            return

        logger.info("🤖 Calling AI analyzer...")
        # Get answer from AI
        answer = ai_analyzer.answer_question(question)
        logger.info(f"✅ AI response received: {len(answer)} chars")

        response = f"💡 **Question:** {question}\n\n" +\
                  f"**Answer:**\n{answer}\n\n" +\
                  f"📎 *Based on analyzed data room*"

        client.chat_postMessage(
            channel=channel_id,
            text=response
        )
        logger.info("✅ Response sent to Slack")

    except Exception as e:
        logger.error(f"❌ Error in ask command: {e}")
        logger.error(f"❌ Full error: {str(e)}")
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

        if not ai_analyzer or not config.openai_configured:
            client.chat_postMessage(
                channel=channel_id,
                text="❌ AI analysis is not configured. Please configure OpenAI API key."
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

        if not ai_analyzer or not config.openai_configured:
            client.chat_postMessage(
                channel=channel_id,
                text="❌ AI analysis is not configured. Please configure OpenAI API key."
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

        if not ai_analyzer or not config.openai_configured:
            client.chat_postMessage(
                channel=channel_id,
                text="❌ AI analysis is not configured. Please configure OpenAI API key."
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

        # Reset AI analyzer if available
        if ai_analyzer:
            ai_analyzer.reset_analysis()

        # NEW: Reset market research orchestrator if available  
        if market_research_orchestrator:
            # Future: add reset method when needed
            pass

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

        ai_status = "✅" if (ai_analyzer and config.openai_configured) else "⚠️"
        ai_note = "Full AI analysis available" if (ai_analyzer and config.openai_configured) else "AI analysis requires OpenAI configuration"

        response = "👋 Hi! I'm the DataRoom Intelligence Bot running on Railway.\n\n" +\
                  f"{ai_status} **AI Status:** {ai_note}\n\n" +\
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

@app.event("message")
def handle_message_events(body, client, logger):
    """Handle direct messages and prevent unhandled request warnings"""
    # Ignore messages from bots to prevent loops
    if body.get("event", {}).get("bot_id"):
        return

    # Only respond to direct messages, not channel messages
    event = body.get("event", {})
    if event.get("channel_type") == "im":  # Direct message
        client.chat_postMessage(
            channel=event["channel"],
            text="👋 Hi! Use `/analyze [google-drive-link]` to start analyzing a data room, or mention me with @DataRoom Intelligence Bot for help!"
        )

# ==========================================
# RAILWAY DEPLOYMENT ARCHITECTURE
# ==========================================

def run_slack_bot():
    """Run Slack bot in background thread"""
    try:
        logger.info("🚀 Starting Slack Socket Mode Handler...")
        handler = SocketModeHandler(app, config.SLACK_APP_TOKEN)
        handler.start()
    except Exception as e:
        logger.error(f"❌ Slack bot failed: {e}")

def main():
    """Main application entry point for Railway"""
    try:
        logger.info("🚀 Starting DataRoom Intelligence Bot on Railway...")
        logger.info(f"Environment: {config.ENVIRONMENT}")
        logger.info(f"Debug mode: {config.DEBUG}")
        logger.info(f"Port: {config.PORT}")

        # Validate configuration
        config_status = config.validate_configuration()
        logger.info(f"Configuration status: {config_status}")

        if not config.slack_configured:
            logger.error("❌ Slack configuration missing")
        else:
            logger.info("✅ Slack configured - Bot will start")

        if not config.google_drive_configured:
            logger.error("❌ Google Drive configuration missing")
        else:
            logger.info("✅ Google Drive configured")

        if not config.openai_configured:
            logger.warning("⚠️ OpenAI configuration missing - AI analysis will be disabled")
        else:
            logger.info("✅ OpenAI configured - Full AI analysis available")

        # Start Slack bot in background thread
        if config.slack_configured:
            slack_thread = threading.Thread(target=run_slack_bot, daemon=True)
            slack_thread.start()
            logger.info("✅ Slack bot started in background thread")
        else:
            logger.warning("⚠️ Slack bot not started due to missing configuration")

        # Start Flask server for Railway health checks (MAIN THREAD)
        logger.info(f"🌐 Starting Flask server on {config.HOST}:{config.PORT}...")
        logger.info("📋 Available endpoints:")
        logger.info("   • GET / - Service info")
        logger.info("   • GET /health - Health check (for Railway)")
        logger.info("   • GET /status - Detailed status")
        logger.info("🎯 Slack bot commands:")
        logger.info("   • /analyze [google-drive-link]")
        if config.openai_configured:
            logger.info("   • /ask [question]")
            logger.info("   • /scoring")
            logger.info("   • /memo")
            logger.info("   • /gaps")
        logger.info("   • /reset")
        logger.info("   • /health")
        logger.info("   • Direct messages")
        logger.info("   • @mentions in channels")

        # Run Flask server (blocks main thread)
        flask_app.run(
            host=config.HOST,
            port=config.PORT,
            debug=config.DEBUG
        )

    except KeyboardInterrupt:
        logger.info("🛑 Bot stopped by user")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        raise

if __name__ == "__main__":
    main()
