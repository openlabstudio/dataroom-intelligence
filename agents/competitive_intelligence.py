"""
Competitive Intelligence Agent for DataRoom Intelligence
Analyzes competitive landscape, identifies key competitors, and assesses market positioning

Phase 2B.1 - TASK-001: Competitive Intelligence Implementation
"""

import os
import json
from typing import Dict, List, Any, Optional
from .base_agent import BaseAgent
from utils.logger import get_logger

logger = get_logger(__name__)

class CompetitiveProfile:
    """Data structure for competitive analysis results"""

    def __init__(self):
        self.direct_competitors: List[Dict[str, str]] = []
        self.indirect_competitors: List[Dict[str, str]] = []
        self.competitive_advantages: List[str] = []
        self.competitive_risks: List[str] = []
        self.market_position: str = ""
        self.differentiation_factors: List[str] = []
        self.competitive_moat: str = ""
        self.threat_level: str = ""  # low, medium, high
        self.confidence_score: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            'direct_competitors': self.direct_competitors,
            'indirect_competitors': self.indirect_competitors,
            'competitive_advantages': self.competitive_advantages,
            'competitive_risks': self.competitive_risks,
            'market_position': self.market_position,
            'differentiation_factors': self.differentiation_factors,
            'competitive_moat': self.competitive_moat,
            'threat_level': self.threat_level,
            'confidence_score': self.confidence_score
        }

