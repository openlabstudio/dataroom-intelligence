"""
Competitive Intelligence Agent for DataRoom Intelligence
Analyzes competitive landscape, identifies key competitors, and assesses market positioning

Phase 2B.1 - TASK-001: Competitive Intelligence Implementation

🔧 TEMPORARY FIX APPLIED: Enhanced search queries for niche markets (lines 504-590)
⚠️  IMPORTANT: This fix will be replaced by Enhanced Intelligence System
    - Enhanced queries with alternative terms (vendors, providers, players)
    - Quoted searches for exact technology terms
    - Multiple search variations for B2B niches
    - TODO: Replace with systematic 12-query expansion in Enhanced Intelligence System
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
        # MEJORAS CALIDAD: 3-level competitive analysis
        # Level 1: Solution competitors
        self.solution_competitors: List[Dict[str, Any]] = []
        # Level 2: Sub-vertical competitors
        self.subvertical_competitors: List[Dict[str, Any]] = []
        # Level 3: Vertical competitors
        self.vertical_competitors: List[Dict[str, Any]] = []
        
        # Legacy fields for backward compatibility
        self.market_leaders: List[Dict[str, Any]] = []  # Major players with funding info
        self.similar_propositions: List[Dict[str, Any]] = []  # Similar startups with outcomes
        
        # Insights and risks with source tracking
        self.competitive_risks: List[Any] = []  # Key risks with URLs
        self.market_opportunities: List[Any] = []  # Opportunities with URLs
        self.failure_patterns: List[str] = []  # Common failure patterns in similar startups
        self.regulatory_insights: List[Dict[str, Any]] = []  # Regulatory requirements with URLs
        
        # Startup claims (for PDF comparison later)
        self.startup_claimed_competitors: List[str] = []  # What startup claims
        self.startup_claimed_advantages: List[str] = []  # Their claimed differentiators
        
        # Level data for display
        self.levels_data: Dict[str, str] = {}  # solution, sub_vertical, vertical names
        
        # Analysis metadata
        self.market_position: str = ""  # Assessment of competitive landscape
        self.threat_level: str = ""  # low, medium, high
        self.sources: List[Dict[str, Any]] = []  # Summary of sources by level
        self.all_sources: List[Dict[str, Any]] = []  # All sources with URLs (top 15)
        self.confidence_score: float = 0.0
        self.meets_requirements: Dict[str, Any] = {}  # Track if min requirements are met

    def to_dict(self) -> Dict[str, Any]:
        return {
            # MEJORAS CALIDAD: 3-level competitive analysis
            'independent_analysis': {
                'solution_competitors': self.solution_competitors,
                'subvertical_competitors': self.subvertical_competitors,
                'vertical_competitors': self.vertical_competitors,
                'levels_data': self.levels_data,
                # Legacy fields
                'market_leaders': self.market_leaders or self.solution_competitors,
                'similar_propositions': self.similar_propositions,
                'competitive_risks': self.competitive_risks,
                'market_opportunities': self.market_opportunities,
                'failure_patterns': self.failure_patterns,
                'regulatory_insights': self.regulatory_insights,
                'market_position': self.market_position,
                'threat_level': self.threat_level,
                'sources_count': len(self.all_sources),
                'confidence_score': self.confidence_score,
                'meets_requirements': self.meets_requirements
            },
            # Startup claims for PDF comparison
            'startup_claims_extracted': {
                'claimed_competitors': self.startup_claimed_competitors,
                'claimed_advantages': self.startup_claimed_advantages
            },
            # Full sources for PDF
            'sources_summary': self.sources,
            'all_sources': self.all_sources
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
        
        # MVP DEMO: GPT-4 Competitive Extraction Prompt
        self.COMPETITIVE_EXTRACTION_PROMPT = """
You are a senior VC analyst extracting competitor information from web search results.

TASK: Extract exact company names, valuations, and key details from the following search results.

RULES:
1. Extract only real company names (not descriptions like "provider of electrochemical")
2. Consolidate parent companies and subsidiaries - don't list separately (e.g., "Veralto" and "Axine Water Technologies" → "Veralto - Axine Water Technologies")
3. Avoid duplicates - if a subsidiary is mentioned, only list the consolidated form
4. Include funding amount and date if mentioned  
5. Include URL if available
6. Maximum 8 competitors
7. Focus on direct competitors, not suppliers/customers
8. Return empty array if no clear competitors found

CRITICAL: Respond with ONLY valid JSON. No explanation, no additional text, no markdown formatting.

Web search results:
{web_search_results}

