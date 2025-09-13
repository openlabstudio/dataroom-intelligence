"""
DataRoom Intelligence Bot - Railway Production Deployment
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

# Initialize logger first
logger = get_logger(__name__)

# NEW: Vision processing integration (with graceful fallback)
try:
    from handlers.vision_integration_coordinator import vision_integration_coordinator
    vision_integration_available = True
    logger.info("✅ Vision integration coordinator loaded successfully")
except ImportError as e:
    logger.warning(f"⚠️ Vision integration not available: {e}")
    logger.warning("💡 Vision processing will be disabled - install vision dependencies to enable")
    vision_integration_coordinator = None
    vision_integration_available = False
except Exception as e:
    logger.error(f"❌ Vision integration failed to load: {e}")
    vision_integration_coordinator = None
    vision_integration_available = False

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
                "market_research": market_research_orchestrator is not None,
                "vision_integration": vision_integration_available
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
    # CRITICAL: Acknowledge immediately to prevent dispatch_failed
    try:
        ack()
        logger.info("✅ Command acknowledged successfully")
    except Exception as e:
        logger.error(f"❌ Failed to acknowledge command: {e}")
        return
    
    # IMMEDIATE: Send progress message before ANY complex processing
    try:
        channel_id = body['channel_id']
        client.chat_postMessage(
            channel=channel_id,
            text="🔍 **Analysis Request Received**\n\n⏳ Processing your data room analysis request..."
        )
    except:
        pass  # Don't fail if progress message fails

    # DEFERRED: All complex processing after immediate response
    try:
        user_id = body['user_id']
        channel_id = body['channel_id']
        drive_link = body.get('text', '').strip()
        
        # SPECIAL DEBUG MODE: /analyze debug
        if drive_link.lower() == 'debug':
            return debug_sessions(user_id, channel_id, client)

        # Debug logs after immediate acknowledgment
        logger.info(f"🎯 ANALYZE COMMAND - Starting for user {user_id}")
        logger.info(f"🎯 ANALYZE COMMAND - Channel: {channel_id}")
        logger.info(f"🎯 ANALYZE COMMAND - Drive link: {drive_link}")

        if not drive_link:
            logger.info("🎯 ANALYZE COMMAND - No drive link provided")
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

        # Send detailed initial response with drive link
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
            
        # NEW: Vision processing status
        if 'vision_analysis' in session_data and session_data['vision_analysis']:
            response += f"• Vision processing available: ✅\n"
            processing_metadata = session_data['vision_analysis'].get('processing_summary', {})
            pages_analyzed = processing_metadata.get('total_pages_analyzed', 0)
            if pages_analyzed > 0:
                response += f"• Pages analyzed with GPT Vision: {pages_analyzed}\n"
        else:
            response += f"• Vision processing available: ❌\n"

        if 'extraction_metadata' in session_data:
            metadata = session_data['extraction_metadata']
            response += f"• Hybrid processing used: {'✅' if metadata.get('hybrid_processing_used', False) else '❌'}\n"
            
        if 'analysis_timestamp' in session_data:
            response += f"• Created at: {session_data['analysis_timestamp']}\n"

        response += "\n✅ **Session is active - commands should work!**"
    else:
        response += f"**❌ YOUR SESSION (ID: {user_id}):** Not found\n"
        response += "\n⚠️ **Please run `/analyze [google-drive-link]` first**"
    
    # Instructions
    response += "\n\n**📚 TROUBLESHOOTING:**\n"
    response += "1. Run `/analyze [google-drive-link]` to start analysis\n"
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
        logger.info(f"🔍 ============ ANALYSIS START ============")
        logger.info(f"🔍 User: {user_id}")
        logger.info(f"🔍 Process PID: {os.getpid()}")
        logger.info(f"🔍 ========================================")

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

        # Step 3: AI Analysis
        logger.info("📊 Proceeding with GPT-5 analysis")
        
        if ai_analyzer and config.openai_configured:
            client.chat_update(
                channel=channel_id,
                ts=message_ts,
                text="🔍 **Analysis in Progress**\n\n" +
                     f"📄 Processed {document_summary['successful_processing']} documents\n" +
                     f"🧠 **Analyzing with AI (GPT-5)...**"
            )

            analysis_result = ai_analyzer.analyze_dataroom(processed_documents, document_summary)

            # Get market taxonomy for context (minimal cost - ~$0.01)
            market_profile = None
            if market_research_orchestrator:
                try:
                    market_profile = market_research_orchestrator.market_detector.detect_vertical(
                        processed_documents, document_summary
                    )
                    logger.info(f"✅ Market taxonomy detected: {market_profile.vertical}/{market_profile.sub_vertical}")
                except Exception as e:
                    logger.warning(f"⚠️ Market taxonomy detection failed: {e}")

            # Format and send AI analysis response with market taxonomy
            formatted_response = format_analysis_response(analysis_result, document_summary, market_profile)

            # Enhanced response to mention market research
            if market_research_orchestrator:
                formatted_response += "\n\nUse `/market-research` for comprehensive market intelligence analysis."

            # CRITICAL: Create basic session data for vision processing
            basic_session_data = {
                'analysis_result': analysis_result,
                'document_summary': document_summary,
                'processed_documents': processed_documents,
                'drive_link': drive_link,
                'market_profile': market_profile,  # Store for /market-research
                'analysis_timestamp': datetime.now().isoformat()
            }

            # NEW: Vision processing integration (BEFORE showing final response)
            final_session_data = basic_session_data  # Default fallback
            vision_status_message = ""
            
            try:
                # Find PDF files for vision processing
                pdf_files = [f for f in downloaded_files if f.get('mime_type') == 'application/pdf']
                
                if pdf_files and config.openai_configured and vision_integration_available:
                    # Process first PDF with vision (can be extended for multiple PDFs)
                    pdf_path = pdf_files[0]['path']
                    logger.info(f"🔍 Starting vision processing for: {pdf_files[0]['name']}")
                    
                    # Update progress with processing message
                    client.chat_update(
                        channel=channel_id,
                        ts=message_ts,
                        text="🔍 **Analysis in Progress**\n\n" +
                             f"📄 Found {len(downloaded_files)} documents\n" +
                             f"📊 AI analysis complete\n" +
                             f"🔍 **Processing visual elements...** ({len(pdf_files)} PDF files detected)"
                    )
                    
                    # Process with vision integration coordinator (with timeout protection)
                    try:
                        enhanced_session, vision_results = vision_integration_coordinator.process_document_with_vision(
                            pdf_path, user_id, basic_session_data
                        )
                        
                        # Use enhanced session as final session
                        final_session_data = enhanced_session
                        
                        if vision_results and vision_results.get('processing_metadata'):
                            pages_analyzed = vision_results['processing_metadata'].get('total_pages_analyzed', 0)
                            if pages_analyzed > 0:
                                logger.info(f"✅ Vision processing completed: {pages_analyzed} pages analyzed")
                                vision_status_message = f"\n\n✅ **Vision Enhanced:** {pages_analyzed} pages analyzed with GPT Vision"
                            else:
                                logger.info("📄 Vision processing: No visual elements required analysis")
                                vision_status_message = "\n\n📄 **Text Analysis:** No visual processing required"
                        else:
                            logger.info("📄 Vision processing: Text-only analysis sufficient")
                            vision_status_message = "\n\n📄 **Text-Only Analysis:** Visual processing not needed"
                            
                    except Exception as vision_error:
                        logger.error(f"❌ Vision processing failed: {vision_error}")
                        vision_status_message = "\n\n⚠️ **Note:** Vision processing unavailable, using text-only analysis"
                        # Keep basic session data as fallback
                        
                elif vision_integration_available and pdf_files:
                    # Create enhanced session even without vision processing for consistency
                    try:
                        enhanced_session, _ = vision_integration_coordinator.process_document_with_vision(
                            None, user_id, basic_session_data
                        )
                        final_session_data = enhanced_session
                        logger.info("📄 Enhanced session created without vision processing")
                        vision_status_message = "\n\n📄 **Text-Only Analysis:** Vision processing not needed"
                    except Exception as e:
                        logger.error(f"❌ Enhanced session creation failed: {e}")
                        vision_status_message = "\n\n⚠️ **Note:** Using basic text analysis"
                        
                else:
                    # No PDFs, OpenAI not configured, or vision not available - use basic session
                    if not pdf_files:
                        logger.info("📄 No PDF files found - vision processing skipped")
                        vision_status_message = "\n\n📄 **Document Analysis:** Non-PDF documents processed"
                    elif not config.openai_configured:
                        logger.info("🔧 OpenAI not configured - vision processing disabled")
                        vision_status_message = "\n\n🔧 **Configuration:** Vision processing disabled"
                    elif not vision_integration_available:
                        logger.info("🔧 Vision integration not available - using text-only processing")
                        vision_status_message = "\n\n📄 **Text-Only Mode:** Vision integration unavailable"
                        
            except Exception as e:
                logger.error(f"❌ Vision processing pipeline failed: {e}")
                vision_status_message = "\n\n⚠️ **Note:** Vision processing error, using text-only analysis"
                # final_session_data already defaults to basic_session_data
            
            # Store the final session data (enhanced or basic)
            user_sessions[user_id] = final_session_data
            
            # Show final response with vision status
            final_response = formatted_response + vision_status_message
            client.chat_update(
                channel=channel_id,
                ts=message_ts,
                text=final_response
            )
            
            # DEBUG: Log session storage
            logger.info(f"✅ PRODUCTION MODE - Session stored for user {user_id}")
            logger.info(f"✅ PRODUCTION MODE - With GPT-5 analysis results")
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

            # Store documents in user session (fallback mode - no AI/vision processing)
            basic_session_data = {
                'processed_documents': processed_documents,
                'document_summary': document_summary,
                'drive_link': drive_link,
                'analysis_timestamp': datetime.now().isoformat()
            }
            
            # Create enhanced session even in fallback mode (for consistency)
            if vision_integration_available:
                try:
                    enhanced_session, _ = vision_integration_coordinator.process_document_with_vision(
                        None, user_id, basic_session_data  # No PDF path in fallback mode
                    )
                    user_sessions[user_id] = enhanced_session
                    logger.info(f"✅ Enhanced session created in fallback mode for user {user_id}")
                except Exception as e:
                    logger.error(f"❌ Enhanced session creation failed in fallback: {e}")
                    # Final fallback - use basic session
                    user_sessions[user_id] = basic_session_data
            else:
                # Vision integration not available - use basic session
                user_sessions[user_id] = basic_session_data
                logger.info("📄 Using basic session (vision integration not available)")
            
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
    """Handle /market-research command - CRITICAL: ack() immediately to prevent dispatch_failed"""
    # CRITICAL: Acknowledge IMMEDIATELY before any other processing
    try:
        ack()
        logger.info("✅ /market-research command acknowledged successfully")
    except Exception as e:
        logger.error(f"❌ CRITICAL: Failed to acknowledge /market-research command: {e}")
        return

    # Log after acknowledgment
    logger.info("📨 Processing /market-research command")
    logger.info(f"📨 Current active sessions: {list(user_sessions.keys())}")
    logger.info(f"📨 User requesting: {body.get('user_id')}")
    
    # Process command after acknowledgment
    if market_research_handler:
        # Don't pass ack since we already acknowledged
        try:
            market_research_handler.handle_command_post_ack(body, client)
        except Exception as e:
            logger.error(f"❌ Error in market research handler: {e}")
            client.chat_postMessage(
                channel=body['channel_id'],
                text=f"❌ Error in market analysis: {str(e)}"
            )
    else:
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
        
        # Show progress message for complex questions
        if len(question) > 20:  # Only show for non-trivial questions
            try:
                client.chat_postMessage(
                    channel=channel_id,
                    text=f"🤔 **Analyzing Your Question...**\n\n❓ *\"{question}\"*\n\n⏳ Searching through analyzed documents for relevant information..."
                )
            except:
                pass  # Don't fail if progress message fails

        if user_id not in user_sessions:
            logger.info(f"❌ No session found for user {user_id}")
            logger.info(f"📊 Active sessions: {list(user_sessions.keys())}")
            client.chat_postMessage(
                channel=channel_id,
                text="❌ No data room analysis found. Please run `/analyze [google-drive-link]` first.\n\n💡 **Tip:** Use `/analyze debug` to check your session status."
            )
            return

        session_data = user_sessions[user_id]

        if not ai_analyzer or not config.openai_configured:
            logger.info("❌ AI not configured")
            client.chat_postMessage(
                channel=channel_id,
                text="❌ AI analysis is not configured. Please configure OpenAI API key."
            )
            return

        logger.info("🤖 Calling AI analyzer...")
        
        # NEW: Check for enhanced session data and vision capabilities
        vision_ask_enhancement = None
        if vision_integration_available:
            try:
                vision_ask_enhancement = vision_integration_coordinator.enhance_ask_command(session_data, question)
                if vision_ask_enhancement.get('enhanced_context', {}).get('visual_context'):
                    logger.info("🔍 Ask command enhanced with vision data")
            except Exception as e:
                logger.warning(f"⚠️ Vision enhancement failed for /ask: {e}")
        else:
            logger.debug("📄 Vision integration not available for /ask command")
        
        # Get answer from AI
        answer = ai_analyzer.answer_question(question)
        logger.info(f"✅ AI response received: {len(answer)} chars")

        response = f"💡 **Question:** {question}\n\n" +\
                  f"**Answer:**\n{answer}\n\n" +\
                  f"📎 *Based on analyzed data room"

        # Add vision context if available
        if vision_ask_enhancement and vision_ask_enhancement.get('answer_sources', {}).get('visual_extraction'):
            chart_refs = vision_ask_enhancement.get('answer_sources', {}).get('chart_references', 0)
            if chart_refs > 0:
                response += f" with {chart_refs} visual references"

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
    
    # Immediate progress message for better UX
    try:
        channel_id = body['channel_id']
        client.chat_postMessage(
            channel=channel_id,
            text="📊 **Generating Scoring Analysis...**\n\n⏳ Calculating detailed investment scores across all evaluation criteria. Analyzing metrics and benchmarks..."
        )
    except:
        pass  # Don't fail if progress message fails

    try:
        user_id = body['user_id']
        channel_id = body['channel_id']

        if user_id not in user_sessions:
            client.chat_postMessage(
                channel=channel_id,
                text="❌ No data room analysis found. Please run `/analyze [google-drive-link]` first.\n\n💡 **Tip:** Use `/analyze debug` to check your session status."
            )
            return

        session_data = user_sessions[user_id]

        if not ai_analyzer or not config.openai_configured:
            client.chat_postMessage(
                channel=channel_id,
                text="❌ AI analysis is not configured. Please configure OpenAI API key."
            )
            return

        # NEW: Check for enhanced session data and vision capabilities
        vision_scoring_enhancement = None
        if vision_integration_available:
            try:
                vision_scoring_enhancement = vision_integration_coordinator.enhance_scoring_command(session_data)
                if vision_scoring_enhancement.get('comprehensive_metrics', {}).get('visual_extracted_metrics'):
                    logger.info("🔍 Scoring command enhanced with vision metrics")
            except Exception as e:
                logger.warning(f"⚠️ Vision enhancement failed for /scoring: {e}")
        else:
            logger.debug("📄 Vision integration not available for /scoring command")

        # Pass enhanced session data to AI analyzer for vision-enhanced scoring
        scoring_data = ai_analyzer.get_detailed_scoring(session_data)

        if 'error' in scoring_data:
            client.chat_postMessage(
                channel=channel_id,
                text=f"❌ {scoring_data['error']}"
            )
            return

        # Format enhanced scoring response (AC5: Response Enhancement)
        response = "📊 **ENHANCED SCORING BREAKDOWN**\n\n"
        
        # Show enhanced overall score if available
        if 'enhanced_overall_score' in scoring_data:
            enhanced_score = scoring_data['enhanced_overall_score']
            methodology = scoring_data.get('scoring_methodology', {})
            includes_visual = methodology.get('includes_visual_assessment', False)
            
            response += f"🎯 **Enhanced Overall Score: {enhanced_score}/10**"
            if includes_visual:
                response += f" ✨ *Vision-Enhanced*\n"
                response += f"   📊 Text Analysis: {scoring_data['overall_score']}/10 (Weight: {methodology.get('text_analysis_weight', 1.0):.0%})\n"
                response += f"   🎨 Visual Analysis: Weight: {methodology.get('visual_analysis_weight', 0.0):.0%}\n\n"
            else:
                response += f" 📄 *Text-Only Analysis*\n\n"
        else:
            response += f"🎯 **Overall Score: {scoring_data['overall_score']}/10**\n\n"

        response += "**Category Scores:**\n"
        for category, data in scoring_data['category_scores'].items():
            category_name = category.replace('_', ' ').title()
            score = data.get('score', 0)
            justification = data.get('justification', 'No justification available')
            response += f"• **{category_name}:** {score}/10 - {justification}\n"

        # Add enhanced visual scoring details if available
        if 'enhanced_scoring' in scoring_data:
            enhanced = scoring_data['enhanced_scoring']
            visual_presentation = enhanced.get('visual_presentation_quality', {})
            visual_completeness = enhanced.get('visual_content_completeness', {})
            
            if visual_presentation.get('score', 0) > 0 or visual_completeness.get('score', 0) > 0:
                response += "\n**Enhanced Visual Assessment:**\n"
                if visual_presentation.get('score', 0) > 0:
                    response += f"• **Visual Presentation Quality:** {visual_presentation['score']}/10 - {visual_presentation.get('justification', 'N/A')}\n"
                if visual_completeness.get('score', 0) > 0:
                    response += f"• **Visual Content Completeness:** {visual_completeness['score']}/10 - {visual_completeness.get('justification', 'N/A')}\n"

        response += f"\n🎯 **Recommendation:** {scoring_data['recommendation']}\n"

        # Add vision-enhanced scoring insights if available
        if vision_scoring_enhancement:
            scoring_confidence = vision_scoring_enhancement.get('scoring_confidence', {})
            final_confidence = scoring_confidence.get('final_scoring_confidence', 0.0)
            if final_confidence > 0.8:
                response += f"\n📈 **Analysis Confidence:** {final_confidence:.1%} (Vision-Enhanced)"
                
            visual_metrics = vision_scoring_enhancement.get('comprehensive_metrics', {}).get('visual_extracted_metrics', {})
            if visual_metrics:
                response += "\n🎨 **Visual Analysis:** Financial charts and metrics analyzed"

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
    
    # Immediate progress message for better UX
    try:
        channel_id = body['channel_id']
        client.chat_postMessage(
            channel=channel_id,
            text="📝 **Building Investment Memo...**\n\n⏳ Analyzing data room documents and generating comprehensive investment memo. This may take a few moments..."
        )
    except:
        pass  # Don't fail if progress message fails

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

        if not ai_analyzer or not config.openai_configured:
            client.chat_postMessage(
                channel=channel_id,
                text="❌ AI analysis is not configured. Please configure OpenAI API key."
            )
            return

        # NEW: Check for enhanced session data and vision capabilities
        vision_memo_enhancement = None
        if vision_integration_available:
            try:
                vision_memo_enhancement = vision_integration_coordinator.enhance_memo_command(session_data)
                if vision_memo_enhancement.get('comprehensive_evidence', {}).get('visual_evidence'):
                    logger.info("🔍 Memo command enhanced with visual evidence")
            except Exception as e:
                logger.warning(f"⚠️ Vision enhancement failed for /memo: {e}")
        else:
            logger.debug("📄 Vision integration not available for /memo command")

        # Pass enhanced session data to AI analyzer for vision-enhanced memo generation  
        memo = ai_analyzer.generate_investment_memo(session_data)

        response = "📄 **INVESTMENT MEMO**\n\n" + memo

        # Add vision-enhanced memo insights if available
        if vision_memo_enhancement:
            thesis_strength = vision_memo_enhancement.get('investment_thesis_strength', {})
            comprehensive_strength = thesis_strength.get('comprehensive_thesis_strength', 0.0)
            if comprehensive_strength > 0.9:
                response += f"\n\n💎 **Investment Thesis Strength:** {comprehensive_strength:.1%} (Professional Grade)"
                
            chart_references = vision_memo_enhancement.get('comprehensive_evidence', {}).get('chart_references', [])
            if chart_references:
                response += f"\n📊 **Visual Evidence:** {len(chart_references)} supporting charts analyzed"

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
    
    # Immediate progress message for better UX
    try:
        channel_id = body['channel_id']
        client.chat_postMessage(
            channel=channel_id,
            text="🔍 **Gaps Analysis in Progress...**\n\n⏳ Identifying missing information and potential data room gaps. Analyzing documentation comprehensiveness..."
        )
    except:
        pass  # Don't fail if progress message fails

    try:
        user_id = body['user_id']
        channel_id = body['channel_id']

        if user_id not in user_sessions:
            client.chat_postMessage(
                channel=channel_id,
                text="❌ No data room analysis found. Please run `/analyze [google-drive-link]` first.\n\n💡 **Tip:** Use `/analyze debug` to check your session status."
            )
            return

        session_data = user_sessions[user_id]

        if not ai_analyzer or not config.openai_configured:
            client.chat_postMessage(
                channel=channel_id,
                text="❌ AI analysis is not configured. Please configure OpenAI API key."
            )
            return

        # NEW: Check for enhanced session data and vision capabilities
        vision_gaps_enhancement = None
        if vision_integration_available:
            try:
                vision_gaps_enhancement = vision_integration_coordinator.enhance_gaps_command(session_data)
                if vision_gaps_enhancement.get('comprehensive_gap_analysis', {}).get('visual_gaps'):
                    logger.info("🔍 Gaps command enhanced with vision analysis")
            except Exception as e:
                logger.warning(f"⚠️ Vision enhancement failed for /gaps: {e}")
        else:
            logger.debug("📄 Vision integration not available for /gaps command")

        # Pass enhanced session data to AI analyzer for vision-enhanced gap analysis
        gaps_analysis = ai_analyzer.analyze_gaps(session_data)

        response = "🔍 **INFORMATION GAPS ANALYSIS**\n\n" + gaps_analysis

        # Add vision-enhanced gap insights if available
        if vision_gaps_enhancement:
            completeness = vision_gaps_enhancement.get('completeness_assessment', {})
            overall_completeness = completeness.get('overall_completeness', 0.0)
            if overall_completeness > 0:
                response += f"\n\n📊 **Enhanced Analysis Completeness:** {overall_completeness:.1%}"
                
            recommendations = vision_gaps_enhancement.get('actionable_recommendations', [])
            if recommendations:
                response += "\n\n🎯 **Vision-Enhanced Recommendations:**\n"
                for rec in recommendations[:3]:  # Top 3 recommendations
                    response += f"• {rec}\n"

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
        health_response += f"• Vision Integration: {'✅' if vision_integration_available else '❌'}\n"
        health_response += f"• Active Sessions: {len(user_sessions)}\n"
        health_response += f"• Your Session: {'✅ Active' if user_id in user_sessions else '❌ Not found'}\n"
        

        
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
        


        response = "👋 Hi! I'm the DataRoom Intelligence Bot running on Railway with Phase 2B Market Research (Production Ready).\n\n" +\
                  f"{ai_status} **AI Status:** {ai_note}\n" +\
                  f"{market_status} **Market Research:** {market_note}\n\n" +\
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
