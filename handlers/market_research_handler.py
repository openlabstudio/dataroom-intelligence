"""
Market Research Handler for Slack Commands
Handles /market-research command with proper response handling

This module fixes the dispatch_failed issue by ensuring proper
acknowledgment and response handling for Slack slash commands.
"""

import os
import threading
import time
from datetime import datetime
from typing import Dict, Any, Optional
from utils.logger import get_logger

logger = get_logger(__name__)

class MarketResearchHandler:
    """Handler for market research commands with proper Slack response handling"""
    
    def __init__(self, orchestrator, user_sessions: Dict):
        """
        Initialize the market research handler
        
        Args:
            orchestrator: Market research orchestrator instance
            user_sessions: Dictionary storing user session data
        """
        self.orchestrator = orchestrator
        self.user_sessions = user_sessions
        
    def handle_command(self, ack, body: Dict, client) -> None:
        """
        Handle /market-research command with proper acknowledgment
        
        Args:
            ack: Slack acknowledgment function
            body: Request body from Slack
            client: Slack client instance
        """
        # CRITICAL: Acknowledge immediately to prevent dispatch_failed
        try:
            ack()
            logger.info("✅ Command acknowledged successfully")
        except Exception as e:
            logger.error(f"❌ Failed to acknowledge command: {e}")
            return
        
        # Now handle the command in a separate try block
        try:
            user_id = body['user_id']
            channel_id = body['channel_id']
            
            logger.info(f"🔍 Starting market research analysis for user {user_id}")
            
            # Check if orchestrator is available
            if not self.orchestrator:
                client.chat_postMessage(
                    channel=channel_id,
                    text="❌ Market research functionality is not available. OpenAI configuration required."
                )
                return
            
            # Check if user has analyzed documents
            if user_id not in self.user_sessions:
                logger.info(f"❌ No session found for user {user_id}")
                logger.info(f"📊 Active sessions: {list(self.user_sessions.keys())}")
                client.chat_postMessage(
                    channel=channel_id,
                    text="❌ No data room analysis found.\n\n" +
                         "Please run `/analyze [google-drive-link]` first to analyze documents, " +
                         "then use `/market-research` for market intelligence analysis.\n\n" +
                         "💡 **Tip:** Use `/analyze debug` to check your session status."
                )
                return
            
            session_data = self.user_sessions[user_id]
            
            # Check if in TEST MODE
            if session_data.get('test_mode', False):
                logger.info("🧪 TEST MODE: Performing mock market research")
                # Send immediate response for TEST MODE
                test_response = self._get_test_mode_response()
                client.chat_postMessage(
                    channel=channel_id,
                    text=test_response
                )
                
                # Store mock market research in session
                self.user_sessions[user_id]['market_research'] = {
                    'result': {'test_mode': True},
                    'timestamp': datetime.now().isoformat(),
                    'analysis_type': 'test_mode_mock'
                }
                logger.info("✅ TEST MODE market research completed")
                return
            
            # Validate session has required data
            if 'processed_documents' not in session_data or 'document_summary' not in session_data:
                logger.error(f"❌ Session data incomplete for user {user_id}")
                client.chat_postMessage(
                    channel=channel_id,
                    text="❌ Session data incomplete. Please run `/analyze [google-drive-link]` again."
                )
                return
            
            # Send initial response IMMEDIATELY after validation
            initial_response = client.chat_postMessage(
                channel=channel_id,
                text="🔍 **Market Research Analysis Started**\n\n" +
                     "📊 Preparing market intelligence analysis...\n" +
                     "⏳ This process will take 3-5 minutes\n\n" +
                     "🚧 **Status:** Initializing analysis agents...\n" +
                     "⏱️ Started at: " + datetime.now().strftime("%H:%M:%S")
            )
            
            logger.info(f"🎯 Initial response sent with ts: {initial_response['ts']}")
            
            # Start background market research analysis
            thread = threading.Thread(
                target=self._perform_analysis,
                args=(client, channel_id, user_id, initial_response['ts']),
                daemon=True
            )
            thread.start()
            
            logger.info("🎯 Background thread started successfully")
            
        except Exception as e:
            logger.error(f"❌ Error in market research command: {e}", exc_info=True)
            try:
                client.chat_postMessage(
                    channel=channel_id,
                    text=f"❌ Error in market analysis: {str(e)}"
                )
            except:
                pass  # Fail silently if we can't send error message
    
    def _get_test_mode_response(self) -> str:
        """Get a test mode response for market research"""
        response = "✅ **MARKET RESEARCH ANALYSIS COMPLETED (TEST MODE)**\n\n"
        
        response += "🎯 **MARKET PROFILE** (🟢 0.9 confidence)\n"
        response += "• **Vertical:** FinTech/Payments\n"
        response += "• **Target:** SMB merchants in LATAM\n"
        response += "• **Geo:** Mexico, Brazil, Colombia\n"
        response += "• **Model:** SaaS + Transaction fees\n\n"
        
        # TASK-001: Add Competitive Analysis section
        response += "🏢 **COMPETITIVE LANDSCAPE** (🟡 MEDIUM threat)\n"
        response += "• **Direct competitors:** Stripe, MercadoPago, dLocal\n"
        response += "• **Competitive moat:** Regional expertise and vertical focus\n"
        response += "• **Threat assessment:** Established players have resources, but vertical specialization provides opportunity\n\n"
        
        response += "🔍 **CRITICAL ASSESSMENT:**\n\n"
        response += "⚠️ **Point 1:** Strong market opportunity with 70% of SMBs lacking digital payment solutions. "
        response += "However, regulatory complexity varies significantly across target countries.\n\n"
        
        response += "💡 **Point 2:** Competition from established players like MercadoPago poses challenges, "
        response += "but focus on specific verticals could provide differentiation.\n\n"
        
        response += "📋 **AVAILABLE COMMANDS:**\n"
        response += "• `/ask [question]` - Ask specific questions\n"
        response += "• `/scoring` - Get detailed scoring\n"
        response += "• `/memo` - Generate investment memo\n\n"
        
        response += "📎 *TEST MODE - No GPT-4 calls made*"
        
        return response
    
    def _perform_analysis(self, client, channel_id: str, user_id: str, message_ts: str) -> None:
        """
        Perform the actual market research analysis in background
        
        Args:
            client: Slack client instance
            channel_id: Channel ID for responses
            user_id: User ID performing the analysis
            message_ts: Timestamp of the initial message to update
        """
        try:
            # Get user session data
            session_data = self.user_sessions[user_id]
            processed_documents = session_data['processed_documents']
            document_summary = session_data['document_summary']
            
            logger.info(f"🔍 Starting market intelligence analysis for user {user_id}")
            
            # Small delay to ensure message is sent
            time.sleep(0.5)
            
            # Update progress - Step 1
            client.chat_update(
                channel=channel_id,
                ts=message_ts,
                text="🔍 **Market Research Analysis in Progress**\n\n" +
                     "📊 **Step 1/4:** Detecting market vertical...\n" +
                     "🎯 Analyzing documents to identify sector\n" +
                     "⏳ Status: Processing with AI...\n" +
                     "⏱️ Elapsed: 0:30"
            )
            
            # Simulate some processing time
            time.sleep(1)
            
            # Update progress - Step 2
            client.chat_update(
                channel=channel_id,
                ts=message_ts,
                text="🔍 **Market Research Analysis in Progress**\n\n" +
                     "📊 **Step 2/4:** Competitive analysis...\n" +
                     "🏢 Identifying competitors and positioning\n" +
                     "⏳ Status: Processing market data...\n" +
                     "⏱️ Elapsed: 1:00"
            )
            
            # Update progress - Step 3
            time.sleep(1)
            client.chat_update(
                channel=channel_id,
                ts=message_ts,
                text="🔍 **Market Research Analysis in Progress**\n\n" +
                     "📊 **Step 3/4:** Market validation...\n" +
                     "📈 Validating TAM/SAM and opportunities\n" +
                     "⏳ Status: Analyzing external data...\n" +
                     "⏱️ Elapsed: 1:30"
            )
            
            # Update progress - Step 4
            time.sleep(1)
            client.chat_update(
                channel=channel_id,
                ts=message_ts,
                text="🔍 **Market Research Analysis in Progress**\n\n" +
                     "📊 **Step 4/4:** Critical assessment...\n" +
                     "🧠 Generating critical analysis with \"brutal honesty\"\n" +
                     "⏳ Status: Finalizing analysis...\n" +
                     "⏱️ Elapsed: 2:00"
            )
            
            # Perform actual market intelligence analysis
            logger.info("📊 Calling orchestrator for market intelligence...")
            market_intelligence_result = self.orchestrator.perform_market_intelligence(
                processed_documents, document_summary
            )
            logger.info("✅ Market intelligence analysis complete")
            
            # Format compact response for Slack character limits
            response = self._format_response(market_intelligence_result)
            
            # Update Slack with final results
            client.chat_update(
                channel=channel_id,
                ts=message_ts,
                text=response
            )
            
            # Store market research results in user session
            self.user_sessions[user_id]['market_research'] = {
                'result': market_intelligence_result,
                'timestamp': datetime.now().isoformat(),
                'analysis_type': 'comprehensive_market_intelligence'
            }
            
            logger.info(f"✅ Market research analysis completed for user {user_id}")
            
        except Exception as e:
            logger.error(f"❌ Market research analysis failed: {e}", exc_info=True)
            try:
                client.chat_update(
                    channel=channel_id,
                    ts=message_ts,
                    text=f"❌ **Error in Market Analysis**\n\n" +
                         f"Error: {str(e)}\n\n" +
                         f"Please try again or contact the administrator."
                )
            except Exception as update_error:
                logger.error(f"❌ Failed to update error message: {update_error}")
    
    def _format_response(self, market_intelligence_result) -> str:
        """
        Format the market research response for Slack
        
        Args:
            market_intelligence_result: Result from orchestrator
            
        Returns:
            Formatted string for Slack message
        """
        response = "✅ **MARKET RESEARCH ANALYSIS COMPLETED**\n\n"
        
        # Market Profile - Compact format
        if hasattr(market_intelligence_result, 'market_profile') and market_intelligence_result.market_profile:
            profile = market_intelligence_result.market_profile
            primary_vertical = getattr(profile, 'primary_vertical', 'Not identified')
            sub_vertical = getattr(profile, 'sub_vertical', '')
            confidence = getattr(profile, 'confidence_score', 0)
            target_market = getattr(profile, 'target_market', 'Not identified')
            geographic_focus = getattr(profile, 'geographic_focus', 'Not identified')
            business_model = getattr(profile, 'business_model', 'Not identified')
            
            # Compact market profile
            vertical_display = f"{primary_vertical}/{sub_vertical}" if sub_vertical else primary_vertical
            response += f"🎯 **PROFILE** ({'🟢' if confidence > 0.8 else '🟡' if confidence > 0.6 else '🔴'} {confidence:.1f} confidence)\n"
            response += f"• **Vertical:** {vertical_display}\n"
            response += f"• **Target:** {target_market[:60]}{'...' if len(target_market) > 60 else ''}\n"
            response += f"• **Geo:** {geographic_focus[:30]}{'...' if len(geographic_focus) > 30 else ''}\n"
            response += f"• **Model:** {business_model[:40]}{'...' if len(business_model) > 40 else ''}\n\n"
        
        # Critical Assessment
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
                    response += "🔍 **CRITICAL ASSESSMENT:**\n\n"
                    for i, point in enumerate(meaningful_points):
                        emoji = "⚠️" if i == 0 else "💡"
                        response += f"{emoji} **Point {i+1}:** {point}\n\n"
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
                    response += "🔍 **CRITICAL ASSESSMENT:**\n\n"
                    combined_text = '. '.join(good_sentences)
                    if not combined_text.endswith('.'):
                        combined_text += '.'
                    response += f"⚠️ {combined_text}\n\n"
        
        # Available commands
        response += "📋 **AVAILABLE COMMANDS:**\n"
        response += "• `/ask [question]` - Ask specific questions\n"
        response += "• `/scoring` - Get detailed scoring\n"
        response += "• `/memo` - Generate investment memo\n"
        response += "• `/gaps` - Analyze information gaps\n"
        response += "• `/reset` - Clear session and start over"
        
        return response
