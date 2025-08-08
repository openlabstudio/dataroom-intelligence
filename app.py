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
        "version": "2.0.0-phase2a",
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
            "phase": "2A - Market Research Agent",
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

        # NUEVO: Debug logs para capturar el problema
        logger.info(f"🎯 ANALYZE COMMAND - Starting for user {user_id}")
        logger.info(f"🎯 ANALYZE COMMAND - Channel: {channel_id}")
        logger.info(f"🎯 ANALYZE COMMAND - Drive link: {drive_link}")

        if not drive_link:
            logger.info("🎯 ANALYZE COMMAND - No drive link provided")

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
        # NUEVO: Debug logs para diagnosticar el problema
        import os
        test_mode_value = os.getenv('TEST_MODE', 'false')
        logger.info(f"🔍 DEBUG - Starting analysis for user {user_id}")
        logger.info(f"🔍 DEBUG - TEST_MODE environment variable: '{test_mode_value}'")
        logger.info(f"🔍 DEBUG - TEST_MODE lower: '{test_mode_value.lower()}'")
        logger.info(f"🔍 DEBUG - Condition result: {test_mode_value.lower() == 'true'}")

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

# Check for test mode - skip expensive AI analysis
        import os
        if os.getenv('TEST_MODE', 'false').lower() == 'true':
            test_mode_check = os.getenv('TEST_MODE', 'false').lower() == 'true'
            logger.info(f"🔍 DEBUG - Second TEST_MODE check: {test_mode_check}")

        if test_mode_check:
            logger.info("🧪 TEST MODE: Skipping AI analysis, using mock session data")
            # Create mock response
            mock_response = "✅ **ANALYSIS COMPLETE (TEST MODE)**\n\n"
            mock_response += f"📊 **Processing Summary:**\n"
            mock_response += f"• **Documents Processed:** {len(processed_documents)}\n"
            mock_response += f"• **Total Content:** Successfully extracted\n\n"
            mock_response += "🎯 **Available Commands:**\n"
            mock_response += "• `/ask [question]` - Ask questions about documents\n"
            mock_response += "• `/scoring` - Get VC scoring\n"
            mock_response += "• `/memo` - Generate investment memo\n"
            mock_response += "• `/gaps` - Analyze information gaps\n"
            mock_response += "• `/market-research` - NEW: Market intelligence (TEST)\n"
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
                'test_mode': True
            }

            logger.info(f"✅ Analysis completed (TEST MODE) for user {user_id}")
            return

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

            # Enhanced response to mention market research
            if market_research_orchestrator:
                formatted_response += "\n\n🎯 **NEW: Market Research Available!**\n"
                formatted_response += "Use `/market-research` for comprehensive market intelligence analysis."

            client.chat_update(
                channel=channel_id,
                ts=message_ts,
                text=formatted_response
            )

            # CRITICAL: Store analysis in user session BEFORE cleanup
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

            # CRITICAL: Store documents in user session BEFORE cleanup
            user_sessions[user_id] = {
                'processed_documents': processed_documents,
                'document_summary': document_summary,
                'drive_link': drive_link
            }

        # AI analysis completed successfully
        logger.info("✅ AI analysis completed successfully")

        # CRITICAL: Cleanup temporary files AFTER session storage
        drive_handler.cleanup_temp_files()
        logger.info("🗑️ Cleaned up temporary files")
        logger.info("💾 Freed temp storage: ./temp")

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

        if market_research_orchestrator:
            response += "• `/market-research` - NEW: Comprehensive market intelligence\n"
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

# ==========================================
# PHASE 2A: MARKET RESEARCH COMMANDS
# ==========================================

@app.command("/market-research")
def handle_market_research_command(ack, body, client):
    """Handle /market-research command - Comprehensive market intelligence analysis"""
    logger.info("📨 Received /market-research command")
    handle_market_research_logic(ack, body, client)

@app.command("/market_research")
def handle_market_research_command_alt(ack, body, client):
    """Handle /market_research command (underscore variant)"""
    logger.info("📨 Received /market_research command (underscore variant)")
    handle_market_research_logic(ack, body, client)

