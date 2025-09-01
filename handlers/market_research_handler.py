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
            
            # Check if in TEST MODE (forced false in production)
            PRODUCTION_MODE = os.getenv('PRODUCTION_MODE', 'false').lower() == 'true'
            test_mode_active = False if PRODUCTION_MODE else session_data.get('test_mode', False)
            if test_mode_active:
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
        
        # MEJORAS CALIDAD: Market Taxonomy TEST MODE
        response += "📊 **MARKET TAXONOMY** (9.0/10)\n"
        response += "• **Solution:** AI-powered invoice factoring platform\n"
        response += "• **Sub-vertical:** Invoice financing\n"
        response += "• **Vertical:** FinTech\n"
        response += "• **Industry:** Financial technology\n"
        response += "• **Target:** SMB merchants in LATAM\n\n"
        
        # FASE 2A: Enhanced Competitive Landscape (TEST MODE)
        response += "🏢 **COMPETITIVE LANDSCAPE** (High risk - 6 sources)\n"
        response += "• **Market leaders:** Stripe ($95B valuation), MercadoPago\n"
        response += "• **Similar play:** FactorX - Failed to raise B\n"
        response += "• **Key risk:** 3 of 5 similar AI factoring startups failed in 18 months\n\n"
        
        # FASE 2B: Enhanced Market Validation (TEST MODE)
        response += "📈 **MARKET VALIDATION** (medium confidence - 3 sources)\n"
        response += "• **Expert:** McKinsey 2024: 48h approval technically feasible but requires regulatory pre-approval\n"
        response += "• **Precedent:** QuickFactor - Failed - regulatory issues\n"
        response += "• **Assessment:** Feasible but regulatory-dependent\n\n"
        
        # FASE 2C: Enhanced Funding Benchmarks (TEST MODE)
        response += "💰 **FUNDING BENCHMARKS** (medium confidence - 8 sources)\n"
        response += "• **Market:** TechCrunch 2024: FinTech Series A rounds averaging $8M, down 30% from 2022\n"
        response += "• **Recent:** PayFlow - Raised $12M Series A at $60M valuation\n"
        response += "• **Climate:** Cautious - 25% down from peak\n\n"
        
        
        response += "🧠 **KEY INSIGHT:**\n"
        response += "⚠️ Strong market opportunity but regulatory complexity varies significantly across target countries.\n\n"
        
        response += "📋 `/ask` `/scoring` `/memo` `/gaps` `/reset`\n\n"
        
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
            
            # Update progress - Phase 1 of 5
            client.chat_update(
                channel=channel_id,
                ts=message_ts,
                text="🔍 **Market Research Analysis in Progress**\n\n" +
                     "📊 **Phase 1/5:** Market Detection & Taxonomy...\n" +
                     "🎯 Identifying 4-level hierarchy (Solution → Sub-vertical → Vertical → Industry)\n" +
                     "⏳ Status: Processing documents with GPT-4..."
            )
            
            # Simulate some processing time
            time.sleep(1)
            
            # Update progress - Phase 2 of 5
            client.chat_update(
                channel=channel_id,
                ts=message_ts,
                text="🔍 **Market Research Analysis in Progress**\n\n" +
                     "📊 **Phase 2/5:** Competitive Intelligence...\n" +
                     "🏢 Executing 3-level hierarchical search via Tavily API\n" +
                     "⏳ Status: Searching across Solution, Sub-vertical & Vertical levels..."
            )
            
            # Update progress - Phase 3 of 5
            time.sleep(1)
            client.chat_update(
                channel=channel_id,
                ts=message_ts,
                text="🔍 **Market Research Analysis in Progress**\n\n" +
                     "📊 **Phase 3/5:** Market Validation (TAM/SAM/SOM)...\n" +
                     "📈 Validating market size with 3-level analysis\n" +
                     "⏳ Status: Gathering expert opinions & precedents..."
            )
            
            # Update progress - Phase 4 of 5
            time.sleep(1)
            client.chat_update(
                channel=channel_id,
                ts=message_ts,
                text="🔍 **Market Research Analysis in Progress**\n\n" +
                     "📊 **Phase 4/5:** Funding & Metrics Benchmarking...\n" +
                     "💰 Analyzing funding patterns across 3 market levels\n" +
                     "⏳ Status: Benchmarking valuations and metrics..."
            )
            
            # Update progress - Phase 5 of 5 (Critical Assessment - takes longer)
            time.sleep(1.5)
            client.chat_update(
                channel=channel_id,
                ts=message_ts,
                text="🔍 **Market Research Analysis in Progress**\n\n" +
                     "📊 **Phase 5/5:** Critical Assessment & Investment Decision...\n" +
                     "🧠 Generating brutal honest analysis with GPT-4\n" +
                     "⏳ **Note:** This phase may take 1-2 minutes - synthesizing all intelligence..."
            )
            
            # Get analysis result from /analyze for funding benchmarking
            analysis_result = session_data.get('analysis_result', {})
            
            # Perform actual market intelligence analysis
            logger.info("📊 Calling orchestrator for market intelligence...")
            market_intelligence_result = self.orchestrator.perform_market_intelligence(
                processed_documents, document_summary, analysis_result
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
        Format the market research response for Slack with analyst-focused clarity
        
        Args:
            market_intelligence_result: Result from orchestrator
            
        Returns:
            Formatted string for Slack message
        """
        # Use new analyst formatter for clarity and actionability
        try:
            # MVP DEMO: Use expert formatter for GPT-4 enhanced output
            from utils.expert_formatter import format_expert_market_research
            return format_expert_market_research(market_intelligence_result)
        except ImportError:
            logger.warning("Analyst formatter not available, using fallback")
            # Simple fallback if new formatter fails
            pass
        
        response = "✅ **MARKET RESEARCH ANALYSIS COMPLETED**\n\n"
        
        # Check if we have any valid data
        has_data = (
            (hasattr(market_intelligence_result, 'market_profile') and market_intelligence_result.market_profile) or
            (hasattr(market_intelligence_result, 'competitive_analysis') and market_intelligence_result.competitive_analysis) or
            (hasattr(market_intelligence_result, 'market_validation') and market_intelligence_result.market_validation) or
            (hasattr(market_intelligence_result, 'funding_benchmarks') and market_intelligence_result.funding_benchmarks) or
            (hasattr(market_intelligence_result, 'critical_assessment') and market_intelligence_result.critical_assessment)
        )
        
        if not has_data:
            response += "⚠️ **ANALYSIS INCOMPLETE**\n\n"
            response += "The market research analysis encountered issues and could not generate complete results. This may happen when:\n"
            response += "• OpenAI API calls fail or timeout\n"
            response += "• Documents don't contain sufficient market information\n"
            response += "• Network connectivity issues\n\n"
            response += "**Recommendations:**\n"
            response += "• Try running the analysis again\n"
            response += "• Ensure documents contain market, competition, and business model information\n"
            response += "• Check system logs for specific error details\n\n"
            response += "📋 **AVAILABLE COMMANDS:**\n"
            response += "• `/analyze [google-drive-link]` - Re-analyze documents\n"
            response += "• `/ask [question]` - Ask specific questions\n"
            response += "• `/reset` - Clear session and start over"
            return response
        
        # MEJORAS CALIDAD: Market Taxonomy section
        if hasattr(market_intelligence_result, 'market_profile') and market_intelligence_result.market_profile:
            profile = market_intelligence_result.market_profile            
            # Extract taxonomy fields
            solution = getattr(profile, 'solution', 'Not identified')
            sub_vertical = getattr(profile, 'sub_vertical', 'Not identified')
            vertical = getattr(profile, 'vertical', 'Not identified')
            industry = getattr(profile, 'industry', 'technology')
            target_market = getattr(profile, 'target_market', 'Not identified')
            confidence = getattr(profile, 'confidence_score', 0)
            
            # Calculate overall score from confidence
            overall_score = confidence * 10
            
            # New Market Taxonomy format
            response += f"📊 **MARKET TAXONOMY** ({overall_score:.1f}/10)\n"
            response += f"• **Solution:** {solution}\n"
            response += f"• **Sub-vertical:** {sub_vertical}\n"
            response += f"• **Vertical:** {vertical}\n"
            response += f"• **Industry:** {industry}\n"
            response += f"• **Target:** {target_market}\n\n"
        
        # FASE 2A: Enhanced Competitive Landscape section
        if hasattr(market_intelligence_result, 'competitive_analysis') and market_intelligence_result.competitive_analysis:
            comp_analysis = market_intelligence_result.competitive_analysis
            if isinstance(comp_analysis, dict):
                # Get threat level and sources count
                threat_level = comp_analysis.get('threat_level', 'Unknown')
                sources_count = comp_analysis.get('sources_count', 0)
                market_position = comp_analysis.get('market_position', 'Unknown market position')
                
                # Format threat level for display
                threat_display = threat_level.capitalize() if threat_level else "Unknown"
                if sources_count > 0:
                    header = f"🏢 **COMPETITIVE LANDSCAPE** ({threat_display} risk - {sources_count} sources)\n"
                else:
                    header = f"🏢 **COMPETITIVE LANDSCAPE** ({threat_display} risk)\n"
                response += header
                
                # Show market leaders
                market_leaders = comp_analysis.get('market_leaders', [])
                if market_leaders:
                    # Format top 2 market leaders compactly
                    leaders = []
                    for leader in market_leaders[:2]:
                        if isinstance(leader, dict):
                            name = leader.get('name', 'Unknown')
                            funding = leader.get('funding', '')
                            if funding and 'valuation' in funding.lower():
                                leaders.append(f"{name} ({funding})")
                            else:
                                leaders.append(name)
                        else:
                            leaders.append(str(leader))
                    if leaders:
                        response += f"• **Market leaders:** {', '.join(leaders)}\n"
                
                # Show similar propositions with outcomes
                similar_props = comp_analysis.get('similar_propositions', [])
                if similar_props:
                    # Show first similar proposition with outcome
                    prop = similar_props[0]
                    if isinstance(prop, dict):
                        name = prop.get('name', 'Unknown')
                        outcome = prop.get('outcome', '')
                        desc = prop.get('description', '')
                        if outcome:
                            response += f"• **Similar play:** {name} - {outcome}\n"
                        elif desc:
                            response += f"• **Similar play:** {name} - {desc[:50]}\n"
                
                # Show key risk
                risks = comp_analysis.get('competitive_risks', [])
                if risks:
                    # Take first risk, limit length
                    risk = str(risks[0])[:100] if risks[0] else "Not identified"
                    response += f"• **Key risk:** {risk}\n"
                
                response += "\n"
        
        # FASE 2B: Enhanced Market Validation section with integrated web search
        if hasattr(market_intelligence_result, 'market_validation') and market_intelligence_result.market_validation:
            validation = market_intelligence_result.market_validation
            if isinstance(validation, dict):
                # Get independent analysis data (new structure)
                independent = validation.get('independent_analysis', validation)
                
                # Get confidence level and score
                confidence_level = independent.get('confidence_level', 'Unknown')
                score = independent.get('validation_score', validation.get('validation_score', 0))
                sources_count = len(independent.get('sources', []))
                
                # Format header based on confidence
                if sources_count > 0:
                    header = f"📈 **MARKET VALIDATION** ({confidence_level} confidence - {sources_count} sources)\n"
                else:
                    header = f"📈 **MARKET VALIDATION** ({confidence_level} confidence)\n"
                response += header
                
                # Show expert consensus (most important)
                expert_consensus = independent.get('expert_consensus', [])
                if expert_consensus and len(expert_consensus) > 0:
                    # Take first expert opinion, limit length
                    expert = str(expert_consensus[0])[:100] if expert_consensus[0] else ""
                    if expert:
                        response += f"• **Expert:** {expert}\n"
                
                # Show precedent analysis (similar companies outcomes)
                precedents = independent.get('precedent_analysis', [])
                if precedents and len(precedents) > 0:
                    precedent = precedents[0]
                    if isinstance(precedent, dict):
                        company = precedent.get('company', 'Unknown')
                        outcome = precedent.get('outcome', '')
                        if outcome:
                            response += f"• **Precedent:** {company} - {outcome}\n"
                
                # Show feasibility assessment or key risk
                feasibility = independent.get('feasibility_assessment', '')
                if feasibility and len(feasibility) > 20:
                    response += f"• **Assessment:** {feasibility[:80]}\n"
                else:
                    # Fallback to risks if no feasibility
                    risks = independent.get('market_risks', validation.get('red_flags', []))
                    if risks:
                        risk = str(risks[0])[:80] if risks else "Not identified"
                        response += f"• **Risk:** {risk}\n"
                
                response += "\n"
        
        # FASE 2C: Enhanced Funding Benchmarks section with integrated web search
        if hasattr(market_intelligence_result, 'funding_benchmarks') and market_intelligence_result.funding_benchmarks:
            benchmarks = market_intelligence_result.funding_benchmarks
            if isinstance(benchmarks, dict):
                # Get independent analysis data (new structure)
                independent = benchmarks.get('independent_analysis', benchmarks)
                
                # Get confidence level and sources
                confidence_level = independent.get('confidence_level', 'Unknown')
                sources_count = len(independent.get('sources', []))
                funding_climate = independent.get('funding_climate', '')
                
                # Format header based on confidence
                if sources_count > 0:
                    header = f"💰 **FUNDING BENCHMARKS** ({confidence_level} confidence - {sources_count} sources)\n"
                else:
                    header = f"💰 **FUNDING BENCHMARKS** ({confidence_level} confidence)\n"
                response += header
                
                # Show market funding pattern (most important)
                patterns = independent.get('market_funding_patterns', [])
                if patterns and len(patterns) > 0:
                    # Take first pattern, limit length
                    pattern = str(patterns[0])[:100] if patterns[0] else ""
                    if pattern:
                        response += f"• **Market:** {pattern}\n"
                
                # Show similar deal
                similar_deals = independent.get('similar_deals', [])
                if similar_deals and len(similar_deals) > 0:
                    deal = similar_deals[0]
                    if isinstance(deal, dict):
                        company = deal.get('company', 'Unknown')
                        details = deal.get('details', '')[:50]  # Limit details length
                        if details:
                            response += f"• **Recent:** {company} - {details}\n"
                
                # Show climate
                if funding_climate:
                    response += f"• **Climate:** {funding_climate}\n"
                
                response += "\n"
        
        
        # COMPACT FORMAT: Reduced Critical Assessment - Only 1 key point
        if hasattr(market_intelligence_result, 'critical_assessment') and market_intelligence_result.critical_assessment:
            assessment = market_intelligence_result.critical_assessment
            
            response += "🧠 **KEY INSIGHT:**\n"
            
            # Extract only the most important point
            if isinstance(assessment, dict):
                # Find the first meaningful point
                for key, value in assessment.items():
                    if isinstance(value, str) and len(value) > 50:
                        clean_text = value.replace('"', '').replace("'", "").strip()
                        # Truncate to max 300 characters for compact format
                        if len(clean_text) > 300:
                            cut_point = clean_text.find('.', 250)
                            if cut_point > 200:
                                clean_text = clean_text[:cut_point + 1]
                            else:
                                clean_text = clean_text[:300] + "..."
                        response += f"⚠️ {clean_text}\n\n"
                        break
            else:
                # Handle string format - take first meaningful sentence
                assessment_text = str(assessment)
                sentences = assessment_text.replace('.', '.|').split('|')
                for sentence in sentences:
                    sentence = sentence.strip()
                    if sentence and len(sentence) > 30:
                        # Limit to 300 characters
                        if len(sentence) > 300:
                            sentence = sentence[:300] + "..."
                        response += f"⚠️ {sentence}\n\n"
                        break
        
        # COMPACT: Available commands
        response += "📋 `/ask` `/scoring` `/memo` `/gaps` `/reset`"
        
        return response