class CompetitiveIntelligenceAgent(BaseAgent):
    """Specialized agent for competitive landscape analysis"""

    def __init__(self):
        super().__init__("Competitive Intelligence")
        self.competitor_databases = {
            'fintech': ['Stripe', 'Square', 'PayPal', 'Adyen', 'Klarna', 'Revolut'],
            'healthtech': ['Teladoc', 'Babylon Health', 'Oscar Health', 'Ro', 'Hims'],
            'enterprise': ['Salesforce', 'HubSpot', 'Slack', 'Zoom', 'Monday.com'],
            'cleantech': ['Tesla', 'Sunrun', 'ChargePoint', 'Veolia', 'Suez'],
            'edtech': ['Coursera', 'Udemy', 'Duolingo', 'Chegg', 'Khan Academy']
        }

    def analyze_competitors(self, market_profile: Dict[str, Any],
                          processed_documents: List[Dict[str, Any]],
                          document_summary: Dict[str, Any]) -> CompetitiveProfile:
        """Main method to analyze competitive landscape"""
        try:
            logger.info("🏢 Starting competitive intelligence analysis...")

            # Check TEST MODE first
            if os.getenv('TEST_MODE', 'false').lower() == 'true':
                logger.info("🧪 TEST MODE: Returning mock competitive data")
                return self._get_mock_competitive_data(market_profile)

            # Real implementation
            logger.info("🔍 Analyzing competitive landscape from documents...")

            # Prepare document context
            document_context = self._prepare_document_context(processed_documents, max_content_length=12000)

            # Create competitive analysis prompts
            system_prompt = self._get_competitive_system_prompt()
            user_prompt = self._get_competitive_user_prompt(market_profile, document_context, document_summary)

            # Call OpenAI for competitive analysis
            response = self._call_openai(system_prompt, user_prompt, max_tokens=1200, temperature=0.3)

            logger.debug(f"Competitive analysis response: {response[:200]}...")

            # Parse response into CompetitiveProfile
            competitive_profile = self._parse_competitive_response(response)

            # Log key findings
            logger.info(f"✅ Found {len(competitive_profile.direct_competitors)} direct competitors")
            logger.info(f"⚠️ Threat level: {competitive_profile.threat_level}")
            logger.info(f"🛡️ Competitive moat: {competitive_profile.competitive_moat}")
            logger.info(f"📊 Confidence: {competitive_profile.confidence_score:.2f}")

            return competitive_profile

        except Exception as e:
            logger.error(f"❌ Competitive analysis failed: {e}")
            return self._get_fallback_competitive_data()

    def _get_mock_competitive_data(self, market_profile: Dict[str, Any]) -> CompetitiveProfile:
        """Return mock competitive data for TEST MODE"""
        profile = CompetitiveProfile()

        # Mock data based on detected market
        vertical = market_profile.get('vertical', 'unknown').lower()

        # Get relevant mock competitors for the vertical
        mock_competitors = self.competitor_databases.get(vertical, ['Generic Competitor A', 'Generic Competitor B'])

        profile.direct_competitors = [
            {
                'name': mock_competitors[0] if len(mock_competitors) > 0 else 'Direct Competitor A',
                'description': f'Leading {vertical} platform with $1B+ valuation',
                'strengths': 'Market leadership, brand recognition, funding',
                'market_share': '25%'
            },
            {
                'name': mock_competitors[1] if len(mock_competitors) > 1 else 'Direct Competitor B',
                'description': f'Fast-growing {vertical} challenger',
                'strengths': 'Innovation, customer focus, agility',
                'market_share': '15%'
            }
        ]

        profile.indirect_competitors = [
            {
                'name': 'Traditional Solution Provider',
                'description': 'Legacy industry player adapting to digital',
                'strengths': 'Established relationships, regulatory compliance',
                'market_share': '30%'
            }
        ]

        profile.competitive_advantages = [
            '60% lower cost than competitors',
            'Proprietary technology with patent pending',
            'Superior user experience (NPS 70+)',
            'First-mover in specific niche'
        ]

        profile.competitive_risks = [
            'Limited funding compared to competitors',
            'Competitors have stronger brand recognition',
            'Risk of platform giants entering the space',
            'Regulatory uncertainty in target markets'
        ]

        profile.market_position = 'Emerging challenger with differentiated approach'

        profile.differentiation_factors = [
            'AI-powered automation reducing manual work by 80%',
            'Focus on underserved SMB segment',
            'Vertical-specific solution vs horizontal competitors'
        ]

        profile.competitive_moat = 'Technology innovation and customer lock-in through data'
        profile.threat_level = 'medium'
        profile.confidence_score = 0.85

        logger.info(f"🧪 Generated mock competitive data for {vertical} vertical")
        return profile

    def _get_competitive_system_prompt(self) -> str:
        """System prompt for competitive analysis"""
        return """
ROLE: Senior Competitive Intelligence Analyst at top-tier VC fund
TASK: Analyze competitive landscape and identify threats/opportunities
CONTEXT: Investment decisions require brutal honesty about competition

You are an expert at competitive analysis with deep knowledge of startup ecosystems.
Your analysis must be realistic about competitive threats and differentiation.

Key Analysis Areas:
1. Direct Competitors: Companies solving same problem for same customers
2. Indirect Competitors: Alternative solutions or substitutes
3. Competitive Advantages: What makes this startup unique
4. Competitive Risks: Threats from existing or potential competitors
5. Market Position: Where startup fits in competitive landscape
6. Differentiation: Sustainable competitive advantages
7. Competitive Moat: Barriers to competition
8. Threat Assessment: Overall competitive threat level

Respond with JSON format:
{
  "direct_competitors": [
    {"name": "company", "description": "what they do", "strengths": "key strengths", "market_share": "estimate"}
  ],
  "indirect_competitors": [
    {"name": "company", "description": "what they do", "strengths": "key strengths", "market_share": "estimate"}
  ],
  "competitive_advantages": ["advantage 1", "advantage 2"],
  "competitive_risks": ["risk 1", "risk 2"],
  "market_position": "assessment of where startup fits",
  "differentiation_factors": ["factor 1", "factor 2"],
  "competitive_moat": "description of barriers to competition",
  "threat_level": "low/medium/high",
  "confidence_score": 0.0-1.0,
  "missing_competitor_info": ["what's not mentioned but should be"]
}
"""

    def _get_competitive_user_prompt(self, market_profile: Dict[str, Any],
                                    document_context: str,
                                    document_summary: Dict[str, Any]) -> str:
        """User prompt with market and document context"""
        return f"""
Analyze the competitive landscape for this startup:

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

Based on this information:
1. Identify direct competitors (companies mentioned or implied)
2. Identify indirect competitors and substitutes
3. Extract competitive advantages claimed by the startup
4. Assess competitive risks and threats
5. Determine market position and differentiation
6. Evaluate sustainability of competitive moat
7. Assess overall threat level from competition
8. Note any missing competitive information that should concern investors

Be brutally honest about competitive reality. Look for:
- Competitors NOT mentioned that should be
- Unrealistic competitive claims
- Weak differentiation
- Platform risk (could Google/Amazon/Microsoft do this?)

Provide your analysis in the JSON format specified.
"""

    def _parse_competitive_response(self, response: str) -> CompetitiveProfile:
        """Parse OpenAI response into CompetitiveProfile object"""
        profile = CompetitiveProfile()

        fallback_structure = {
            'direct_competitors': [],
            'indirect_competitors': [],
            'competitive_advantages': [],
            'competitive_risks': ['Analysis incomplete'],
            'market_position': 'Unknown',
            'differentiation_factors': [],
            'competitive_moat': 'Unclear',
            'threat_level': 'high',
            'confidence_score': 0.0,
            'missing_competitor_info': []
        }

        try:
            # Extract JSON from response
            parsed_data = self._extract_json_from_response(response, fallback_structure)

            # Populate CompetitiveProfile
            profile.direct_competitors = parsed_data.get('direct_competitors', [])
            profile.indirect_competitors = parsed_data.get('indirect_competitors', [])
            profile.competitive_advantages = parsed_data.get('competitive_advantages', [])
            profile.competitive_risks = parsed_data.get('competitive_risks', [])
            profile.market_position = parsed_data.get('market_position', 'Unknown')
            profile.differentiation_factors = parsed_data.get('differentiation_factors', [])
            profile.competitive_moat = parsed_data.get('competitive_moat', 'Unclear')
            profile.threat_level = parsed_data.get('threat_level', 'high')
            profile.confidence_score = min(1.0, max(0.0, float(parsed_data.get('confidence_score', 0.0))))

            # Add missing competitor info to risks if present
            missing_info = parsed_data.get('missing_competitor_info', [])
            if missing_info:
                profile.competitive_risks.extend([f"Missing info: {info}" for info in missing_info])

            return profile

        except Exception as e:
            logger.error(f"❌ Failed to parse competitive response: {e}")
            return self._get_fallback_competitive_data()

    def _get_fallback_competitive_data(self) -> CompetitiveProfile:
        """Return fallback data when analysis fails"""
        profile = CompetitiveProfile()
        profile.competitive_risks = ['Competitive analysis failed - manual review required']
        profile.threat_level = 'unknown'
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

        competitive_profile = self.analyze_competitors(market_profile, processed_documents, document_summary)

        return {
            'agent': 'competitive_intelligence',
            'analysis_type': 'competitive_landscape',
            'results': competitive_profile.to_dict(),
            'status': 'completed' if competitive_profile.confidence_score > 0.5 else 'low_confidence'
        }