def handle_market_research_logic(ack, body, client):
    """Core logic for market research command"""
    ack()

    try:
        user_id = body['user_id']
        channel_id = body['channel_id']

        logger.info(f"🔍 Starting market research analysis for user {user_id}")

        # Check if market research orchestrator is available
        if not market_research_orchestrator:
            client.chat_postMessage(
                channel=channel_id,
                text="❌ Market research functionality is not available. OpenAI configuration required."
            )
            return

        # Check if user has analyzed documents
        if user_id not in user_sessions:
            logger.info(f"❌ No session found for user {user_id}")
            logger.info(f"📊 Active sessions: {list(user_sessions.keys())}")
            client.chat_postMessage(
                channel=channel_id,
                text="❌ No data room analysis found.\n\n" +
                     "Please run `/analyze [google-drive-link]` first to analyze documents, " +
                     "then use `/market-research` for market intelligence analysis."
            )
            return

        session_data = user_sessions[user_id]

        # Validate session has required data
        if 'processed_documents' not in session_data or 'document_summary' not in session_data:
            logger.error(f"❌ Session data incomplete for user {user_id}")
            client.chat_postMessage(
                channel=channel_id,
                text="❌ Session data incomplete. Please run `/analyze [google-drive-link]` again."
            )
            return

        # Send initial response
        initial_response = client.chat_postMessage(
            channel=channel_id,
            text="🔍 **Análisis de Mercado Iniciado**\n\n" +
                 "📊 Preparando análisis de inteligencia de mercado...\n" +
                 "⏳ Este proceso puede tomar 3-5 minutos\n\n" +
                 "🚧 **Estado:** Inicializando agentes de análisis..."
        )
        # NUEVO: Log antes del thread
        logger.info("🎯 ANALYZE COMMAND - About to start background thread")
        # Start background market research analysis
        threading.Thread(
            target=perform_market_research_analysis,
            args=(client, channel_id, user_id, initial_response['ts']),
            daemon=True
        ).start()

        logger.info("🎯 ANALYZE COMMAND - Background thread started successfully")


    except Exception as e:
        logger.error(f"❌ Error in market research command: {e}")
        client.chat_postMessage(
            channel=channel_id,
            text=f"❌ Error en análisis de mercado: {str(e)}"
        )

def perform_market_research_analysis(client, channel_id, user_id, message_ts):
    """Perform comprehensive market research analysis"""
    try:
        # Get user session data
        session_data = user_sessions[user_id]
        processed_documents = session_data['processed_documents']
        document_summary = session_data['document_summary']

        logger.info(f"🔍 Starting market intelligence analysis for user {user_id}")

        # Step 1: Market Detection
        client.chat_update(
            channel=channel_id,
            ts=message_ts,
            text="🔍 **Análisis de Mercado en Progreso**\n\n" +
                 "📊 **Paso 1/4:** Detectando vertical de mercado...\n" +
                 "🎯 Analizando documentos para identificar sector\n" +
                 "⏳ Estado: Procesando con IA..."
        )

        # Step 2: Competitive Analysis (placeholder)
        client.chat_update(
            channel=channel_id,
            ts=message_ts,
            text="🔍 **Análisis de Mercado en Progreso**\n\n" +
                 "📊 **Paso 2/4:** Análisis competitivo...\n" +
                 "🏢 Identificando competidores y posicionamiento\n" +
                 "⏳ Estado: Procesando datos de mercado..."
        )

        # Step 3: Market Validation (placeholder)
        client.chat_update(
            channel=channel_id,
            ts=message_ts,
            text="🔍 **Análisis de Mercado en Progreso**\n\n" +
                 "📊 **Paso 3/4:** Validación de mercado...\n" +
                 "📈 Validando TAM/SAM y oportunidades\n" +
                 "⏳ Estado: Analizando datos externos..."
        )

        # Step 4: Critical Assessment
        client.chat_update(
            channel=channel_id,
            ts=message_ts,
            text="🔍 **Análisis de Mercado en Progreso**\n\n" +
                 "📊 **Paso 4/4:** Evaluación crítica...\n" +
                 "🧠 Generando análisis crítico con \"brutal honesty\"\n" +
                 "⏳ Estado: Finalizando análisis..."
        )

        # Perform actual market intelligence analysis
        market_intelligence_result = market_research_orchestrator.perform_market_intelligence(
            processed_documents, document_summary
        )

        # Format compact response for Slack character limits
        response = format_compact_market_research_response(market_intelligence_result)

        # Update Slack with final results
        client.chat_update(
            channel=channel_id,
            ts=message_ts,
            text=response
        )

        # CRITICAL FIX: Store market research results in user session BEFORE any cleanup
        user_sessions[user_id]['market_research'] = {
            'result': market_intelligence_result,
            'timestamp': datetime.now().isoformat(),
            'analysis_type': 'comprehensive_market_intelligence'
        }

        logger.info("✅ AI analysis completed successfully")

        # CRITICAL: NO cleanup here - documents must remain for subsequent commands
        # The cleanup will be handled by the reset command or session expiry
        # drive_handler.cleanup_temp_files()  # REMOVED TO PREVENT SESSION LOSS

        logger.info(f"✅ Market research analysis completed for user {user_id}")

    except Exception as e:
        logger.error(f"❌ Market research analysis failed: {e}")
        client.chat_update(
            channel=channel_id,
            ts=message_ts,
            text=f"❌ **Error en Análisis de Mercado**\n\n" +
                 f"Error: {str(e)}\n\n" +
                 f"Por favor, intenta nuevamente o contacta al administrador."
        )

