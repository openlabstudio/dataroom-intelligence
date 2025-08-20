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
        # FASE 2A: Enhanced structure for independent analysis + startup claims
        # Independent market analysis
        self.market_leaders: List[Dict[str, Any]] = []  # Major players with funding info
        self.similar_propositions: List[Dict[str, Any]] = []  # Similar startups with outcomes
        self.competitive_risks: List[str] = []  # Key risks from market analysis
        self.market_opportunities: List[str] = []  # Opportunities identified
        self.failure_patterns: List[str] = []  # Common failure patterns in similar startups
        
        # Startup claims (for PDF comparison later)
        self.startup_claimed_competitors: List[str] = []  # What startup claims
        self.startup_claimed_advantages: List[str] = []  # Their claimed differentiators
        
        # Analysis metadata
        self.market_position: str = ""  # Assessment of competitive landscape
        self.threat_level: str = ""  # low, medium, high
        self.sources: List[Dict[str, str]] = []  # Web search sources
        self.confidence_score: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            # Independent analysis for Slack
            'independent_analysis': {
                'market_leaders': self.market_leaders,
                'similar_propositions': self.similar_propositions,
                'competitive_risks': self.competitive_risks,
                'market_opportunities': self.market_opportunities,
                'failure_patterns': self.failure_patterns,
                'market_position': self.market_position,
                'threat_level': self.threat_level,
                'sources_count': len(self.sources),
                'confidence_score': self.confidence_score
            },
            # Startup claims for PDF comparison
            'startup_claims_extracted': {
                'claimed_competitors': self.startup_claimed_competitors,
                'claimed_advantages': self.startup_claimed_advantages
            },
            # Full sources for PDF
            'sources': self.sources
        }

