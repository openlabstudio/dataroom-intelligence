"""
DataRoom Intelligence Bot - Railway-Compatible Version with Phase 2A Market Research
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
from handlers.market_research_handler import MarketResearchHandler  # NEW IMPORT
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
                "temp_storage": config.temp_dir.exists(),
                "market_research": market_research_orchestrator is not None
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
        "version": "2.0.0-production-ready",
        "platform": "Railway",
        "features": ["Document Analysis", "Market Research", "AI Intelligence"],
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
            "configuration_status": config.validate_configuration(),
            "phase": "2B - Market Research Agent (Production Ready)",
            "market_research_available": market_research_orchestrator is not None
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

# Initialize Phase 2A agents
market_research_orchestrator = None
try:
    if config.openai_configured:
        from agents.market_research_orchestrator import MarketResearchOrchestrator
        market_research_orchestrator = MarketResearchOrchestrator()
        logger.info("🔧 Market Research Orchestrator initialized: True")
    else:
        logger.warning("🔧 Market Research Orchestrator initialized: False (OpenAI not configured)")
except Exception as e:
    logger.error(f"❌ Failed to initialize Market Research Orchestrator: {e}")
    market_research_orchestrator = None

# Log initialization status
logger.info(f"🔧 AI Analyzer initialized: {ai_analyzer is not None}")
logger.info(f"🔧 OpenAI configured: {config.openai_configured}")

# Store user sessions (in production, use a database)
user_sessions = {}

# Initialize market research handler (NEW)
market_research_handler = None
if market_research_orchestrator:
    market_research_handler = MarketResearchHandler(market_research_orchestrator, user_sessions)
    logger.info("🔧 Market Research Handler initialized: True")

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
        
        # SPECIAL DEBUG MODE: /analyze debug
        if drive_link.lower() == 'debug':
            return debug_sessions(user_id, channel_id, client)

        # NUEVO: Debug logs para capturar el problema
        logger.info(f"🎯 ANALYZE COMMAND - Starting for user {user_id}")
        logger.info(f"🎯 ANALYZE COMMAND - Channel: {channel_id}")
        logger.info(f"🎯 ANALYZE COMMAND - Drive link: {drive_link}")

        if not drive_link:
            logger.info("🎯 ANALYZE COMMAND - No drive link provided")

        if not drive_link:
            client.chat_postMessage(
                channel=channel_id,
                text="❌ Please provide a Google Drive folder link.\n\nUsage: `/analyze [google-drive-link]`\n\n💡 **Debug tip:** Use `/analyze debug` to check active sessions"
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

def debug_sessions(user_id, channel_id, client):
    """Debug function to check active sessions"""
    logger.info(f"🔍 Debug sessions requested by user {user_id}")
    
    response = "🔍 **DEBUG: ACTIVE SESSIONS & SYSTEM STATUS**\n\n"
    
    # System info
    response += "**🖥️ SYSTEM INFO:**\n"
    response += f"• Process PID: {os.getpid()}\n"
    # Debug shows production mode status
    PRODUCTION_MODE = True
    test_mode_value = 'false (forced)' if PRODUCTION_MODE else os.getenv('TEST_MODE', 'not set')
    test_mode_active = False if PRODUCTION_MODE else os.getenv('TEST_MODE', 'false').lower() == 'true'
    response += f"• TEST_MODE: '{test_mode_value}'\n"
    response += f"• TEST_MODE Active: {'✅' if test_mode_active else '❌ (Production Mode)'}\n"
    response += f"• OpenAI Configured: {'✅' if config.openai_configured else '❌'}\n"
    response += f"• Market Research Available: {'✅' if market_research_orchestrator else '❌'}\n\n"
    
    # Session info
    response += f"**📊 SESSION INFO:**\n"
    response += f"• Total Sessions: {len(user_sessions)}\n"
    response += f"• Active Users: {list(user_sessions.keys()) if user_sessions else 'None'}\n\n"

    if user_id in user_sessions:
        session_data = user_sessions[user_id]
        response += f"**✅ YOUR SESSION (ID: {user_id}):**\n"
        response += f"• Session keys: {list(session_data.keys())}\n"

        if 'processed_documents' in session_data:
            response += f"• Processed documents: {len(session_data['processed_documents'])}\n"

        if 'document_summary' in session_data:
            response += f"• Document summary available: ✅\n"

        if 'analysis_result' in session_data:
            response += f"• Analysis result available: ✅\n"

        if 'market_research' in session_data:
            response += f"• Market research available: ✅\n"
            
        if 'test_mode' in session_data:
            response += f"• Test mode session: ✅\n"
            
        if 'analysis_timestamp' in session_data:
            response += f"• Created at: {session_data['analysis_timestamp']}\n"

        response += "\n✅ **Session is active - commands should work!**"
    else:
        response += f"**❌ YOUR SESSION (ID: {user_id}):** Not found\n"
        response += "\n⚠️ **Please run `/analyze [google-drive-link]` first**"
    
    # Instructions
    response += "\n\n**📚 TROUBLESHOOTING:**\n"
    response += "1. If TEST_MODE is not 'true', set it: `export TEST_MODE=true`\n"
    response += "2. After `/analyze`, your session should appear here\n"
    response += "3. If session disappears, the bot may be restarting\n"
    response += "4. Use `/health` to check overall system status"

    client.chat_postMessage(
        channel=channel_id,
        text=response
    )

def perform_dataroom_analysis(client, channel_id, user_id, drive_link, message_ts):
    """Perform the complete data room analysis with AI"""
    try:
        # PRODUCTION MODE: Force TEST_MODE=false for Railway deployment
        PRODUCTION_MODE = True  # Set to False for local development
        test_mode_check = False if PRODUCTION_MODE else os.getenv('TEST_MODE', 'false').lower() == 'true'
        test_mode_value = 'false (forced)' if PRODUCTION_MODE else os.getenv('TEST_MODE', 'false')
        
        # CRITICAL LOG
        logger.info(f"🔍 ============ ANALYSIS START ============")
        logger.info(f"🔍 User: {user_id}")
        logger.info(f"🔍 Process PID: {os.getpid()}")
        logger.info(f"🔍 TEST_MODE raw value: '{test_mode_value}'")
        logger.info(f"🔍 TEST_MODE check result: {test_mode_check}")
        logger.info(f"🔍 Will skip GPT-4: {'YES ✅' if test_mode_check else 'NO ❌ (WILL USE GPT-4)'}")
        logger.info(f"🔍 ========================================")

        # Step 1: Download documents
        client.chat_update(
            channel=channel_id,
            ts=message_ts,
            text="🔍 **Analysis in Progress**\n\n" +
                 f"📁 Link: {drive_link}\n" +
                 f"📥 **Downloading documents from Google Drive...**" +
                 (f"\n\n⚠️ **TEST MODE ACTIVE** - Will skip GPT-4" if test_mode_check else "")
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
                 f"📖 **Processing document contents...**" +
                 (f"\n\n⚠️ **TEST MODE ACTIVE** - Will skip GPT-4" if test_mode_check else "")
        )

        processed_documents = doc_processor.process_dataroom_documents(downloaded_files)
        document_summary = doc_processor.get_content_summary(processed_documents)

        # CRITICAL FIX: Check TEST_MODE IMMEDIATELY and handle it FIRST
        if test_mode_check:
            logger.info("🧪 ========== TEST MODE ACTIVE ==========")
            logger.info("🧪 Skipping AI analysis completely")
            logger.info("🧪 Creating mock session data")
            
            # Create mock response
            mock_response = "✅ **ANALYSIS COMPLETE (TEST MODE)**\n\n"
            mock_response += "⚠️ **TEST MODE ACTIVE** - No GPT-4 calls made\n\n"
            mock_response += f"📊 **Processing Summary:**\n"
            mock_response += f"• **Documents Processed:** {len(processed_documents)}\n"
            mock_response += f"• **Total Content:** Successfully extracted\n\n"
            mock_response += "🎯 **Available Commands:**\n"
            mock_response += "• `/ask [question]` - Ask questions about documents (TEST MODE)\n"
            mock_response += "• `/scoring` - Get VC scoring (TEST MODE)\n"
            mock_response += "• `/memo` - Generate investment memo (TEST MODE)\n"
            mock_response += "• `/gaps` - Analyze information gaps (TEST MODE)\n"
            mock_response += "• `/market-research` - NEW: Market intelligence (TEST MODE)\n"
            mock_response += "• `/analyze debug` - Check session status\n"
            mock_response += "• `/reset` - Clear session\n"

            client.chat_update(
                channel=channel_id,
                ts=message_ts,
                text=mock_response
            )

            # Store mock session data
            user_sessions[user_id] = {
                'processed_documents': processed_documents,
                'document_summary': document_summary,
                'drive_link': drive_link,
                'test_mode': True,
                'analysis_timestamp': datetime.now().isoformat()
            }
            
            # DEBUG: Log session storage
            logger.info(f"✅ TEST MODE - Session stored for user {user_id}")
            logger.info(f"✅ TEST MODE - Session keys: {list(user_sessions[user_id].keys())}")
            logger.info(f"✅ TEST MODE - Active sessions: {list(user_sessions.keys())}")
            logger.info(f"✅ TEST MODE - Process PID: {os.getpid()}")
            logger.info("🧪 ========== TEST MODE COMPLETE ==========")

            # RETURN HERE - DO NOT CONTINUE TO AI ANALYSIS
            return

        # Step 3: AI Analysis (ONLY if NOT in test mode)
        logger.info("📊 ========== PRODUCTION MODE ==========")
        logger.info("📊 TEST_MODE is not active, proceeding with GPT-4 analysis")
        
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

            # Enhanced response to mention market research
            if market_research_orchestrator:
                formatted_response += "\n\nUse `/market-research` for comprehensive market intelligence analysis."
            

            client.chat_update(
                channel=channel_id,
                ts=message_ts,
                text=formatted_response
            )

            # CRITICAL: Store analysis in user session
            user_sessions[user_id] = {
                'analysis_result': analysis_result,
                'document_summary': document_summary,
                'processed_documents': processed_documents,
                'drive_link': drive_link,
                'analysis_timestamp': datetime.now().isoformat()
            }
            
            # DEBUG: Log session storage
            logger.info(f"✅ PRODUCTION MODE - Session stored for user {user_id}")
            logger.info(f"✅ PRODUCTION MODE - With GPT-4 analysis results")
            logger.info(f"✅ PRODUCTION MODE - Active sessions: {list(user_sessions.keys())}")

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

            # Store documents in user session
            user_sessions[user_id] = {
                'processed_documents': processed_documents,
                'document_summary': document_summary,
                'drive_link': drive_link,
                'analysis_timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"✅ FALLBACK MODE - Session stored for user {user_id}")

        logger.info(f"✅ Analysis completed for user {user_id}")
        logger.info("💾 Session data preserved (temp files NOT cleaned)")

    except Exception as e:
        logger.error(f"❌ Analysis failed: {e}")
        logger.error(f"❌ Full traceback: ", exc_info=True)
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

        if market_research_orchestrator:
            response += "• `/market-research` - NEW: Comprehensive market intelligence\n"
    else:
        response += "🎯 **Status:** Document extraction successful!\n"
        response += "🤖 **Note:** AI analysis requires OpenAI configuration\n\n"

    response += "• `/analyze debug` - Check session status\n"
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

# ==========================================
# PHASE 2B: FIXED MARKET RESEARCH COMMANDS
# ==========================================

@app.command("/market-research")
def handle_market_research_command(ack, body, client):
    """Handle /market-research command - Uses new handler to fix dispatch_failed"""
    logger.info("📨 Received /market-research command")
    logger.info(f"📨 Current active sessions: {list(user_sessions.keys())}")
    logger.info(f"📨 User requesting: {body.get('user_id')}")
    
    if market_research_handler:
        market_research_handler.handle_command(ack, body, client)
    else:
        ack()
        client.chat_postMessage(
            channel=body['channel_id'],
            text="❌ Market research functionality is not available. OpenAI configuration required."
        )

@app.command("/market_research")
def handle_market_research_command_alt(ack, body, client):
    """Handle /market_research command (underscore variant)"""
    logger.info("📨 Received /market_research command (underscore variant)")
    logger.info(f"📨 Current active sessions: {list(user_sessions.keys())}")
    logger.info(f"📨 User requesting: {body.get('user_id')}")
    
    if market_research_handler:
        market_research_handler.handle_command(ack, body, client)
    else:
        ack()
        client.chat_postMessage(
            channel=body['channel_id'],
            text="❌ Market research functionality is not available. OpenAI configuration required."
        )

@app.command("/market")
def handle_market_command_short(ack, body, client):
    """Handle /market command (short variant)"""
    logger.info("📨 Received /market command (short variant)")
    logger.info(f"📨 Current active sessions: {list(user_sessions.keys())}")
    logger.info(f"📨 User requesting: {body.get('user_id')}")
    
    if market_research_handler:
        market_research_handler.handle_command(ack, body, client)
    else:
        ack()
        client.chat_postMessage(
            channel=body['channel_id'],
            text="❌ Market research functionality is not available. OpenAI configuration required."
        )

# ==========================================
# ORIGINAL COMMANDS - ENHANCED FOR PHASE 2A
# ==========================================

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
                text="❌ No data room analysis found. Please run `/analyze [google-drive-link]` first.\n\n💡 **Tip:** Use `/analyze debug` to check your session status."
            )
            return

        # Check if in TEST MODE (forced false in production)
        session_data = user_sessions[user_id]
        PRODUCTION_MODE = True  # Force production mode
        test_mode_active = False if PRODUCTION_MODE else session_data.get('test_mode', False)
        if test_mode_active:
            logger.info("🧪 TEST MODE: Returning mock answer")
            response = f"💡 **Question:** {question}\n\n"
            response += f"**Answer (TEST MODE):**\n"
            response += "This is a test mode response. In production, this would analyze your documents and provide a real answer based on the content.\n\n"
            response += "📎 *TEST MODE - No GPT-4 calls made*"
            
            client.chat_postMessage(
                channel=channel_id,
                text=response
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
                  f"📎 *Based on analyzed data room"

        # Add market research context if available
        if 'market_research' in user_sessions[user_id]:
            response += " and market intelligence analysis"

        response += "*"

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
                text="❌ No data room analysis found. Please run `/analyze [google-drive-link]` first.\n\n💡 **Tip:** Use `/analyze debug` to check your session status."
            )
            return

        # Check if in TEST MODE (forced false in production)
        session_data = user_sessions[user_id]
        PRODUCTION_MODE = True  # Force production mode
        test_mode_active = False if PRODUCTION_MODE else session_data.get('test_mode', False)
        if test_mode_active:
            logger.info("🧪 TEST MODE: Returning mock scoring")
            response = "📊 **DETAILED SCORING BREAKDOWN (TEST MODE)**\n\n"
            response += "🎯 **Overall Score: 7.5/10** (Mock)\n\n"
            response += "**Category Scores:**\n"
            response += "• **Market Opportunity:** 8/10 - Strong market potential\n"
            response += "• **Team:** 7/10 - Experienced founders\n"
            response += "• **Product:** 7/10 - MVP ready\n"
            response += "• **Traction:** 6/10 - Early stage\n\n"
            response += "🎯 **Recommendation:** Proceed with due diligence\n\n"
            response += "📎 *TEST MODE - No GPT-4 calls made*"
            
            client.chat_postMessage(
                channel=channel_id,
                text=response
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

        # Add market research note if available
        if 'market_research' in user_sessions[user_id]:
            response += "\n📊 **Market Intelligence:** Market research data available\n"
            response += "Use `/ask` to query market-specific insights."

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
                text="❌ No data room analysis found. Please run `/analyze [google-drive-link]` first.\n\n💡 **Tip:** Use `/analyze debug` to check your session status."
            )
            return

        # Check if in TEST MODE (forced false in production)
        session_data = user_sessions[user_id]
        PRODUCTION_MODE = True  # Force production mode
        test_mode_active = False if PRODUCTION_MODE else session_data.get('test_mode', False)
        if test_mode_active:
            logger.info("🧪 TEST MODE: Returning mock memo")
            response = "📄 **INVESTMENT MEMO (TEST MODE)**\n\n"
            response += "**Executive Summary:**\n"
            response += "This is a test mode investment memo. In production, this would provide a comprehensive analysis of the investment opportunity.\n\n"
            response += "**Key Points:**\n"
            response += "• Strong market opportunity\n"
            response += "• Experienced team\n"
            response += "• Clear revenue model\n"
            response += "• Competitive advantages\n\n"
            response += "📎 *TEST MODE - No GPT-4 calls made*"
            
            client.chat_postMessage(
                channel=channel_id,
                text=response
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

        # Add market research note if available
        if 'market_research' in user_sessions[user_id]:
            response += "\n\n📊 **Market Intelligence Integrated**\n"
            response += "This memo includes market research insights."

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
                text="❌ No data room analysis found. Please run `/analyze [google-drive-link]` first.\n\n💡 **Tip:** Use `/analyze debug` to check your session status."
            )
            return

        # Check if in TEST MODE (forced false in production)
        session_data = user_sessions[user_id]
        PRODUCTION_MODE = True  # Force production mode
        test_mode_active = False if PRODUCTION_MODE else session_data.get('test_mode', False)
        if test_mode_active:
            logger.info("🧪 TEST MODE: Returning mock gaps analysis")
            response = "🔍 **INFORMATION GAPS ANALYSIS (TEST MODE)**\n\n"
            response += "**Missing Information:**\n"
            response += "• Financial projections for next 3 years\n"
            response += "• Customer acquisition cost details\n"
            response += "• Competitive analysis depth\n"
            response += "• Technical architecture documentation\n\n"
            response += "**Recommendations:**\n"
            response += "• Request detailed financial model\n"
            response += "• Ask for unit economics breakdown\n\n"
            response += "📎 *TEST MODE - No GPT-4 calls made*"
            
            client.chat_postMessage(
                channel=channel_id,
                text=response
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

        # Add market research note if available
        if 'market_research' in user_sessions[user_id]:
            response += "\n\n📊 **Market Research Recommendation**\n"
            response += "Consider market intelligence data for deeper gap analysis."

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

        # Reset market research orchestrator if available
        if market_research_orchestrator:
            # Market research orchestrator reset (placeholder)
            pass

        # FIX #2: NOW is the right time to cleanup temp files
        if drive_handler:
            drive_handler.cleanup_temp_files()
            logger.info("🗑️ Cleaned up temporary files in /reset command")

        client.chat_postMessage(
            channel=channel_id,
            text="🔄 **Session Reset Complete**\n\n" +
                 "✅ Analysis context cleared\n" +
                 "✅ Market research data cleared\n" +
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
        user_id = body['user_id']
        
        health_response = format_health_response()

        # Add Phase 2A status
        health_response += f"\n🔬 **Phase 2B Status (Production Ready):**\n"
        health_response += f"• Market Research Orchestrator: {'✅' if market_research_orchestrator else '❌'}\n"
        health_response += f"• Market Research Handler: {'✅' if market_research_handler else '❌'}\n"
        health_response += f"• Active Sessions: {len(user_sessions)}\n"
        health_response += f"• Your Session: {'✅ Active' if user_id in user_sessions else '❌ Not found'}\n"
        
        # Show TEST_MODE status (forced in production)
        PRODUCTION_MODE = True
        test_mode_value = 'false (forced)' if PRODUCTION_MODE else os.getenv('TEST_MODE', 'false')
        test_mode_active = False if PRODUCTION_MODE else test_mode_value.lower() == 'true'
        health_response += f"• TEST_MODE: '{test_mode_value}' ({'✅ Active' if test_mode_active else '❌ Inactive (Production)'})\n"
        
        health_response += f"• Available Commands: `/analyze`, `/market-research`, `/ask`, `/scoring`, `/memo`, `/gaps`, `/reset`\n\n"
        health_response += "💡 **Tip:** Use `/analyze debug` to check detailed session info"

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

        market_status = "✅" if market_research_orchestrator else "⚠️"
        market_note = "Market research available (fixed)" if market_research_orchestrator else "Market research requires OpenAI configuration"
        
        # Check TEST_MODE (forced in production)
        PRODUCTION_MODE = True
        test_mode_value = 'false (forced)' if PRODUCTION_MODE else os.getenv('TEST_MODE', 'false')
        test_mode_active = False if PRODUCTION_MODE else test_mode_value.lower() == 'true'
        test_mode_status = f"TEST MODE: {'✅ ACTIVE' if test_mode_active else '❌ INACTIVE (Production)'}"

        response = "👋 Hi! I'm the DataRoom Intelligence Bot running on Railway with Phase 2B Market Research (Production Ready).\n\n" +\
                  f"{ai_status} **AI Status:** {ai_note}\n" +\
                  f"{market_status} **Market Research:** {market_note}\n" +\
                  f"🧪 **{test_mode_status}**\n\n" +\
                  "**Available commands:**\n" +\
                  "• `/analyze [google-drive-link]` - Analyze a data room\n" +\
                  "• `/analyze debug` - Check session status (NEW!)\n" +\
                  "• `/market-research` - NEW: Comprehensive market intelligence (FIXED)\n" +\
                  "• `/ask [question]` - Ask questions about analyzed data room\n" +\
                  "• `/scoring` - Get detailed scoring breakdown\n" +\
                  "• `/memo` - Generate investment memo\n" +\
                  "• `/gaps` - Analyze missing information\n" +\
                  "• `/reset` - Reset current session\n" +\
                  "• `/health` - Check system status\n\n" +\
                  "Start by analyzing a data room with `/analyze`, then use `/market-research` for market intelligence!"

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
            text="👋 Hi! Use `/analyze [google-drive-link]` to start analyzing a data room, then `/market-research` for market intelligence, or mention me with @DataRoom Intelligence Bot for help!\n\n💡 **New:** Use `/analyze debug` to check your session status!"
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
        logger.info("🔬 Phase 2B: Market Research Agent (Production Ready)")
        logger.info(f"Environment: {config.ENVIRONMENT}")
        logger.info(f"Debug mode: {config.DEBUG}")
        logger.info(f"Port: {config.PORT}")
        logger.info(f"Process PID: {os.getpid()}")
        
        # LOG TEST_MODE STATUS AT STARTUP (forced in production)
        PRODUCTION_MODE = True  # Force production mode for Railway deployment
        test_mode_value = 'false (forced)' if PRODUCTION_MODE else os.getenv('TEST_MODE', 'false')
        test_mode_active = False if PRODUCTION_MODE else os.getenv('TEST_MODE', 'false').lower() == 'true'
        logger.info(f"🔧 PRODUCTION_MODE: {'✅ ENABLED - Forcing TEST_MODE=false' if PRODUCTION_MODE else '❌ DISABLED - Using env var'}")
        logger.info(f"🔧 TEST_MODE environment variable: '{test_mode_value}'")
        logger.info(f"🔧 TEST_MODE is active: {'✅ YES - Will skip GPT-4 calls' if test_mode_active else '❌ NO - Will use GPT-4 ($$$ Production costs)'}")

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

        logger.info(f"🔧 Market Research Orchestrator: {'✅' if market_research_orchestrator else '❌'}")
        logger.info(f"🔧 Market Research Handler: {'✅' if market_research_handler else '❌'}")

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
        logger.info("   • /analyze debug - Check session status (NEW!)")
        if market_research_orchestrator:
            logger.info("   • /market-research - NEW: Market intelligence (FIXED)")
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
            debug=False
        )

    except KeyboardInterrupt:
        logger.info("🛑 Bot stopped by user")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        raise

if __name__ == "__main__":
    main()
