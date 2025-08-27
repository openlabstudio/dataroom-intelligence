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
        # FASE 2B: Enhanced structure for independent analysis + startup claims
        # Independent market analysis
        self.expert_consensus: List[str] = []  # Expert opinions from web
        self.precedent_analysis: List[Dict[str, Any]] = []  # Similar companies outcomes
        self.regulatory_assessment: List[str] = []  # Regulatory insights
        self.market_risks: List[str] = []  # Key risks identified
        self.market_opportunities: List[str] = []  # Opportunities found
        self.feasibility_assessment: str = ""  # Overall feasibility
        
        # Startup claims (for PDF comparison later)
        self.startup_claimed_tam: str = ""
        self.startup_claimed_timeline: str = ""
        self.startup_claimed_differentiators: List[str] = []
        
        # Analysis metadata
        self.validation_score: float = 0.0
        self.confidence_level: str = ""  # low, medium, high
        self.sources: List[Dict[str, Any]] = []  # Web search sources
        self.confidence_score: float = 0.0
        
        # Legacy fields for backward compatibility
        self.tam_assessment: Dict[str, Any] = {}
        self.sam_assessment: Dict[str, Any] = {}
        self.som_assessment: Dict[str, Any] = {}
        self.red_flags: List[str] = []  # Mapped to market_risks
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            # Independent analysis for Slack
            'independent_analysis': {
                'expert_consensus': self.expert_consensus,
                'precedent_analysis': self.precedent_analysis,
                'regulatory_assessment': self.regulatory_assessment,
                'market_risks': self.market_risks,
                'market_opportunities': self.market_opportunities,
                'feasibility_assessment': self.feasibility_assessment,
                'validation_score': self.validation_score,
                'confidence_level': self.confidence_level,
                'sources': self.sources,
                'confidence_score': self.confidence_score
            },
            # Startup claims for PDF comparison
            'startup_claims_extracted': {
                'claimed_tam': self.startup_claimed_tam,
                'claimed_timeline': self.startup_claimed_timeline,
                'claimed_differentiators': self.startup_claimed_differentiators
            },
            # Legacy fields for backward compatibility
            'tam_assessment': self.tam_assessment,
            'sam_assessment': self.sam_assessment,
            'som_assessment': self.som_assessment,
            'red_flags': self.red_flags or self.market_risks,
            'validation_score': self.validation_score,
            'confidence_score': self.confidence_score
        }