class CompetitiveIntelligenceAgent(BaseAgent):
    """Specialized agent for competitive landscape analysis with integrated web search"""

    def __init__(self):
        super().__init__("Competitive Intelligence")
        # FASE 2A: Initialize web search engine
        self.web_search_engine = None  # Will be initialized on first use
        self.competitor_databases = {
            'fintech': ['Stripe', 'Square', 'PayPal', 'Adyen', 'Klarna', 'Revolut'],
            'healthtech': ['Teladoc', 'Babylon Health', 'Oscar Health', 'Ro', 'Hims'],
            'enterprise': ['Salesforce', 'HubSpot', 'Slack', 'Zoom', 'Monday.com'],
            'cleantech': ['Tesla', 'Sunrun', 'ChargePoint', 'Veolia', 'Suez'],
            'edtech': ['Coursera', 'Udemy', 'Duolingo', 'Chegg', 'Khan Academy']
        }
    
    def _init_web_search(self):
        """Lazy initialize web search engine"""
        if self.web_search_engine is None:
            try:
                from utils.web_search import WebSearchEngine
                self.web_search_engine = WebSearchEngine(provider='duckduckgo')
            except ImportError as e:
                logger.warning(f"Web search not available: {e}")
                self.web_search_engine = None

    def analyze_competitors(self, market_profile: Dict[str, Any],
                          processed_documents: List[Dict[str, Any]],
                          document_summary: Dict[str, Any]) -> CompetitiveProfile:
        """Main method to analyze competitive landscape with integrated web search"""
        try:
            logger.info("🏢 Starting competitive intelligence analysis with web search...")

            # Check TEST MODE first
            if os.getenv('TEST_MODE', 'false').lower() == 'true':
                logger.info("🧪 TEST MODE: Returning enhanced mock competitive data")
                return self._get_mock_competitive_data_enhanced(market_profile)

            # FASE 2A: Extract value proposition for targeted web search
            value_proposition = self._extract_value_proposition(processed_documents, document_summary)
            logger.info(f"🎯 Value proposition: {value_proposition}")

            # Step 1: Extract startup claims from documents
            startup_claims = self._extract_startup_claims(processed_documents, document_summary)
            
            # Step 2: Perform independent web search for competitive intelligence
            web_intelligence = self._perform_competitive_web_search(value_proposition, market_profile)
            
            # Step 3: Analyze with GPT-4 if available (combining both perspectives)
            gpt4_analysis = None
            if self._has_openai_key():
                gpt4_analysis = self._perform_gpt4_competitive_analysis(
                    market_profile, processed_documents, document_summary
                )
            
            # Step 4: Integrate all sources into comprehensive profile
            competitive_profile = self._integrate_competitive_intelligence(
                startup_claims, web_intelligence, gpt4_analysis
            )

            # Log key findings
            logger.info(f"✅ Found {len(competitive_profile.market_leaders)} market leaders")
            logger.info(f"⚠️ Found {len(competitive_profile.similar_propositions)} similar propositions")
            logger.info(f"📊 Threat level: {competitive_profile.threat_level}")
            logger.info(f"🔍 Sources analyzed: {len(competitive_profile.sources)}")

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
    
    # ========== FASE 2A: NEW METHODS FOR WEB SEARCH INTEGRATION ==========
    
    def _extract_value_proposition(self, documents: List[Dict], document_summary: Dict) -> str:
        """Extract value proposition for targeted web search"""
        try:
            # Initialize web search if needed
            self._init_web_search()
            
            if self.web_search_engine:
                from utils.web_search import ValuePropositionExtractor
                extractor = ValuePropositionExtractor()
                extraction = extractor.extract_simple(documents, document_summary)
                return extraction.get('value_proposition', 'innovative business solution')
            else:
                # Fallback to basic extraction
                return self._basic_value_prop_extraction(document_summary)
        except Exception as e:
            logger.warning(f"Value proposition extraction failed: {e}")
            return "innovative business solution"
    
    def _basic_value_prop_extraction(self, document_summary: Dict) -> str:
        """Basic fallback extraction without web_search module"""
        summary_text = str(document_summary.get('summary', '')).lower()
        
        # Look for key industry terms
        if 'fintech' in summary_text or 'payment' in summary_text:
            return "fintech payment solution"
        elif 'health' in summary_text or 'medical' in summary_text:
            return "healthcare technology solution"
        elif 'clean' in summary_text or 'sustain' in summary_text:
            return "cleantech sustainability solution"
        else:
            return "technology business solution"
    
    def _extract_startup_claims(self, documents: List[Dict], document_summary: Dict) -> Dict[str, Any]:
        """Extract what the startup claims about competitors and advantages"""
        claimed_competitors = []
        claimed_advantages = []
        
        # Simple extraction from document summary
        summary_text = str(document_summary.get('summary', ''))
        
        # Look for competitor mentions (basic pattern matching)
        import re
        competitor_patterns = [
            r'compete(?:s)? with ([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*)',
            r'competitors? (?:include|are) ([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*)',
            r'unlike ([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*)',
        ]
        
        for pattern in competitor_patterns:
            matches = re.findall(pattern, summary_text)
            claimed_competitors.extend(matches[:3])  # Limit to 3
        
        # Look for advantage claims
        advantage_keywords = ['unique', 'first', 'only', 'proprietary', 'patented', 'innovative']
        for keyword in advantage_keywords:
            if keyword in summary_text.lower():
                claimed_advantages.append(f"{keyword} solution")
        
        return {
            'claimed_competitors': list(set(claimed_competitors))[:5],
            'claimed_advantages': claimed_advantages[:5]
        }
    
    def _perform_competitive_web_search(self, value_proposition: str, 
                                       market_profile: Dict) -> Dict[str, Any]:
        """Perform web search for competitive intelligence"""
        try:
            # Initialize web search if needed
            self._init_web_search()
            
            if not self.web_search_engine:
                logger.warning("Web search engine not available")
                return {'sources': [], 'competitors': [], 'insights': []}
            
            # Build targeted search queries
            vertical = market_profile.get('vertical', 'technology')
            geo = market_profile.get('geo_focus', 'global')
            
            queries = [
                f"{value_proposition} competitors funding analysis",
                f"{value_proposition} failed startups case studies",
                f"similar companies {value_proposition} investor sentiment",
                f"{vertical} {geo} competitive landscape 2024"
            ]
            
            # Execute searches
            web_results = self.web_search_engine.search_multiple(queries[:3], max_results_per_query=3)
            
            # Process results for competitive intelligence
            return self._process_web_results_for_competition(web_results)
            
        except Exception as e:
            logger.error(f"Web search failed: {e}")
            return {'sources': [], 'competitors': [], 'insights': []}
    
    def _process_web_results_for_competition(self, web_results: Dict) -> Dict[str, Any]:
        """Process web search results into competitive intelligence"""
        competitive_intel = {
            'competitors': [],
            'failed_startups': [],
            'market_insights': [],
            'sources': []
        }
        
        # Extract competitors from search results
        for competitor in web_results.get('competitors_found', []):
            if isinstance(competitor, str):
                # Parse competitor info (e.g., "FactorX (AI invoice factoring)")
                parts = competitor.split('(')
                name = parts[0].strip() if parts else competitor
                desc = parts[1].replace(')', '').strip() if len(parts) > 1 else ''
                competitive_intel['competitors'].append({
                    'name': name,
                    'description': desc,
                    'source': 'web search'
                })
        
        # Extract insights
        for insight in web_results.get('expert_insights', []):
            if isinstance(insight, str) and len(insight) > 20:
                competitive_intel['market_insights'].append(insight[:200])
        
        # Track sources
        competitive_intel['sources'] = [{
            'type': 'web_search',
            'count': web_results.get('sources_count', 0),
            'queries': web_results.get('search_terms_used', [])
        }]
        
        return competitive_intel
    
    def _perform_gpt4_competitive_analysis(self, market_profile: Dict,
                                          documents: List[Dict],
                                          document_summary: Dict) -> Dict[str, Any]:
        """Perform GPT-4 analysis of competitive landscape"""
        try:
            # Prepare document context
            document_context = self._prepare_document_context(documents, max_content_length=8000)
            
            # Use existing prompt methods
            system_prompt = self._get_competitive_system_prompt()
            user_prompt = self._get_competitive_user_prompt(market_profile, document_context, document_summary)
            
            # Call OpenAI
            response = self._call_openai(system_prompt, user_prompt, max_tokens=1000, temperature=0.3)
            
            # Parse response
            return self._parse_gpt4_response(response)
            
        except Exception as e:
            logger.error(f"GPT-4 analysis failed: {e}")
            return {}
    
    def _parse_gpt4_response(self, response: str) -> Dict[str, Any]:
        """Parse GPT-4 response into structured format"""
        try:
            # Try to extract JSON from response
            import json
            import re
            
            # Look for JSON in response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                # Fallback parsing
                return {'raw_response': response}
        except Exception as e:
            logger.warning(f"Failed to parse GPT-4 response: {e}")
            return {'raw_response': response}
    
    def _integrate_competitive_intelligence(self, startup_claims: Dict,
                                           web_intelligence: Dict,
                                           gpt4_analysis: Optional[Dict]) -> CompetitiveProfile:
        """Integrate all sources into comprehensive competitive profile"""
        profile = CompetitiveProfile()
        
        # Store startup claims for PDF comparison
        profile.startup_claimed_competitors = startup_claims.get('claimed_competitors', [])
        profile.startup_claimed_advantages = startup_claims.get('claimed_advantages', [])
        
        # Build independent analysis from web search
        for comp in web_intelligence.get('competitors', [])[:5]:
            if isinstance(comp, dict):
                profile.market_leaders.append({
                    'name': comp.get('name', 'Unknown'),
                    'description': comp.get('description', ''),
                    'funding': 'Data not available',  # Would come from enhanced search
                    'status': 'Active'
                })
        
        # Add market insights as risks/opportunities
        insights = web_intelligence.get('market_insights', [])
        for insight in insights:
            if 'fail' in insight.lower() or 'shut' in insight.lower() or 'risk' in insight.lower():
                profile.competitive_risks.append(insight[:150])
                profile.failure_patterns.append(insight[:150])
            else:
                profile.market_opportunities.append(insight[:150])
        
        # Integrate GPT-4 analysis if available
        if gpt4_analysis:
            # Add GPT-4 competitors if not already in web results
            for comp in gpt4_analysis.get('direct_competitors', []):
                if isinstance(comp, dict):
                    name = comp.get('name', '')
                    if not any(ml['name'] == name for ml in profile.market_leaders):
                        profile.market_leaders.append({
                            'name': name,
                            'description': comp.get('description', ''),
                            'funding': comp.get('market_share', 'Unknown'),
                            'status': 'Active'
                        })
            
            # Add GPT-4 risks
            profile.competitive_risks.extend(gpt4_analysis.get('competitive_risks', []))
            
            # Set threat level from GPT-4
            profile.threat_level = gpt4_analysis.get('threat_level', 'medium')
        else:
            # Determine threat level from web findings
            failure_count = len([i for i in insights if 'fail' in i.lower()])
            if failure_count >= 2:
                profile.threat_level = 'high'
            elif failure_count == 1:
                profile.threat_level = 'medium'
            else:
                profile.threat_level = 'low'
        
        # Set market position assessment
        if len(profile.market_leaders) > 5:
            profile.market_position = "Highly competitive market with established players"
        elif len(profile.failure_patterns) > 2:
            profile.market_position = "Challenging market with pattern of failures"
        else:
            profile.market_position = "Emerging market with opportunities"
        
        # Track sources
        profile.sources = web_intelligence.get('sources', [])
        
        # Set confidence based on data availability
        data_points = len(profile.market_leaders) + len(profile.competitive_risks) + len(insights)
        profile.confidence_score = min(0.9, data_points * 0.1)
        
        return profile
    
    def _has_openai_key(self) -> bool:
        """Check if OpenAI key is available"""
        return bool(os.getenv('OPENAI_API_KEY'))
    
    def _get_mock_competitive_data_enhanced(self, market_profile: Dict[str, Any]) -> CompetitiveProfile:
        """Enhanced mock data for TEST MODE with new structure"""
        profile = CompetitiveProfile()
        
        # Market leaders with funding info
        profile.market_leaders = [
            {
                'name': 'Stripe',
                'description': 'Global payment processing leader',
                'funding': '$95B valuation, Series I',
                'status': 'Dominant'
            },
            {
                'name': 'MercadoPago',
                'description': 'LATAM payment leader',
                'funding': 'Public ($80B market cap)',
                'status': 'Regional leader'
            }
        ]
        
        # Similar propositions with outcomes
        profile.similar_propositions = [
            {
                'name': 'FactorX',
                'description': 'AI invoice factoring - promised 48h, delivers 72h',
                'funding': '$15M Series A → Failed to raise B',
                'outcome': 'Struggling'
            },
            {
                'name': 'QuickFactor',
                'description': '24h invoice factoring attempt',
                'funding': '$5M Seed',
                'outcome': 'Shut down - regulatory issues'
            }
        ]
        
        # Competitive risks from market analysis
        profile.competitive_risks = [
            "3 of 5 similar AI factoring startups failed in 18 months",
            "Regulatory compliance requires 24-36 months establishment",
            "Established players have 100x resources and market presence"
        ]
        
        # Market opportunities
        profile.market_opportunities = [
            "$2.1B funding gap in SME invoice factoring (Bain 2024)",
            "LATAM market underserved by global players"
        ]
        
        # Failure patterns
        profile.failure_patterns = [
            "Underestimated regulatory complexity",
            "48h approval claims consistently unachievable",
            "Customer acquisition cost exceeded LTV"
        ]
        
        # Startup claims (for PDF comparison)
        profile.startup_claimed_competitors = ["Basic payment processors", "Traditional banks"]
        profile.startup_claimed_advantages = ["First AI-powered", "48h approval guarantee"]
        
        # Analysis metadata
        profile.market_position = "Highly competitive with pattern of failures"
        profile.threat_level = "high"
        profile.sources = [
            {'type': 'web_search', 'count': 6, 'queries': ['AI invoice factoring competitors', 'failed startups']}
        ]
        profile.confidence_score = 0.85
        
        return profile