# Also register a short variant
@app.command("/market")
def handle_market_command_short(ack, body, client):
    """Handle /market command (short variant)"""
    logger.info("📨 Received /market command (short variant)")
    handle_market_research_logic(ack, body, client)

# Debug command to check sessions
@app.command("/debug-sessions")
def handle_debug_sessions_command(ack, body, client):
    """Handle /debug-sessions command - Check active sessions"""
    ack()

    try:
        user_id = body['user_id']
        channel_id = body['channel_id']

        logger.info(f"🔍 Debug sessions command from user {user_id}")

        response = "🔍 **DEBUG: ACTIVE SESSIONS**\n\n"
        response += f"**Total Sessions:** {len(user_sessions)}\n"
        response += f"**Active Users:** {list(user_sessions.keys())}\n\n"

        if user_id in user_sessions:
            session_data = user_sessions[user_id]
            response += f"**Your Session (ID: {user_id}):**\n"
            response += f"• Session keys: {list(session_data.keys())}\n"

            if 'processed_documents' in session_data:
                response += f"• Processed documents: {len(session_data['processed_documents'])}\n"

            if 'document_summary' in session_data:
                response += f"• Document summary available: ✅\n"

            if 'analysis_result' in session_data:
                response += f"• Analysis result available: ✅\n"

            if 'market_research' in session_data:
                response += f"• Market research available: ✅\n"

            response += "\n✅ **Market research should work!**"
        else:
            response += f"**Your Session (ID: {user_id}):** ❌ Not found\n"
            response += "\n⚠️ **Please run `/analyze [link]` first**"

        client.chat_postMessage(
            channel=channel_id,
            text=response
        )

    except Exception as e:
        logger.error(f"❌ Error in debug-sessions command: {e}")
        client.chat_postMessage(
            channel=channel_id,
            text=f"❌ Debug error: {str(e)}"
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

        # Cleanup temp files
        if drive_handler:
            drive_handler.cleanup_temp_files()

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
        health_response = format_health_response()

        # Add Phase 2A status
        health_response += f"\n🔬 **Phase 2A Status:**\n"
        health_response += f"• Market Research Orchestrator: {'✅' if market_research_orchestrator else '❌'}\n"
        health_response += f"• Active Sessions: {len(user_sessions)}\n"
        health_response += f"• Available Commands: `/analyze`, `/market-research`, `/ask`, `/scoring`, `/memo`, `/gaps`, `/reset`"

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
        market_note = "Market research available" if market_research_orchestrator else "Market research requires OpenAI configuration"

        response = "👋 Hi! I'm the DataRoom Intelligence Bot running on Railway with Phase 2A Market Research.\n\n" +\
                  f"{ai_status} **AI Status:** {ai_note}\n" +\
                  f"{market_status} **Market Research:** {market_note}\n\n" +\
                  "**Available commands:**\n" +\
                  "• `/analyze [google-drive-link]` - Analyze a data room\n" +\
                  "• `/market-research` - NEW: Comprehensive market intelligence\n" +\
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
            text="👋 Hi! Use `/analyze [google-drive-link]` to start analyzing a data room, then `/market-research` for market intelligence, or mention me with @DataRoom Intelligence Bot for help!"
        )

