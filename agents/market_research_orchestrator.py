"""
Market Research Orchestrator for DataRoom Intelligence
Coordinates multiple specialized agents for comprehensive market intelligence

Phase 2A: Multi-Agent Market Intelligence System
"""

import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from .base_agent import BaseAgent
from .market_detection import MarketDetectionAgent, MarketProfile
from utils.logger import get_logger

logger = get_logger(__name__)

def get_mock_market_intelligence_result():
    """Return mock data for testing without GPT-4 calls"""
    from dataclasses import dataclass
    from typing import Dict, Any

    @dataclass
    class MockMarketProfile:
        primary_vertical: str = "cleantech"
        sub_vertical: str = "water treatment"
        business_model: str = "Direct-to-Business, Technology Licensing"
        target_market: str = "B2B, specifically pharmaceutical and cosmetics industries"
        geographic_focus: str = "Europe, expanding to North America"
        confidence_score: float = 0.85
        clarity_score: int = 9
        consistency_score: int = 8
        specificity_score: int = 9
        data_quality_score: int = 7

    @dataclass
    class MockResult:
        market_profile: MockMarketProfile = MockMarketProfile()
        critical_assessment: Dict[str, str] = None
        intelligence_summary: str = "Mock analysis completed"

        def __post_init__(self):
            if self.critical_assessment is None:
                self.critical_assessment = {
                    "market_reality_check": "The startup's claim of TAM €1.6B seems optimistic but not unreasonable for the water treatment sector. However, the path from €40M SOM to €15M revenue in 5 years requires aggressive market penetration that may face regulatory and adoption challenges.",
                    "competitive_concern": "No mention of major competitors like Veolia, Suez, or emerging cleantech players. The 60% energy reduction claim needs independent validation. Patents pending status creates IP risk if not granted.",
                    "business_model_assessment": "B2B licensing model is sound but requires significant upfront investment in customer education and regulatory compliance. Revenue projections seem aggressive for hardware sales in conservative pharmaceutical industry."
                }

    return MockResult()

class MarketIntelligenceResult:
    """Comprehensive market intelligence analysis result"""

    def __init__(self):
        self.market_profile: Optional[MarketProfile] = None
        self.competitive_analysis: Dict[str, Any] = {}
        self.market_validation: Dict[str, Any] = {}
        self.critical_assessment: Dict[str, Any] = {}
        self.timestamp = datetime.now().isoformat()
        self.processing_steps: List[str] = []
        self.confidence_score: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            'market_profile': self.market_profile.to_dict() if self.market_profile else {},
            'competitive_analysis': self.competitive_analysis,
            'market_validation': self.market_validation,
            'critical_assessment': self.critical_assessment,
            'timestamp': self.timestamp,
            'processing_steps': self.processing_steps,
            'confidence_score': self.confidence_score
        }

