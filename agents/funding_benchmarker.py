"""
Funding Benchmarker Agent for DataRoom Intelligence
Benchmarks funding metrics against industry standards and similar companies

Phase 2B.1 - TASK-003: Funding Benchmarker Implementation
"""

import os
import json
from typing import Dict, List, Any, Optional
from .base_agent import BaseAgent
from utils.logger import get_logger

logger = get_logger(__name__)

class FundingBenchmarkProfile:
    """Data structure for funding benchmark results"""
    
    def __init__(self):
        # FASE 2C: Enhanced structure for independent analysis + startup claims
        # Independent market analysis
        self.market_funding_patterns: List[str] = []  # Recent funding patterns from web
        self.similar_deals: List[Dict[str, Any]] = []  # Similar deals with outcomes
        self.investor_sentiment: List[str] = []  # Current investor sentiment
        self.funding_climate: str = ""  # Current funding climate assessment
        self.typical_ranges: Dict[str, str] = {}  # Typical funding ranges for sector
        self.success_factors: List[str] = []  # What's working in current market
        
        # Startup claims (for PDF comparison later)
        self.startup_claimed_stage: str = ""
        self.startup_claimed_amount: str = ""
        self.startup_claimed_valuation: str = ""
        self.startup_claimed_metrics: List[str] = []
        
        # Analysis metadata
        self.market_assessment: str = ""  # Overall market assessment
        self.confidence_level: str = ""  # low, medium, high
        self.sources: List[Dict[str, Any]] = []  # Web search sources
        self.confidence_score: float = 0.0
        
        # Legacy fields for backward compatibility
        self.stage: str = ""  
        self.amount_raised: str = ""
        self.valuation: str = ""
        self.industry_benchmarks: Dict[str, Any] = {}
        self.metrics_comparison: Dict[str, Any] = {}
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            # Independent analysis for Slack
            'independent_analysis': {
                'market_funding_patterns': self.market_funding_patterns,
                'similar_deals': self.similar_deals,
                'investor_sentiment': self.investor_sentiment,
                'funding_climate': self.funding_climate,
                'typical_ranges': self.typical_ranges,
                'success_factors': self.success_factors,
                'market_assessment': self.market_assessment,
                'confidence_level': self.confidence_level,
                'sources_count': len(self.sources),
                'confidence_score': self.confidence_score
            },
            # Startup claims for PDF comparison
            'startup_claims_extracted': {
                'claimed_stage': self.startup_claimed_stage,
                'claimed_amount': self.startup_claimed_amount,
                'claimed_valuation': self.startup_claimed_valuation,
                'claimed_metrics': self.startup_claimed_metrics
            },
            # Legacy fields for backward compatibility
            'stage': self.stage or self.startup_claimed_stage,
            'amount_raised': self.amount_raised or self.startup_claimed_amount,
            'valuation': self.valuation or self.startup_claimed_valuation,
            'industry_benchmarks': self.industry_benchmarks or self.typical_ranges,
            'metrics_comparison': self.metrics_comparison,
            'confidence_score': self.confidence_score
        }