class MarketValidationAgent(BaseAgent):
    """Specialized agent for validating market size and opportunity claims"""
    
    def __init__(self):
        super().__init__("Market Validation")
        # FASE 2B: Initialize web search engine
        self.web_search_engine = None  # Will be initialized on first use
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
        """Main method to validate market opportunity with integrated web search"""
        try:
            logger.info("📈 Starting market validation analysis with web search...")
            
            # Check TEST MODE first
            if os.getenv('TEST_MODE', 'false').lower() == 'true':
                logger.info("🧪 TEST MODE: Returning enhanced mock validation data")
                return self._get_mock_validation_data_enhanced(market_profile)
            
            # FASE 2B: Build value proposition from market profile
            value_proposition = self._build_value_proposition_from_profile(market_profile)
            logger.info(f"🎯 Value proposition: {value_proposition}")
            
            # Step 1: Extract startup claims from documents
            startup_claims = self._extract_startup_market_claims(processed_documents, document_summary)
            
            # Step 2: Perform independent 3-level hierarchical web search for market validation
            web_validation = self._perform_multilevel_validation_search(market_profile)
            
            # Step 3: Analyze with GPT-4 if available (expert analysis with web validation)
            gpt4_validation = None
            if self._has_openai_key():
                gpt4_validation = self._perform_gpt4_market_validation(
                    market_profile, processed_documents, document_summary,
                    startup_claims, web_validation
                )
            
            # Step 4: Integrate all sources into comprehensive profile
            validation_profile = self._integrate_market_validation(
                startup_claims, web_validation, gpt4_validation
            )
            
            # Log key findings
            logger.info(f"✅ Found {len(validation_profile.expert_consensus)} expert opinions")
            logger.info(f"📦 Found {len(validation_profile.precedent_analysis)} precedent cases")
            logger.info(f"📊 Validation score: {validation_profile.validation_score:.2f}")
            logger.info(f"🔍 Sources analyzed: {len(validation_profile.sources)}")
            
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
        """Expert-level system prompt for market validation"""
        # Import expert prompts
        try:
            from prompts.expert_level_prompts import VALIDATION_EXPERT_SYSTEM
            return VALIDATION_EXPERT_SYSTEM
        except ImportError:
            # Fallback to original prompt
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
                                   document_summary: Dict[str, Any],
                                   startup_claims: Optional[Dict] = None,
                                   web_validation: Optional[Dict] = None) -> str:
        """Expert-level user prompt with startup claims and web validation"""
        # Try to use expert prompt if web validation available
        if startup_claims and web_validation:
            try:
                from prompts.expert_level_prompts import get_validation_prompts
                prompts = get_validation_prompts(market_profile, startup_claims, web_validation)
                return prompts['user']
            except ImportError:
                pass
        
        # Fallback to original prompt format
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
    
    # ========== FASE 2B: NEW METHODS FOR WEB SEARCH INTEGRATION ==========
    
    def _build_value_proposition_from_profile(self, market_profile: Dict[str, Any]) -> str:
        """Build value proposition from detected market profile"""
        try:
            # Use the detected market taxonomy
            solution = market_profile.get('solution', '')
            sub_vertical = market_profile.get('sub_vertical', '')
            vertical = market_profile.get('vertical', '')
            target_market = market_profile.get('target_market', '')
            
            # Build a proper value proposition based on detected market
            if solution:
                value_prop = f"{solution}"
            elif sub_vertical:
                value_prop = f"{sub_vertical}"
            elif vertical:
                value_prop = f"{vertical}"
            else:
                value_prop = "innovative technology solution"
            
            # Add target market if available
            if target_market:
                value_prop = f"{value_prop} for {target_market}"
            
            return value_prop
            
        except Exception as e:
            logger.warning(f"Failed to build value proposition from profile: {e}")
            return "innovative business solution"
    
    def _init_web_search(self):
        """Lazy initialize web search engine"""
        if self.web_search_engine is None:
            try:
                from utils.web_search import WebSearchEngine
                self.web_search_engine = WebSearchEngine()  # Uses default (Tavily if available)
            except ImportError as e:
                logger.warning(f"Web search not available: {e}")
                self.web_search_engine = None
    
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
    
    def _extract_startup_market_claims(self, documents: List[Dict], document_summary: Dict) -> Dict[str, Any]:
        """Extract what the startup claims about market size and timeline"""
        claimed_tam = ""
        claimed_timeline = ""
        claimed_differentiators = []
        
        # Simple extraction from document summary
        summary_text = str(document_summary.get('summary', ''))
        
        # Look for TAM/market size claims (basic pattern matching)
        import re
        tam_patterns = [
            r'\$\d+[BMK]?\s*(?:billion|million)?.*?(?:TAM|market|opportunity)',
            r'TAM.*?\$\d+[BMK]?',
            r'market size.*?\$\d+[BMK]?',
            r'market opportunity.*?\$\d+[BMK]?'
        ]
        
        for pattern in tam_patterns:
            match = re.search(pattern, summary_text, re.IGNORECASE)
            if match:
                claimed_tam = match.group()[:100]
                break
        
        # Look for timeline claims
        timeline_patterns = [
            r'\d+[\s-]?(?:hour|hr|h|day|month|year)',
            r'(?:within|in)\s+\d+\s+(?:hours?|days?|months?|years?)',
            r'immediate|instant|real[\s-]?time'
        ]
        
        for pattern in timeline_patterns:
            match = re.search(pattern, summary_text, re.IGNORECASE)
            if match:
                claimed_timeline = match.group()
                break
        
        # Look for differentiator claims
        differentiator_keywords = ['unique', 'first', 'only', 'proprietary', 'patented', 'revolutionary']
        for keyword in differentiator_keywords:
            if keyword in summary_text.lower():
                claimed_differentiators.append(f"{keyword} solution")
        
        return {
            'claimed_tam': claimed_tam or "Not specified",
            'claimed_timeline': claimed_timeline or "Not specified",
            'claimed_differentiators': claimed_differentiators[:5]
        }
    
    def _perform_multilevel_validation_search(self, market_profile: Dict) -> Dict[str, Any]:
        """MEJORAS CALIDAD: Perform 3-level hierarchical search for market validation"""
        try:
            # Initialize web search if needed
            self._init_web_search()
            
            if not self.web_search_engine:
                logger.warning("Web search engine not available")
                return {'sources': [], 'expert_opinions': [], 'precedents': []}
            
            # Extract all levels from market profile
            solution = market_profile.get('solution', '')
            sub_vertical = market_profile.get('sub_vertical', '')
            vertical = market_profile.get('vertical', '')
            
            # Level 1: Solution-specific validation (most specific)
            solution_queries = []
            if solution:
                solution_queries = [
                    f"{solution} market viability expert opinion",
                    f"{solution} regulatory requirements compliance",
                    f"{solution} TAM SAM market size analysis"
                ]
            
            # Level 2: Sub-vertical validation (broader)
            subvertical_queries = []
            if sub_vertical:
                subvertical_queries = [
                    f"{sub_vertical} market growth trends 2024",
                    f"{sub_vertical} regulatory landscape analysis",
                    f"{sub_vertical} market opportunity assessment"
                ]
            
            # Level 3: Vertical validation (broadest)
            vertical_queries = []
            if vertical:
                vertical_queries = [
                    f"{vertical} industry TAM growth forecast",
                    f"{vertical} market maturity analysis",
                    f"{vertical} regulatory environment 2024"
                ]
            
            logger.info(f"🔍 Executing 3-level validation search:")
            logger.info(f"   Level 1 (Solution): {solution}")
            logger.info(f"   Level 2 (Sub-vertical): {sub_vertical}")
            logger.info(f"   Level 3 (Vertical): {vertical}")
            
            # Execute searches at each level
            all_results = {'expert_insights': [], 'competitors_found': [], 'sources_count': 0}
            
            if solution_queries:
                solution_results = self.web_search_engine.search_multiple(
                    solution_queries[:2], max_results_per_query=3
                )
                all_results['expert_insights'].extend(solution_results.get('expert_insights', []))
                all_results['competitors_found'].extend(solution_results.get('competitors_found', []))
                all_results['sources_count'] += solution_results.get('sources_count', 0)
            
            if subvertical_queries:
                subvertical_results = self.web_search_engine.search_multiple(
                    subvertical_queries[:2], max_results_per_query=3
                )
                all_results['expert_insights'].extend(subvertical_results.get('expert_insights', []))
                all_results['competitors_found'].extend(subvertical_results.get('competitors_found', []))
                all_results['sources_count'] += subvertical_results.get('sources_count', 0)
            
            if vertical_queries:
                vertical_results = self.web_search_engine.search_multiple(
                    vertical_queries[:2], max_results_per_query=3
                )
                all_results['expert_insights'].extend(vertical_results.get('expert_insights', []))
                all_results['competitors_found'].extend(vertical_results.get('competitors_found', []))
                all_results['sources_count'] += vertical_results.get('sources_count', 0)
            
            # Process combined results
            return self._process_web_results_for_validation(all_results)
            
        except Exception as e:
            logger.error(f"Multilevel validation search failed: {e}")
            return {'sources': [], 'expert_opinions': [], 'precedents': []}
    
    def _perform_validation_web_search(self, value_proposition: str, 
                                      market_profile: Dict) -> Dict[str, Any]:
        """Perform web search for market validation intelligence - LEGACY METHOD"""
        try:
            # Initialize web search if needed
            self._init_web_search()
            
            if not self.web_search_engine:
                logger.warning("Web search engine not available")
                return {'sources': [], 'expert_opinions': [], 'precedents': []}
            
            # Build targeted search queries (NO GEOGRAPHY)
            vertical = market_profile.get('vertical', 'technology')
            
            # SIMPLIFIED: Remove geography for global analysis
            queries = [
                f"{value_proposition} expert opinion scalability feasibility",
                f"{value_proposition} regulatory challenges requirements",
                f"similar companies {value_proposition} success failure case studies",
                f"{vertical} market validation expert analysis 2024"  # Removed {geo}
            ]
            
            # Execute searches
            web_results = self.web_search_engine.search_multiple(queries[:3], max_results_per_query=3)
            
            # Process results for market validation
            return self._process_web_results_for_validation(web_results)
            
        except Exception as e:
            logger.error(f"Web search failed: {e}")
            return {'sources': [], 'expert_opinions': [], 'precedents': []}
    
    def _process_web_results_for_validation(self, web_results: Dict) -> Dict[str, Any]:
        """Process web search results into market validation intelligence with URLs"""
        validation_intel = {
            'expert_opinions': [],
            'regulatory_insights': [],
            'precedent_cases': [],
            'market_insights': [],
            'all_sources': [],
            'sources': []
        }
        
        # Extract expert insights with URLs
        for insight in web_results.get('expert_insights', []):
            if isinstance(insight, dict):  # Enhanced format with URL
                text = insight.get('insight', '')
                if any(word in text.lower() for word in ['regulatory', 'compliance', 'legal', 'requirement']):
                    validation_intel['regulatory_insights'].append({
                        'text': text[:200],
                        'url': insight.get('url', ''),
                        'source': insight.get('source', ''),
                        'jurisdiction': 'EU' if 'eu' in text.lower() else 'US' if 'us' in text.lower() else 'Unknown'
                    })
                elif any(word in text.lower() for word in ['expert', 'analysis', 'study', 'research', 'mckinsey', 'gartner']):
                    validation_intel['expert_opinions'].append({
                        'text': text[:200],
                        'url': insight.get('url', ''),
                        'source': insight.get('source', ''),
                        'source_type': insight.get('source_type', 'general')
                    })
                else:
                    validation_intel['market_insights'].append({
                        'text': text[:200],
                        'url': insight.get('url', ''),
                        'source': insight.get('source', '')
                    })
            elif isinstance(insight, str) and len(insight) > 20:  # Fallback
                # Categorize insights
                if any(word in insight.lower() for word in ['regulatory', 'compliance', 'legal', 'requirement']):
                    validation_intel['regulatory_insights'].append({'text': insight[:200]})
                elif any(word in insight.lower() for word in ['expert', 'analysis', 'study', 'research']):
                    validation_intel['expert_opinions'].append({'text': insight[:200]})
                else:
                    validation_intel['market_insights'].append({'text': insight[:200]})
        
        # Extract precedent cases from competitors found with URLs
        for competitor in web_results.get('competitors_found', []):
            if isinstance(competitor, dict):  # Enhanced format with URL
                name = competitor.get('name', '')
                description = competitor.get('description', '')
                mention = competitor.get('mention_context', '')
                
                # Determine outcome from context
                context = f"{description} {mention}".lower()
                if any(word in context for word in ['failed', 'shut', 'struggled', 'pivoted', 'acquired']):
                    outcome = 'failure/struggle'
                elif any(word in context for word in ['raised', 'funding', 'series', 'growth']):
                    outcome = 'success/operating'
                else:
                    outcome = 'operating'
                
                validation_intel['precedent_cases'].append({
                    'company': name,
                    'outcome': outcome,
                    'description': description[:100],
                    'url': competitor.get('url', ''),
                    'source_domain': competitor.get('source_domain', 'web search')
                })
            elif isinstance(competitor, str):  # Fallback
                # Parse for precedent information
                if any(word in competitor.lower() for word in ['failed', 'shut', 'struggled', 'acquired']):
                    validation_intel['precedent_cases'].append({
                        'company': competitor,
                        'outcome': 'failure/struggle',
                        'source': 'web search'
                    })
                else:
                    validation_intel['precedent_cases'].append({
                        'company': competitor,
                        'outcome': 'operating',
                        'source': 'web search'
                    })
        
        # Track all sources with URLs
        validation_intel['all_sources'] = web_results.get('all_sources', [])
        
        # Track sources summary
        validation_intel['sources'] = [{
            'type': 'web_search',
            'count': web_results.get('sources_count', 0),
            'queries': web_results.get('search_terms_used', []),
            'total_unique_sources': len(validation_intel['all_sources'])
        }]
        
        return validation_intel
    
    def _perform_gpt4_market_validation(self, market_profile: Dict,
                                       documents: List[Dict],
                                       document_summary: Dict,
                                       startup_claims: Optional[Dict] = None,
                                       web_validation: Optional[Dict] = None) -> Dict[str, Any]:
        """Perform expert-level GPT-4 analysis of market validation"""
        try:
            # Prepare document context
            document_context = self._prepare_document_context(documents, max_content_length=8000)
            
            # Use expert prompts with web validation
            system_prompt = self._get_validation_system_prompt()
            user_prompt = self._get_validation_user_prompt(market_profile, document_context, 
                                                          document_summary, startup_claims, web_validation)
            
            # Call OpenAI with expert parameters
            response = self._call_openai(system_prompt, user_prompt, 
                                       max_tokens=1500,  # Increased for detailed analysis
                                       temperature=0.2)  # Lower for more focused output
            
            # Parse response
            return self._parse_gpt4_validation_response(response)
            
        except Exception as e:
            logger.error(f"GPT-4 validation failed: {e}")
            return {}
    
    def _parse_gpt4_validation_response(self, response: str) -> Dict[str, Any]:
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
    
    def _integrate_market_validation(self, startup_claims: Dict,
                                    web_validation: Dict,
                                    gpt4_validation: Optional[Dict]) -> MarketValidationProfile:
        """Integrate all sources into comprehensive validation profile with URLs"""
        profile = MarketValidationProfile()
        
        # Store startup claims for PDF comparison
        profile.startup_claimed_tam = startup_claims.get('claimed_tam', 'Not specified')
        profile.startup_claimed_timeline = startup_claims.get('claimed_timeline', 'Not specified')
        profile.startup_claimed_differentiators = startup_claims.get('claimed_differentiators', [])
        
        # Build independent analysis from web search with URLs
        # Expert consensus - extract text and preserve URLs
        for expert_opinion in web_validation.get('expert_opinions', [])[:3]:
            if isinstance(expert_opinion, dict):
                text = expert_opinion.get('text', '')
                url = expert_opinion.get('url', '')
                source = expert_opinion.get('source', '')
                # Format for display: include source if available
                if source and len(source) > 0:
                    formatted = f"{source}: {text}" if len(source) < 50 else text
                else:
                    formatted = text
                profile.expert_consensus.append(formatted[:200])
                # Store URL separately for later use
                if not hasattr(profile, 'expert_urls'):
                    profile.expert_urls = []
                profile.expert_urls.append(url)
            elif isinstance(expert_opinion, str):
                profile.expert_consensus.append(expert_opinion[:200])
        
        # Regulatory assessment with URLs
        for reg_insight in web_validation.get('regulatory_insights', [])[:3]:
            if isinstance(reg_insight, dict):
                text = reg_insight.get('text', '')
                jurisdiction = reg_insight.get('jurisdiction', '')
                if jurisdiction:
                    formatted = f"[{jurisdiction}] {text}"
                else:
                    formatted = text
                profile.regulatory_assessment.append(formatted[:200])
            elif isinstance(reg_insight, str):
                profile.regulatory_assessment.append(reg_insight[:200])
        
        # Process precedent cases with URLs
        for case in web_validation.get('precedent_cases', [])[:5]:  # Increased limit
            if isinstance(case, dict):
                profile.precedent_analysis.append({
                    'company': case.get('company', 'Unknown'),
                    'outcome': case.get('outcome', 'Unknown'),
                    'description': case.get('description', ''),
                    'url': case.get('url', ''),
                    'source_domain': case.get('source_domain', ''),
                    'relevance': 'Similar business model'
                })
        
        # Extract risks and opportunities with URLs
        insights = web_validation.get('market_insights', [])
        for insight in insights[:10]:  # Process more insights
            if isinstance(insight, dict):
                text = insight.get('text', '')
                if any(word in text.lower() for word in ['risk', 'challenge', 'difficult', 'fail', 'threat']):
                    profile.market_risks.append(text[:150])
                else:
                    profile.market_opportunities.append(text[:150])
            elif isinstance(insight, str):
                if any(word in insight.lower() for word in ['risk', 'challenge', 'difficult', 'fail']):
                    profile.market_risks.append(insight[:150])
                else:
                    profile.market_opportunities.append(insight[:150])
        
        # Integrate GPT-4 validation if available
        if gpt4_validation:
            # Add GPT-4 insights
            if 'red_flags' in gpt4_validation:
                profile.market_risks.extend(gpt4_validation['red_flags'][:2])
            if 'opportunities' in gpt4_validation:
                profile.market_opportunities.extend(gpt4_validation['opportunities'][:2])
            
            # Set validation score from GPT-4
            profile.validation_score = gpt4_validation.get('validation_score', 5.0)
        else:
            # Calculate validation score from web findings
            risk_count = len(profile.market_risks)
            opportunity_count = len(profile.market_opportunities)
            precedent_failures = len([p for p in profile.precedent_analysis if 'fail' in str(p.get('outcome', '')).lower()])
            
            # Score calculation (10 = best, 0 = worst)
            base_score = 5.0
            base_score += (opportunity_count * 0.5)  # Opportunities increase score
            base_score -= (risk_count * 0.5)  # Risks decrease score
            base_score -= (precedent_failures * 1.0)  # Failures decrease more
            profile.validation_score = max(0, min(10, base_score))
        
        # Set confidence level
        if len(profile.expert_consensus) >= 2:
            profile.confidence_level = "high"
        elif len(profile.expert_consensus) >= 1:
            profile.confidence_level = "medium"
        else:
            profile.confidence_level = "low"
        
        # Set feasibility assessment
        if profile.validation_score >= 7:
            profile.feasibility_assessment = "Feasible with strong market opportunity"
        elif profile.validation_score >= 5:
            profile.feasibility_assessment = "Feasible but regulatory-dependent"
        else:
            profile.feasibility_assessment = "Challenging - significant risks identified"
        
        # Track all sources with URLs for citation
        profile.sources = web_validation.get('all_sources', [])[:15]  # Top 15 sources
        if not profile.sources:  # Fallback to summary if no detailed sources
            profile.sources = web_validation.get('sources', [])
        
        # Set confidence based on data availability
        data_points = len(profile.expert_consensus) + len(profile.precedent_analysis) + len(profile.regulatory_assessment)
        profile.confidence_score = min(0.9, data_points * 0.15)
        
        return profile
    
    def _has_openai_key(self) -> bool:
        """Check if OpenAI key is available"""
        return bool(os.getenv('OPENAI_API_KEY'))
    
    def _get_mock_validation_data_enhanced(self, market_profile: Dict[str, Any]) -> MarketValidationProfile:
        """Enhanced mock data for TEST MODE with new structure"""
        profile = MarketValidationProfile()
        
        # Expert consensus from web search
        profile.expert_consensus = [
            "McKinsey 2024: 48h approval technically feasible but requires regulatory pre-approval",
            "Industry Report: Similar models typically achieve 72-96h in practice, not 48h",
            "Expert analysis: Regulatory complexity in LATAM varies significantly by country"
        ]
        
        # Precedent analysis
        profile.precedent_analysis = [
            {
                'company': 'QuickFactor',
                'outcome': 'Failed - regulatory issues',
                'relevance': '24h invoice factoring attempt'
            },
            {
                'company': 'InvoiceAI',
                'outcome': 'Pivoted to 72h model',
                'relevance': 'Started with 48h promise'
            }
        ]
        
        # Regulatory assessment
        profile.regulatory_assessment = [
            "LATAM requires country-specific financial licenses (6-18 months)",
            "48h approval requires pre-established banking partnerships",
            "Compliance costs estimated at $2-5M per country"
        ]
        
        # Market risks
        profile.market_risks = [
            "Regulatory timeline typically 24-36 months, not 12 months",
            "Customer acquisition in SME segment expensive ($500-2000 CAC)",
            "Similar models struggled with unit economics at scale"
        ]
        
        # Market opportunities
        profile.market_opportunities = [
            "SME invoice factoring underserved in LATAM ($2.1B gap)",
            "Digital adoption accelerating post-COVID"
        ]
        
        # Feasibility assessment
        profile.feasibility_assessment = "Feasible but regulatory-dependent"
        
        # Startup claims (for PDF comparison)
        profile.startup_claimed_tam = "$1.6B TAM in target markets"
        profile.startup_claimed_timeline = "48-hour approval"
        profile.startup_claimed_differentiators = ["AI-powered", "48h guarantee", "First in LATAM"]
        
        # Analysis metadata
        profile.validation_score = 6.5
        profile.confidence_level = "medium"
        profile.sources = [
            {'type': 'web_search', 'count': 9, 'queries': ['48h factoring expert opinion', 'regulatory requirements']}
        ]
        profile.confidence_score = 0.75
        
        return profile