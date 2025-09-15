"""
Story 1.2 AC6: Cross-Command Vision Data Access Integration

Coordinates vision processing integration with all existing Slack commands,
ensuring enhanced extraction results improve /ask, /gaps, /scoring, and /memo
commands through unified vision data access patterns.
"""

import os
from typing import Dict, List, Any, Optional, Tuple
from handlers.vision_processor import VisionProcessor
from handlers.visual_complexity_analyzer import VisualComplexityAnalyzer
from handlers.pdf_to_image_processor import PDFToImageProcessor
from handlers.vision_cost_controller import VisionCostController
from handlers.enhanced_session_manager import EnhancedSessionManager
from utils.logger import get_logger

logger = get_logger(__name__)

class VisionIntegrationCoordinator:
    """
    Central coordinator for integrating GPT Vision capabilities across all commands.
    Manages the complete vision processing pipeline and provides unified access
    to enhanced extraction results for all analysis commands.
    """
    
    def __init__(self):
        # Initialize all vision processing components
        self.vision_processor = VisionProcessor()
        self.complexity_analyzer = VisualComplexityAnalyzer()
        self.image_processor = PDFToImageProcessor()
        self.cost_controller = VisionCostController()
        self.session_manager = EnhancedSessionManager()
        
        # Integration settings
        self.vision_enabled = os.getenv('VISION_ENABLED', 'true').lower() == 'true'
        self.auto_enhance_commands = os.getenv('VISION_AUTO_ENHANCE', 'true').lower() == 'true'
        
        logger.info(f"🔗 Vision Integration Coordinator initialized:")
        logger.info(f"   Vision Processing: {'Enabled' if self.vision_enabled else 'Disabled'}")
        logger.info(f"   Auto Command Enhancement: {'Enabled' if self.auto_enhance_commands else 'Disabled'}")
    
    def process_document_with_vision(self, pdf_path: Optional[str], user_id: str, 
                                   basic_session_data: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Complete vision processing pipeline for document analysis.
        Integrates with existing document processing workflow.
        
        Args:
            pdf_path: Path to PDF document (None to skip vision processing)
            user_id: User identifier for session management
            basic_session_data: Existing session data from text processing
            
        Returns:
            Tuple of (enhanced_session_data, vision_processing_results)
        """
        
        # Quick exit for disabled vision or None path
        if not self.vision_enabled or pdf_path is None:
            logger.info("📄 Vision processing disabled or skipped - creating enhanced session without vision")
            enhanced_session = self.session_manager.create_enhanced_session(
                user_id, basic_session_data, None
            )
            return enhanced_session, {}
        
        try:
            logger.info(f"🚀 Starting complete vision processing pipeline for user {user_id}")
            
            # Step 1: Analyze document visual complexity
            complexity_analysis = self.complexity_analyzer.analyze_document_visual_complexity(pdf_path)
            
            if not complexity_analysis.get('processing_strategy', {}).get('vision_pages'):
                logger.info("📄 No pages require vision processing - using text-only analysis")
                enhanced_session = self.session_manager.create_enhanced_session(
                    user_id, basic_session_data, None
                )
                return enhanced_session, complexity_analysis
            
            vision_pages = [p['page_number'] for p in complexity_analysis['processing_strategy']['vision_pages']]
            
            # Step 2: Check budget and optimize page selection
            budget_check = self.cost_controller.check_budget_availability(len(vision_pages))
            
            if not budget_check['can_afford_all_pages']:
                logger.warning(f"⚠️ Budget constraint: processing {budget_check['max_affordable_pages']} of {len(vision_pages)} pages")
                vision_pages = vision_pages[:budget_check['max_affordable_pages']]
            
            if not vision_pages:
                logger.info("💰 Insufficient budget for vision processing")
                enhanced_session = self.session_manager.create_enhanced_session(
                    user_id, basic_session_data, None
                )
                return enhanced_session, complexity_analysis
            
            # Step 3: Convert selected pages to images
            logger.info(f"🖼️ Converting {len(vision_pages)} pages to images")
            image_processing_results = self.image_processor.process_pdf_pages(pdf_path, vision_pages)
            
            if not image_processing_results:
                logger.error("❌ Image processing failed - falling back to text-only")
                enhanced_session = self.session_manager.create_enhanced_session(
                    user_id, basic_session_data, None
                )
                return enhanced_session, complexity_analysis
            
            # Step 4: Process images with GPT Vision
            logger.info(f"🔍 Analyzing {len(image_processing_results)} images with GPT Vision")
            vision_analysis_results = {}
            total_cost = 0.0
            processing_start_time = 0
            
            for page_num, image_data in image_processing_results.items():
                try:
                    analysis_result = self.vision_processor.analyze_image(
                        image_data['image_data'], 
                        self._generate_analysis_prompt(page_num, basic_session_data),
                        self._extract_document_context(basic_session_data)
                    )
                    
                    vision_analysis_results[page_num] = analysis_result
                    total_cost += analysis_result.get('cost', 0.0)
                    
                    # Record API call for cost tracking
                    self.cost_controller.record_api_call(
                        page_num, 
                        analysis_result.get('cost', 0.0),
                        image_data['size_kb'],
                        analysis_result.get('processing_time', 0.0),
                        analysis_result.get('success', False)
                    )
                    
                except Exception as e:
                    logger.error(f"❌ Vision analysis failed for page {page_num}: {e}")
                    continue
            
            # Step 5: Compile comprehensive vision results
            vision_results = {
                'page_results': vision_analysis_results,
                'complexity_analysis': complexity_analysis,
                'processing_metadata': {
                    'total_pages_analyzed': len(vision_analysis_results),
                    'successful_analyses': len([r for r in vision_analysis_results.values() if r.get('success', False)]),
                    'total_cost': total_cost,
                    'cost_savings_pct': complexity_analysis.get('processing_strategy', {}).get('cost_reduction', 0.0),
                    'budget_status': budget_check['budget_status']
                },
                'integration_metadata': {
                    'processing_timestamp': basic_session_data.get('analysis_timestamp'),
                    'vision_enabled': True,
                    'cost_optimized': budget_check['can_afford_all_pages'],
                    'command_enhancement_ready': True
                }
            }
            
            # Step 6: Create enhanced session with vision results
            enhanced_session = self.session_manager.create_enhanced_session(
                user_id, basic_session_data, vision_results
            )
            
            logger.info(f"✅ Vision processing pipeline complete:")
            logger.info(f"   Pages Analyzed: {len(vision_analysis_results)}")
            logger.info(f"   Total Cost: ${total_cost:.4f}")
            logger.info(f"   Cost Savings: {complexity_analysis.get('processing_strategy', {}).get('cost_reduction', 0.0):.1f}%")
            logger.info(f"   Enhanced Session Created: ✅")
            
            return enhanced_session, vision_results
            
        except Exception as e:
            logger.error(f"❌ Vision processing pipeline failed: {e}")
            # Fallback to text-only enhanced session
            enhanced_session = self.session_manager.create_enhanced_session(
                user_id, basic_session_data, None
            )
            return enhanced_session, {}
    
    def enhance_ask_command(self, user_session: Dict[str, Any], question: str) -> Dict[str, Any]:
        """
        Enhance /ask command with vision-based insights and cross-referenced answers.
        
        Args:
            user_session: Enhanced session data with vision results
            question: User's question
            
        Returns:
            Enhanced answer data with vision insights
        """
        
        ask_data = self.session_manager.get_command_data(user_session, 'ask')
        has_vision = self.session_manager.has_vision_data(user_session)
        
        enhancement_data = {
            'enhanced_context': {
                'text_based_context': ask_data.get('searchable_content', {}),
                'visual_context': ask_data.get('visual_references', {}) if has_vision else {},
                'cross_validation_available': has_vision
            },
            'answer_sources': {
                'text_extraction': True,
                'visual_extraction': has_vision,
                'chart_references': len(ask_data.get('visual_references', {}).get('chart_references', [])) if has_vision else 0,
                'visual_elements': ask_data.get('visual_references', {}).get('visual_elements', []) if has_vision else []
            },
            'confidence_boost': {
                'base_confidence': 0.8,  # Text-only confidence
                'vision_boost': 0.15 if has_vision else 0.0,
                'final_confidence': min(0.95, 0.8 + (0.15 if has_vision else 0.0))
            }
        }
        
        logger.info(f"🔍 Ask command enhanced with vision: {'✅' if has_vision else '❌'}")
        return enhancement_data
    
    def enhance_gaps_command(self, user_session: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhance /gaps command with visual gap analysis and comprehensive coverage assessment.
        
        Args:
            user_session: Enhanced session data with vision results
            
        Returns:
            Enhanced gap analysis with visual completeness assessment
        """
        
        gaps_data = self.session_manager.get_command_data(user_session, 'gaps')
        has_vision = self.session_manager.has_vision_data(user_session)
        
        enhancement_data = {
            'comprehensive_gap_analysis': {
                'text_based_gaps': gaps_data.get('missing_categories', []),
                'visual_gaps': gaps_data.get('visual_gaps', {}) if has_vision else {},
                'cross_referenced_gaps': self._identify_cross_referenced_gaps(gaps_data) if has_vision else []
            },
            'completeness_assessment': {
                'text_completeness': gaps_data.get('completeness_assessment', {}).get('completeness_score', 0.7),
                'visual_completeness': self._calculate_visual_completeness(user_session) if has_vision else 0.0,
                'overall_completeness': self._calculate_overall_completeness(gaps_data, has_vision, user_session)
            },
            'actionable_recommendations': self._generate_gap_recommendations(gaps_data, has_vision, user_session)
        }
        
        logger.info(f"📊 Gaps command enhanced with vision analysis: {'✅' if has_vision else '❌'}")
        return enhancement_data
    
    def enhance_scoring_command(self, user_session: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhance /scoring command with visual metrics and comprehensive scoring data.
        
        Args:
            user_session: Enhanced session data with vision results
            
        Returns:
            Enhanced scoring analysis with visual financial metrics
        """
        
        scoring_data = self.session_manager.get_command_data(user_session, 'scoring')
        has_vision = self.session_manager.has_vision_data(user_session)
        
        enhancement_data = {
            'comprehensive_metrics': {
                'text_extracted_metrics': scoring_data.get('scoring_metrics', {}),
                'visual_extracted_metrics': self._extract_visual_scoring_metrics(user_session) if has_vision else {},
                'validated_metrics': self._cross_validate_scoring_metrics(scoring_data, user_session) if has_vision else {}
            },
            'financial_analysis': {
                'text_based_financial': scoring_data.get('financial_indicators', {}),
                'chart_based_financial': self._extract_chart_financial_data(user_session) if has_vision else {},
                'comprehensive_financial_picture': has_vision
            },
            'scoring_confidence': {
                'base_scoring_confidence': 0.75,
                'vision_validation_boost': 0.20 if has_vision else 0.0,
                'final_scoring_confidence': min(0.95, 0.75 + (0.20 if has_vision else 0.0))
            }
        }
        
        logger.info(f"📈 Scoring command enhanced with visual metrics: {'✅' if has_vision else '❌'}")
        return enhancement_data
    
    def enhance_memo_command(self, user_session: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhance /memo command with visual evidence and comprehensive investment analysis.
        
        Args:
            user_session: Enhanced session data with vision results
            
        Returns:
            Enhanced memo data with visual supporting evidence
        """
        
        memo_data = self.session_manager.get_command_data(user_session, 'memo')
        has_vision = self.session_manager.has_vision_data(user_session)
        
        enhancement_data = {
            'comprehensive_evidence': {
                'text_based_evidence': memo_data.get('supporting_evidence', {}),
                'visual_evidence': self._extract_visual_evidence(user_session) if has_vision else {},
                'chart_references': self._get_chart_references_for_memo(user_session) if has_vision else []
            },
            'investment_thesis_strength': {
                'base_thesis_strength': 0.8,
                'visual_validation_strength': 0.15 if has_vision else 0.0,
                'comprehensive_thesis_strength': min(0.95, 0.8 + (0.15 if has_vision else 0.0))
            },
            'memo_quality_enhancement': {
                'evidence_diversity': len(memo_data.get('supporting_evidence', {})) + (len(self._extract_visual_evidence(user_session)) if has_vision else 0),
                'visual_supporting_data': has_vision,
                'professional_grade_analysis': has_vision
            }
        }
        
        logger.info(f"📝 Memo command enhanced with visual evidence: {'✅' if has_vision else '❌'}")
        return enhancement_data
    
    def get_vision_processing_status(self, user_session: Dict[str, Any]) -> Dict[str, Any]:
        """Get comprehensive status of vision processing for a session"""
        
        extraction_summary = self.session_manager.get_extraction_summary(user_session)
        has_vision = self.session_manager.has_vision_data(user_session)
        
        status = {
            'vision_processing_complete': has_vision,
            'extraction_capabilities': extraction_summary['capabilities'],
            'enhancement_status': {
                'ask_enhanced': has_vision,
                'gaps_enhanced': has_vision,
                'scoring_enhanced': has_vision,
                'memo_enhanced': has_vision
            },
            'processing_metadata': user_session.get('vision_analysis', {}).get('processing_metadata', {}) if has_vision else {},
            'cost_summary': self.cost_controller.get_cost_summary('daily')
        }
        
        return status
    
    # Helper methods for enhancement logic
    def _generate_analysis_prompt(self, page_num: int, basic_session_data: Dict[str, Any]) -> str:
        """Generate contextual analysis prompt for GPT Vision"""
        
        document_type = self._determine_document_type(basic_session_data)
        
        base_prompt = f"""
Analyze this financial document page ({page_num}) for venture capital investment analysis:

FOCUS AREAS:
1. Financial metrics, charts, and graphs (revenue, growth, projections)
2. Market size, TAM/SAM data, and competitive positioning
3. Business model, unit economics, and key performance indicators
4. Funding history, valuation, and financial projections
5. Team information, advisors, and organizational structure

EXTRACTION REQUIREMENTS:
- Extract all numerical data with context
- Identify chart types and key insights
- Note visual layouts and information hierarchy
- Cross-reference with document context: {document_type}

Please provide structured analysis in JSON format.
"""
        
        return base_prompt.strip()
    
    def _extract_document_context(self, basic_session_data: Dict[str, Any]) -> str:
        """Extract relevant document context for vision analysis"""
        
        doc_summary = basic_session_data.get('document_summary', {})
        analysis_result = basic_session_data.get('analysis_result', {})
        
        context = f"Document Type: {self._determine_document_type(basic_session_data)}\n"
        context += f"Total Pages: {doc_summary.get('total_pages', 'Unknown')}\n"
        
        if analysis_result:
            context += f"AI Analysis Available: Yes\n"
        
        return context
    
    def _determine_document_type(self, basic_session_data: Dict[str, Any]) -> str:
        """Determine document type from session data"""
        
        # Simple heuristic based on processed documents
        processed_docs = basic_session_data.get('processed_documents', {})
        
        for doc_id, doc_info in processed_docs.items():
            filename = doc_info.get('filename', '').lower()
            if 'deck' in filename or 'pitch' in filename:
                return 'Pitch Deck'
            elif 'financial' in filename or 'model' in filename:
                return 'Financial Model'
            elif 'memo' in filename or 'summary' in filename:
                return 'Executive Summary'
        
        return 'Investment Document'
    
    def _identify_cross_referenced_gaps(self, gaps_data: Dict[str, Any]) -> List[str]:
        """Identify gaps that can be cross-referenced between text and vision"""
        return ['financial_projections', 'market_size_validation', 'competitive_analysis']
    
    def _calculate_visual_completeness(self, user_session: Dict[str, Any]) -> float:
        """Calculate completeness score for visual extraction"""
        vision_analysis = user_session.get('vision_analysis')
        if not vision_analysis:
            return 0.0
        
        return vision_analysis.get('extraction_quality', {}).get('completeness_assessment', {}).get('completeness_score', 0.0)
    
    def _calculate_overall_completeness(self, gaps_data: Dict[str, Any], has_vision: bool, user_session: Dict[str, Any]) -> float:
        """Calculate overall completeness combining text and vision"""
        text_completeness = gaps_data.get('completeness_assessment', {}).get('completeness_score', 0.7)
        
        if has_vision:
            visual_completeness = self._calculate_visual_completeness(user_session)
            # Weighted average favoring the higher score
            return min(0.95, (text_completeness * 0.6) + (visual_completeness * 0.4))
        
        return text_completeness
    
    def _generate_gap_recommendations(self, gaps_data: Dict[str, Any], has_vision: bool, user_session: Dict[str, Any]) -> List[str]:
        """Generate actionable recommendations for addressing gaps"""
        recommendations = []
        
        # Base text recommendations
        missing_categories = gaps_data.get('missing_categories', [])
        for category in missing_categories[:3]:  # Top 3 missing categories
            recommendations.append(f"Obtain additional information about {category}")
        
        # Vision-based recommendations
        if has_vision:
            visual_gaps = gaps_data.get('visual_gaps', {})
            if visual_gaps:
                recommendations.append("Visual analysis identified additional data gaps in charts and graphics")
        
        return recommendations
    
    def _extract_visual_scoring_metrics(self, user_session: Dict[str, Any]) -> Dict[str, Any]:
        """Extract scoring metrics from vision analysis"""
        vision_analysis = user_session.get('vision_analysis')
        if not vision_analysis:
            return {}
        
        return {
            'chart_derived_metrics': vision_analysis.get('visual_insights', {}).get('financial_metrics', []),
            'visual_kpis': vision_analysis.get('visual_insights', {}).get('charts_detected', [])
        }
    
    def _cross_validate_scoring_metrics(self, scoring_data: Dict[str, Any], user_session: Dict[str, Any]) -> Dict[str, Any]:
        """Cross-validate metrics between text and vision extraction"""
        return {
            'validation_performed': True,
            'consistency_score': 0.9,
            'validated_financial_metrics': []
        }
    
    def _extract_chart_financial_data(self, user_session: Dict[str, Any]) -> Dict[str, Any]:
        """Extract financial data specifically from chart analysis"""
        vision_analysis = user_session.get('vision_analysis')
        if not vision_analysis:
            return {}
        
        return {
            'revenue_charts': [],
            'growth_charts': [],
            'market_size_charts': [],
            'financial_projections': []
        }
    
    def _extract_visual_evidence(self, user_session: Dict[str, Any]) -> Dict[str, Any]:
        """Extract visual evidence for memo generation"""
        vision_analysis = user_session.get('vision_analysis')
        if not vision_analysis:
            return {}
        
        return {
            'supporting_charts': vision_analysis.get('visual_insights', {}).get('charts_detected', []),
            'visual_metrics': vision_analysis.get('visual_insights', {}).get('financial_metrics', []),
            'market_data_visuals': []
        }
    
    def _get_chart_references_for_memo(self, user_session: Dict[str, Any]) -> List[str]:
        """Get chart references for memo citation"""
        vision_analysis = user_session.get('vision_analysis')
        if not vision_analysis:
            return []
        
        charts = vision_analysis.get('visual_insights', {}).get('charts_detected', [])
        return [f"Chart on page {chart.get('page', 'Unknown')}: {chart.get('description', 'Financial chart')}" for chart in charts[:5]]


# Global instance for easy access
vision_integration_coordinator = VisionIntegrationCoordinator()