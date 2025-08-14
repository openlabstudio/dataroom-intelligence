"""
Market Validation Agent for DataRoom Intelligence
Validates market size claims (TAM/SAM/SOM), timing, and opportunity assessment

Phase 2B.1 - TASK-002: Market Validation Implementation
"""

import os
import json
from typing import Dict, List, Any, Optional
from .base_agent import BaseAgent
from utils.logger import get_logger

logger = get_logger(__name__)

class MarketValidationProfile:
    """Data structure for market validation results"""
    
    def __init__(self):
        self.tam_assessment: Dict[str, Any] = {}
        self.sam_assessment: Dict[str, Any] = {}
        self.som_assessment: Dict[str, Any] = {}
        self.market_timing: str = ""
        self.market_trends: List[str] = []
        self.validation_score: float = 0.0
        self.reality_check: str = ""
        self.red_flags: List[str] = []
        self.opportunities: List[str] = []
        self.confidence_score: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'tam_assessment': self.tam_assessment,
            'sam_assessment': self.sam_assessment,
            'som_assessment': self.som_assessment,
            'market_timing': self.market_timing,
            'market_trends': self.market_trends,
            'validation_score': self.validation_score,
            'reality_check': self.reality_check,
            'red_flags': self.red_flags,
            'opportunities': self.opportunities,
            'confidence_score': self.confidence_score
        }

