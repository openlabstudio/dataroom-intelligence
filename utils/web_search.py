"""
Web Search Integration for DataRoom Intelligence
Phase 2B.2 - TASK-005 FASE 1: MVP Web Search

This module provides web search capabilities for external market validation.
Implements a flexible architecture to support multiple search providers.
"""

import os
import re
import json
import time
import logging
from typing import Dict, List, Any, Optional
from abc import ABC, abstractmethod
import requests
from utils.logger import get_logger

logger = get_logger(__name__)


class SearchProvider(ABC):
    """Abstract base class for search providers"""
    
    @abstractmethod
    def search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Execute a search query and return results"""
        pass


class DuckDuckGoProvider(SearchProvider):
    """DuckDuckGo search provider - Free, unlimited API"""
    
    def __init__(self):
        self.base_url = "https://api.duckduckgo.com/"
        self.headers = {
            'User-Agent': 'DataRoom Intelligence Bot 1.0'
        }
    
    def search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Execute DuckDuckGo search
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return
            
        Returns:
            List of search results with title, url, snippet
        """
        try:
            # DuckDuckGo instant answer API
            params = {
                'q': query,
                'format': 'json',
                'no_html': 1,
                'skip_disambig': 1
            }
            
            response = requests.get(
                self.base_url,
                params=params,
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code != 200:
                logger.warning(f"DuckDuckGo API returned status {response.status_code}")
                return []
            
            data = response.json()
            results = []
            
            # Extract results from various DuckDuckGo response fields
            # Abstract + RelatedTopics provide the best results
            if data.get('Abstract'):
                results.append({
                    'title': data.get('Heading', 'Abstract Result'),
                    'url': data.get('AbstractURL', ''),
                    'snippet': data.get('AbstractText', '')[:500]
                })
            
            # Add related topics (usually the actual search results)
            for topic in data.get('RelatedTopics', [])[:max_results]:
                if isinstance(topic, dict) and topic.get('Text'):
                    results.append({
                        'title': topic.get('Text', '').split(' - ')[0][:100],
                        'url': topic.get('FirstURL', ''),
                        'snippet': topic.get('Text', '')[:500]
                    })
            
            # If we have no results, try the Answer field
            if not results and data.get('Answer'):
                results.append({
                    'title': 'Direct Answer',
                    'url': data.get('AnswerType', ''),
                    'snippet': data.get('Answer', '')
                })
            
            logger.info(f"DuckDuckGo search for '{query}' returned {len(results)} results")
            return results[:max_results]
            
        except requests.RequestException as e:
            logger.error(f"DuckDuckGo search failed: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error in DuckDuckGo search: {e}")
            return []


class TavilyProvider(SearchProvider):
    """Tavily search provider - Professional AI-focused search"""
    
    def __init__(self):
        self.api_key = os.getenv('TAVILY_API_KEY')
        if not self.api_key:
            logger.warning("TAVILY_API_KEY not found in environment variables")
            
    def _categorize_source(self, domain: str) -> str:
        """Categorize source type based on domain"""
        domain = domain.lower()
        
        # Academic/Research
        if any(term in domain for term in ['nature.com', 'sciencedirect', 'springer', 'ieee', 'arxiv', '.edu']):
            return 'academic'
        
        # Industry Reports/Analysis
        elif any(term in domain for term in ['mckinsey', 'gartner', 'forrester', 'frost', 'idc']):
            return 'industry_report'
        
        # Financial Data
        elif any(term in domain for term in ['crunchbase', 'pitchbook', 'cbinsights', 'bloomberg', 'reuters']):
            return 'financial'
        
        # Regulatory/Government
        elif any(term in domain for term in ['.gov', '.eu', 'europa.eu', 'eur-lex']):
            return 'regulatory'
        
        # Tech News
        elif any(term in domain for term in ['techcrunch', 'venturebeat', 'wired', 'arstechnica']):
            return 'tech_news'
        
        # Business News
        elif any(term in domain for term in ['ft.com', 'wsj.com', 'economist', 'businessinsider']):
            return 'business_news'
        
        else:
            return 'general'
    
    def search(self, query: str, max_results: int = 5, include_raw: bool = False) -> List[Dict[str, Any]]:
        """
        Execute enhanced Tavily search with metadata extraction
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return
            include_raw: Include raw content for deeper analysis
            
        Returns:
            List of search results with enhanced metadata
        """
        if not self.api_key:
            logger.error("Tavily API key not configured")
            return []
        
        try:
            from tavily import TavilyClient
            
            # Initialize Tavily client
            client = TavilyClient(api_key=self.api_key)
            
            # Perform search with enhanced parameters for expert analysis
            response = client.search(
                query=query,
                search_depth="advanced",  # More comprehensive results
                max_results=max_results * 2,  # Get more results for filtering
                include_answer=False,  # We want raw results, not AI summary
                include_raw_content=include_raw,  # For deep analysis when needed
                include_images=False,
                include_domains=[  # Prioritize quality sources
                    "nature.com", "sciencedirect.com", "crunchbase.com",
                    "techcrunch.com", "reuters.com", "bloomberg.com",
                    "pitchbook.com", "cbinsights.com", "ft.com",
                    "eur-lex.europa.eu", "fda.gov", "epa.gov"
                ] if "regulatory" in query.lower() or "competitor" in query.lower() else None
            )
            
            # Extract enhanced metadata from results
            results = []
            for result in response.get('results', [])[:max_results]:
                # Extract domain for source quality assessment
                from urllib.parse import urlparse
                domain = urlparse(result.get('url', '')).netloc
                
                enhanced_result = {
                    'title': result.get('title', ''),
                    'url': result.get('url', ''),
                    'snippet': result.get('content', '')[:500],
                    'full_content': result.get('content', '') if include_raw else None,
                    'published_date': result.get('published_date'),
                    'domain': domain,
                    'score': result.get('score', 0),  # Relevance score from Tavily
                    'source_type': self._categorize_source(domain)
                }
                results.append(enhanced_result)
            
            # Sort by relevance score
            results.sort(key=lambda x: x.get('score', 0), reverse=True)
            
            logger.info(f"Enhanced Tavily search for '{query}' returned {len(results)} results with metadata")
            return results
            
        except ImportError as e:
            logger.error(f"Tavily library not installed: {e}")
            logger.error("Please run: pip install tavily")
            return []
        except Exception as e:
            logger.error(f"Tavily search failed: {e}")
            # Return empty list for transparent error handling
            return []


class MockSearchProvider(SearchProvider):
    """Mock search provider for TEST_MODE"""
    
    def search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Return mock search results for testing"""
        
        # Generate contextual mock results based on query
        mock_results = []
        
        if 'competitor' in query.lower():
            mock_results.extend([
                {
                    'title': 'FactorX - AI-Powered Invoice Factoring Platform',
                    'url': 'https://techcrunch.com/2024/factorx-series-a',
                    'snippet': 'FactorX raised $15M Series A for AI invoice factoring. Claims 48h approval but averages 72h in practice due to regulatory requirements.'
                },
                {
                    'title': 'PaymentFlow Expands Invoice Factoring to LATAM',
                    'url': 'https://fintech-news.com/paymentflow-latam-expansion',
                    'snippet': 'PaymentFlow, a competitor in AI-driven invoice factoring, expanded to LATAM markets with 60-hour approval times for SMEs.'
                }
            ])
        
        if 'expert' in query.lower() or 'opinion' in query.lower():
            mock_results.extend([
                {
                    'title': 'McKinsey SME Working Capital Report 2024',
                    'url': 'https://mckinsey.com/sme-working-capital-2024',
                    'snippet': 'Industry analysis shows 72-96 hour standard for invoice factoring approval. Sub-48h requires pre-established regulatory frameworks.'
                },
                {
                    'title': 'Expert Analysis: AI in Financial Services',
                    'url': 'https://harvard-business.com/ai-fintech-analysis',
                    'snippet': 'Harvard Business Review: AI can reduce approval times by 40% but regulatory compliance remains the bottleneck.'
                }
            ])
        
        if 'failed' in query.lower() or 'succeeded' in query.lower():
            mock_results.append({
                'title': 'Case Study: QuickFactor Shutdown After Regulatory Issues',
                'url': 'https://fintech-failures.com/quickfactor-case',
                'snippet': 'QuickFactor promised 24h invoice factoring but shut down after failing to meet regulatory requirements in multiple markets.'
            })
        
        # Default fallback result
        if not mock_results:
            mock_results.append({
                'title': 'General Market Analysis for Query',
                'url': 'https://market-research.com/analysis',
                'snippet': f'Market analysis related to: {query[:100]}. Industry trends show increasing competition and regulatory scrutiny.'
            })
        
        logger.info(f"Mock search for '{query}' returned {len(mock_results)} results")
        return mock_results[:max_results]


class WebSearchEngine:
    """Main web search engine with provider flexibility"""
    
    # FASE 2D: Expert-level configuration
    MIN_SOURCES_REQUIRED = 10
    MIN_COMPETITORS_REQUIRED = 5
    
    def __init__(self, provider: str = 'tavily'):
        """
        Initialize web search engine
        
        Args:
            provider: Search provider to use ('tavily', 'duckduckgo', 'mock')
        """
        self.provider_name = provider
        
        # Check if TEST_MODE is active
        if os.getenv('TEST_MODE', 'false').lower() == 'true':
            logger.info("🧪 TEST MODE: Using mock search provider")
            self.provider = MockSearchProvider()
        else:
            # Production mode - use real search provider
            if provider == 'tavily':
                # Check if Tavily API key is available
                if os.getenv('TAVILY_API_KEY'):
                    logger.info("🔍 Using Tavily search provider")
                    self.provider = TavilyProvider()
                else:
                    logger.warning("TAVILY_API_KEY not found, falling back to DuckDuckGo")
                    self.provider = DuckDuckGoProvider()
            elif provider == 'duckduckgo':
                logger.info("🦆 Using DuckDuckGo search provider")
                self.provider = DuckDuckGoProvider()
            elif provider == 'mock':
                self.provider = MockSearchProvider()
            else:
                # Default to Tavily if available, otherwise DuckDuckGo
                if os.getenv('TAVILY_API_KEY'):
                    logger.info(f"Unknown provider {provider}, defaulting to Tavily")
                    self.provider = TavilyProvider()
                else:
                    logger.warning(f"Unknown provider {provider}, defaulting to DuckDuckGo")
                    self.provider = DuckDuckGoProvider()
    
    def search_multiple(self, queries: List[str], max_results_per_query: int = 3) -> Dict[str, Any]:
        """
        Execute multiple searches and aggregate results
        
        Args:
            queries: List of search queries
            max_results_per_query: Max results per individual query
            
        Returns:
            Aggregated search intelligence
        """
        start_time = time.time()
        all_results = []
        search_terms_used = []
        
        for query in queries[:3]:  # FASE 1: Limit to 2-3 searches
            logger.info(f"Executing search: {query}")
            results = self.provider.search(query, max_results_per_query)
            all_results.extend(results)
            search_terms_used.append(query)
            
            # Small delay to avoid rate limiting (not needed for mock)
            if self.provider_name != 'mock' and os.getenv('TEST_MODE', 'false').lower() != 'true':
                time.sleep(0.5)
        
        elapsed_time = time.time() - start_time
        logger.info(f"Completed {len(queries)} searches in {elapsed_time:.2f} seconds")
        
        # Process and structure results
        web_intelligence = self._process_results(all_results, search_terms_used)
        web_intelligence['search_time_seconds'] = round(elapsed_time, 2)
        
        return web_intelligence
    
    def _process_results(self, results: List[Dict], search_terms: List[str]) -> Dict[str, Any]:
        """
        Process raw search results into structured intelligence with URLs and metadata
        
        FASE 2D: Enhanced processing with source tracking
        """
        competitors = []
        expert_insights = []
        regulatory_insights = []
        all_sources = []
        
        for result in results:
            snippet = result.get('snippet', '').lower()
            title = result.get('title', '').lower()
            url = result.get('url', '')
            source_type = result.get('source_type', 'general')
            domain = result.get('domain', '')
            
            # Track all sources for citation
            source_entry = {
                'title': result.get('title', ''),
                'url': url,
                'domain': domain,
                'type': source_type,
                'published_date': result.get('published_date'),
                'relevance_score': result.get('score', 0)
            }
            all_sources.append(source_entry)
            
            # Enhanced competitor extraction with URLs
            if any(term in snippet or term in title for term in ['competitor', 'raises', 'series', 'funding', 'platform']):
                # Extract potential competitor names
                competitor_patterns = re.findall(r'([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*)', result.get('snippet', ''))
                for comp in competitor_patterns[:2]:
                    if len(comp) > 3 and comp not in ['Series', 'The', 'This', 'That', 'Report', 'Analysis']:
                        # Check if it's a company name (heuristic: contains funding info or is mentioned as company)
                        if any(indicator in snippet for indicator in ['raised', 'funding', 'valuation', 'startup', 'company']):
                            competitors.append({
                                'name': comp,
                                'description': result.get('title', '')[:100],
                                'url': url,
                                'source_domain': domain,
                                'mention_context': result.get('snippet', '')[:200]
                            })
            
            # Enhanced expert insights with source attribution
            if source_type in ['academic', 'industry_report'] or any(term in snippet or term in title for term in ['analysis', 'report', 'expert', 'study', 'research']):
                sentences = result.get('snippet', '').split('.')
                for sentence in sentences:
                    if any(term in sentence.lower() for term in ['market', 'growth', 'trend', 'forecast', 'cagr', 'billion']):
                        expert_insights.append({
                            'insight': sentence.strip()[:200],
                            'source': result.get('title', '')[:50],
                            'url': url,
                            'source_type': source_type,
                            'date': result.get('published_date')
                        })
                        break
            
            # Regulatory insights extraction with URLs
            if source_type == 'regulatory' or any(term in snippet or term in title for term in ['regulation', 'compliance', 'directive', 'fda', 'epa', 'eu', 'requirement']):
                sentences = result.get('snippet', '').split('.')
                for sentence in sentences:
                    if any(term in sentence.lower() for term in ['require', 'must', 'mandate', 'compliance', 'certification', 'approval']):
                        regulatory_insights.append({
                            'regulation': sentence.strip()[:200],
                            'source': result.get('title', '')[:50],
                            'url': url,
                            'jurisdiction': 'EU' if 'eu' in domain.lower() else 'US' if '.gov' in domain else 'Unknown'
                        })
                        break
        
        # Deduplicate and limit results
        seen_competitors = set()
        unique_competitors = []
        for comp in competitors:
            if comp['name'] not in seen_competitors:
                seen_competitors.add(comp['name'])
                unique_competitors.append(comp)
        
        # Sort sources by relevance score
        all_sources.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
        
        return {
            'competitors_found': unique_competitors[:10],  # Increased limit for expert analysis
            'expert_insights': expert_insights[:10],
            'regulatory_insights': regulatory_insights[:5],
            'all_sources': all_sources[:15],  # Keep top 15 sources for citation
            'sources_count': len(results),
            'search_terms_used': search_terms,
            'source_quality_breakdown': {
                'academic': len([s for s in all_sources if s['type'] == 'academic']),
                'industry_report': len([s for s in all_sources if s['type'] == 'industry_report']),
                'financial': len([s for s in all_sources if s['type'] == 'financial']),
                'regulatory': len([s for s in all_sources if s['type'] == 'regulatory'])
            }
        }


class ValuePropositionExtractor:
    """Extract value proposition and keywords from documents - FASE 1: Simple regex approach"""
    
    def __init__(self):
        self.industry_keywords = {
            'fintech': ['payment', 'finance', 'banking', 'lending', 'invoice', 'factoring'],
            'saas': ['software', 'platform', 'cloud', 'subscription', 'enterprise'],
            'healthtech': ['health', 'medical', 'patient', 'clinical', 'pharma'],
            'cleantech': ['sustainable', 'renewable', 'energy', 'carbon', 'climate'],
            'marketplace': ['marketplace', 'ecommerce', 'b2b', 'b2c', 'platform']
        }
    
    def extract_simple(self, documents: List[Dict], document_summary: Dict) -> Dict[str, Any]:
        """
        Simple extraction using regex and keyword matching
        
        Args:
            documents: Processed documents from dataroom
            document_summary: Summary from initial analysis
            
        Returns:
            Extracted value proposition and keywords
        """
        try:
            # Combine all text for analysis
            full_text = ""
            if document_summary:
                full_text += str(document_summary.get('summary', ''))
            
            for doc in documents[:5]:  # Limit to first 5 docs for speed
                if 'content' in doc:
                    full_text += " " + str(doc['content'])[:1000]  # First 1000 chars per doc
            
            full_text = full_text.lower()
            
            # Extract industry vertical
            industry = self._detect_industry(full_text)
            
            # Extract key differentiators (look for specific patterns)
            differentiators = self._extract_differentiators(full_text)
            
            # Extract target market
            target_market = self._extract_target_market(full_text)
            
            # Build value proposition string
            value_proposition = self._build_value_proposition(industry, differentiators, target_market)
            
            logger.info(f"Extracted value proposition: {value_proposition}")
            
            return {
                'value_proposition': value_proposition,
                'key_differentiators': differentiators,
                'industry_keywords': self._get_industry_keywords(industry),
                'target_market': target_market,
                'extraction_method': 'simple_regex'
            }
            
        except Exception as e:
            logger.error(f"Value proposition extraction failed: {e}")
            # Return safe defaults
            return {
                'value_proposition': 'innovative business solution',
                'key_differentiators': ['technology', 'efficiency'],
                'industry_keywords': ['business', 'solution'],
                'target_market': 'enterprises',
                'extraction_method': 'fallback'
            }
    
    def _detect_industry(self, text: str) -> str:
        """Detect primary industry from text"""
        industry_scores = {}
        
        for industry, keywords in self.industry_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text)
            if score > 0:
                industry_scores[industry] = score
        
        if industry_scores:
            return max(industry_scores, key=industry_scores.get)
        return 'technology'
    
    def _extract_differentiators(self, text: str) -> List[str]:
        """Extract key differentiators using patterns"""
        differentiators = []
        
        # Look for time-based claims (e.g., "48 hour", "24h", "instant")
        time_patterns = re.findall(r'(\d+[\s-]?(?:hour|hr|h|day|minute|instant|real[\s-]?time))', text)
        differentiators.extend(time_patterns[:2])
        
        # Look for AI/ML mentions
        if 'ai' in text or 'artificial intelligence' in text or 'machine learning' in text:
            differentiators.append('AI-powered')
        
        # Look for geographic focus
        geo_patterns = ['latam', 'latin america', 'europe', 'asia', 'africa', 'global']
        for geo in geo_patterns:
            if geo in text:
                differentiators.append(geo.upper())
                break
        
        # Look for specific technology claims
        tech_patterns = ['blockchain', 'automated', 'proprietary', 'patented', 'unique']
        for tech in tech_patterns:
            if tech in text:
                differentiators.append(tech)
                break
        
        return differentiators[:4]  # Limit to 4 differentiators
    
    def _extract_target_market(self, text: str) -> str:
        """Extract target market from text"""
        market_patterns = {
            'SME': ['sme', 'small business', 'small and medium'],
            'Enterprise': ['enterprise', 'fortune 500', 'large companies'],
            'B2B': ['b2b', 'business to business'],
            'B2C': ['b2c', 'consumer', 'retail'],
            'Startups': ['startup', 'early stage', 'emerging companies']
        }
        
        for market, patterns in market_patterns.items():
            for pattern in patterns:
                if pattern in text:
                    return market
        
        return 'businesses'
    
    def _build_value_proposition(self, industry: str, differentiators: List[str], target: str) -> str:
        """Build a value proposition string from components"""
        diff_str = ' '.join(differentiators[:2]) if differentiators else industry
        return f"{diff_str} {industry} solution for {target}"
    
    def _get_industry_keywords(self, industry: str) -> List[str]:
        """Get relevant keywords for the industry"""
        return self.industry_keywords.get(industry, ['business', 'solution', 'platform'])


def perform_web_search(documents: List[Dict], document_summary: Dict, 
                      market_profile: Any = None) -> Dict[str, Any]:
    """
    Main entry point for web search functionality
    
    Args:
        documents: Processed documents from dataroom
        document_summary: Summary from initial analysis
        market_profile: Market profile from detection agent
        
    Returns:
        Web intelligence results
    """
    try:
        logger.info("🔍 Starting web search intelligence gathering...")
        
        # Extract value proposition
        extractor = ValuePropositionExtractor()
        extraction = extractor.extract_simple(documents, document_summary)
        
        # Build search queries based on extraction
        value_prop = extraction['value_proposition']
        differentiators = extraction['key_differentiators']
        target = extraction['target_market']
        
        # FASE 1: 2-3 focused searches
        queries = [
            f"{value_prop} competitors market analysis",
            f"{differentiators[0] if differentiators else value_prop} expert opinion",
        ]
        
        # Add third query if we have enough info
        if len(differentiators) > 1:
            queries.append(f"companies similar to {value_prop} success failure")
        
        # Execute searches
        search_engine = WebSearchEngine(provider='duckduckgo')
        web_intelligence = search_engine.search_multiple(queries)
        
        # Add extraction info to results
        web_intelligence['extraction_info'] = extraction
        
        logger.info(f"✅ Web search completed. Found {web_intelligence['sources_count']} sources")
        
        return web_intelligence
        
    except Exception as e:
        logger.error(f"Web search failed: {e}")
        # Return safe fallback
        return {
            'competitors_found': ['Web search unavailable'],
            'expert_insights': ['Web search unavailable'],
            'sources_count': 0,
            'search_terms_used': [],
            'extraction_info': {
                'value_proposition': 'Unable to extract',
                'extraction_method': 'error'
            }
        }