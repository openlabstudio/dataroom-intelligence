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
                 business_model: str = "", confidence_score: float = 0.0):
        self.vertical = vertical
        self.sub_vertical = sub_vertical  
        self.target_market = target_market
        self.geo_focus = geo_focus
        self.business_model = business_model
        self.confidence_score = confidence_score
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'vertical': self.vertical,
            'sub_vertical': self.sub_vertical,
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
        """System prompt for market detection"""
        return """
ROLE: Senior Market Intelligence Analyst at top-tier VC fund
TASK: Analyze documents to precisely identify target market and vertical
CONTEXT: Wrong market analysis kills deals - your reputation depends on accuracy

You are an expert at identifying market verticals, business models, and target markets from startup documents.
Your analysis will be used for critical investment decisions.

Market Categories Available:
- FinTech: neobank, payments, lending, insurtech, wealthtech, regtech, cryptocurrency  
- HealthTech: digital_health, medtech, biotech, pharmatech, healthai, telemedicine
- Enterprise: saas, hr_tech, sales_tech, marketing_tech, productivity, cybersecurity
- Consumer: ecommerce, social, gaming, entertainment, food_delivery, mobility
- DeepTech: ai_ml, robotics, iot, blockchain, quantum, space_tech
- Sustainability: cleantech, climate_tech, renewable_energy, carbon_management
- EdTech: online_learning, corporate_training, language_learning, skill_development

Respond with JSON format only:
{
  "vertical": "primary market vertical",
  "sub_vertical": "specific sub-category", 
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
        return f"""
Analyze the following startup documents to identify the market vertical and positioning:

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
            'vertical': 'unknown',
            'sub_vertical': 'unspecified',
            'target_market': 'unclear',
            'geo_focus': 'unknown',
            'business_model': 'unspecified',
            'confidence_score': 0.0,
            'key_indicators': []
        }
        
        try:
            # Extract JSON from response
            parsed_data = self._extract_json_from_response(response, fallback_structure)
            
            # Create MarketProfile with validated data
            return MarketProfile(
                vertical=parsed_data.get('vertical', 'unknown'),
                sub_vertical=parsed_data.get('sub_vertical', 'unspecified'),
                target_market=parsed_data.get('target_market', 'unclear'),
                geo_focus=parsed_data.get('geo_focus', 'unknown'),
                business_model=parsed_data.get('business_model', 'unspecified'),
                confidence_score=min(1.0, max(0.0, float(parsed_data.get('confidence_score', 0.0))))
            )
            
        except Exception as e:
            logger.error(f"❌ Failed to parse market response: {e}")
            return MarketProfile(vertical="unknown", confidence_score=0.0)
    
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
