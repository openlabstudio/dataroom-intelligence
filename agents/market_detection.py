"""
Market Detection Agent for DataRoom Intelligence
Analyzes documents to identify market vertical, sub-vertical, target market, and geographic focus

Phase 2A - Week 1.1: Market Detection Engine
"""

import json
from typing import Dict, List, Any, Optional
from .base_agent import BaseAgent
from utils.logger import get_logger

logger = get_logger(__name__)

class MarketProfile:
    """Data structure for market profile analysis results"""
    
    def __init__(self, vertical: str = "", sub_vertical: str = "", 
                 target_market: str = "", geo_focus: str = "", 
                 business_model: str = "", confidence_score: float = 0.0,
                 solution: str = "", industry: str = ""):
        # MEJORAS CALIDAD: Market Taxonomy hierarchy
        self.solution = solution  # Level 1: Most specific (e.g., "electrochemical wastewater treatment")
        self.sub_vertical = sub_vertical  # Level 2: Sub-vertical (e.g., "water treatment technology")
        self.vertical = vertical  # Level 3: Vertical (e.g., "cleantech sustainability")
        self.industry = industry  # Level 4: Broad industry (e.g., "environmental technology")
        self.target_market = target_market
        self.geo_focus = geo_focus
        self.business_model = business_model
        self.confidence_score = confidence_score
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'solution': self.solution,  # New: Most specific solution
            'sub_vertical': self.sub_vertical,
            'vertical': self.vertical,
            'industry': self.industry,  # New: Broad industry category
            'target_market': self.target_market,
            'geo_focus': self.geo_focus,
            'business_model': self.business_model,
            'confidence_score': self.confidence_score
        }

