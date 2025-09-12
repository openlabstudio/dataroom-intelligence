"""
Enhanced Multi-Source Intelligence Collection for DataRoom Intelligence
Story 1.2: Expands from 24 to 50+ high-quality sources with intelligent quality scoring

Professional Implementation Strategy:
- Expands current Tavily API integration from 3→12+ queries
- Adds intelligent source quality scoring and filtering  
- Implements source diversity validation
- Maintains cost control with progressive search strategy
"""

import os
import time
from typing import Dict, List, Any, Optional, Set, Tuple
from datetime import datetime
from dataclasses import dataclass
from utils.logger import get_logger
from utils.web_search import WebSearchEngine

logger = get_logger(__name__)

@dataclass
class SourceQualityMetrics:
    """Metrics for evaluating source quality"""
    domain_authority: float  # 0-1 score based on domain reputation
    content_relevance: float  # 0-1 score based on title/content matching
    temporal_relevance: float  # 0-1 score based on publication date
    source_type: str  # 'professional', 'news', 'academic', 'industry', 'blog'
    geographic_relevance: float  # 0-1 score based on geographic focus
    overall_score: float  # Weighted composite score
    
@dataclass
class EnhancedSourceResult:
    """Enhanced source with quality scoring"""
    url: str
    title: str
    content: str
    quality_metrics: SourceQualityMetrics
    search_query: str
    collection_timestamp: datetime
    source_category: str  # 'competitive', 'validation', 'funding', 'regulatory'