class MarketResearchOrchestrator(BaseAgent):
    """Orchestrates multi-agent market research analysis"""

    def __init__(self):
        super().__init__("Market Research Orchestrator")
        self.market_detector = MarketDetectionAgent()
        # Future agents will be added here in subsequent weeks
        # self.competitor_analyst = CompetitiveIntelAgent()
        # self.market_validator = MarketSizingValidator()
        # self.report_generator = CriticalReportAgent()

    def perform_market_intelligence(self, processed_documents: List[Dict[str, Any]],
                                  document_summary: Dict[str, Any]) -> MarketIntelligenceResult:
        """Orchestrate comprehensive market intelligence analysis"""
        try:
            logger.info("🔍 Starting comprehensive market intelligence analysis...")

            # Check if we're in test mode
            import os
            if os.getenv('TEST_MODE', 'false').lower() == 'true':
                logger.info("🧪 TEST MODE: Using mock data instead of GPT-4")
                return get_mock_market_intelligence_result()

            result = MarketIntelligenceResult()

            # Step 1: Market Detection (Week 1.1 - Current Implementation)
            logger.info("🎢 Step 1/4: Market Detection and Vertical Classification")
            result.processing_steps.append("Market Detection Started")

            market_profile = self.market_detector.detect_vertical(processed_documents, document_summary)
            result.market_profile = market_profile
            result.processing_steps.append(f"Market Detected: {market_profile.vertical} -> {market_profile.sub_vertical}")

            # Step 2: Competitive Analysis (Week 1.2 - Future Implementation)
            logger.info("🎢 Step 2/4: Competitive Analysis (Future - Week 1.2)")
            result.competitive_analysis = {
                'status': 'planned_for_week_1_2',
                'description': 'Crunchbase API integration for competitor discovery',
                'market_vertical': market_profile.vertical
            }
            result.processing_steps.append("Competitive Analysis: Planned for Week 1.2")

            # Step 3: Market Validation (Week 1.3 - Future Implementation)
            logger.info("🎢 Step 3/4: Market Validation (Future - Week 1.3)")
            result.market_validation = {
                'status': 'planned_for_week_1_3',
                'description': 'TAM/SAM claim validation with external data',
                'target_market': market_profile.target_market
            }
            result.processing_steps.append("Market Validation: Planned for Week 1.3")

            # Step 4: Critical Assessment (Current - Basic Implementation)
            logger.info("🎢 Step 4/4: Critical Assessment Generation")
            critical_assessment = self._generate_critical_assessment(market_profile, processed_documents)
            result.critical_assessment = critical_assessment
            result.processing_steps.append("Critical Assessment: Generated")

            # Calculate overall confidence
            result.confidence_score = self._calculate_overall_confidence(result)

            logger.info(f"✅ Market intelligence analysis completed with confidence: {result.confidence_score:.2f}")
            return result

        except Exception as e:
            logger.error(f"❌ Market intelligence analysis failed: {e}")
            result = MarketIntelligenceResult()
            result.processing_steps.append(f"ERROR: {str(e)}")
            return result

    def _generate_critical_assessment(self, market_profile: MarketProfile,
                                     processed_documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate critical assessment based on market detection"""
        try:
            logger.info("🧐 Generating critical market assessment...")

            # Prepare context for critical analysis
            document_context = self._prepare_document_context(processed_documents, max_content_length=8000)

            system_prompt = """
ROLE: Market Sizing Expert & BS Detector
TASK: Validate market claims with brutal honesty
CONTEXT: Startups always inflate market size - find the truth

Your job is to critically assess market claims and provide honest, evidence-based analysis.
Look for red flags, unrealistic assumptions, and missing competitive context.

Provide JSON response with:
- market_reality_check: honest assessment of market claims
- red_flags: specific concerns about market positioning
- missing_competitive_context: competitors or threats not mentioned
- market_timing_assessment: is this the right time for this market?
- realistic_tam_sam: more realistic market size estimates if provided
- go_no_go_factors: critical factors for investment decision
"""

            user_prompt = f"""
Analyze this startup's market positioning with brutal honesty:

DETECTED MARKET PROFILE:
- Vertical: {market_profile.vertical}
- Sub-vertical: {market_profile.sub_vertical}
- Target Market: {market_profile.target_market}
- Geographic Focus: {market_profile.geo_focus}
- Business Model: {market_profile.business_model}

DOCUMENT CONTENT:
{document_context}

Provide critical assessment focusing on:
1. Are the market size claims realistic?
2. What major competitors are missing from their analysis?
3. Is the market timing right?
4. What are the biggest red flags in their market approach?
5. What would make you say GO vs NO GO on this market opportunity?

Be brutally honest - this analysis will be used for investment decisions.
"""

            response = self._call_openai(system_prompt, user_prompt, max_tokens=1000, temperature=0.2)

            # Parse response into structured format
            fallback_structure = {
                'market_reality_check': 'Analysis failed',
                'red_flags': [],
                'missing_competitive_context': [],
                'market_timing_assessment': 'Unknown',
                'realistic_tam_sam': 'Not analyzed',
                'go_no_go_factors': []
            }

            critical_data = self._extract_json_from_response(response, fallback_structure)

            logger.info("✅ Critical assessment generated")
            return critical_data

        except Exception as e:
            logger.error(f"❌ Critical assessment failed: {e}")
            return {
                'market_reality_check': f'Assessment failed: {str(e)}',
                'red_flags': ['Technical analysis error'],
                'missing_competitive_context': [],
                'market_timing_assessment': 'Unknown due to error',
                'realistic_tam_sam': 'Not analyzed',
                'go_no_go_factors': ['Technical analysis needs resolution']
            }

    def _calculate_overall_confidence(self, result: MarketIntelligenceResult) -> float:
        """Calculate overall confidence score for market intelligence"""
        try:
            confidence_factors = []

            # Market detection confidence
            if result.market_profile:
                confidence_factors.append(result.market_profile.confidence_score)

            # Analysis completeness (currently only market detection is implemented)
            analysis_completeness = 0.25  # 1/4 agents currently implemented
            confidence_factors.append(analysis_completeness)

            # Critical assessment quality (basic implementation)
            if result.critical_assessment and 'red_flags' in result.critical_assessment:
                assessment_quality = 0.7  # Basic assessment available
                confidence_factors.append(assessment_quality)

            return sum(confidence_factors) / len(confidence_factors) if confidence_factors else 0.0

        except Exception as e:
            logger.error(f"❌ Confidence calculation failed: {e}")
            return 0.0

    def analyze(self, processed_documents: List[Dict[str, Any]],
               document_summary: Dict[str, Any]) -> Dict[str, Any]:
        """Implementation of base class analyze method"""
        intelligence_result = self.perform_market_intelligence(processed_documents, document_summary)
        return {
            'agent': 'market_research_orchestrator',
            'analysis_type': 'comprehensive_market_intelligence',
            'results': intelligence_result.to_dict(),
            'status': 'completed' if intelligence_result.confidence_score > 0.6 else 'needs_improvement'
        }
