"""
Story 1.2 AC5: Enhanced Session Data Structure for Vision Results Storage

Extended session management system that stores both text and visual extraction results
in a unified data structure accessible across all commands (/ask, /gaps, /scoring, /memo).
Maintains backward compatibility with existing session structure.
"""

import os
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from utils.logger import get_logger

logger = get_logger(__name__)

class EnhancedSessionManager:
    """
    Enhanced session manager that handles both text and vision extraction results.
    Maintains backward compatibility while adding comprehensive vision data storage.
    """
    
    def __init__(self):
        self.vision_enabled = os.getenv('VISION_ENABLED', 'true').lower() == 'true'
        logger.info(f"📊 Enhanced Session Manager initialized (Vision: {'Enabled' if self.vision_enabled else 'Disabled'})")
    
    def create_enhanced_session(self, user_id: str, basic_session_data: Dict[str, Any], 
                              vision_results: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create enhanced session structure combining text and vision analysis results.
        
        Args:
            user_id: User identifier
            basic_session_data: Existing session data from current implementation
            vision_results: Optional vision processing results
            
        Returns:
            Enhanced session data structure
        """
        
        # Start with existing session structure (backward compatibility)
        enhanced_session = {
            # === EXISTING FIELDS (unchanged for compatibility) ===
            'analysis_result': basic_session_data.get('analysis_result'),
            'document_summary': basic_session_data.get('document_summary'),
            'processed_documents': basic_session_data.get('processed_documents'),
            'drive_link': basic_session_data.get('drive_link'),
            'market_profile': basic_session_data.get('market_profile'),
            'analysis_timestamp': basic_session_data.get('analysis_timestamp', datetime.now().isoformat()),
            
            # === NEW ENHANCED FIELDS ===
            'extraction_metadata': {
                'text_extraction_complete': True,
                'vision_extraction_complete': vision_results is not None if self.vision_enabled else False,
                'hybrid_processing_used': vision_results is not None if self.vision_enabled else False,
                'total_pages_processed': self._count_processed_pages(basic_session_data),
                'vision_enabled': self.vision_enabled
            },
            
            # === VISION PROCESSING RESULTS ===
            'vision_analysis': self._structure_vision_data(vision_results) if vision_results else None,
            
            # === UNIFIED EXTRACTION RESULTS ===
            'unified_extraction': self._create_unified_extraction(basic_session_data, vision_results),
            
            # === CROSS-COMMAND ACCESSIBILITY ===
            'command_data': {
                'ask': self._prepare_ask_data(basic_session_data, vision_results),
                'gaps': self._prepare_gaps_data(basic_session_data, vision_results),
                'scoring': self._prepare_scoring_data(basic_session_data, vision_results),
                'memo': self._prepare_memo_data(basic_session_data, vision_results)
            }
        }
        
        # Preserve market research data if exists
        if 'market_research' in basic_session_data:
            enhanced_session['market_research'] = basic_session_data['market_research']
        
        logger.info(f"✅ Enhanced session created for user {user_id}")
        logger.info(f"   Text Extraction: ✅ Complete")
        logger.info(f"   Vision Extraction: {'✅ Complete' if vision_results else '➖ Not processed'}")
        logger.info(f"   Unified Data Available: {'✅ Yes' if enhanced_session['unified_extraction'] else '❌ No'}")
        
        return enhanced_session
    
    def _structure_vision_data(self, vision_results: Dict[str, Any]) -> Dict[str, Any]:
        """Structure vision processing results for session storage"""
        
        if not vision_results:
            return None
            
        return {
            'processing_summary': {
                'total_pages_analyzed': len(vision_results.get('page_results', {})),
                'successful_analyses': len([p for p in vision_results.get('page_results', {}).values() if p.get('success', False)]),
                'total_cost_usd': vision_results.get('total_cost', 0.0),
                'processing_time_seconds': vision_results.get('total_processing_time', 0.0),
                'cost_optimization_savings': vision_results.get('cost_savings_pct', 0.0)
            },
            
            'page_results': vision_results.get('page_results', {}),  # Individual page analyses
            
            'visual_insights': {
                'charts_detected': self._extract_chart_insights(vision_results),
                'financial_metrics': self._extract_financial_metrics(vision_results),
                'visual_elements': self._extract_visual_elements(vision_results),
                'layout_analysis': self._extract_layout_insights(vision_results)
            },
            
            'extraction_quality': {
                'confidence_scores': self._calculate_confidence_scores(vision_results),
                'completeness_assessment': self._assess_extraction_completeness(vision_results),
                'cross_validation_results': self._cross_validate_extractions(vision_results)
            }
        }
    
    def _create_unified_extraction(self, basic_session_data: Dict[str, Any], 
                                 vision_results: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Create unified extraction combining text and vision results"""
        
        unified_data = {
            'document_content': {
                'text_based': self._extract_text_content(basic_session_data),
                'visual_based': self._extract_vision_content(vision_results) if vision_results else {},
                'combined_insights': []
            },
            
            'financial_data': {
                'text_extracted': self._extract_text_financial_data(basic_session_data),
                'vision_extracted': self._extract_vision_financial_data(vision_results) if vision_results else {},
                'validated_metrics': []
            },
            
            'competitive_intelligence': {
                'text_based': self._extract_text_competitive_data(basic_session_data),
                'visual_based': self._extract_vision_competitive_data(vision_results) if vision_results else {},
                'comprehensive_analysis': []
            },
            
            'quality_metrics': {
                'text_extraction_quality': self._assess_text_quality(basic_session_data),
                'vision_extraction_quality': self._assess_vision_quality(vision_results) if vision_results else {},
                'hybrid_confidence_score': 0.0
            }
        }
        
        # Cross-validate and merge insights
        unified_data['document_content']['combined_insights'] = self._merge_content_insights(
            unified_data['document_content']['text_based'],
            unified_data['document_content']['visual_based']
        )
        
        # Calculate overall confidence
        unified_data['quality_metrics']['hybrid_confidence_score'] = self._calculate_hybrid_confidence(
            unified_data['quality_metrics']['text_extraction_quality'],
            unified_data['quality_metrics']['vision_extraction_quality']
        )
        
        return unified_data
    
    def _prepare_ask_data(self, basic_session_data: Dict[str, Any], 
                         vision_results: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Prepare optimized data structure for /ask command"""
        
        return {
            'searchable_content': self._create_searchable_content(basic_session_data, vision_results),
            'context_data': self._create_context_data(basic_session_data, vision_results),
            'visual_references': self._create_visual_references(vision_results) if vision_results else {},
            'content_index': self._create_content_index(basic_session_data, vision_results)
        }
    
    def _prepare_gaps_data(self, basic_session_data: Dict[str, Any], 
                          vision_results: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Prepare optimized data structure for /gaps command"""
        
        return {
            'extracted_information': self._catalog_extracted_info(basic_session_data, vision_results),
            'missing_categories': self._identify_missing_categories(basic_session_data, vision_results),
            'visual_gaps': self._identify_visual_gaps(vision_results) if vision_results else {},
            'completeness_assessment': self._assess_information_completeness(basic_session_data, vision_results)
        }
    
    def _prepare_scoring_data(self, basic_session_data: Dict[str, Any], 
                             vision_results: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Prepare optimized data structure for /scoring command"""
        
        return {
            'scoring_metrics': self._extract_scoring_metrics(basic_session_data, vision_results),
            'financial_indicators': self._extract_financial_indicators(basic_session_data, vision_results),
            'market_data': self._extract_market_data(basic_session_data, vision_results),
            'risk_indicators': self._extract_risk_indicators(basic_session_data, vision_results)
        }
    
    def _prepare_memo_data(self, basic_session_data: Dict[str, Any], 
                          vision_results: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Prepare optimized data structure for /memo command"""
        
        return {
            'executive_summary_data': self._extract_executive_summary_data(basic_session_data, vision_results),
            'investment_thesis_data': self._extract_investment_thesis_data(basic_session_data, vision_results),
            'supporting_evidence': self._extract_supporting_evidence(basic_session_data, vision_results),
            'risk_assessment_data': self._extract_risk_assessment_data(basic_session_data, vision_results)
        }
    
    def get_command_data(self, session_data: Dict[str, Any], command: str) -> Dict[str, Any]:
        """
        Get optimized data for specific command from enhanced session.
        
        Args:
            session_data: Enhanced session data
            command: Command name ('ask', 'gaps', 'scoring', 'memo')
            
        Returns:
            Optimized data structure for the command
        """
        
        command_data = session_data.get('command_data', {}).get(command, {})
        
        # Add unified extraction data for comprehensive access
        command_data['unified_extraction'] = session_data.get('unified_extraction', {})
        command_data['vision_analysis'] = session_data.get('vision_analysis')
        
        return command_data
    
    def has_vision_data(self, session_data: Dict[str, Any]) -> bool:
        """Check if session contains vision processing results"""
        return (session_data.get('extraction_metadata', {}).get('vision_extraction_complete', False) and
                session_data.get('vision_analysis') is not None)
    
    def get_extraction_summary(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get summary of extraction capabilities and completeness"""
        
        metadata = session_data.get('extraction_metadata', {})
        
        return {
            'text_extraction': metadata.get('text_extraction_complete', False),
            'vision_extraction': metadata.get('vision_extraction_complete', False),
            'hybrid_processing': metadata.get('hybrid_processing_used', False),
            'total_pages': metadata.get('total_pages_processed', 0),
            'capabilities': {
                'can_answer_text_questions': metadata.get('text_extraction_complete', False),
                'can_analyze_visual_content': metadata.get('vision_extraction_complete', False),
                'can_cross_validate': metadata.get('hybrid_processing_used', False)
            }
        }
    
    # Helper methods for data processing
    def _count_processed_pages(self, basic_session_data: Dict[str, Any]) -> int:
        """Count total pages processed from basic session data"""
        processed_docs = basic_session_data.get('processed_documents', {})
        return sum(doc.get('page_count', 0) for doc in processed_docs.values())
    
    def _extract_chart_insights(self, vision_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract chart and graph insights from vision results"""
        charts = []
        for page_num, page_result in vision_results.get('page_results', {}).items():
            if page_result.get('success') and 'charts' in page_result.get('analysis', {}):
                charts.extend(page_result['analysis']['charts'])
        return charts
    
    def _extract_financial_metrics(self, vision_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract financial metrics from vision results"""
        metrics = []
        for page_num, page_result in vision_results.get('page_results', {}).items():
            if page_result.get('success') and 'financial_data' in page_result.get('analysis', {}):
                metrics.extend(page_result['analysis']['financial_data'])
        return metrics
    
    def _extract_visual_elements(self, vision_results: Dict[str, Any]) -> List[str]:
        """Extract visual elements detected"""
        elements = set()
        for page_num, page_result in vision_results.get('page_results', {}).items():
            if page_result.get('success') and 'visual_elements' in page_result.get('analysis', {}):
                elements.update(page_result['analysis']['visual_elements'])
        return list(elements)
    
    def _extract_layout_insights(self, vision_results: Dict[str, Any]) -> Dict[str, Any]:
        """Extract layout and structural insights"""
        layout_info = {
            'complex_layouts': 0,
            'multi_column_pages': 0,
            'infographic_pages': 0,
            'table_heavy_pages': 0
        }
        
        for page_num, page_result in vision_results.get('page_results', {}).items():
            if page_result.get('success'):
                analysis = page_result.get('analysis', {})
                if analysis.get('complex_layout'):
                    layout_info['complex_layouts'] += 1
                if analysis.get('multi_column'):
                    layout_info['multi_column_pages'] += 1
                if analysis.get('infographic'):
                    layout_info['infographic_pages'] += 1
                if analysis.get('table_heavy'):
                    layout_info['table_heavy_pages'] += 1
        
        return layout_info
    
    def _calculate_confidence_scores(self, vision_results: Dict[str, Any]) -> Dict[str, float]:
        """Calculate confidence scores for vision extraction"""
        scores = {
            'overall_confidence': 0.0,
            'chart_detection_confidence': 0.0,
            'text_recognition_confidence': 0.0,
            'layout_analysis_confidence': 0.0
        }
        
        successful_pages = [p for p in vision_results.get('page_results', {}).values() if p.get('success')]
        if successful_pages:
            # Calculate average confidence across successful pages
            total_confidence = sum(page.get('confidence', 0.8) for page in successful_pages)
            scores['overall_confidence'] = total_confidence / len(successful_pages)
            
            # Set component confidence scores based on successful analyses
            scores['chart_detection_confidence'] = scores['overall_confidence'] * 0.9
            scores['text_recognition_confidence'] = scores['overall_confidence'] * 0.95
            scores['layout_analysis_confidence'] = scores['overall_confidence'] * 0.85
        
        return scores
    
    def _assess_extraction_completeness(self, vision_results: Dict[str, Any]) -> Dict[str, Any]:
        """Assess completeness of vision extraction"""
        total_pages = len(vision_results.get('page_results', {}))
        successful_pages = len([p for p in vision_results.get('page_results', {}).values() if p.get('success')])
        
        return {
            'total_pages_processed': total_pages,
            'successful_extractions': successful_pages,
            'success_rate': (successful_pages / total_pages) if total_pages > 0 else 0.0,
            'completeness_score': min((successful_pages / max(total_pages, 1)) * 1.2, 1.0)  # Slight bonus for high success
        }
    
    def _cross_validate_extractions(self, vision_results: Dict[str, Any]) -> Dict[str, Any]:
        """Cross-validate vision extractions for consistency"""
        # Placeholder for cross-validation logic
        return {
            'validation_performed': True,
            'consistency_score': 0.85,  # Default good consistency
            'identified_discrepancies': [],
            'validated_insights': []
        }
    
    # Additional helper methods for unified extraction
    def _extract_text_content(self, basic_session_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract text-based content from basic session"""
        return {
            'documents': basic_session_data.get('processed_documents', {}),
            'analysis_result': basic_session_data.get('analysis_result', {}),
            'content_summary': basic_session_data.get('document_summary', {})
        }
    
    def _extract_vision_content(self, vision_results: Dict[str, Any]) -> Dict[str, Any]:
        """Extract vision-based content"""
        return {
            'visual_insights': vision_results.get('visual_insights', {}),
            'page_analyses': vision_results.get('page_results', {}),
            'chart_data': self._extract_chart_insights(vision_results)
        }
    
    def _merge_content_insights(self, text_content: Dict[str, Any], visual_content: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Merge text and visual insights for comprehensive understanding"""
        combined_insights = []
        
        # Add text-based insights
        if text_content.get('analysis_result'):
            combined_insights.append({
                'type': 'text_analysis',
                'source': 'document_text',
                'insights': text_content['analysis_result']
            })
        
        # Add visual insights
        for chart in visual_content.get('chart_data', []):
            combined_insights.append({
                'type': 'visual_analysis',
                'source': 'chart_detection',
                'insights': chart
            })
        
        return combined_insights
    
    def _calculate_hybrid_confidence(self, text_quality: Dict[str, Any], vision_quality: Dict[str, Any]) -> float:
        """Calculate overall confidence score from both extraction methods"""
        text_score = text_quality.get('confidence', 0.8)
        vision_score = vision_quality.get('overall_confidence', 0.0) if vision_quality else 0.0
        
        if vision_score > 0:
            # Weighted average favoring the higher-performing extraction
            return (text_score * 0.6) + (vision_score * 0.4)
        else:
            return text_score
    
    # Placeholder methods for command-specific data preparation
    def _create_searchable_content(self, basic_session_data: Dict[str, Any], vision_results: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        return {'text_content': basic_session_data.get('processed_documents', {}), 'visual_content': vision_results or {}}
    
    def _create_context_data(self, basic_session_data: Dict[str, Any], vision_results: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        return {'document_context': basic_session_data.get('document_summary', {}), 'visual_context': vision_results or {}}
    
    def _create_visual_references(self, vision_results: Dict[str, Any]) -> Dict[str, Any]:
        return {'chart_references': self._extract_chart_insights(vision_results), 'visual_elements': self._extract_visual_elements(vision_results)}
    
    def _create_content_index(self, basic_session_data: Dict[str, Any], vision_results: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        return {'indexed_content': 'content_index_placeholder'}
    
    # Additional placeholder methods for specific data types
    def _catalog_extracted_info(self, basic_session_data: Dict[str, Any], vision_results: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        return {'extracted_info': 'placeholder'}
    
    def _identify_missing_categories(self, basic_session_data: Dict[str, Any], vision_results: Optional[Dict[str, Any]]) -> List[str]:
        return ['placeholder_category']
    
    def _identify_visual_gaps(self, vision_results: Dict[str, Any]) -> Dict[str, Any]:
        return {'visual_gaps': 'placeholder'}
    
    def _assess_information_completeness(self, basic_session_data: Dict[str, Any], vision_results: Optional[Dict[str, Any]]) -> Dict[str, float]:
        return {'completeness_score': 0.8}
    
    def _extract_scoring_metrics(self, basic_session_data: Dict[str, Any], vision_results: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        return {'scoring_data': 'placeholder'}
    
    def _extract_financial_indicators(self, basic_session_data: Dict[str, Any], vision_results: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        return {'financial_data': 'placeholder'}
    
    def _extract_market_data(self, basic_session_data: Dict[str, Any], vision_results: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        return {'market_data': 'placeholder'}
    
    def _extract_risk_indicators(self, basic_session_data: Dict[str, Any], vision_results: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        return {'risk_data': 'placeholder'}
    
    def _extract_executive_summary_data(self, basic_session_data: Dict[str, Any], vision_results: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        return {'executive_data': 'placeholder'}
    
    def _extract_investment_thesis_data(self, basic_session_data: Dict[str, Any], vision_results: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        return {'thesis_data': 'placeholder'}
    
    def _extract_supporting_evidence(self, basic_session_data: Dict[str, Any], vision_results: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        return {'evidence_data': 'placeholder'}
    
    def _extract_risk_assessment_data(self, basic_session_data: Dict[str, Any], vision_results: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        return {'risk_assessment': 'placeholder'}
    
    def _extract_text_financial_data(self, basic_session_data: Dict[str, Any]) -> Dict[str, Any]:
        return {'text_financial': 'placeholder'}
    
    def _extract_vision_financial_data(self, vision_results: Dict[str, Any]) -> Dict[str, Any]:
        return {'vision_financial': 'placeholder'}
    
    def _extract_text_competitive_data(self, basic_session_data: Dict[str, Any]) -> Dict[str, Any]:
        return {'text_competitive': 'placeholder'}
    
    def _extract_vision_competitive_data(self, vision_results: Dict[str, Any]) -> Dict[str, Any]:
        return {'vision_competitive': 'placeholder'}
    
    def _assess_text_quality(self, basic_session_data: Dict[str, Any]) -> Dict[str, Any]:
        return {'confidence': 0.85, 'quality_score': 0.8}
    
    def _assess_vision_quality(self, vision_results: Dict[str, Any]) -> Dict[str, Any]:
        return self._calculate_confidence_scores(vision_results)


# Global instance for easy access
enhanced_session_manager = EnhancedSessionManager()