class EnhancedSourceCollector:
    """
    Enhanced multi-source intelligence collector for Story 1.2
    Expands from current 24 to 50+ high-quality sources
    """
    
    def __init__(self):
        self.web_search_engine = WebSearchEngine(provider='tavily')
        
        # Quality thresholds for source filtering
        self.min_quality_threshold = 0.6  # Minimum acceptable quality score
        self.professional_source_domains = {
            'mckinsey.com', 'bcg.com', 'bain.com', 'deloitte.com', 'pwc.com',
            'kpmg.com', 'accenture.com', 'mordorintelligence.com', 'startus-insights.com',
            'crunchbase.com', 'pitchbook.com', 'cbinsights.com', 'techcrunch.com',
            'venturebeat.com', 'reuters.com', 'bloomberg.com', 'wsj.com', 'ft.com',
            'forbes.com', 'businessinsider.com', 'harvard.edu', 'stanford.edu',
            'mit.edu', 'weforum.org', 'oecd.org', 'statista.com'
        }
        
        # Source diversity tracking
        self.collected_domains: Set[str] = set()
        self.collected_source_types: Dict[str, int] = {}
        self.geographic_coverage: Set[str] = set()
        
        # Cost monitoring and control (Story 1.2)
        self.api_calls_count = 0
        self.total_sources_requested = 0
        self.estimated_cost_usd = 0.0
        self.cost_per_query = 0.02  # Estimated Tavily API cost per query
        self.max_cost_limit = 2.0   # Maximum cost limit per analysis ($2 USD)
        self.max_api_calls = 100    # Maximum API calls per analysis
        
    def collect_enhanced_sources(self, market_profile, target_sources: int = 50) -> Dict[str, Any]:
        """
        Main method to collect 50+ enhanced sources with intelligent quality scoring
        
        Args:
            market_profile: Market profile from MarketDetectionAgent
            target_sources: Target number of high-quality sources (default: 50)
            
        Returns:
            Enhanced source collection with quality metrics and diversity validation
        """
        try:
            logger.info(f"🔍 Enhanced Source Collection: Target {target_sources} high-quality sources")
            start_time = time.time()
            

            
            # Reset diversity tracking
            self.collected_domains.clear()
            self.collected_source_types.clear()
            self.geographic_coverage.clear()
            
            # Progressive search strategy to reach 50+ sources
            all_enhanced_sources = []
            
            # Phase 1: Core competitive intelligence (Target: 15-20 sources)
            competitive_sources = self._collect_competitive_sources(market_profile, target=18)
            all_enhanced_sources.extend(competitive_sources)
            logger.info(f"✅ Phase 1: {len(competitive_sources)} competitive sources collected")
            
            # Phase 2: Market validation intelligence (Target: 12-15 sources)
            validation_sources = self._collect_validation_sources(market_profile, target=12)
            all_enhanced_sources.extend(validation_sources)
            logger.info(f"✅ Phase 2: {len(validation_sources)} validation sources collected")
            
            # Phase 3: Funding & financial intelligence (Target: 10-12 sources)
            funding_sources = self._collect_funding_sources(market_profile, target=10)
            all_enhanced_sources.extend(funding_sources)
            logger.info(f"✅ Phase 3: {len(funding_sources)} funding sources collected")
            
            # Phase 4: Regulatory & industry intelligence (Target: 8-10 sources)
            regulatory_sources = self._collect_regulatory_sources(market_profile, target=8)
            all_enhanced_sources.extend(regulatory_sources)
            logger.info(f"✅ Phase 4: {len(regulatory_sources)} regulatory sources collected")
            
            # Quality filtering and ranking
            filtered_sources = self._apply_quality_filtering(all_enhanced_sources)
            top_sources = self._rank_and_select_top_sources(filtered_sources, target_sources)
            
            # Diversity validation
            diversity_metrics = self._validate_source_diversity(top_sources)
            
            collection_time = time.time() - start_time
            
            result = {
                'enhanced_sources': [self._source_to_dict(source) for source in top_sources],
                'quality_summary': self._generate_quality_summary(top_sources),
                'diversity_metrics': diversity_metrics,
                'collection_metadata': {
                    'total_sources_collected': len(all_enhanced_sources),
                    'sources_after_filtering': len(filtered_sources),
                    'final_source_count': len(top_sources),
                    'collection_time_seconds': round(collection_time, 2),
                    'target_achieved': len(top_sources) >= target_sources,
                    'average_quality_score': sum(s.quality_metrics.overall_score for s in top_sources) / len(top_sources) if top_sources else 0
                },
                'cost_summary': self._get_cost_summary()  # Story 1.2: Cost monitoring
            }
            
            logger.info(f"✅ Enhanced collection complete: {len(top_sources)} sources, avg quality: {result['collection_metadata']['average_quality_score']:.2f}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Enhanced source collection failed: {e}")
            return self._create_fallback_sources(target_sources)
    
    def _collect_competitive_sources(self, market_profile, target: int) -> List[EnhancedSourceResult]:
        """Collect competitive intelligence sources with enhanced query strategy"""
        queries = self._generate_competitive_queries(market_profile, comprehensive=True)
        return self._execute_enhanced_search(queries[:6], target, 'competitive')  # 6 queries × 3 = 18 max
    
    def _collect_validation_sources(self, market_profile, target: int) -> List[EnhancedSourceResult]:
        """Collect market validation sources with enhanced query strategy"""  
        queries = self._generate_validation_queries(market_profile, comprehensive=True)
        return self._execute_enhanced_search(queries[:4], target, 'validation')  # 4 queries × 3 = 12 max
    
    def _collect_funding_sources(self, market_profile, target: int) -> List[EnhancedSourceResult]:
        """Collect funding intelligence sources with enhanced query strategy"""
        queries = self._generate_funding_queries(market_profile, comprehensive=True)
        return self._execute_enhanced_search(queries[:4], target, 'funding')  # 4 queries × 3 = 12 max
    
    def _collect_regulatory_sources(self, market_profile, target: int) -> List[EnhancedSourceResult]:
        """Collect regulatory and industry sources with enhanced query strategy"""
        queries = self._generate_regulatory_queries(market_profile)
        return self._execute_enhanced_search(queries[:3], target, 'regulatory')  # 3 queries × 3 = 9 max
    
    def _execute_enhanced_search(self, queries: List[str], target: int, category: str) -> List[EnhancedSourceResult]:
        """Execute search queries with enhanced processing and quality scoring"""
        enhanced_sources = []
        
        for query in queries:
            try:
                # Cost monitoring: Check limits before API call
                if not self._check_cost_limits():
                    logger.warning(f"⚠️  Cost/API limits reached. Stopping search at {self.api_calls_count} calls, ${self.estimated_cost_usd:.2f}")
                    break
                
                # Execute search with higher results per query  
                raw_results = self.web_search_engine.provider.search(query, max_results=4)  # Increased from 3
                
                # Update cost tracking
                self._update_cost_metrics(query, len(raw_results))
                
                # Process each result with quality scoring
                for result in raw_results:
                    if len(enhanced_sources) >= target:
                        break
                        
                    enhanced_source = self._create_enhanced_source(result, query, category)
                    if enhanced_source and enhanced_source.quality_metrics.overall_score >= self.min_quality_threshold:
                        enhanced_sources.append(enhanced_source)
                
                # Rate limiting
                time.sleep(0.3)  # Rate limiting for API calls
                    
            except Exception as e:
                logger.error(f"Search failed for query '{query}': {e}")
                continue
        
        return enhanced_sources
    
    def _create_enhanced_source(self, raw_result: Dict[str, Any], query: str, category: str) -> Optional[EnhancedSourceResult]:
        """Create enhanced source with quality metrics from raw search result"""
        try:
            url = raw_result.get('url', '')
            title = raw_result.get('title', '')
            content = raw_result.get('content', '')
            
            if not url or not title:
                return None
            
            # Calculate quality metrics
            quality_metrics = self._calculate_quality_metrics(url, title, content, query)
            
            return EnhancedSourceResult(
                url=url,
                title=title,
                content=content,
                quality_metrics=quality_metrics,
                search_query=query,
                collection_timestamp=datetime.now(),
                source_category=category
            )
            
        except Exception as e:
            logger.error(f"Failed to create enhanced source: {e}")
            return None
    
    def _calculate_quality_metrics(self, url: str, title: str, content: str, query: str) -> SourceQualityMetrics:
        """Calculate comprehensive quality metrics for a source"""
        
        # Domain authority based on professional source list
        domain = self._extract_domain(url)
        domain_authority = 0.9 if domain in self.professional_source_domains else 0.5
        
        # Content relevance based on title/content matching query terms
        query_terms = set(query.lower().split())
        title_terms = set(title.lower().split())
        content_terms = set(content.lower().split()[:100])  # First 100 words
        
        title_matches = len(query_terms.intersection(title_terms)) / len(query_terms) if query_terms else 0
        content_matches = len(query_terms.intersection(content_terms)) / len(query_terms) if query_terms else 0
        content_relevance = (title_matches * 0.7 + content_matches * 0.3)
        
        # Temporal relevance (favor recent sources)
        temporal_relevance = 0.8  # Default for unknown dates, could be enhanced
        
        # Source type classification
        source_type = self._classify_source_type(domain, title, content)
        
        # Geographic relevance (default high, could be enhanced with location detection)
        geographic_relevance = 0.7
        
        # Calculate overall weighted score
        weights = {
            'domain_authority': 0.25,
            'content_relevance': 0.35,
            'temporal_relevance': 0.15,
            'geographic_relevance': 0.15,
            'source_type_bonus': 0.10
        }
        
        source_type_bonus = 0.9 if source_type == 'professional' else 0.6
        
        overall_score = (
            domain_authority * weights['domain_authority'] +
            content_relevance * weights['content_relevance'] + 
            temporal_relevance * weights['temporal_relevance'] +
            geographic_relevance * weights['geographic_relevance'] +
            source_type_bonus * weights['source_type_bonus']
        )
        
        return SourceQualityMetrics(
            domain_authority=domain_authority,
            content_relevance=content_relevance,
            temporal_relevance=temporal_relevance,
            source_type=source_type,
            geographic_relevance=geographic_relevance,
            overall_score=min(overall_score, 1.0)  # Cap at 1.0
        )
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        try:
            from urllib.parse import urlparse
            return urlparse(url).netloc.lower().replace('www.', '')
        except:
            return ''
    
    def _classify_source_type(self, domain: str, title: str, content: str) -> str:
        """Classify source type for quality assessment"""
        if domain in self.professional_source_domains:
            return 'professional'
        elif any(indicator in domain for indicator in ['news', 'reuters', 'bloomberg', 'wsj']):
            return 'news'
        elif any(indicator in domain for indicator in ['edu', 'research', 'study']):
            return 'academic'
        elif any(indicator in domain for indicator in ['industry', 'trade', 'association']):
            return 'industry'
        else:
            return 'blog'
    
    def _generate_competitive_queries(self, market_profile, comprehensive: bool = False) -> List[str]:
        """Generate comprehensive competitive intelligence queries"""
        solution = market_profile.solution
        sub_vertical = market_profile.sub_vertical
        vertical = market_profile.vertical
        target_market = market_profile.target_market
        
        queries = []
        
        # Enhanced solution-focused queries
        if solution:
            queries.extend([
                f'"{solution}" competitors market leaders analysis 2024',
                f'"{solution}" companies competitive landscape startups',
                f'"{solution}" technology providers vendors comparison'
            ])
            
        # Enhanced sub-vertical competitive queries
        if sub_vertical:
            queries.extend([
                f'"{sub_vertical}" competitive analysis market leaders',
                f'"{sub_vertical}" companies startups technology providers',
                f'"{sub_vertical}" market competition analysis 2024'
            ])
        
        # Enhanced vertical competitive queries  
        if vertical:
            queries.extend([
                f'"{vertical}" industry leaders competitive landscape',
                f'"{vertical}" major players market analysis 2024'
            ])
            
        # Combination queries for comprehensive coverage
        if solution and vertical:
            queries.append(f'"{solution}" {vertical} competitive analysis companies')
            
        if sub_vertical and target_market:
            queries.append(f'"{sub_vertical}" competitors "{target_market}" market')
        
        return queries
    
    def _generate_validation_queries(self, market_profile, comprehensive: bool = False) -> List[str]:
        """Generate comprehensive market validation queries"""
        solution = market_profile.solution
        sub_vertical = market_profile.sub_vertical
        vertical = market_profile.vertical
        target_market = market_profile.target_market
        
        queries = []
        
        # Enhanced validation queries
        if solution and target_market:
            queries.extend([
                f'"{solution}" market size TAM "{target_market}" 2024',
                f'"{solution}" market validation growth trends analysis',
                f'"{solution}" market opportunity "{target_market}" forecast'
            ])
            
        if sub_vertical:
            queries.extend([
                f'"{sub_vertical}" market size growth forecast 2024',
                f'"{sub_vertical}" industry analysis market validation'
            ])
            
        if vertical:
            queries.extend([
                f'"{vertical}" market size TAM addressable market 2024',
                f'"{vertical}" industry growth forecast analysis'
            ])
        
        return queries
    
    def _generate_funding_queries(self, market_profile, comprehensive: bool = False) -> List[str]:
        """Generate comprehensive funding intelligence queries"""
        solution = market_profile.solution
        sub_vertical = market_profile.sub_vertical
        vertical = market_profile.vertical
        
        queries = []
        
        # Enhanced funding queries
        if solution:
            queries.extend([
                f'"{solution}" startups funding rounds valuations 2024',
                f'"{solution}" venture capital investment deals'
            ])
            
        if sub_vertical:
            queries.extend([
                f'"{sub_vertical}" funding landscape startups 2024',
                f'"{sub_vertical}" venture capital investment rounds'
            ])
            
        if vertical:
            queries.extend([
                f'"{vertical}" startup funding venture capital 2024',
                f'"{vertical}" investment trends valuations analysis'
            ])
        
        return queries
    
    def _generate_regulatory_queries(self, market_profile) -> List[str]:
        """Generate regulatory and industry intelligence queries"""
        solution = market_profile.solution
        sub_vertical = market_profile.sub_vertical
        vertical = market_profile.vertical
        
        queries = []
        
        if solution:
            queries.append(f'"{solution}" regulatory requirements compliance 2024')
            
        if sub_vertical:
            queries.append(f'"{sub_vertical}" regulatory landscape industry analysis')
            
        if vertical:
            queries.append(f'"{vertical}" industry regulations compliance requirements')
        
        return queries
    
    def _apply_quality_filtering(self, sources: List[EnhancedSourceResult]) -> List[EnhancedSourceResult]:
        """Apply quality filtering to remove low-quality sources"""
        return [source for source in sources if source.quality_metrics.overall_score >= self.min_quality_threshold]
    
    def _rank_and_select_top_sources(self, sources: List[EnhancedSourceResult], target: int) -> List[EnhancedSourceResult]:
        """Rank sources by quality and select top N ensuring diversity"""
        # Sort by quality score (descending)
        sorted_sources = sorted(sources, key=lambda s: s.quality_metrics.overall_score, reverse=True)
        
        # Select top sources while maintaining diversity
        selected_sources = []
        used_domains = set()
        
        for source in sorted_sources:
            if len(selected_sources) >= target:
                break
                
            domain = self._extract_domain(source.url)
            
            # Allow up to 3 sources from the same domain to maintain quality
            domain_count = sum(1 for s in selected_sources if self._extract_domain(s.url) == domain)
            if domain_count < 3:
                selected_sources.append(source)
                used_domains.add(domain)
        
        return selected_sources
    
    def _validate_source_diversity(self, sources: List[EnhancedSourceResult]) -> Dict[str, Any]:
        """Validate source diversity across multiple dimensions"""
        if not sources:
            return {}
            
        # Domain diversity
        domains = [self._extract_domain(s.url) for s in sources]
        unique_domains = len(set(domains))
        
        # Source type diversity
        source_types = [s.quality_metrics.source_type for s in sources]
        unique_source_types = len(set(source_types))
        
        # Category diversity
        categories = [s.source_category for s in sources]
        category_distribution = {cat: categories.count(cat) for cat in set(categories)}
        
        return {
            'domain_diversity': unique_domains,
            'source_type_diversity': unique_source_types,
            'category_distribution': category_distribution,
            'professional_source_percentage': (sum(1 for s in sources if s.quality_metrics.source_type == 'professional') / len(sources)) * 100,
            'average_quality_score': sum(s.quality_metrics.overall_score for s in sources) / len(sources),
            'diversity_score': min((unique_domains / 20) + (unique_source_types / 5), 1.0)  # Normalized diversity score
        }
    
    def _generate_quality_summary(self, sources: List[EnhancedSourceResult]) -> Dict[str, Any]:
        """Generate quality summary for collected sources"""
        if not sources:
            return {}
            
        quality_scores = [s.quality_metrics.overall_score for s in sources]
        
        return {
            'total_sources': len(sources),
            'average_quality': sum(quality_scores) / len(quality_scores),
            'min_quality': min(quality_scores),
            'max_quality': max(quality_scores),
            'high_quality_sources': sum(1 for score in quality_scores if score >= 0.8),
            'professional_sources': sum(1 for s in sources if s.quality_metrics.source_type == 'professional'),
            'quality_distribution': {
                'excellent': sum(1 for score in quality_scores if score >= 0.9),
                'good': sum(1 for score in quality_scores if 0.7 <= score < 0.9),
                'acceptable': sum(1 for score in quality_scores if 0.6 <= score < 0.7)
            }
        }
    
    def _source_to_dict(self, source: EnhancedSourceResult) -> Dict[str, Any]:
        """Convert enhanced source to dictionary for JSON serialization"""
        return {
            'url': source.url,
            'title': source.title,
            'content': source.content[:500] + '...' if len(source.content) > 500 else source.content,  # Truncate for size
            'quality_score': source.quality_metrics.overall_score,
            'source_type': source.quality_metrics.source_type,
            'source_category': source.source_category,
            'search_query': source.search_query,
            'domain_authority': source.quality_metrics.domain_authority,
            'content_relevance': source.quality_metrics.content_relevance
        }
    

    
    def _check_cost_limits(self) -> bool:
        """Check if cost and API call limits are within acceptable range"""
        if self.api_calls_count >= self.max_api_calls:
            logger.warning(f"API call limit reached: {self.api_calls_count}/{self.max_api_calls}")
            return False
            
        if self.estimated_cost_usd >= self.max_cost_limit:
            logger.warning(f"Cost limit reached: ${self.estimated_cost_usd:.2f}/${self.max_cost_limit:.2f}")
            return False
            
        return True
    
    def _update_cost_metrics(self, query: str, results_count: int):
        """Update cost tracking metrics after API call"""
        self.api_calls_count += 1
        self.total_sources_requested += results_count
        self.estimated_cost_usd += self.cost_per_query
        
        logger.info(f"💰 Cost tracking: Call #{self.api_calls_count}, ${self.estimated_cost_usd:.3f} total, {results_count} results")
    
    def _get_cost_summary(self) -> Dict[str, Any]:
        """Generate cost summary for monitoring and reporting"""
        return {
            'api_calls_made': self.api_calls_count,
            'total_sources_requested': self.total_sources_requested,
            'estimated_cost_usd': round(self.estimated_cost_usd, 3),
            'cost_per_query': self.cost_per_query,
            'cost_efficiency_ratio': round(self.total_sources_requested / self.estimated_cost_usd, 2) if self.estimated_cost_usd > 0 else 0,
            'within_cost_limits': self.estimated_cost_usd <= self.max_cost_limit,
            'within_api_limits': self.api_calls_count <= self.max_api_calls
        }

    def _create_fallback_sources(self, target_sources: int) -> Dict[str, Any]:
        """Create fallback sources when collection fails"""
        return {
            'enhanced_sources': [],
            'quality_summary': {'total_sources': 0, 'error': 'Collection failed'},
            'diversity_metrics': {'error': 'Collection failed'},
            'collection_metadata': {
                'total_sources_collected': 0,
                'final_source_count': 0,
                'target_achieved': False,
                'error': 'Enhanced collection failed, fallback activated'
            },
            'cost_summary': self._get_cost_summary()
        }