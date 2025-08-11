"""
Market Research Handler for Slack Commands
Handles /market-research command with proper response handling

This module fixes the dispatch_failed issue by ensuring proper
acknowledgment and response handling for Slack slash commands.
"""

import threading
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
        ack()
        
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
                         "then use `/market-research` for market intelligence analysis."
                )
                return
            
            session_data = self.user_sessions[user_id]
            
            # Validate session has required data
            if 'processed_documents' not in session_data or 'document_summary' not in session_data:
                logger.error(f"❌ Session data incomplete for user {user_id}")
                client.chat_postMessage(
                    channel=channel_id,
                    text="❌ Session data incomplete. Please run `/analyze [google-drive-link]` again."
                )
                return
            
            # Send initial response (after ack, this is the actual first message)
            initial_response = client.chat_postMessage(
                channel=channel_id,
                text="🔍 **Análisis de Mercado Iniciado**\n\n" +
                     "📊 Preparando análisis de inteligencia de mercado...\n" +
                     "⏳ Este proceso puede tomar 3-5 minutos\n\n" +
                     "🚧 **Estado:** Inicializando agentes de análisis..."
            )
            
            logger.info("🎯 Starting background thread for market research")
            
            # Start background market research analysis
            thread = threading.Thread(
                target=self._perform_analysis,
                args=(client, channel_id, user_id, initial_response['ts']),
                daemon=True
            )
            thread.start()
            
            logger.info("🎯 Background thread started successfully")
            
        except Exception as e:
            logger.error(f"❌ Error in market research command: {e}")
            try:
                client.chat_postMessage(
                    channel=channel_id,
                    text=f"❌ Error en análisis de mercado: {str(e)}"
                )
            except:
                pass  # Fail silently if we can't send error message
    
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
            
            # Update progress - Step 1
            client.chat_update(
                channel=channel_id,
                ts=message_ts,
                text="🔍 **Análisis de Mercado en Progreso**\n\n" +
                     "📊 **Paso 1/4:** Detectando vertical de mercado...\n" +
                     "🎯 Analizando documentos para identificar sector\n" +
                     "⏳ Estado: Procesando con IA..."
            )
            
            # Update progress - Step 2
            client.chat_update(
                channel=channel_id,
                ts=message_ts,
                text="🔍 **Análisis de Mercado en Progreso**\n\n" +
                     "📊 **Paso 2/4:** Análisis competitivo...\n" +
                     "🏢 Identificando competidores y posicionamiento\n" +
                     "⏳ Estado: Procesando datos de mercado..."
            )
            
            # Update progress - Step 3
            client.chat_update(
                channel=channel_id,
                ts=message_ts,
                text="🔍 **Análisis de Mercado en Progreso**\n\n" +
                     "📊 **Paso 3/4:** Validación de mercado...\n" +
                     "📈 Validando TAM/SAM y oportunidades\n" +
                     "⏳ Estado: Analizando datos externos..."
            )
            
            # Update progress - Step 4
            client.chat_update(
                channel=channel_id,
                ts=message_ts,
                text="🔍 **Análisis de Mercado en Progreso**\n\n" +
                     "📊 **Paso 4/4:** Evaluación crítica...\n" +
                     "🧠 Generando análisis crítico con \"brutal honesty\"\n" +
                     "⏳ Estado: Finalizando análisis..."
            )
            
            # Perform actual market intelligence analysis
            market_intelligence_result = self.orchestrator.perform_market_intelligence(
                processed_documents, document_summary
            )
            
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
            logger.error(f"❌ Market research analysis failed: {e}")
            try:
                client.chat_update(
                    channel=channel_id,
                    ts=message_ts,
                    text=f"❌ **Error en Análisis de Mercado**\n\n" +
                         f"Error: {str(e)}\n\n" +
                         f"Por favor, intenta nuevamente o contacta al administrador."
                )
            except:
                pass  # Fail silently if we can't update message
    
    def _format_response(self, market_intelligence_result) -> str:
        """
        Format the market research response for Slack
        
        Args:
            market_intelligence_result: Result from orchestrator
            
        Returns:
            Formatted string for Slack message
        """
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