def format_compact_market_research_response(market_intelligence_result):
    """Format compact market research response to stay within Slack limits"""
    response = "✅ **ANÁLISIS DE MERCADO COMPLETADO**\n\n"

    # Market Profile - Compact format
    if hasattr(market_intelligence_result, 'market_profile') and market_intelligence_result.market_profile:
        profile = market_intelligence_result.market_profile
        primary_vertical = getattr(profile, 'primary_vertical', 'No identificado')
        sub_vertical = getattr(profile, 'sub_vertical', '')
        confidence = getattr(profile, 'confidence_score', 0)
        target_market = getattr(profile, 'target_market', 'No identificado')
        geographic_focus = getattr(profile, 'geographic_focus', 'No identificado')
        business_model = getattr(profile, 'business_model', 'No identificado')

        # Compact market profile
        vertical_display = f"{primary_vertical}/{sub_vertical}" if sub_vertical else primary_vertical
        response += f"🎯 **PERFIL** ({'🟢' if confidence > 0.8 else '🟡' if confidence > 0.6 else '🔴'} {confidence:.1f} confianza)\n"
        response += f"• **Vertical:** {vertical_display}\n"
        response += f"• **Target:** {target_market[:60]}{'...' if len(target_market) > 60 else ''}\n"
        response += f"• **Geo:** {geographic_focus[:30]}{'...' if len(geographic_focus) > 30 else ''}\n"
        response += f"• **Modelo:** {business_model[:40]}{'...' if len(business_model) > 40 else ''}\n\n"

    # Critical Assessment - Better formatting with complete thoughts
    if hasattr(market_intelligence_result, 'critical_assessment') and market_intelligence_result.critical_assessment:
        assessment = market_intelligence_result.critical_assessment

        # Handle different data types
        if isinstance(assessment, dict):
            # Extract meaningful content from dictionary
            meaningful_points = []
            for key, value in assessment.items():
                if isinstance(value, str) and len(value) > 50:
                    clean_text = value.replace('"', '').replace("'", "").strip()
                    # Find a good stopping point (end of sentence)
                    if len(clean_text) > 400:
                        # Try to cut at end of sentence
                        cut_point = clean_text.find('.', 300)
                        if cut_point > 300:
                            clean_text = clean_text[:cut_point + 1]
                        else:
                            clean_text = clean_text[:400] + "..."
                    meaningful_points.append(clean_text)
                    if len(meaningful_points) >= 2:
                        break

            if meaningful_points:
                response += "🔍 **EVALUACIÓN CRÍTICA:**\n\n"
                for i, point in enumerate(meaningful_points):
                    emoji = "⚠️" if i == 0 else "💡"
                    response += f"{emoji} **Punto {i+1}:** {point}\n\n"
        else:
            # Handle string format
            assessment_text = str(assessment)
            # Try to split into meaningful sentences
            sentences = assessment_text.replace('.', '.|').split('|')
            good_sentences = []

            current_length = 0
            for sentence in sentences:
                sentence = sentence.strip()
                if sentence and len(sentence) > 30 and current_length + len(sentence) < 800:
                    good_sentences.append(sentence)
                    current_length += len(sentence)
                    if len(good_sentences) >= 3:  # Max 3 sentences
                        break

            if good_sentences:
                response += "🔍 **EVALUACIÓN CRÍTICA:**\n\n"
                combined_text = '. '.join(good_sentences)
                if not combined_text.endswith('.'):
                    combined_text += '.'
                response += f"⚠️ {combined_text}\n\n"

    # Available commands
    response += "📋 **COMANDOS DISPONIBLES:**\n"
    response += "• `/market-critical` - Evaluación detallada\n"
    response += "• `/market-full` - Informe completo PDF\n"
    response += "• `/ask [pregunta]` - Consultas específicas\n"
    response += "• `/scoring` - Puntuación detallada"

    return response

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
        logger.info("🔬 Phase 2A: Market Research Agent")
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

        logger.info(f"🔧 Market Research Orchestrator: {'✅' if market_research_orchestrator else '❌'}")

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
        if market_research_orchestrator:
            logger.info("   • /market-research - NEW: Market intelligence")
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