class FundingBenchmarkerAgent(BaseAgent):
    """Specialized agent for benchmarking funding metrics against industry standards"""
    
    def __init__(self):
        super().__init__("Funding Benchmarker")
        # FASE 2C: Initialize web search engine
        self.web_search_engine = None  # Will be initialized on first use
        self.funding_benchmarks = {
            'seed': {
                'typical_range': '$500K-$2M',
                'valuation_range': '$3M-$10M',
                'runway_months': '12-18',
                'metrics_focus': ['Product-market fit', 'Early traction', 'Team strength']
            },
            'series_a': {
                'typical_range': '$2M-$15M',
                'valuation_range': '$10M-$50M',
                'runway_months': '18-24',
                'metrics_focus': ['ARR growth', 'Unit economics', 'Market expansion']
            },
            'series_b': {
                'typical_range': '$10M-$50M',
                'valuation_range': '$30M-$200M',
                'runway_months': '18-24',
                'metrics_focus': ['Revenue growth', 'Market share', 'Expansion strategy']
            }
        }
        
        self.industry_multiples = {
            'saas': {'revenue_multiple': '5-15x', 'arr_growth': '100-200%'},
            'fintech': {'revenue_multiple': '4-10x', 'arr_growth': '80-150%'},
            'marketplace': {'gmv_multiple': '0.5-2x', 'take_rate': '10-30%'},
            'hardware': {'revenue_multiple': '2-5x', 'gross_margin': '30-50%'}
        }
    
    def analyze(self, processed_documents: List[Dict[str, Any]], 
               document_summary: Dict[str, Any]) -> Dict[str, Any]:
        """
        Required abstract method from BaseAgent - delegates to benchmark_funding
        
        Args:
            processed_documents: List of processed documents
            document_summary: Summary of documents
            
        Returns:
            Dict with funding benchmark analysis
        """
        # For compatibility with BaseAgent, delegate to benchmark_funding
        # Use a simple market profile for this method
        from .market_detection import MarketProfile
        market_profile = MarketProfile()
        
        funding_profile = self.benchmark_funding(
            market_profile, 
            processed_documents,
            None
        )
        return funding_profile.to_dict()
    
    def _init_web_search(self):
        """Lazy initialize web search engine"""
        if self.web_search_engine is None:
            try:
                from utils.web_search import WebSearchEngine
                self.web_search_engine = WebSearchEngine()  # Uses default (Tavily if available)
            except ImportError as e:
                logger.warning(f"Web search not available: {e}")
                self.web_search_engine = None
    
    def benchmark_funding(self, market_profile: Any, documents: List[Dict], 
                         competitive_analysis: Optional[Dict] = None,
                         analysis_result: Optional[Dict] = None) -> FundingBenchmarkProfile:
        """
        FASE 2C: Enhanced funding benchmark with integrated web search
        
        Provides independent, market-based funding analysis without comparisons
        to startup claims. Web search provides recent market intelligence.
        
        Args:
            market_profile: Market profile from detection agent
            documents: Processed documents (for value prop extraction)
            competitive_analysis: Optional competitive intelligence
            analysis_result: Optional analysis result from /analyze
            
        Returns:
            FundingBenchmarkProfile with independent market analysis
        """
        logger.info(f"💰 Starting funding benchmark analysis with web search...")
        
        # Check TEST MODE first
        if os.getenv('TEST_MODE', 'false').lower() == 'true':
            logger.info("🧪 TEST MODE: Returning enhanced mock funding data")
            return self._get_mock_funding_benchmark_enhanced(market_profile)
        
        try:
            # FASE 2C: Build value proposition from market profile
            value_proposition = self._build_value_proposition_from_profile(market_profile)
            logger.info(f"🎯 Value proposition: {value_proposition}")
            
            # Step 1: Extract startup claims from documents
            startup_claims = self._extract_startup_funding_claims(documents, analysis_result)
            
            # Step 2: Perform independent 3-level hierarchical web search for funding intelligence
            web_intelligence = self._perform_multilevel_funding_search(market_profile)
            
            # Step 3: Analyze with GPT-4 if available (expert-level with web intelligence)
            gpt4_analysis = None
            if self._has_openai_key():
                gpt4_analysis = self._perform_gpt4_funding_analysis(
                    market_profile, documents, analysis_result, web_intelligence
                )
            
            # Step 4: Integrate all sources into comprehensive profile
            funding_profile = self._integrate_funding_intelligence(
                startup_claims, web_intelligence, gpt4_analysis, market_profile
            )
            
            # Log key findings
            logger.info(f"✅ Found {len(funding_profile.market_funding_patterns)} funding patterns")
            logger.info(f"📊 Found {len(funding_profile.similar_deals)} similar deals")
            logger.info(f"🌡️ Funding climate: {funding_profile.funding_climate}")
            logger.info(f"🔍 Sources analyzed: {len(funding_profile.sources)}")
            
            return funding_profile
            
        except Exception as e:
            logger.error(f"❌ Funding benchmark analysis failed: {e}")
            return self._get_basic_benchmark_fallback(market_profile)
    
    def _get_mock_funding_benchmark(self) -> FundingBenchmarkProfile:
        """Return mock independent funding benchmark data for TEST MODE"""
        profile = FundingBenchmarkProfile()
        
        # Market Analysis (not startup-specific)
        profile.stage = "Market Analysis"
        profile.amount_raised = "N/A - Market Analysis"
        profile.valuation = "N/A - Market Analysis"
        
        # Independent market benchmarks for FinTech in Europe
        profile.industry_benchmarks = {
            'market_sector': 'fintech in europe',
            'series_a_range': '$2M-$15M',
            'series_b_range': '$10M-$50M',
            'typical_revenue_multiple': '6-8x',
            'median_runway_months': '18-24',
            'funding_climate_2024': 'Cautious - 25% down from 2022 peak',
            'investor_focus': 'Strong emphasis on unit economics and path to profitability',
            'regulatory_factor': 'GDPR and EU regulations add complexity'
        }
        
        profile.comparable_companies = [
            {
                'note': 'Market-based analysis',
                'sector': 'FinTech in Europe',
                'patterns': 'Typical funding rounds show conservative valuations',
                'investor_behavior': 'European VCs prioritize sustainable growth'
            }
        ]
        
        # Independent market analysis (not startup specific)
        profile.metrics_comparison = {
            'market_analysis': 'Independent analysis of fintech funding patterns in europe',
            'funding_climate': 'Cautious - 25% down from 2022 peak',
            'investor_priorities': 'Strong emphasis on unit economics and path to profitability',
            'typical_series_a': '$2M-$15M',
            'revenue_expectations': '6-8x',
            'runway_standards': '18-24 months',
            'regulatory_considerations': 'GDPR and EU regulations add complexity'
        }
        
        profile.funding_efficiency = "Market efficiency in fintech/europe: Cautious - 25% down from 2022 peak. Investors focusing on strong emphasis on unit economics and path to profitability."
        profile.runway_analysis = "Typical fintech companies maintain 18-24 runway post-funding to reach next milestones"
        profile.investor_quality = "Investor landscape for fintech in europe: Mix of specialist VCs and generalist funds. Quality varies - focus on funds with sector experience and portfolio company support."
        profile.next_round_readiness = "2024 fundraising climate for fintech in europe: Selective market with emphasis on unit economics. Companies need strong metrics and clear path to profitability."
        
        profile.confidence_score = 0.8  # Higher confidence for market analysis
        
        return profile
    
    def _get_funding_from_analysis(self, analysis_result: Optional[Dict]) -> Dict[str, Any]:
        """Extract funding data from /analyze results (what startup claims)"""
        
        if not analysis_result:
            logger.warning("⚠️ No analysis result provided - cannot extract funding data")
            return {
                'stage': 'Unknown',
                'amount_raised': 'Not disclosed',
                'valuation': 'Not disclosed',
                'investors': [],
                'burn_rate': 'Unknown',
                'runway': 'Unknown',
                'revenue': 'Unknown',
                'growth_rate': 'Unknown'
            }
        
        # Extract funding information from analysis result
        # Analysis result typically contains sections like financial_summary, etc.
        funding_claims = {
            'stage': 'Unknown',
            'amount_raised': 'Not disclosed', 
            'valuation': 'Not disclosed',
            'investors': [],
            'burn_rate': 'Unknown',
            'runway': 'Unknown',
            'revenue': 'Unknown',
            'growth_rate': 'Unknown'
        }
        
        # Try to extract from various sections of the analysis
        if 'scoring' in analysis_result:
            scoring = analysis_result['scoring']
            if 'financials' in scoring:
                financials = scoring['financials']
                # Extract any funding-related info from scoring
                logger.info(f"📋 Found financials section in analysis: {financials}")
        
        # Look for executive summary or other sections that might contain funding info
        if 'executive_summary' in analysis_result:
            summary = analysis_result['executive_summary']
            logger.info(f"📋 Found executive summary for funding extraction: {type(summary)}")
            
        logger.info("📋 Extracted funding claims from /analyze results")
        return funding_claims
    
    def _get_industry_vertical(self, market_profile: Any) -> str:
        """Get industry vertical from market profile for benchmarking"""
        if hasattr(market_profile, 'vertical') and market_profile.vertical:
            vertical = market_profile.vertical.lower()
            # Map to standard industry categories for benchmarking
            if 'fintech' in vertical or 'payment' in vertical or 'financial' in vertical:
                return 'fintech'
            elif 'saas' in vertical or 'software' in vertical:
                return 'saas'
            elif 'cleantech' in vertical or 'sustainability' in vertical or 'green' in vertical:
                return 'cleantech'
            elif 'health' in vertical or 'medical' in vertical or 'pharma' in vertical:
                return 'healthtech'
            elif 'marketplace' in vertical or 'ecommerce' in vertical:
                return 'marketplace'
            else:
                return vertical
        return 'general'
    
    def _get_external_benchmarks(self, industry: str, stage: str) -> Dict[str, Any]:
        """Get external industry benchmarks (independent from startup claims)"""
        
        # Base benchmarks by stage
        stage_benchmarks = self.funding_benchmarks.get(
            stage.lower().replace(' ', '_'), 
            self.funding_benchmarks.get('series_a', {})
        )
        
        # Industry-specific multiples and metrics
        industry_data = self.industry_multiples.get(industry, {})
        
        # Enhanced benchmarks with real market data
        benchmarks = {
            'stage_typical': stage_benchmarks,
            'industry_multiples': industry_data,
            'market_conditions_2024': {
                'median_valuation_change': '-30% vs 2021-2022 peak',
                'funding_difficulty': 'High - quality bar raised significantly',
                'investor_focus': 'Unit economics and path to profitability'
            }
        }
        
        return benchmarks
    
    def _perform_independent_analysis(self, claims: Dict, benchmarks: Dict, industry: str) -> Dict[str, Any]:
        """Perform independent analysis comparing claims vs market reality"""
        
        analysis = {
            'valuation_assessment': 'Unable to assess - insufficient data',
            'stage_appropriateness': 'Unknown',
            'market_positioning': 'Unknown',
            'funding_efficiency': 'Unknown',
            'verdict': 'Insufficient data for independent assessment'
        }
        
        # Basic analysis based on available data
        if claims.get('stage') != 'Unknown':
            analysis['stage_appropriateness'] = f"Stage identified as {claims['stage']}"
        
        if industry != 'general':
            analysis['market_positioning'] = f"Operating in {industry} sector with specific benchmarks available"
        
        return analysis
    
    def _determine_funding_stage(self, funding_data: Dict) -> str:
        """Determine the company's funding stage"""
        # Logic to determine stage based on funding data
        return funding_data.get('last_round', 'Seed')
    
    def _determine_industry(self, market_profile: Any) -> str:
        """Determine industry vertical for benchmarking"""
        if hasattr(market_profile, 'vertical'):
            vertical = market_profile.vertical.lower()
            if 'saas' in vertical or 'software' in vertical:
                return 'saas'
            elif 'fintech' in vertical or 'payment' in vertical:
                return 'fintech'
            elif 'marketplace' in vertical:
                return 'marketplace'
        return 'general'
    
    def _get_industry_benchmarks(self, stage: str, industry: str) -> Dict[str, Any]:
        """Get industry-specific benchmarks for the funding stage"""
        stage_key = stage.lower().replace(' ', '_')
        benchmarks = self.funding_benchmarks.get(stage_key, {})
        industry_data = self.industry_multiples.get(industry, {})
        
        return {
            **benchmarks,
            **industry_data
        }
    
    def _find_comparables(self, market_profile: Any, stage: str, industry: str) -> List[Dict]:
        """Find comparable companies for benchmarking"""
        # In production, would search for real comparables
        return []
    
    def _compare_metrics(self, funding_data: Dict, benchmarks: Dict, 
                        comparables: List[Dict]) -> Dict[str, Any]:
        """Compare company metrics against benchmarks and comparables"""
        return {
            'status': 'Analysis pending',
            'key_metrics': {}
        }
    
    def _assess_efficiency_vs_market(self, claims: Dict, benchmarks: Dict) -> str:
        """Assess funding efficiency vs market standards (independent analysis)"""
        
        if claims.get('amount_raised') == 'Not disclosed':
            return "Cannot assess efficiency - funding amount not disclosed"
        
        # Generic market-based assessment
        return "Funding efficiency analysis requires revenue and burn rate data for accurate benchmarking"
    
    def _assess_runway_vs_stage(self, claims: Dict, benchmarks: Dict) -> str:
        """Assess runway vs stage expectations (independent analysis)"""
        
        stage = claims.get('stage', 'Unknown')
        if stage == 'Unknown':
            return "Cannot assess runway - funding stage not identified"
        
        # Stage-based runway expectations
        stage_benchmarks = benchmarks.get('stage_typical', {})
        expected_runway = stage_benchmarks.get('runway_months', 'Unknown')
        
        if expected_runway != 'Unknown':
            return f"Typical {stage} companies maintain {expected_runway} runway - assessment requires burn rate data"
        
        return "Runway analysis requires financial disclosure and burn rate information"
    
    def _assess_investor_quality(self, claims: Dict) -> str:
        """Assess investor quality based on disclosed information"""
        
        investors = claims.get('investors', [])
        if not investors:
            return "Investor information not disclosed in documents"
        
        return f"Investor assessment available for {len(investors)} disclosed investors"
    
    def _assess_next_round_readiness_independent(self, claims: Dict, analysis: Dict) -> str:
        """Independent assessment of next round readiness"""
        
        stage = claims.get('stage', 'Unknown')
        
        if stage == 'Unknown':
            return "Next round readiness assessment requires stage identification"
        
        # Market conditions context
        return "Next round readiness depends on market conditions (2024: high bar for quality metrics, profitability focus)"
    
    def _calculate_analysis_confidence(self, claims: Dict) -> float:
        """Calculate confidence in independent analysis based on data availability"""
        
        data_completeness = [
            claims.get('stage') != 'Unknown',
            claims.get('amount_raised') != 'Not disclosed', 
            claims.get('valuation') != 'Not disclosed',
            claims.get('revenue') != 'Unknown',
            claims.get('growth_rate') != 'Unknown'
        ]
        
        base_confidence = sum(data_completeness) / len(data_completeness)
        
        # Adjust for analysis type (independent analysis has inherent uncertainty)
        adjusted_confidence = base_confidence * 0.7  # Independent analysis is inherently less certain
        
        return max(0.3, adjusted_confidence)  # Minimum confidence for independent analysis
    
    def _get_geography(self, market_profile: Any) -> str:
        """Extract geography from market profile"""
        if hasattr(market_profile, 'geo_focus') and market_profile.geo_focus:
            geo = market_profile.geo_focus.lower()
            # Map to standard geographic regions for benchmarking
            if 'europe' in geo or 'eu' in geo:
                return 'europe'
            elif 'north america' in geo or 'usa' in geo or 'us' in geo or 'canada' in geo:
                return 'north_america'
            elif 'latam' in geo or 'latin america' in geo or 'south america' in geo:
                return 'latam'
            elif 'asia' in geo or 'apac' in geo:
                return 'asia'
            else:
                return geo
        return 'global'
    
    def _get_market_funding_benchmarks(self, industry: str, geography: str) -> Dict[str, Any]:
        """Get independent market-based funding benchmarks for industry + geography"""
        
        # Base industry benchmarks (global)
        base_benchmarks = {
            'fintech': {
                'seed_range': '$500K-$2M',
                'series_a_range': '$2M-$15M',
                'series_b_range': '$10M-$50M',
                'typical_revenue_multiple': '6-8x',
                'median_runway_months': '18-24'
            },
            'saas': {
                'seed_range': '$500K-$3M',
                'series_a_range': '$3M-$20M', 
                'series_b_range': '$15M-$60M',
                'typical_revenue_multiple': '8-15x',
                'median_runway_months': '18-24'
            },
            'cleantech': {
                'seed_range': '$1M-$5M',
                'series_a_range': '$5M-$25M',
                'series_b_range': '$20M-$100M',
                'typical_revenue_multiple': '3-6x',
                'median_runway_months': '24-36'
            },
            'healthtech': {
                'seed_range': '$1M-$4M',
                'series_a_range': '$4M-$20M',
                'series_b_range': '$15M-$80M',
                'typical_revenue_multiple': '4-8x',
                'median_runway_months': '24-30'
            },
            'marketplace': {
                'seed_range': '$500K-$3M',
                'series_a_range': '$3M-$18M',
                'series_b_range': '$12M-$70M',
                'gmv_multiple': '0.5-2x',
                'median_runway_months': '18-24'
            }
        }
        
        # Geographic adjustments for funding climate
        geo_adjustments = {
            'europe': {
                'funding_climate_2024': 'Cautious - 25% down from 2022 peak',
                'investor_focus': 'Strong emphasis on unit economics and path to profitability',
                'regulatory_factor': 'GDPR and EU regulations add complexity'
            },
            'north_america': {
                'funding_climate_2024': 'Selective - high bar for growth metrics', 
                'investor_focus': 'Revenue growth and clear monetization',
                'regulatory_factor': 'Sector-specific regulations vary by state'
            },
            'latam': {
                'funding_climate_2024': 'Emerging - growing investor interest',
                'investor_focus': 'Market penetration and local partnerships',
                'regulatory_factor': 'Regulatory environment varies significantly by country'
            },
            'asia': {
                'funding_climate_2024': 'Mixed - strong in certain verticals',
                'investor_focus': 'Scalability and market dominance',
                'regulatory_factor': 'Complex regulatory landscape'
            },
            'global': {
                'funding_climate_2024': 'Challenging - investors prioritize quality over quantity',
                'investor_focus': 'Proven business models with clear ROI',
                'regulatory_factor': 'Multi-jurisdictional compliance required'
            }
        }
        
        industry_data = base_benchmarks.get(industry, base_benchmarks['saas'])
        geo_data = geo_adjustments.get(geography, geo_adjustments['global'])
        
        return {
            'industry_benchmarks': industry_data,
            'geographic_context': geo_data,
            'market_sector': f"{industry} in {geography}",
            'data_source': 'Independent market analysis 2024'
        }
    
    def _analyze_market_funding_patterns(self, industry: str, geography: str, benchmarks: Dict) -> Dict[str, Any]:
        """Analyze market funding patterns for this industry/geography combination"""
        
        industry_data = benchmarks.get('industry_benchmarks', {})
        geo_context = benchmarks.get('geographic_context', {})
        
        return {
            'market_analysis': f"Independent analysis of {industry} funding patterns in {geography}",
            'funding_climate': geo_context.get('funding_climate_2024', 'Unknown'),
            'investor_priorities': geo_context.get('investor_focus', 'Standard due diligence'),
            'typical_series_a': industry_data.get('series_a_range', 'Data not available'),
            'revenue_expectations': industry_data.get('typical_revenue_multiple', 'Varies by sector'),
            'runway_standards': industry_data.get('median_runway_months', '18-24 months typical'),
            'regulatory_considerations': geo_context.get('regulatory_factor', 'Standard compliance required')
        }
    
    def _assess_market_efficiency_patterns(self, industry: str, geography: str, benchmarks: Dict) -> str:
        """Assess market efficiency patterns for this sector/geography"""
        geo_context = benchmarks.get('geographic_context', {})
        climate = geo_context.get('funding_climate_2024', 'Unknown')
        
        return f"Market efficiency in {industry}/{geography}: {climate}. Investors focusing on {geo_context.get('investor_focus', 'standard metrics')}."
    
    def _assess_market_runway_patterns(self, industry: str, benchmarks: Dict) -> str:
        """Assess typical runway patterns for this industry"""
        industry_data = benchmarks.get('industry_benchmarks', {})
        typical_runway = industry_data.get('median_runway_months', '18-24')
        
        return f"Typical {industry} companies maintain {typical_runway} runway post-funding to reach next milestones"
    
    def _assess_market_investor_patterns(self, industry: str, geography: str) -> str:
        """Assess investor quality patterns in this market"""
        return f"Investor landscape for {industry} in {geography}: Mix of specialist VCs and generalist funds. Quality varies - focus on funds with sector experience and portfolio company support."
    
    def _assess_market_fundraising_climate(self, industry: str, geography: str) -> str:
        """Assess current fundraising climate for this market"""
        return f"2024 fundraising climate for {industry} in {geography}: Selective market with emphasis on unit economics. Companies need strong metrics and clear path to profitability."
    
    def _calculate_market_confidence(self, industry: str, geography: str) -> float:
        """Calculate confidence based on market data availability"""
        # Higher confidence for well-known industry/geography combinations
        known_industries = ['fintech', 'saas', 'cleantech', 'healthtech', 'marketplace']
        known_geographies = ['europe', 'north_america', 'latam', 'asia']
        
        confidence = 0.7  # Base confidence for market analysis
        
        if industry in known_industries:
            confidence += 0.1
        if geography in known_geographies:
            confidence += 0.1
            
        return min(confidence, 0.9)  # Max 0.9 for independent analysis
    
    def _get_basic_benchmark_fallback(self, market_profile: Any) -> FundingBenchmarkProfile:
        """Return basic benchmark when full analysis fails"""
        
        profile = FundingBenchmarkProfile()
        
        industry = self._get_industry_vertical(market_profile)
        geography = self._get_geography(market_profile)
        
        profile.stage = "Market Analysis"
        profile.amount_raised = "N/A - Market Analysis"
        profile.valuation = "N/A - Market Analysis"
        
        profile.industry_benchmarks = {
            'industry': industry,
            'geography': geography,
            'note': 'Limited data available for comprehensive market benchmarking'
        }
        
        profile.metrics_comparison = {
            'assessment': f'Basic market analysis for {industry} in {geography}',
            'recommendation': 'Independent market benchmarking based on sector and geography only'
        }
        
        profile.funding_efficiency = f"Market patterns for {industry}: varies by specific business model and metrics"
        profile.runway_analysis = f"Typical {industry} runway: 18-24 months post-funding"
        profile.investor_quality = f"Investor landscape for {geography}: mix of local and international funds"
        profile.next_round_readiness = f"Market conditions for {industry} fundraising: selective with focus on metrics"
        
        profile.confidence_score = 0.6  # Moderate confidence for market analysis
        
        return profile
    
    # ========== FASE 2C: NEW METHODS FOR WEB SEARCH INTEGRATION ==========
    
    def _build_value_proposition_from_profile(self, market_profile) -> str:
        """Build value proposition from detected market profile"""
        try:
            # Handle both MarketProfile object and dict
            if hasattr(market_profile, 'solution'):
                solution = market_profile.solution
                sub_vertical = market_profile.sub_vertical
                vertical = market_profile.vertical
                target_market = market_profile.target_market
            else:
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
    
    def _extract_value_proposition(self, documents: List[Dict], analysis_result: Optional[Dict]) -> str:
        """Extract value proposition for targeted web search"""
        try:
            # Initialize web search if needed
            self._init_web_search()
            
            if self.web_search_engine:
                from utils.web_search import ValuePropositionExtractor
                extractor = ValuePropositionExtractor()
                # Use documents if available, otherwise use analysis_result
                extraction = extractor.extract_simple(documents, analysis_result or {})
                return extraction.get('value_proposition', 'innovative business solution')
            else:
                # Fallback to basic extraction
                return self._basic_value_prop_extraction(analysis_result)
        except Exception as e:
            logger.warning(f"Value proposition extraction failed: {e}")
            return "innovative business solution"
    
    def _basic_value_prop_extraction(self, analysis_result: Optional[Dict]) -> str:
        """Basic fallback extraction without web_search module"""
        if not analysis_result:
            return "technology business solution"
        
        summary_text = str(analysis_result.get('executive_summary', '')).lower()
        
        # Look for key industry terms
        if 'fintech' in summary_text or 'payment' in summary_text:
            return "fintech payment solution"
        elif 'health' in summary_text or 'medical' in summary_text:
            return "healthcare technology solution"
        elif 'clean' in summary_text or 'sustain' in summary_text:
            return "cleantech sustainability solution"
        else:
            return "technology business solution"
    
    def _extract_startup_funding_claims(self, documents: List[Dict], analysis_result: Optional[Dict]) -> Dict[str, Any]:
        """Extract what the startup claims about funding and metrics"""
        claimed_stage = ""
        claimed_amount = ""
        claimed_valuation = ""
        claimed_metrics = []
        
        # Try to extract from analysis_result if available
        if analysis_result:
            # Look for funding info in various sections
            if 'scoring' in analysis_result:
                scoring = analysis_result.get('scoring', {})
                if 'financials' in scoring:
                    claimed_metrics.append("Financial metrics provided")
            
            # Extract from executive summary
            summary = str(analysis_result.get('executive_summary', ''))
            
            # Simple pattern matching for funding stage
            import re
            stage_patterns = ['seed', 'series a', 'series b', 'series c', 'pre-seed']
            for pattern in stage_patterns:
                if pattern in summary.lower():
                    claimed_stage = pattern.title()
                    break
            
            # Look for funding amounts
            amount_pattern = r'\$\d+[MKB]?\s*(?:million|billion)?'
            amount_match = re.search(amount_pattern, summary, re.IGNORECASE)
            if amount_match:
                claimed_amount = amount_match.group()
        
        return {
            'claimed_stage': claimed_stage or "Not specified",
            'claimed_amount': claimed_amount or "Not disclosed",
            'claimed_valuation': claimed_valuation or "Not disclosed",
            'claimed_metrics': claimed_metrics[:5]
        }
    
    def _perform_multilevel_funding_search(self, market_profile: Any) -> Dict[str, Any]:
        """MEJORAS CALIDAD: Perform 3-level hierarchical search for funding intelligence"""
        try:
            # Initialize web search if needed
            self._init_web_search()
            
            if not self.web_search_engine:
                logger.warning("Web search engine not available")
                return {'sources': [], 'funding_patterns': [], 'deals': []}
            
            # Extract all levels from market profile
            solution = getattr(market_profile, 'solution', '') if hasattr(market_profile, 'solution') else market_profile.get('solution', '')
            sub_vertical = getattr(market_profile, 'sub_vertical', '') if hasattr(market_profile, 'sub_vertical') else market_profile.get('sub_vertical', '')
            vertical = getattr(market_profile, 'vertical', '') if hasattr(market_profile, 'vertical') else market_profile.get('vertical', '')
            
            # Level 1: Solution-specific funding (most specific)
            solution_queries = []
            if solution:
                solution_queries = [
                    f"{solution} companies funding rounds valuations",
                    f"{solution} investment deals 2024",
                    f"{solution} startup funding metrics"
                ]
            
            # Level 2: Sub-vertical funding (broader)
            subvertical_queries = []
            if sub_vertical:
                subvertical_queries = [
                    f"{sub_vertical} funding landscape 2024",
                    f"{sub_vertical} series A B valuations",
                    f"{sub_vertical} investor sentiment trends"
                ]
            
            # Level 3: Vertical funding (broadest)
            vertical_queries = []
            if vertical:
                vertical_queries = [
                    f"{vertical} venture capital investment 2024",
                    f"{vertical} startup valuations benchmarks",
                    f"{vertical} funding ecosystem analysis"
                ]
            
            logger.info(f"🔍 Executing 3-level funding search:")
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
            
            # Process combined results for funding patterns
            return self._process_web_results_for_funding(all_results)
            
        except Exception as e:
            logger.error(f"Multilevel funding search failed: {e}")
            return {'sources': [], 'funding_patterns': [], 'deals': []}
    
    def _perform_funding_web_search(self, value_proposition: str, market_profile: Any) -> Dict[str, Any]:
        """Perform web search for funding intelligence - LEGACY METHOD"""
        try:
            # Initialize web search if needed
            self._init_web_search()
            
            if not self.web_search_engine:
                logger.warning("Web search engine not available")
                return {'sources': [], 'funding_patterns': [], 'deals': []}
            
            # Build targeted search queries (NO GEOGRAPHY)
            vertical = self._get_industry_vertical(market_profile)
            
            # SIMPLIFIED: Remove geography for global analysis
            queries = [
                f"{value_proposition} recent funding rounds 2024",
                f"{vertical} funding trends investor sentiment",  # Removed {geo}
                f"similar companies {value_proposition} series A B valuations",
                f"{vertical} funding climate 2024 investor priorities"
            ]
            
            # Execute searches
            web_results = self.web_search_engine.search_multiple(queries[:3], max_results_per_query=3)
            
            # Process results for funding intelligence
            return self._process_web_results_for_funding(web_results)
            
        except Exception as e:
            logger.error(f"Web search failed: {e}")
            return {'sources': [], 'funding_patterns': [], 'deals': []}
    
    def _process_web_results_for_funding(self, web_results: Dict) -> Dict[str, Any]:
        """Process web search results into funding intelligence"""
        funding_intel = {
            'funding_patterns': [],
            'recent_deals': [],
            'investor_insights': [],
            'market_trends': [],
            'sources': []
        }
        
        # Extract funding patterns from search results
        for insight in web_results.get('expert_insights', []):
            if isinstance(insight, str) and len(insight) > 20:
                # Categorize insights
                if any(word in insight.lower() for word in ['funding', 'raised', 'valuation', 'series']):
                    funding_intel['funding_patterns'].append(insight[:200])
                elif any(word in insight.lower() for word in ['investor', 'vc', 'sentiment']):
                    funding_intel['investor_insights'].append(insight[:200])
                else:
                    funding_intel['market_trends'].append(insight[:200])
        
        # Extract recent deals from competitors found
        for competitor in web_results.get('competitors_found', []):
            if isinstance(competitor, str):
                # Parse for funding information
                if any(word in competitor.lower() for word in ['raised', 'funding', 'series', 'valuation']):
                    funding_intel['recent_deals'].append({
                        'company': competitor.split('(')[0].strip() if '(' in competitor else competitor,
                        'details': competitor,
                        'source': 'web search'
                    })
        
        # Track sources
        funding_intel['sources'] = [{
            'type': 'web_search',
            'count': web_results.get('sources_count', 0),
            'queries': web_results.get('search_terms_used', [])
        }]
        
        return funding_intel
    
    def _perform_gpt4_funding_analysis(self, market_profile: Any, documents: List[Dict], 
                                       analysis_result: Optional[Dict],
                                       web_intelligence: Optional[Dict] = None) -> Dict[str, Any]:
        """Perform expert-level GPT-4 analysis of funding landscape"""
        try:
            # Try to use expert prompts
            try:
                from prompts.expert_level_prompts import FUNDING_EXPERT_SYSTEM, get_funding_prompts
                
                # Get current stage from analysis if available
                current_stage = 'Seed'  # Default
                if analysis_result:
                    # Try to extract stage from analysis
                    if 'scoring' in analysis_result:
                        # Look for stage in scoring or other fields
                        current_stage = analysis_result.get('scoring', {}).get('stage', 'Seed')
                
                if web_intelligence:
                    prompts = get_funding_prompts(market_profile, web_intelligence, current_stage)
                    system_prompt = FUNDING_EXPERT_SYSTEM
                    user_prompt = prompts['user']
                else:
                    # Fallback if no web intelligence
                    industry = self._get_industry_vertical(market_profile)
                    geography = self._get_geography(market_profile)
                    system_prompt = FUNDING_EXPERT_SYSTEM
                    user_prompt = f"""Analyze funding landscape for {industry} in {geography}.
Provide specific recent deals, active funds, and realistic valuations."""
            except ImportError:
                # Original prompts as fallback
                industry = self._get_industry_vertical(market_profile)
                geography = self._get_geography(market_profile)
                system_prompt = f"""You are a senior VC analyst evaluating funding patterns for {industry} in {geography}.
Provide independent market analysis of funding trends, typical ranges, and investor sentiment.
Do not compare with startup claims - focus only on market reality."""
                user_prompt = f"""Analyze current funding landscape for {industry} startups in {geography}.
Focus on: typical funding ranges, investor priorities, success factors, and current climate."""
            
            # Call OpenAI with expert parameters
            response = self._call_openai(system_prompt, user_prompt, 
                                       max_tokens=1500,  # Increased for detailed analysis
                                       temperature=0.2)  # Lower for more focused output
            
            # Parse response
            return self._parse_gpt4_funding_response(response)
            
        except Exception as e:
            logger.error(f"GPT-4 funding analysis failed: {e}")
            return {}
    
    def _parse_gpt4_funding_response(self, response: str) -> Dict[str, Any]:
        """Parse GPT-4 response for funding insights"""
        try:
            # Try to extract structured data from response
            import json
            import re
            
            # Look for JSON in response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            
            # If no JSON, return raw response
            return {'raw_analysis': response}
        except Exception as e:
            logger.warning(f"Failed to parse GPT-4 funding response: {e}")
            return {'raw_analysis': response}
    
    def _integrate_funding_intelligence(self, startup_claims: Dict, web_intelligence: Dict,
                                       gpt4_analysis: Optional[Dict], market_profile: Any) -> FundingBenchmarkProfile:
        """Integrate all sources into comprehensive funding profile"""
        profile = FundingBenchmarkProfile()
        
        # Store startup claims for PDF comparison
        profile.startup_claimed_stage = startup_claims.get('claimed_stage', 'Not specified')
        profile.startup_claimed_amount = startup_claims.get('claimed_amount', 'Not disclosed')
        profile.startup_claimed_valuation = startup_claims.get('claimed_valuation', 'Not disclosed')
        profile.startup_claimed_metrics = startup_claims.get('claimed_metrics', [])
        
        # Build independent analysis from web search
        profile.market_funding_patterns = web_intelligence.get('funding_patterns', [])[:3]
        profile.investor_sentiment = web_intelligence.get('investor_insights', [])[:3]
        
        # Process recent deals
        for deal in web_intelligence.get('recent_deals', [])[:3]:
            if isinstance(deal, dict):
                profile.similar_deals.append({
                    'company': deal.get('company', 'Unknown'),
                    'details': deal.get('details', ''),
                    'relevance': 'Similar sector/stage'
                })
        
        # Determine funding climate
        industry = self._get_industry_vertical(market_profile)
        geography = self._get_geography(market_profile)
        
        # Set funding climate based on findings
        if len(profile.investor_sentiment) > 0:
            profile.funding_climate = "Selective - investors focusing on metrics"
        else:
            profile.funding_climate = "Cautious - higher bar for funding"
        
        # Set typical ranges for the sector
        profile.typical_ranges = {
            'seed': '$500K-$2M',
            'series_a': '$2M-$15M',
            'series_b': '$10M-$50M'
        }
        
        # Extract success factors
        trends = web_intelligence.get('market_trends', [])
        for trend in trends[:2]:
            if 'success' in trend.lower() or 'growth' in trend.lower():
                profile.success_factors.append(trend[:150])
        
        # Set market assessment
        if len(profile.market_funding_patterns) >= 2:
            profile.market_assessment = f"Active funding market for {industry} in {geography}"
        else:
            profile.market_assessment = f"Limited funding activity for {industry} in {geography}"
        
        # Set confidence level
        if len(profile.market_funding_patterns) >= 2:
            profile.confidence_level = "high"
        elif len(profile.market_funding_patterns) >= 1:
            profile.confidence_level = "medium"
        else:
            profile.confidence_level = "low"
        
        # Track sources
        profile.sources = web_intelligence.get('sources', [])
        
        # Set confidence score
        data_points = len(profile.market_funding_patterns) + len(profile.similar_deals) + len(profile.investor_sentiment)
        profile.confidence_score = min(0.9, data_points * 0.15)
        
        # Set legacy fields for compatibility
        profile.stage = "Market Analysis"
        profile.amount_raised = "N/A - Market Analysis"
        profile.valuation = "N/A - Market Analysis"
        profile.industry_benchmarks = profile.typical_ranges
        profile.metrics_comparison = {
            'funding_climate': profile.funding_climate,
            'market_assessment': profile.market_assessment
        }
        
        return profile
    
    def _has_openai_key(self) -> bool:
        """Check if OpenAI key is available"""
        return bool(os.getenv('OPENAI_API_KEY'))
    
    def _get_mock_funding_benchmark_enhanced(self, market_profile: Any) -> FundingBenchmarkProfile:
        """Enhanced mock data for TEST MODE with new FASE 2C structure"""
        profile = FundingBenchmarkProfile()
        
        # Market funding patterns from web search
        profile.market_funding_patterns = [
            "TechCrunch 2024: FinTech Series A rounds averaging $8M, down 30% from 2022",
            "CB Insights: LATAM fintech seeing increased activity with 15+ deals Q1 2024",
            "PitchBook: Valuation multiples compressed to 6-8x revenue from 12-15x peak"
        ]
        
        # Similar deals with outcomes
        profile.similar_deals = [
            {
                'company': 'PayFlow',
                'details': 'Raised $12M Series A at $60M valuation',
                'relevance': 'Similar invoice factoring model'
            },
            {
                'company': 'QuickPay LATAM',
                'details': 'Raised $8M Series A, acquired by larger player',
                'relevance': 'Same geography and vertical'
            }
        ]
        
        # Investor sentiment
        profile.investor_sentiment = [
            "VCs prioritizing unit economics over growth at all costs",
            "LATAM seen as high-growth opportunity but regulatory complexity concerns",
            "Invoice factoring models need proven collection rates for Series B"
        ]
        
        # Current funding climate
        profile.funding_climate = "Cautious - 25% down from peak"
        
        # Typical ranges for the sector
        profile.typical_ranges = {
            'seed': '$500K-$2M',
            'series_a': '$2M-$15M typical for FinTech',
            'series_b': '$10M-$50M for proven models'
        }
        
        # Success factors in current market
        profile.success_factors = [
            "Strong local partnerships critical for LATAM expansion",
            "Regulatory compliance pre-work reduces funding friction"
        ]
        
        # Startup claims (for PDF comparison)
        profile.startup_claimed_stage = "Series A"
        profile.startup_claimed_amount = "$5M target"
        profile.startup_claimed_valuation = "Not disclosed"
        profile.startup_claimed_metrics = ["48h approval time", "$10M GMV processed"]
        
        # Analysis metadata
        profile.market_assessment = "Moderate funding activity with selective investor interest"
        profile.confidence_level = "medium"
        profile.sources = [
            {'type': 'web_search', 'count': 8, 'queries': ['fintech funding 2024', 'LATAM investor sentiment']}
        ]
        profile.confidence_score = 0.75
        
        # Legacy fields for compatibility
        profile.stage = "Market Analysis"
        profile.amount_raised = "N/A - Market Analysis"
        profile.valuation = "N/A - Market Analysis"
        profile.industry_benchmarks = profile.typical_ranges
        profile.metrics_comparison = {
            'funding_climate': profile.funding_climate,
            'market_assessment': profile.market_assessment
        }
        
        return profile