"""
Market Research Orchestrator for DataRoom Intelligence
Coordinates multiple specialized agents for comprehensive market intelligence

Phase 2B: Chain of Thought with Progress Tracking
"""

import json
import time
from typing import Dict, List, Any, Optional
from datetime import datetime
from .base_agent import BaseAgent
from .market_detection import MarketDetectionAgent, MarketProfile
from .competitive_intelligence import CompetitiveIntelligenceAgent
from .market_validation import MarketValidationAgent
from .progress_tracker import ProgressTracker, create_test_progress_tracker
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
    """Orchestrates multi-agent market research analysis with progress tracking"""

    def __init__(self):
        super().__init__("Market Research Orchestrator")
        self.market_detector = MarketDetectionAgent()
        # TASK-001: Competitive Intelligence Agent
        self.competitive_analyzer = CompetitiveIntelligenceAgent()
        # TASK-002: Market Validation Agent  
        self.market_validator = MarketValidationAgent()
        # Future agents (Phase 2B.1 continuation)
        # self.funding_benchmarker = FundingBenchmarker()
        # self.critical_synthesizer = CriticalSynthesizer()
        
        # Progress tracker will be initialized per analysis
        self.progress_tracker = None

    def perform_market_intelligence(self, processed_documents: List[Dict[str, Any]],
                                  document_summary: Dict[str, Any]) -> MarketIntelligenceResult:
        """Orchestrate comprehensive market intelligence analysis with progress tracking"""
        try:
            logger.info("🔍 Starting comprehensive market intelligence analysis...")
            
            # Initialize progress tracker (no Slack integration yet)
            self.progress_tracker = create_test_progress_tracker()
            logger.info("📊 Progress tracker initialized (test mode - no Slack)")

            # Check if we're in test mode
            import os
            if os.getenv('TEST_MODE', 'false').lower() == 'true':
                logger.info("🧪 TEST MODE: Using mock data with simulated progress")
                return self._perform_test_mode_analysis()

            result = MarketIntelligenceResult()

            # ==== PHASE 1: Market Detection (Agent 1) ====
            logger.info("🎯 PHASE 1/5: Market Detection and Profiling")
            self.progress_tracker.phases[0].status = "running"
            self.progress_tracker.phases[0].start_time = datetime.now()
            logger.info(f"Progress Update: {self.progress_tracker.format_progress_message()[:200]}...")
            result.processing_steps.append("Phase 1: Market Detection Started")

            market_profile = self.market_detector.detect_vertical(processed_documents, document_summary)
            result.market_profile = market_profile
            
            # Update progress tracker with detected market
            self.progress_tracker.detected_market = f"{market_profile.vertical}/{market_profile.sub_vertical}"
            self.progress_tracker.phases[0].status = "completed"
            self.progress_tracker.phases[0].end_time = datetime.now()
            self.progress_tracker.current_phase_index = 1
            
            result.processing_steps.append(f"Market Detected: {market_profile.vertical} -> {market_profile.sub_vertical}")
            logger.info(f"✅ Phase 1 Complete: {self.progress_tracker.detected_market}")

            # ==== PHASE 2: Competitive Intelligence (TASK-001) ====
            logger.info("🏢 PHASE 2/5: Competitive Intelligence Analysis")
            self.progress_tracker.phases[1].status = "running"
            self.progress_tracker.phases[1].start_time = datetime.now()
            
            # Use real competitive intelligence agent
            competitive_profile = self.competitive_analyzer.analyze_competitors(
                market_profile.to_dict(), processed_documents, document_summary
            )
            result.competitive_analysis = competitive_profile.to_dict()
            
            self.progress_tracker.phases[1].status = "completed"
            self.progress_tracker.phases[1].end_time = datetime.now()
            self.progress_tracker.current_phase_index = 2
            result.processing_steps.append("Phase 2: Competitive Intelligence Analysis")
            logger.info("✅ Phase 2 Complete: Competitive Intelligence")

            # ==== PHASE 3: Market Validation (TASK-002) ====
            logger.info("📈 PHASE 3/5: TAM/SAM Market Validation")
            self.progress_tracker.phases[2].status = "running"
            self.progress_tracker.phases[2].start_time = datetime.now()
            
            # Use real market validation agent
            validation_profile = self.market_validator.validate_market_opportunity(
                market_profile.to_dict(), processed_documents, document_summary
            )
            result.market_validation = validation_profile.to_dict()
            
            self.progress_tracker.phases[2].status = "completed"
            self.progress_tracker.phases[2].end_time = datetime.now()
            self.progress_tracker.current_phase_index = 3
            result.processing_steps.append("Phase 3: Market Validation Analysis")
            logger.info("✅ Phase 3 Complete: Market Validation")

            # ==== PHASE 4: Funding Benchmarking (Placeholder) ====
            logger.info("💰 PHASE 4/5: Funding & Metrics Benchmarking (Simulated)")
            self.progress_tracker.phases[3].status = "running"
            self.progress_tracker.phases[3].start_time = datetime.now()
            
            time.sleep(0.5)
            
            # Placeholder for future funding analysis
            self.progress_tracker.phases[3].status = "completed"
            self.progress_tracker.phases[3].end_time = datetime.now()
            self.progress_tracker.current_phase_index = 4
            result.processing_steps.append("Phase 4: Funding Benchmarking (Simulated)")
            logger.info("✅ Phase 4 Complete (Simulated)")

            # ==== PHASE 5: Critical Synthesis (Current Implementation) ====
            logger.info("🧠 PHASE 5/5: Critical Assessment & Synthesis")
            self.progress_tracker.phases[4].status = "running"
            self.progress_tracker.phases[4].start_time = datetime.now()
            
            critical_assessment = self._generate_critical_assessment(market_profile, processed_documents)
            result.critical_assessment = critical_assessment
            
            self.progress_tracker.phases[4].status = "completed"
            self.progress_tracker.phases[4].end_time = datetime.now()
            self.progress_tracker.current_phase_index = 5
            result.processing_steps.append("Phase 5: Critical Assessment Generated")
            logger.info("✅ Phase 5 Complete: Critical Synthesis")

            # Calculate overall confidence
            result.confidence_score = self._calculate_overall_confidence(result)

            # Log final progress state
            logger.info("📊 Final Progress State:")
            logger.info(self.progress_tracker.format_progress_message())
            logger.info(f"✅ Market intelligence analysis completed with confidence: {result.confidence_score:.2f}")
            
            return result

        except Exception as e:
            logger.error(f"❌ Market intelligence analysis failed: {e}")
            result = MarketIntelligenceResult()
            result.processing_steps.append(f"ERROR: {str(e)}")
            return result

    def _perform_test_mode_analysis(self) -> Any:
        """Perform simulated analysis in TEST_MODE with progress tracking"""
        logger.info("🧪 Running TEST_MODE analysis with simulated progress")
        
        # Simulate all 5 phases
        phases_simulation = [
            ("market_detection", "FinTech/Payments", 0.5),
            ("competitive_intelligence", "Analyzing competitors", 0.5),
            ("market_validation", "Validating TAM/SAM", 0.5),
            ("funding_benchmarking", "Benchmarking metrics", 0.5),
            ("critical_synthesis", "Generating assessment", 0.5)
        ]
        
        for i, (phase_id, description, delay) in enumerate(phases_simulation):
            self.progress_tracker.phases[i].status = "running"
            self.progress_tracker.phases[i].start_time = datetime.now()
            
            if i == 0:  # Set detected market in first phase
                self.progress_tracker.detected_market = "FinTech/Payments"
            
            logger.info(f"🔄 Phase {i+1}/5: {description}")
            time.sleep(delay)  # Simulate processing
            
            self.progress_tracker.phases[i].status = "completed"
            self.progress_tracker.phases[i].end_time = datetime.now()
            self.progress_tracker.current_phase_index = i + 1
            
            logger.info(f"✅ Phase {i+1} complete")
        
        logger.info("🧪 TEST_MODE analysis complete with all phases simulated")
        return get_mock_market_intelligence_result()

    def _generate_critical_assessment(self, market_profile: MarketProfile,
                                     processed_documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate critical assessment based on market detection"""
        try:
            logger.info("🧐 Generating critical market assessment...")

            # Prepare context for critical analysis
            document_context = self._prepare_document_context(processed_documents, max_content_length=8000)

            system_prompt = """
ROLE: Senior Partner at top-tier VC fund making final investment decision
TASK: Synthesize market findings into brutal honest investment recommendation
CONTEXT: Your reputation depends on making the right call

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

            # Analysis completeness (2/5 agents currently real, 3 simulated)
            analysis_completeness = 0.4  # 2/5 agents currently implemented
            confidence_factors.append(analysis_completeness)

            # Critical assessment quality
            if result.critical_assessment and 'red_flags' in result.critical_assessment:
                assessment_quality = 0.8  # Good assessment available
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