class MarketValidationAgent(BaseAgent):
    """Specialized agent for validating market size and opportunity claims"""
    
    def __init__(self):
        super().__init__("Market Validation")
        self.market_benchmarks = {
            'fintech': {'tam_typical': '$500B', 'growth_rate': '15%', 'maturity': 'mature'},
            'healthtech': {'tam_typical': '$300B', 'growth_rate': '22%', 'maturity': 'growing'},
            'enterprise': {'tam_typical': '$200B', 'growth_rate': '12%', 'maturity': 'mature'},
            'cleantech': {'tam_typical': '$150B', 'growth_rate': '25%', 'maturity': 'emerging'},
            'edtech': {'tam_typical': '$100B', 'growth_rate': '18%', 'maturity': 'growing'}
        }
    
    def validate_market_opportunity(self, market_profile: Dict[str, Any], 
                                  processed_documents: List[Dict[str, Any]],
                                  document_summary: Dict[str, Any]) -> MarketValidationProfile:
        """Main method to validate market opportunity and sizing"""
        try:
            logger.info("📈 Starting market validation analysis...")
            
            # Check TEST MODE first
            if os.getenv('TEST_MODE', 'false').lower() == 'true':
                logger.info("🧪 TEST MODE: Returning mock market validation data")
                return self._get_mock_validation_data(market_profile)
            
            # Real implementation
            logger.info("🔍 Validating market claims from documents...")
            
            # Prepare document context
            document_context = self._prepare_document_context(processed_documents, max_content_length=12000)
            
            # Create market validation prompts
            system_prompt = self._get_validation_system_prompt()
            user_prompt = self._get_validation_user_prompt(market_profile, document_context, document_summary)
            
            # Call OpenAI for market validation
            response = self._call_openai(system_prompt, user_prompt, max_tokens=1200, temperature=0.3)
            
            logger.debug(f"Market validation response: {response[:200]}...")
            
            # Parse response into MarketValidationProfile
            validation_profile = self._parse_validation_response(response)
            
            # Log key findings
            logger.info(f"✅ Market validation completed")
            logger.info(f"📊 Validation score: {validation_profile.validation_score:.2f}")
            logger.info(f"⏰ Market timing: {validation_profile.market_timing}")
            logger.info(f"🚩 Red flags found: {len(validation_profile.red_flags)}")
            logger.info(f"📊 Confidence: {validation_profile.confidence_score:.2f}")
            
            return validation_profile
            
        except Exception as e:
            logger.error(f"❌ Market validation analysis failed: {e}")
            return self._get_fallback_validation_data()
    
    def _get_mock_validation_data(self, market_profile: Dict[str, Any]) -> MarketValidationProfile:
        """Return mock market validation data for TEST MODE"""
        profile = MarketValidationProfile()
        
        # Mock data based on detected market
        vertical = market_profile.get('vertical', 'unknown').lower()
        benchmarks = self.market_benchmarks.get(vertical, self.market_benchmarks['enterprise'])
        
        profile.tam_assessment = {
            'claimed_tam': '$1.6B',
            'realistic_tam': benchmarks['tam_typical'],
            'assessment': 'Reasonable but optimistic',
            'methodology': 'Top-down approach with industry data'
        }
        
        profile.sam_assessment = {
            'claimed_sam': '$400M',
            'realistic_sam': f"~25% of TAM ({benchmarks['tam_typical']})",
            'assessment': 'Achievable with good execution',
            'geographic_factor': 'European focus limits initial SAM'
        }
        
        profile.som_assessment = {
            'claimed_som': '$40M',
            'realistic_som': '2-5% of SAM achievable in 5 years',
            'assessment': 'Aggressive but possible',
            'timeframe': '5-year projection'
        }
        
        profile.market_timing = 'Good - regulatory tailwinds and ESG focus'
        
        profile.market_trends = [
            'Increasing regulatory pressure on sustainability',
            f'Growing adoption in {vertical} sector',
            'Rising costs driving efficiency demand',
            'Post-COVID digital transformation acceleration'
        ]
        
        profile.validation_score = 7.5  # out of 10
        
        profile.reality_check = f'Claims are optimistic but within reason for {vertical} market. TAM methodology appears sound, but SAM/SOM projections require strong execution and market penetration.'
        
        profile.red_flags = [
            'Revenue projections assume rapid adoption curve',
            'Limited discussion of customer acquisition costs',
            'Competitive response not fully considered'
        ]
        
        profile.opportunities = [
            'First-mover advantage in specific niche',
            'Strong regulatory tailwinds supporting adoption',
            'Potential for adjacent market expansion'
        ]
        
        profile.confidence_score = 0.75
        
        logger.info(f"🧪 Generated mock validation data for {vertical} vertical")
        return profile
    
    def _get_validation_system_prompt(self) -> str:
        """System prompt for market validation"""
        return """
ROLE: Senior Market Research Analyst at top-tier consulting firm
TASK: Validate market size claims and opportunity assessment with brutal honesty
CONTEXT: Investment decisions depend on realistic market assessments

You are an expert at validating TAM/SAM/SOM claims and market opportunity assessments.
Your analysis must be realistic and identify both opportunities and red flags.

Key Validation Areas:
1. TAM (Total Addressable Market): Is the overall market size realistic?
2. SAM (Serviceable Addressable Market): Can they realistically serve this segment?
3. SOM (Serviceable Obtainable Market): Can they capture this share?
4. Market Timing: Is now the right time for this opportunity?
5. Market Trends: What macro trends support/threaten this opportunity?
6. Reality Check: Are the projections realistic or overly optimistic?

Respond with JSON format:
{
  "tam_assessment": {
    "claimed_tam": "amount claimed",
    "realistic_tam": "your assessment",
    "assessment": "realistic/optimistic/unrealistic",
    "methodology": "evaluation of their approach"
  },
  "sam_assessment": {
    "claimed_sam": "amount claimed", 
    "realistic_sam": "your assessment",
    "assessment": "evaluation",
    "geographic_factor": "impact of geography"
  },
  "som_assessment": {
    "claimed_som": "amount claimed",
    "realistic_som": "your assessment", 
    "assessment": "evaluation",
    "timeframe": "timeline assessment"
  },
  "market_timing": "early/good/late - with reasoning",
  "market_trends": ["trend 1", "trend 2", "trend 3"],
  "validation_score": 0.0-10.0,
  "reality_check": "honest assessment of claims",
  "red_flags": ["flag 1", "flag 2"],
  "opportunities": ["opportunity 1", "opportunity 2"],
  "confidence_score": 0.0-1.0
}
"""
    
    def _get_validation_user_prompt(self, market_profile: Dict[str, Any],
                                   document_context: str,
                                   document_summary: Dict[str, Any]) -> str:
        """User prompt with market and document context"""
        return f"""
Validate the market opportunity claims for this startup:

MARKET PROFILE:
- Vertical: {market_profile.get('vertical', 'unknown')}
- Sub-vertical: {market_profile.get('sub_vertical', 'unknown')}
- Target Market: {market_profile.get('target_market', 'unknown')}
- Business Model: {market_profile.get('business_model', 'unknown')}
- Geographic Focus: {market_profile.get('geo_focus', 'unknown')}

DOCUMENT SUMMARY:
- Total documents: {document_summary.get('total_documents', 0)}
- Document types: {document_summary.get('document_types', {})}

DOCUMENT CONTENT:
{document_context}

Based on this information, validate:
1. TAM/SAM/SOM claims - are they realistic for this market?
2. Market timing - is this the right time for this opportunity?
3. Market trends - what macro trends support or threaten this?
4. Revenue projections - are the growth assumptions realistic?
5. Market penetration - can they achieve claimed market share?
6. Geographic factors - how does location impact opportunity?
7. Competitive dynamics - how will competition affect market capture?

Be brutally honest about:
- Unrealistic growth assumptions
- Overly optimistic market sizing
- Missing competitive considerations
- Timing risks or opportunities
- Execution challenges

Provide your validation in the JSON format specified.
"""
    
    def _parse_validation_response(self, response: str) -> MarketValidationProfile:
        """Parse OpenAI response into MarketValidationProfile object"""
        profile = MarketValidationProfile()
        
        fallback_structure = {
            'tam_assessment': {'claimed_tam': 'Unknown', 'assessment': 'Analysis failed'},
            'sam_assessment': {'claimed_sam': 'Unknown', 'assessment': 'Analysis failed'},
            'som_assessment': {'claimed_som': 'Unknown', 'assessment': 'Analysis failed'},
            'market_timing': 'Unknown',
            'market_trends': ['Analysis incomplete'],
            'validation_score': 0.0,
            'reality_check': 'Validation analysis failed',
            'red_flags': ['Analysis incomplete'],
            'opportunities': [],
            'confidence_score': 0.0
        }
        
        try:
            # Extract JSON from response
            parsed_data = self._extract_json_from_response(response, fallback_structure)
            
            # Populate MarketValidationProfile
            profile.tam_assessment = parsed_data.get('tam_assessment', fallback_structure['tam_assessment'])
            profile.sam_assessment = parsed_data.get('sam_assessment', fallback_structure['sam_assessment'])
            profile.som_assessment = parsed_data.get('som_assessment', fallback_structure['som_assessment'])
            profile.market_timing = parsed_data.get('market_timing', 'Unknown')
            profile.market_trends = parsed_data.get('market_trends', [])
            profile.validation_score = min(10.0, max(0.0, float(parsed_data.get('validation_score', 0.0))))
            profile.reality_check = parsed_data.get('reality_check', 'No assessment available')
            profile.red_flags = parsed_data.get('red_flags', [])
            profile.opportunities = parsed_data.get('opportunities', [])
            profile.confidence_score = min(1.0, max(0.0, float(parsed_data.get('confidence_score', 0.0))))
            
            return profile
            
        except Exception as e:
            logger.error(f"❌ Failed to parse validation response: {e}")
            return self._get_fallback_validation_data()
    
    def _get_fallback_validation_data(self) -> MarketValidationProfile:
        """Return fallback data when analysis fails"""
        profile = MarketValidationProfile()
        profile.red_flags = ['Market validation analysis failed - manual review required']
        profile.reality_check = 'Technical analysis error prevented validation'
        profile.confidence_score = 0.0
        return profile
    
    def analyze(self, processed_documents: List[Dict[str, Any]],
               document_summary: Dict[str, Any]) -> Dict[str, Any]:
        """Implementation of base class analyze method"""
        # For base class compatibility, create a basic market profile
        market_profile = {
            'vertical': 'unknown',
            'sub_vertical': 'unknown',
            'target_market': 'unknown',
            'business_model': 'unknown',
            'geo_focus': 'unknown'
        }
        
        validation_profile = self.validate_market_opportunity(market_profile, processed_documents, document_summary)
        
        return {
            'agent': 'market_validation',
            'analysis_type': 'market_opportunity_validation',
            'results': validation_profile.to_dict(),
            'status': 'completed' if validation_profile.confidence_score > 0.5 else 'low_confidence'
        }