Respond with ONLY this JSON structure:
{{
  "competitors": [
    {{
      "name": "Company Name",
      "funding": "Amount Series, Year", 
      "description": "Brief description",
      "url": "https://company.com",
      "relevance_score": 0.95
    }}
  ],
  "market_assessment": "Brief market assessment",
  "confidence": 0.8
}}
"""
    
    def _init_web_search(self):
        """Lazy initialize web search engine"""
        if self.web_search_engine is None:
            try:
                from utils.web_search import WebSearchEngine
                self.web_search_engine = WebSearchEngine()  # Uses default (Tavily if available)
            except ImportError as e:
                logger.warning(f"Web search not available: {e}")
                self.web_search_engine = None

    def _extract_competitors_with_gpt4(self, web_results: Dict) -> Dict[str, Any]:
        """MVP DEMO: Use GPT-4 to extract clean competitor names from web search results"""
        import json
        import re
        
        try:
            logger.info("🤖 Using GPT-4 to extract competitor names...")
            
            # Initialize OpenAI client if not available
            if not hasattr(self, 'client'):
                try:
                    from openai import OpenAI
                    self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
                    logger.info("✅ OpenAI client initialized for GPT-4 enhancement")
                except ImportError:
                    logger.error("❌ OpenAI library not available")
                    return self._fallback_regex_extraction(web_results)
                except Exception as e:
                    logger.error(f"❌ Failed to initialize OpenAI client: {e}")
                    return self._fallback_regex_extraction(web_results)
            
            # Format web search results for GPT-4
            formatted_results = self._format_web_results_for_gpt4(web_results)
            
            if not formatted_results.strip():
                logger.warning("No web results to process with GPT-4")
                return {"competitors": [], "market_assessment": "No data available", "confidence": 0.0}
            
            # Create GPT-4 prompt
            user_prompt = self.COMPETITIVE_EXTRACTION_PROMPT.format(
                web_search_results=formatted_results
            )
            
            # Call GPT-4 with competitive extraction prompt
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a senior VC analyst specializing in competitive intelligence extraction."},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=1500
            )
            
            # Parse JSON response
            response_text = response.choices[0].message.content.strip()
            logger.info(f"🤖 GPT-4 competitive extraction response: {len(response_text)} characters")
            
            # Extract JSON from response with improved parsing
            
            logger.info(f"🔍 GPT-4 raw response (first 200 chars): {response_text[:200]}...")
            logger.info(f"🔍 GPT-4 raw response (full): {repr(response_text)}")
            
            # Clean response to remove common GPT-4 formatting issues
            cleaned_response = response_text
            # Remove markdown code blocks if present
            cleaned_response = re.sub(r'```json\s*', '', cleaned_response)
            cleaned_response = re.sub(r'```\s*$', '', cleaned_response)
            # Remove any leading/trailing explanation text that might be outside JSON
            cleaned_response = cleaned_response.strip()
            
            if cleaned_response != response_text:
                logger.info(f"🧹 Cleaned response: {repr(cleaned_response)}")
            
            # Try multiple JSON extraction methods
            extracted_data = None
            
            # Method 1: Try to parse the cleaned response directly as JSON
            try:
                extracted_data = json.loads(cleaned_response)
                competitors_count = len(extracted_data.get('competitors', [])) if isinstance(extracted_data, dict) else 0
                logger.info(f"✅ GPT-4 extracted {competitors_count} competitors (direct parse)")
            except json.JSONDecodeError as direct_error:
                logger.warning(f"Direct JSON parse failed: {direct_error}")
                
                # Method 2: Look for complete JSON blocks
                json_patterns = [
                    r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}',  # Better nested JSON matching
                    r'\{.*?\}',  # Non-greedy match
                    r'\{.*\}',   # Original greedy match as fallback
                ]
                
                for pattern in json_patterns:
                    json_match = re.search(pattern, cleaned_response, re.DOTALL)
                    if json_match:
                        try:
                            json_text = json_match.group()
                            logger.info(f"🔍 Attempting to parse JSON: {json_text[:100]}...")
                            extracted_data = json.loads(json_text)
                            competitors_count = len(extracted_data.get('competitors', [])) if isinstance(extracted_data, dict) else 0
                            logger.info(f"✅ GPT-4 extracted {competitors_count} competitors")
                            break
                        except json.JSONDecodeError as je:
                            logger.warning(f"JSON parsing failed for pattern {pattern}: {je}")
                            continue
            
            if extracted_data:
                # Post-processing: Remove duplicates and consolidate parent/subsidiary companies
                cleaned_data = self._clean_competitor_duplicates(extracted_data)
                return cleaned_data
            else:
                logger.warning("No valid JSON found in GPT-4 response, trying line-by-line extraction")
                # Fallback: Try to extract JSON from each line
                for line in response_text.split('\n'):
                    if line.strip().startswith('{') and line.strip().endswith('}'):
                        try:
                            extracted_data = json.loads(line.strip())
                            competitors_count = len(extracted_data.get('competitors', [])) if isinstance(extracted_data, dict) else 0
                            logger.info(f"✅ GPT-4 extracted from line: {competitors_count} competitors")
                            return extracted_data
                        except json.JSONDecodeError:
                            continue
                
                return {"competitors": [], "market_assessment": "GPT-4 parsing failed", "confidence": 0.0}
                
        except json.JSONDecodeError as je:
            logger.error(f"❌ GPT-4 JSON parsing failed: {je}")
            logger.error(f"❌ Raw JSON string that failed: {repr(je.doc)}")
            # Fallback to regex extraction
            logger.info("🔄 Falling back to regex extraction...")
            return self._fallback_regex_extraction(web_results)
        except Exception as e:
            logger.error(f"❌ GPT-4 competitor extraction failed: {e}")
            logger.error(f"❌ Exception type: {type(e).__name__}")
            # Fallback to regex extraction
            logger.info("🔄 Falling back to regex extraction...")
            return self._fallback_regex_extraction(web_results)
    
    def _clean_competitor_duplicates(self, extracted_data: Dict) -> Dict:
        """Clean up duplicate competitors and consolidate parent/subsidiary companies"""
        if 'competitors' not in extracted_data:
            return extracted_data
        
        competitors = extracted_data['competitors']
        cleaned_competitors = []
        seen_companies = set()
        
        for comp in competitors:
            name = comp.get('name', '').strip()
            
            # Skip if we've already seen this exact name
            if name.lower() in seen_companies:
                continue
            
            # Check for parent/subsidiary relationships
            is_duplicate = False
            for existing in cleaned_competitors:
                existing_name = existing.get('name', '').strip()
                
                # Case 1: Current is parent, existing is subsidiary
                # e.g., name="Veralto", existing="Veralto - Axine Water Technologies"
                if name in existing_name and existing_name != name:
                    is_duplicate = True
                    break
                
                # Case 2: Current is subsidiary, existing is parent  
                # e.g., name="Veralto - Axine Water Technologies", existing="Veralto"
                if existing_name in name and existing_name != name:
                    # Replace the parent with the more specific subsidiary
                    cleaned_competitors.remove(existing)
                    seen_companies.discard(existing_name.lower())
                    break
            
            if not is_duplicate:
                cleaned_competitors.append(comp)
                seen_companies.add(name.lower())
        
        # Update the extracted data with cleaned competitors
        extracted_data['competitors'] = cleaned_competitors
        logger.info(f"🧹 Cleaned competitors: {len(competitors)} → {len(cleaned_competitors)}")
        
        return extracted_data
    
    def _format_web_results_for_gpt4(self, web_results: Dict) -> str:
        """Format web search results for GPT-4 processing"""
        formatted_text = ""
        
        # Add competitors found by web search
        competitors = web_results.get('competitors_found', [])
        if competitors:
            formatted_text += "COMPETITORS FOUND:\n"
            for i, comp in enumerate(competitors[:10], 1):  # Limit to avoid token limit
                if isinstance(comp, dict):
                    formatted_text += f"{i}. {comp.get('name', 'Unknown')} - {comp.get('description', '')}"
                    if comp.get('url'):
                        formatted_text += f" (URL: {comp.get('url')})"
                    formatted_text += "\n"
                elif isinstance(comp, str):
                    formatted_text += f"{i}. {comp}\n"
        
        # Add expert insights
        insights = web_results.get('expert_insights', [])
        if insights:
            formatted_text += "\nEXPERT INSIGHTS:\n"
            for i, insight in enumerate(insights[:5], 1):  # Limit to avoid token limit
                if isinstance(insight, dict):
                    formatted_text += f"{i}. {insight.get('text', insight.get('insight', ''))}"
                    if insight.get('url'):
                        formatted_text += f" (Source: {insight.get('url')})"
                    formatted_text += "\n"
                elif isinstance(insight, str):
                    formatted_text += f"{i}. {insight[:200]}...\n"
        
        # Add sources summary
        sources = web_results.get('all_sources', [])
        if sources:
            formatted_text += f"\nSOURCES: {len(sources)} sources analyzed\n"
            for source in sources[:3]:  # Show top 3 sources
                if isinstance(source, dict):
                    formatted_text += f"- {source.get('title', 'Unknown')} ({source.get('url', 'No URL')})\n"
        
        return formatted_text[:8000]  # Limit to stay within GPT-4 context window
    
    def _fallback_regex_extraction(self, web_results: Dict) -> Dict[str, Any]:
        """Fallback to regex extraction if GPT-4 fails"""
        logger.info("🔄 Using fallback regex extraction...")
        
        competitors = []
        for comp in web_results.get('competitors_found', [])[:8]:
            if isinstance(comp, dict):
                competitors.append({
                    "name": comp.get('name', 'Unknown'),
                    "funding": comp.get('funding', 'Unknown'),
                    "description": comp.get('description', ''),
                    "url": comp.get('url', ''),
                    "relevance_score": 0.7  # Lower confidence for regex
                })
            elif isinstance(comp, str):
                # Parse string format "Company Name (description)"
                parts = comp.split('(')
                name = parts[0].strip() if parts else comp
                desc = parts[1].replace(')', '').strip() if len(parts) > 1 else ''
                
                competitors.append({
                    "name": name,
                    "funding": "Unknown",
                    "description": desc,
                    "url": "",
                    "relevance_score": 0.6  # Even lower for string parsing
                })
        
        return {
            "competitors": competitors,
            "market_assessment": "Regex extraction fallback",
            "confidence": 0.6
        }

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

            # FASE 2A: Build value proposition from market profile
            # Use detected market profile instead of extracting incorrectly
            value_proposition = self._build_value_proposition_from_profile(market_profile, document_summary)
            logger.info(f"🎯 Value proposition: {value_proposition}")

            # Step 1: Extract startup claims from documents
            startup_claims = self._extract_startup_claims(processed_documents, document_summary)
            
            # Step 2: Perform independent 3-level hierarchical web search for competitive intelligence
            web_intelligence = self._perform_multilevel_competitive_search(market_profile)
            
            # Step 3: Analyze with GPT-4 if available (expert-level analysis with web intelligence)
            gpt4_analysis = None
            if self._has_openai_key():
                gpt4_analysis = self._perform_gpt4_competitive_analysis(
                    market_profile, processed_documents, document_summary, web_intelligence
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
        """Expert-level system prompt for competitive analysis"""
        # Import expert prompts
        try:
            from prompts.expert_level_prompts import COMPETITIVE_EXPERT_SYSTEM
            return COMPETITIVE_EXPERT_SYSTEM
        except ImportError:
            # Fallback to original prompt
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
                                    document_summary: Dict[str, Any],
                                    web_intelligence: Optional[Dict] = None) -> str:
        """Expert-level user prompt with market context and web intelligence"""
        # Try to use expert prompt if web intelligence available
        if web_intelligence:
            try:
                from prompts.expert_level_prompts import get_competitive_prompts
                prompts = get_competitive_prompts(market_profile, web_intelligence)
                return prompts['user']
            except ImportError:
                pass
        
        # Fallback to original prompt format
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
    
    def _build_value_proposition_from_profile(self, market_profile: Dict[str, Any], document_summary: Dict) -> str:
        """Build value proposition from detected market profile"""
        try:
            # Use the detected market taxonomy
            solution = market_profile.get('solution', '')
            sub_vertical = market_profile.get('sub_vertical', '')
            vertical = market_profile.get('vertical', '')
            target_market = market_profile.get('target_market', '')
            
            # Build a proper value proposition based on detected market
            if solution:
                # Use the most specific solution if available
                value_prop = f"{solution}"
            elif sub_vertical:
                # Fall back to sub-vertical
                value_prop = f"{sub_vertical}"
            elif vertical:
                # Fall back to vertical
                value_prop = f"{vertical}"
            else:
                # Last resort fallback
                value_prop = "innovative technology solution"
            
            # Add target market if available
            if target_market:
                value_prop = f"{value_prop} for {target_market}"
            
            return value_prop
            
        except Exception as e:
            logger.warning(f"Failed to build value proposition from profile: {e}")
            return "innovative business solution"
    
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
    
    def _perform_multilevel_competitive_search(self, market_profile: Dict) -> Dict[str, Any]:
        """MEJORAS CALIDAD: Perform 3-level hierarchical search for comprehensive competitive intelligence"""
        try:
            # Initialize web search if needed
            self._init_web_search()
            
            if not self.web_search_engine:
                logger.warning("Web search engine not available")
                return {'sources': [], 'competitors': [], 'insights': []}
            
            # Extract all levels from market profile
            solution = market_profile.get('solution', '')
            sub_vertical = market_profile.get('sub_vertical', '')
            vertical = market_profile.get('vertical', '')
            target_market = market_profile.get('target_market', '')
            
            # Level 1: Solution-specific search (most specific)
            solution_queries = []
            if solution:
                # 🔧 TEMPORARY FIX: Enhanced queries for niche markets (will be replaced by Enhanced Intelligence System)
                solution_queries = [
                    f"{solution} competitors market analysis",
                    f"{solution} companies vendors providers",  # More specific terms for B2B niches
                    f'"{solution}" startup companies funding',  # Quoted search for exact technology terms
                    f"{solution} alternative solutions providers"  # Catch indirect competitors
                ]
            
            # Level 2: Sub-vertical search (broader)
            subvertical_queries = []
            if sub_vertical:
                # 🔧 TEMPORARY FIX: Enhanced sub-vertical queries for better competitor discovery
                subvertical_queries = [
                    f"{sub_vertical} market leaders companies 2024",
                    f"{sub_vertical} competitive landscape analysis",
                    f"{sub_vertical} players vendors solutions",  # Alternative terms for B2B markets
                    f'"{sub_vertical}" industry companies list'  # Quoted search for specific industries
                ]
            
            # Level 3: Vertical search (broadest)
            vertical_queries = []
            if vertical:
                # 🔧 TEMPORARY FIX: Enhanced vertical queries for comprehensive market discovery
                vertical_queries = [
                    f"{vertical} industry companies directory 2024",
                    f"{vertical} major players market leaders",
                    f"{vertical} established companies incumbents",  # Catch established players
                    f'"{vertical}" sector competitive analysis'  # Quoted search for specific sectors
                ]
            
            logger.info(f"🔍 Executing 3-level hierarchical search:")
            logger.info(f"   Level 1 (Solution): {solution}")
            logger.info(f"   Level 2 (Sub-vertical): {sub_vertical}")
            logger.info(f"   Level 3 (Vertical): {vertical}")
            
            # Execute searches at each level
            solution_results = {}
            subvertical_results = {}
            vertical_results = {}
            
            if solution_queries:
                solution_results = self.web_search_engine.search_multiple(
                    solution_queries[:2], max_results_per_query=3
                )
            
            if subvertical_queries:
                subvertical_results = self.web_search_engine.search_multiple(
                    subvertical_queries[:2], max_results_per_query=3
                )
            
            if vertical_queries:
                vertical_results = self.web_search_engine.search_multiple(
                    vertical_queries[:2], max_results_per_query=3
                )
            
            # Process multi-level results
            return self._process_multilevel_competition_results(
                solution_results, subvertical_results, vertical_results,
                solution, sub_vertical, vertical
            )
            
        except Exception as e:
            logger.error(f"Multilevel web search failed: {e}")
            return {'sources': [], 'competitors': [], 'insights': []}
    
    def _perform_competitive_web_search(self, value_proposition: str, 
                                       market_profile: Dict) -> Dict[str, Any]:
        """Perform web search for competitive intelligence (geography-free) - LEGACY METHOD"""
        try:
            # Initialize web search if needed
            self._init_web_search()
            
            if not self.web_search_engine:
                logger.warning("Web search engine not available")
                return {'sources': [], 'competitors': [], 'insights': []}
            
            # Build targeted search queries (NO GEOGRAPHY)
            vertical = market_profile.get('vertical', 'technology')
            
            # 🔧 TEMPORARY FIX: Enhanced fallback queries for better competitor discovery
            queries = [
                f"{value_proposition} competitors companies providers",  # Multiple terms for B2B
                f'"{value_proposition}" startup companies funding',  # Quoted exact match
                f"{value_proposition} alternative solutions vendors",  # Indirect competitors
                f"{vertical} competitive landscape players 2024",  # Enhanced vertical search
                f"similar companies {value_proposition} market analysis"  # Broader discovery
            ]
            
            # Execute searches
            web_results = self.web_search_engine.search_multiple(queries[:3], max_results_per_query=3)
            
            # Process results for competitive intelligence
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
            
        except Exception as e:
            logger.error(f"Web search failed: {e}")
            return {'sources': [], 'competitors': [], 'insights': []}
    
    def _process_multilevel_competition_results(self, solution_results: Dict, 
                                                subvertical_results: Dict,
                                                vertical_results: Dict,
                                                solution: str, sub_vertical: str, 
                                                vertical: str) -> Dict[str, Any]:
        """MEJORAS CALIDAD: Process 3-level search results separately with URLs + GPT-4 extraction"""
        competitive_intel = {
            'solution_competitors': [],
            'subvertical_competitors': [],
            'vertical_competitors': [],
            'solution_insights': [],
            'subvertical_insights': [],
            'vertical_insights': [],
            'regulatory_insights': [],
            'all_sources': [],
            'levels_data': {
                'solution': solution,
                'sub_vertical': sub_vertical,
                'vertical': vertical
            }
        }
        
        # MVP DEMO: Use GPT-4 to enhance competitor extraction from each level
        gpt4_enhanced_results = {}
        
        # Only use GPT-4 in production mode and if OpenAI is available
        if os.getenv('TEST_MODE', 'false').lower() != 'true' and self._has_openai_key():
            try:
                logger.info("🤖 Using GPT-4 to enhance competitive intelligence...")
                
                # Process each level with GPT-4 (prioritize solution level)
                if solution_results.get('competitors_found') or solution_results.get('expert_insights'):
                    logger.info("🔬 GPT-4 processing solution-level competitors...")
                    gpt4_enhanced_results['solution'] = self._extract_competitors_with_gpt4(solution_results)
                
                if subvertical_results.get('competitors_found') or subvertical_results.get('expert_insights'):
                    logger.info("🔬 GPT-4 processing sub-vertical competitors...")
                    gpt4_enhanced_results['subvertical'] = self._extract_competitors_with_gpt4(subvertical_results)
                
                # Note: Skip vertical level for GPT-4 to save tokens, focus on most relevant levels
                
            except Exception as e:
                logger.error(f"❌ GPT-4 enhancement failed: {e}")
                gpt4_enhanced_results = {}
        else:
            logger.info("🧪 Skipping GPT-4 enhancement (TEST_MODE or no OpenAI key)")
            gpt4_enhanced_results = {}
        
        # Process Level 1: Solution results (with GPT-4 enhancement)
        if gpt4_enhanced_results.get('solution'):
            # Use GPT-4 enhanced competitors for solution level
            logger.info("✅ Using GPT-4 enhanced solution-level competitors")
            for competitor in gpt4_enhanced_results['solution'].get('competitors', []):
                competitive_intel['solution_competitors'].append({
                    'name': competitor.get('name', 'Unknown'),
                    'description': competitor.get('description', ''),
                    'url': competitor.get('url', ''),
                    'funding': competitor.get('funding', 'Unknown'),
                    'relevance_score': competitor.get('relevance_score', 0.9),
                    'level': 'solution',
                    'enhanced_by_gpt4': True
                })
        else:
            # Fallback to original processing
            for competitor in solution_results.get('competitors_found', []):
                if isinstance(competitor, dict):  # Now expecting dict with URL
                    competitive_intel['solution_competitors'].append({
                        'name': competitor.get('name', 'Unknown'),
                        'description': competitor.get('description', ''),
                        'url': competitor.get('url', ''),
                        'source_domain': competitor.get('source_domain', ''),
                        'level': 'solution'
                    })
                elif isinstance(competitor, str):  # Fallback for string format
                    parts = competitor.split('(')
                    name = parts[0].strip() if parts else competitor
                    desc = parts[1].replace(')', '').strip() if len(parts) > 1 else ''
                    competitive_intel['solution_competitors'].append({
                        'name': name,
                        'description': desc,
                        'level': 'solution'
                    })
        
        for insight in solution_results.get('expert_insights', []):
            if isinstance(insight, dict):  # Now expecting dict with URL
                competitive_intel['solution_insights'].append({
                    'text': insight.get('insight', ''),
                    'source': insight.get('source', ''),
                    'url': insight.get('url', ''),
                    'source_type': insight.get('source_type', 'general')
                })
            elif isinstance(insight, str) and len(insight) > 20:  # Fallback
                competitive_intel['solution_insights'].append({'text': insight[:200]})
        
        # Process Level 2: Sub-vertical results (with GPT-4 enhancement)
        if gpt4_enhanced_results.get('subvertical'):
            # Use GPT-4 enhanced competitors for sub-vertical level  
            logger.info("✅ Using GPT-4 enhanced sub-vertical competitors")
            for competitor in gpt4_enhanced_results['subvertical'].get('competitors', []):
                competitive_intel['subvertical_competitors'].append({
                    'name': competitor.get('name', 'Unknown'),
                    'description': competitor.get('description', ''),
                    'url': competitor.get('url', ''),
                    'funding': competitor.get('funding', 'Unknown'),
                    'relevance_score': competitor.get('relevance_score', 0.9),
                    'level': 'sub_vertical',
                    'enhanced_by_gpt4': True
                })
        else:
            # Fallback to original processing
            for competitor in subvertical_results.get('competitors_found', []):
                if isinstance(competitor, dict):  # Now expecting dict with URL
                    competitive_intel['subvertical_competitors'].append({
                        'name': competitor.get('name', 'Unknown'),
                        'description': competitor.get('description', ''),
                        'url': competitor.get('url', ''),
                        'source_domain': competitor.get('source_domain', ''),
                        'level': 'sub_vertical'
                    })
                elif isinstance(competitor, str):  # Fallback
                    parts = competitor.split('(')
                    name = parts[0].strip() if parts else competitor
                    desc = parts[1].replace(')', '').strip() if len(parts) > 1 else ''
                    competitive_intel['subvertical_competitors'].append({
                        'name': name,
                        'description': desc,
                        'level': 'sub_vertical'
                    })
        
        for insight in subvertical_results.get('expert_insights', []):
            if isinstance(insight, dict):  # Now expecting dict with URL
                competitive_intel['subvertical_insights'].append({
                    'text': insight.get('insight', ''),
                    'source': insight.get('source', ''),
                    'url': insight.get('url', ''),
                    'source_type': insight.get('source_type', 'general')
                })
            elif isinstance(insight, str) and len(insight) > 20:  # Fallback
                competitive_intel['subvertical_insights'].append({'text': insight[:200]})
        
        # Process Level 3: Vertical results
        for competitor in vertical_results.get('competitors_found', []):
            if isinstance(competitor, dict):  # Now expecting dict with URL
                competitive_intel['vertical_competitors'].append({
                    'name': competitor.get('name', 'Unknown'),
                    'description': competitor.get('description', ''),
                    'url': competitor.get('url', ''),
                    'source_domain': competitor.get('source_domain', ''),
                    'level': 'vertical'
                })
            elif isinstance(competitor, str):  # Fallback
                parts = competitor.split('(')
                name = parts[0].strip() if parts else competitor
                desc = parts[1].replace(')', '').strip() if len(parts) > 1 else ''
                competitive_intel['vertical_competitors'].append({
                    'name': name,
                    'description': desc,
                    'level': 'vertical'
                })
        
        for insight in vertical_results.get('expert_insights', []):
            if isinstance(insight, dict):  # Now expecting dict with URL
                competitive_intel['vertical_insights'].append({
                    'text': insight.get('insight', ''),
                    'source': insight.get('source', ''),
                    'url': insight.get('url', ''),
                    'source_type': insight.get('source_type', 'general')
                })
            elif isinstance(insight, str) and len(insight) > 20:  # Fallback
                competitive_intel['vertical_insights'].append({'text': insight[:200]})
        
        # Add regulatory insights if available
        for reg_insight in solution_results.get('regulatory_insights', []):
            if isinstance(reg_insight, dict):
                competitive_intel['regulatory_insights'].append(reg_insight)
        for reg_insight in subvertical_results.get('regulatory_insights', []):
            if isinstance(reg_insight, dict):
                competitive_intel['regulatory_insights'].append(reg_insight)
        
        # Collect all sources with URLs
        all_sources_collected = []
        for source in solution_results.get('all_sources', []):
            all_sources_collected.append(source)
        for source in subvertical_results.get('all_sources', []):
            all_sources_collected.append(source)
        for source in vertical_results.get('all_sources', []):
            all_sources_collected.append(source)
        
        # Deduplicate and sort by relevance
        seen_urls = set()
        unique_sources = []
        for source in all_sources_collected:
            url = source.get('url', '')
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_sources.append(source)
        
        # Sort by relevance score and limit
        unique_sources.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
        competitive_intel['all_sources'] = unique_sources[:15]
        
        # Track sources count
        competitive_intel['sources_summary'] = [
            {'level': 'solution', 'count': solution_results.get('sources_count', 0)},
            {'level': 'sub_vertical', 'count': subvertical_results.get('sources_count', 0)},
            {'level': 'vertical', 'count': vertical_results.get('sources_count', 0)},
            {'total_unique_sources': len(competitive_intel['all_sources'])}
        ]
        
        return competitive_intel
    
    def _perform_gpt4_competitive_analysis(self, market_profile: Dict,
                                          documents: List[Dict],
                                          document_summary: Dict,
                                          web_intelligence: Optional[Dict] = None) -> Dict[str, Any]:
        """Perform expert-level GPT-4 analysis of competitive landscape"""
        try:
            # Prepare document context
            document_context = self._prepare_document_context(documents, max_content_length=8000)
            
            # Use expert prompts with web intelligence
            system_prompt = self._get_competitive_system_prompt()
            user_prompt = self._get_competitive_user_prompt(market_profile, document_context, 
                                                           document_summary, web_intelligence)
            
            # Call OpenAI with expert parameters
            response = self._call_openai(system_prompt, user_prompt, 
                                       max_tokens=1500,  # Increased for detailed analysis
                                       temperature=0.2)  # Lower for more focused output
            
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
        """MEJORAS CALIDAD: Integrate 3-level search results"""
        profile = CompetitiveProfile()
        
        # Store startup claims for PDF comparison
        profile.startup_claimed_competitors = startup_claims.get('claimed_competitors', [])
        profile.startup_claimed_advantages = startup_claims.get('claimed_advantages', [])
        
        # MEJORAS CALIDAD: Store level data for display
        profile.levels_data = web_intelligence.get('levels_data', {})
        
        # Process solution competitors (Level 1) with URLs
        profile.solution_competitors = []
        for comp in web_intelligence.get('solution_competitors', [])[:5]:  # Increased limit
            if isinstance(comp, dict):
                profile.solution_competitors.append({
                    'name': comp.get('name', 'Unknown'),
                    'description': comp.get('description', ''),
                    'url': comp.get('url', ''),  # Add URL
                    'source_domain': comp.get('source_domain', ''),
                    'status': 'Active'
                })
        
        # Process sub-vertical competitors (Level 2) with URLs
        profile.subvertical_competitors = []
        for comp in web_intelligence.get('subvertical_competitors', [])[:5]:  # Increased limit
            if isinstance(comp, dict):
                profile.subvertical_competitors.append({
                    'name': comp.get('name', 'Unknown'),
                    'description': comp.get('description', ''),
                    'url': comp.get('url', ''),  # Add URL
                    'source_domain': comp.get('source_domain', ''),
                    'status': 'Active'
                })
        
        # Process vertical competitors (Level 3) with URLs
        profile.vertical_competitors = []
        for comp in web_intelligence.get('vertical_competitors', [])[:5]:  # Increased limit
            if isinstance(comp, dict):
                profile.vertical_competitors.append({
                    'name': comp.get('name', 'Unknown'),
                    'description': comp.get('description', ''),
                    'url': comp.get('url', ''),  # Add URL
                    'source_domain': comp.get('source_domain', ''),
                    'status': 'Active'
                })
        
        # Process insights by level with URLs
        solution_insights = web_intelligence.get('solution_insights', [])
        subvertical_insights = web_intelligence.get('subvertical_insights', [])
        vertical_insights = web_intelligence.get('vertical_insights', [])
        regulatory_insights = web_intelligence.get('regulatory_insights', [])
        
        # Combine all insights with source tracking
        all_insights_with_sources = []
        for insight in solution_insights[:5]:
            if isinstance(insight, dict):
                all_insights_with_sources.append(insight)
            else:
                all_insights_with_sources.append({'text': str(insight)[:200]})
        
        for insight in subvertical_insights[:5]:
            if isinstance(insight, dict):
                all_insights_with_sources.append(insight)
            else:
                all_insights_with_sources.append({'text': str(insight)[:200]})
        
        for insight in vertical_insights[:5]:
            if isinstance(insight, dict):
                all_insights_with_sources.append(insight)
            else:
                all_insights_with_sources.append({'text': str(insight)[:200]})
        
        # Process regulatory insights separately
        profile.regulatory_insights = regulatory_insights[:5]
        
        # Categorize insights and preserve URLs
        for insight_obj in all_insights_with_sources:
            text = insight_obj.get('text', '')
            if any(word in text.lower() for word in ['fail', 'shut', 'risk', 'challenge', 'difficult']):
                profile.competitive_risks.append({
                    'text': text[:150],
                    'url': insight_obj.get('url', ''),
                    'source': insight_obj.get('source', '')
                })
            else:
                profile.market_opportunities.append({
                    'text': text[:150],
                    'url': insight_obj.get('url', ''),
                    'source': insight_obj.get('source', '')
                })
        
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
            # Combine all insights for analysis
            all_insights = solution_insights + subvertical_insights + vertical_insights
            failure_count = len([i for i in all_insights if 'fail' in i.lower()])
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
        
        # Track all sources with URLs - DEBUG
        all_sources_raw = web_intelligence.get('all_sources', [])
        logger.info(f"🔍 Web intelligence returned {len(all_sources_raw)} sources")
        logger.info(f"🔍 Web intelligence keys: {list(web_intelligence.keys())}")
        
        profile.all_sources = all_sources_raw[:15]
        profile.sources = web_intelligence.get('sources_summary', [])
        
        # Set confidence based on data availability and source quality
        total_competitors = len(profile.solution_competitors) + len(profile.subvertical_competitors) + len(profile.vertical_competitors)
        total_insights = len(all_insights_with_sources) + len(regulatory_insights)
        total_sources = len(profile.all_sources)
        
        # Check minimum requirements
        meets_min_sources = total_sources >= 10
        meets_min_competitors = total_competitors >= 5
        
        # Calculate confidence score
        base_score = 0.5
        if meets_min_sources:
            base_score += 0.2
        if meets_min_competitors:
            base_score += 0.2
        base_score += min(0.1, total_insights * 0.01)
        
        profile.confidence_score = min(0.9, base_score)
        profile.meets_requirements = {
            'sources': {'required': 10, 'found': total_sources, 'met': meets_min_sources},
            'competitors': {'required': 5, 'found': total_competitors, 'met': meets_min_competitors}
        }
        
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