class MarketDetectionAgent(BaseAgent):
    """Specialized agent for detecting and analyzing market positioning"""
    
    def __init__(self):
        super().__init__("Market Detection")
        self.market_categories = {
            'fintech': ['neobank', 'payments', 'lending', 'insurtech', 'wealthtech', 'regtech', 'cryptocurrency'],
            'healthtech': ['digital_health', 'medtech', 'biotech', 'pharmatech', 'healthai', 'telemedicine'],
            'enterprise': ['saas', 'hr_tech', 'sales_tech', 'marketing_tech', 'productivity', 'cybersecurity'],
            'consumer': ['ecommerce', 'social', 'gaming', 'entertainment', 'food_delivery', 'mobility'],
            'deeptech': ['ai_ml', 'robotics', 'iot', 'blockchain', 'quantum', 'space_tech'],
            'sustainability': ['cleantech', 'climate_tech', 'renewable_energy', 'carbon_management'],
            'edtech': ['online_learning', 'corporate_training', 'language_learning', 'skill_development']
        }
    
    def detect_vertical(self, processed_documents: List[Dict[str, Any]], 
                       document_summary: Dict[str, Any]) -> MarketProfile:
        """Main method to detect market vertical from documents"""
        try:
            logger.info("🔍 Starting market vertical detection...")
            
            # Prepare document context for analysis
            document_context = self._prepare_document_context(processed_documents, max_content_length=15000)
            
            # Create specialized market detection prompt
            system_prompt = self._get_market_detection_system_prompt()
            user_prompt = self._get_market_detection_user_prompt(document_context, document_summary)
            
            # Call OpenAI for market analysis
            response = self._call_openai(system_prompt, user_prompt, max_tokens=800, temperature=0.2)
            
            logger.debug(f"Market detection response: {response[:200]}...")
            
            # Parse response into MarketProfile
            market_profile = self._parse_market_response(response)
            
            logger.info(f"✅ Market detected: {market_profile.vertical} -> {market_profile.sub_vertical}")
            logger.info(f"📍 Geographic focus: {market_profile.geo_focus}")
            logger.info(f"🎯 Target market: {market_profile.target_market}")
            logger.info(f"📊 Confidence: {market_profile.confidence_score:.2f}")
            
            return market_profile
            
        except Exception as e:
            logger.error(f"❌ Market detection failed: {e}")
            return MarketProfile(vertical="unknown", confidence_score=0.0)
    
    def _get_market_detection_system_prompt(self) -> str:
        """System prompt for market detection with enhanced taxonomy"""
        return """
ROLE: Senior Market Intelligence Analyst at top-tier VC fund
TASK: Analyze documents to precisely identify market taxonomy with 4-level hierarchy
CONTEXT: Wrong market analysis kills deals - your reputation depends on accuracy

You are an expert at identifying market verticals, business models, and target markets from startup documents.
Your analysis must provide a complete 4-level market taxonomy for investment decisions.

Market Taxonomy Hierarchy (CRITICAL):
1. SOLUTION: The most specific product/service (e.g., "electrochemical wastewater treatment", "AI-powered invoice factoring")
2. SUB_VERTICAL: The specific market category (e.g., "water treatment technology", "invoice financing")  
3. VERTICAL: The broader market vertical (e.g., "cleantech sustainability", "fintech")
4. INDUSTRY: The broadest industry category (e.g., "environmental technology", "financial technology")

Market Categories Available:
- FinTech: neobank, payments, lending, insurtech, wealthtech, regtech, cryptocurrency  
- HealthTech: digital_health, medtech, biotech, pharmatech, healthai, telemedicine
- Enterprise: saas, hr_tech, sales_tech, marketing_tech, productivity, cybersecurity
- Consumer: ecommerce, social, gaming, entertainment, food_delivery, mobility
- DeepTech: ai_ml, robotics, iot, blockchain, quantum, space_tech
- Sustainability: cleantech, climate_tech, renewable_energy, carbon_management, water_treatment
- EdTech: online_learning, corporate_training, language_learning, skill_development

Respond with JSON format only:
{
  "solution": "most specific product/service description",
  "sub_vertical": "specific market sub-category",
  "vertical": "primary market vertical",
  "industry": "broadest industry category (e.g., 'financial technology', 'environmental technology')",
  "target_market": "B2B/B2C/B2B2C and specific customer segment",
  "geo_focus": "geographic market focus (US, EU, Global, LATAM, etc.)",
  "business_model": "SaaS, Marketplace, Direct-to-Consumer, etc.",
  "confidence_score": 0.85,
  "key_indicators": ["evidence from documents that led to this classification"]
}
"""
    
    def _get_market_detection_user_prompt(self, document_context: str, 
                                         document_summary: Dict[str, Any]) -> str:
        """User prompt with document context"""
        
        # Extract key business information from document_summary
        business_description = document_summary.get('business_description', '')
        executive_summary = document_summary.get('executive_summary', '')
        
        return f"""
Analyze the following startup information to identify the market vertical and positioning:

BUSINESS DESCRIPTION:
{business_description}

EXECUTIVE SUMMARY:
{executive_summary}

DOCUMENT SUMMARY:
- Total documents: {document_summary.get('total_documents', 0)}
- Document types: {document_summary.get('document_types', {})}

DOCUMENT CONTENT:
{document_context}

Based on this information, identify:
1. Primary market vertical (fintech, healthtech, enterprise, consumer, deeptech, sustainability, edtech)
2. Specific sub-vertical within that category
3. Target market and customer segment
4. Geographic focus and expansion plans
5. Business model type
6. Your confidence level in this analysis (0.0 to 1.0)

Provide your analysis in JSON format as specified in the system prompt.
"""
    
    def _parse_market_response(self, response: str) -> MarketProfile:
        """Parse OpenAI response into MarketProfile object"""
        fallback_structure = {
            'solution': 'unspecified',  # New: Most specific solution
            'vertical': 'unknown',
            'sub_vertical': 'unspecified',
            'industry': 'technology',  # New: Broad industry
            'target_market': 'unclear',
            'geo_focus': 'unknown',
            'business_model': 'unspecified',
            'confidence_score': 0.0,
            'key_indicators': []
        }
        
        try:
            # Extract JSON from response
            parsed_data = self._extract_json_from_response(response, fallback_structure)
            
            # MEJORAS CALIDAD: Extract solution and industry
            solution = parsed_data.get('solution', '')
            if not solution and 'sub_vertical' in parsed_data:
                # Fallback: Use sub_vertical as solution if not provided
                solution = parsed_data.get('sub_vertical', 'unspecified')
            
            # Determine industry from vertical
            vertical = parsed_data.get('vertical', 'unknown')
            industry = self._determine_industry_from_vertical(vertical)
            if 'industry' in parsed_data:
                industry = parsed_data.get('industry', industry)
            
            # Create MarketProfile with validated data
            return MarketProfile(
                solution=solution,  # Most specific
                sub_vertical=parsed_data.get('sub_vertical', 'unspecified'),
                vertical=vertical,
                industry=industry,  # Broadest category
                target_market=parsed_data.get('target_market', 'unclear'),
                geo_focus=parsed_data.get('geo_focus', 'unknown'),
                business_model=parsed_data.get('business_model', 'unspecified'),
                confidence_score=min(1.0, max(0.0, float(parsed_data.get('confidence_score', 0.0))))
            )
            
        except Exception as e:
            logger.error(f"❌ Failed to parse market response: {e}")
            return MarketProfile(vertical="unknown", confidence_score=0.0)
    
    def _determine_industry_from_vertical(self, vertical: str) -> str:
        """Determine broad industry category from vertical"""
        vertical_lower = vertical.lower()
        
        if any(term in vertical_lower for term in ['fintech', 'payment', 'banking', 'insurance']):
            return 'financial technology'
        elif any(term in vertical_lower for term in ['health', 'medical', 'pharma', 'bio']):
            return 'healthcare technology'
        elif any(term in vertical_lower for term in ['clean', 'sustain', 'environment', 'green']):
            return 'environmental technology'
        elif any(term in vertical_lower for term in ['edu', 'learn', 'training']):
            return 'education technology'
        elif any(term in vertical_lower for term in ['retail', 'commerce', 'consumer']):
            return 'consumer technology'
        elif any(term in vertical_lower for term in ['enterprise', 'b2b', 'saas']):
            return 'enterprise technology'
        else:
            return 'technology'  # Default broad category
    
    def analyze(self, processed_documents: List[Dict[str, Any]], 
               document_summary: Dict[str, Any]) -> Dict[str, Any]:
        """Implementation of base class analyze method"""
        market_profile = self.detect_vertical(processed_documents, document_summary)
        return {
            'agent': 'market_detection',
            'analysis_type': 'market_vertical_detection',
            'results': market_profile.to_dict(),
            'status': 'completed' if market_profile.confidence_score > 0.5 else 'low_confidence'
        }
