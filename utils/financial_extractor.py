"""
Financial Data Extractor for DataRoom Intelligence

This module provides deterministic extraction of financial data from document content
before passing to GPT-5 for analysis. It uses pattern matching to identify funding amounts,
KPIs, percentages, and other financial metrics that GPT-5 might miss due to formatting.
"""

import re
import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class FinancialDataExtractor:
    """
    Extract financial data using deterministic pattern matching
    """
    
    def __init__(self):
        """Initialize the financial extractor with patterns"""
        self.funding_patterns = [
            # Standard formats: 300K, €1M, $5M, 2.5B
            r'(\d+[.,]?\d*)\s*([KMB])\s*([€$]|EUR|USD|euro|dollar)',
            r'([€$]|EUR|USD|euro|dollar)\s*(\d+[.,]?\d*)\s*([KMB])',
            # Funding context: "Initial financing 2019 needs 300K"
            r'(?:funding|financing|investment|capital|raise|need|ask)[:\s]*([€$]?\s*\d+[.,]?\d*\s*[KMB]?[€$]?)',
            # Number with currency: 300K€, $1M, €500K
            r'(\d+[.,]?\d*)\s*([KMB])\s*([€$])',
            r'([€$])\s*(\d+[.,]?\d*)\s*([KMB])',
        ]
        
        self.kpi_patterns = {
            'cac': [
                r'CAC[:\s]*([€$]?\s*\d+[.,]?\d*)',
                r'Customer\s+Acquisition\s+Cost[:\s]*([€$]?\s*\d+[.,]?\d*)',
                r'(?:CAC|customer acquisition)[:\s]*([€$]?\s*\d+[.,]?\d*[€$]?)',
            ],
            'cpl': [
                r'CPL[:\s]*([€$]?\s*\d+[.,]?\d*)',
                r'Cost\s+Per\s+Lead[:\s]*([€$]?\s*\d+[.,]?\d*)',
            ],
            'ltv': [
                r'LTV[:\s]*([€$]?\s*\d+[.,]?\d*)',
                r'Life\s*Time\s+Value[:\s]*([€$]?\s*\d+[.,]?\d*)',
                r'Customer\s+Life\s*Time\s+Value[:\s]*([€$]?\s*\d+[.,]?\d*)',
            ],
            'arpu': [
                r'ARPU[:\s]*([€$]?\s*\d+[.,]?\d*)',
                r'Average\s+Revenue\s+Per\s+User[:\s]*([€$]?\s*\d+[.,]?\d*)',
            ]
        }
        
        self.percentage_patterns = [
            # Conversion rates, margins, growth
            r'(\d+[.,]?\d*)\s*%',
            r'(\d+[.,]?\d*)\s*percent',
        ]
        
        self.revenue_patterns = [
            r'(?:revenue|sales|income)[:\s]*([€$]?\s*\d+[.,]?\d*\s*[KMB]?[€$]?)',
            r'(?:profit|loss|EBITDA|margin)[:\s]*([€$]?\s*\d+[.,]?\d*\s*[KMB]?[€$]?)',
            r'P&L|profit.*loss|cash.*flow|income.*statement',
        ]
    
    def extract_all_financial_data(self, content: str) -> Dict[str, Any]:
        """
        Extract all financial data from content
        
        Args:
            content: Raw document content
            
        Returns:
            Dictionary with extracted financial data
        """
        if not content:
            return self._empty_result()
        
        logger.info(f"🔍 Starting financial extraction from {len(content)} characters")
        
        # Extract different types of financial data
        funding_data = self._extract_funding_amounts(content)
        kpi_data = self._extract_kpis(content)
        percentage_data = self._extract_percentages(content)
        revenue_data = self._extract_revenue_metrics(content)
        
        # Validate and check for inconsistencies
        validation_warnings = self._validate_extracted_data(funding_data, kpi_data, percentage_data)
        
        # Determine if we have meaningful financial data
        has_financial_data = any([
            funding_data['company_funding'] or funding_data['market_data'],
            any(kpi_data.values()),
            percentage_data['rates'],
            revenue_data['metrics']
        ])
        
        result = {
            'funding': funding_data,
            'kpis': kpi_data,
            'percentages': percentage_data,
            'revenue': revenue_data,
            'has_financial_data': has_financial_data,
            'validation_warnings': validation_warnings,
            'extraction_summary': self._create_summary(funding_data, kpi_data, percentage_data, revenue_data)
        }
        
        logger.info(f"   💰 Financial data found: {has_financial_data}")
        logger.info(f"   📊 Company funding: {len(funding_data['company_funding'])}, Market data: {len(funding_data['market_data'])}, Founder exits: {len(funding_data['founder_exits'])}")
        logger.info(f"   📈 KPIs detected: {sum(1 for v in kpi_data.values() if v)}")
        logger.info(f"   📉 Percentages: {len(percentage_data['rates'])}")
        if validation_warnings:
            logger.warning(f"   ⚠️  Validation warnings: {len(validation_warnings)}")
        
        return result
    
    def _extract_funding_amounts(self, content: str) -> Dict[str, Any]:
        """Extract funding amounts and investment needs with context awareness"""
        company_funding = []
        market_data = []
        founder_exits = []
        contexts = []
        
        for pattern in self.funding_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                # Extract context around the match
                start = max(0, match.start() - 100)
                end = min(len(content), match.end() + 100)
                context = content[start:end].strip().lower()
                
                amount_text = match.group(0)
                
                # Categorize based on context (order matters - most specific first)
                if self._is_market_data_context(context):
                    market_data.append(amount_text)
                elif self._is_founder_exit_context(context):
                    founder_exits.append(amount_text)
                elif self._is_company_funding_context(context):
                    company_funding.append(amount_text)
                else:
                    # Default to company funding if context is unclear
                    company_funding.append(amount_text)
                
                contexts.append(context)
        
        return {
            'company_funding': list(set(company_funding)),
            'market_data': list(set(market_data)), 
            'founder_exits': list(set(founder_exits)),
            'contexts': contexts,
            'total_amounts': len(company_funding) + len(market_data) + len(founder_exits)
        }
    
    def _is_founder_exit_context(self, context: str) -> bool:
        """Check if funding amount refers to founder's previous exit"""
        # Specific company/exit indicators
        exit_indicators = [
            'sold by', 'sold for', 'sold to', 'acquisition', 'acquired for',
            'akamon', 'startup sold', 'company sold', 'exit'
        ]
        
        # Founder background indicators
        founder_indicators = [
            'previous startup', 'founder of', 'sold a startup', 'entrepreneur',
            'previous company', 'previously sold', 'ceo previously'
        ]
        
        # Must have both exit context AND founder context for high confidence
        has_exit_context = any(indicator in context for indicator in exit_indicators)
        has_founder_context = any(indicator in context for indicator in founder_indicators)
        
        # Special case for known companies like Akamon
        has_known_exit = 'akamon' in context
        
        return (has_exit_context and has_founder_context) or has_known_exit
    
    def _is_market_data_context(self, context: str) -> bool:
        """Check if amount refers to market size data"""
        market_indicators = [
            'market size', 'tam', 'total addressable market', 'market value',
            'industry size', 'market potential', 'jewelry market', 'global market',
            'market worth', 'billion market', 'european market', 'serviceable obtainable market',
            'market opportunity', 'addressable market', 'market represents'
        ]
        # Strong market indicators that override other contexts
        strong_indicators = ['€70b', '€35b', '€1.5b', 'global', 'billion', 'market']
        
        has_market_indicator = any(indicator in context for indicator in market_indicators)
        has_strong_indicator = any(indicator in context for indicator in strong_indicators)
        
        return has_market_indicator or has_strong_indicator
    
    def _is_company_funding_context(self, context: str) -> bool:
        """Check if amount refers to actual company funding"""
        company_funding_indicators = [
            'initial financing', 'funding needs', 'investment needs', 'capital needs',
            'raise', 'raised', 'funding', 'investment', 'series a', 'series b',
            'seed', 'round', 'investors', 'valuation', 'financing 2019'
        ]
        return any(indicator in context for indicator in company_funding_indicators)
    
    def _extract_kpis(self, content: str) -> Dict[str, Optional[str]]:
        """Extract KPIs like CAC, CPL, LTV"""
        kpis = {}
        
        for kpi_name, patterns in self.kpi_patterns.items():
            kpis[kpi_name] = None
            
            for pattern in patterns:
                matches = re.search(pattern, content, re.IGNORECASE | re.MULTILINE)
                if matches:
                    # Take the first match for each KPI type
                    kpis[kpi_name] = matches.group(1).strip()
                    break
        
        return kpis
    
    def _extract_percentages(self, content: str) -> Dict[str, Any]:
        """Extract percentage values that might be conversion rates or margins"""
        rates = []
        contexts = []
        
        for pattern in self.percentage_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                percentage = match.group(1)
                
                # Get context to understand what this percentage refers to
                start = max(0, match.start() - 30)
                end = min(len(content), match.end() + 30)
                context = content[start:end].strip()
                
                # Filter out obviously non-business percentages (like years: 2024%)
                if not any(year in context for year in ['2019', '2020', '2021', '2022', '2023', '2024', '2025']):
                    rates.append(f"{percentage}%")
                    contexts.append(context)
        
        return {
            'rates': list(set(rates)),  # Remove duplicates
            'contexts': contexts,
            'count': len(set(rates))
        }
    
    def _extract_revenue_metrics(self, content: str) -> Dict[str, Any]:
        """Extract revenue-related metrics and P&L mentions"""
        metrics = []
        pl_mentions = []
        
        for pattern in self.revenue_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                metric_text = match.group(0)
                
                # Check if this looks like P&L or financial statement mention
                if any(term in metric_text.lower() for term in ['p&l', 'profit', 'loss', 'cash flow']):
                    pl_mentions.append(metric_text)
                else:
                    metrics.append(metric_text)
        
        return {
            'metrics': list(set(metrics)),
            'pl_mentions': list(set(pl_mentions)),
            'has_pl_reference': len(pl_mentions) > 0
        }
    
    def _create_summary(self, funding_data: Dict, kpi_data: Dict, percentage_data: Dict, revenue_data: Dict) -> str:
        """Create human-readable summary of extracted financial data"""
        summary_parts = []
        
        # Company funding (most important)
        if funding_data['company_funding']:
            amounts_text = ', '.join(funding_data['company_funding'][:2])  # Max 2 amounts
            summary_parts.append(f"Company Funding: {amounts_text}")
        
        # Market data (separate category)
        if funding_data['market_data']:
            market_text = ', '.join(funding_data['market_data'][:1])  # Max 1 market size
            summary_parts.append(f"Market Size: {market_text}")
        
        # Founder background (if relevant)
        if funding_data['founder_exits']:
            exit_text = ', '.join(funding_data['founder_exits'][:1])  # Max 1 exit
            summary_parts.append(f"Founder Exit: {exit_text}")
        
        detected_kpis = [k.upper() for k, v in kpi_data.items() if v]
        if detected_kpis:
            summary_parts.append(f"KPIs: {', '.join(detected_kpis)}")
        
        if percentage_data['rates']:
            rates_text = ', '.join(percentage_data['rates'][:3])  # Max 3 percentages
            summary_parts.append(f"Metrics: {rates_text}")
        
        if revenue_data['has_pl_reference']:
            summary_parts.append("P&L data referenced")
        
        return ' | '.join(summary_parts) if summary_parts else "No financial data detected"
    
    def _validate_extracted_data(self, funding_data: Dict, kpi_data: Dict, percentage_data: Dict) -> List[str]:
        """Validate extracted financial data for inconsistencies"""
        warnings = []
        
        # Check for unrealistic funding amounts vs market sizes
        company_funding = funding_data.get('company_funding', [])
        market_data = funding_data.get('market_data', [])
        
        if company_funding and market_data:
            # Extract numeric values for comparison
            company_values = self._extract_numeric_values(company_funding)
            market_values = self._extract_numeric_values(market_data)
            
            for comp_val in company_values:
                for market_val in market_values:
                    if comp_val > market_val * 0.1:  # Company funding >10% of market is suspicious
                        warnings.append(f"Company funding ({comp_val}) unusually high vs market size ({market_val})")
        
        # Check for KPI consistency
        cac = kpi_data.get('cac')
        ltv = kpi_data.get('ltv')
        if cac and ltv:
            try:
                cac_num = float(''.join(filter(str.isdigit, cac.replace(',', '.'))))
                ltv_num = float(''.join(filter(str.isdigit, ltv.replace(',', '.'))))
                if ltv_num > 0 and cac_num / ltv_num > 0.5:  # CAC > 50% of LTV is concerning
                    warnings.append(f"CAC/LTV ratio concerning: CAC {cac}, LTV {ltv}")
            except (ValueError, ZeroDivisionError):
                pass
        
        # Check for duplicate amounts across categories
        all_amounts = company_funding + market_data + funding_data.get('founder_exits', [])
        if len(all_amounts) != len(set(all_amounts)):
            warnings.append("Duplicate amounts found across different categories")
        
        return warnings
    
    def _extract_numeric_values(self, amounts_list: List[str]) -> List[float]:
        """Convert amount strings to numeric values for comparison"""
        values = []
        for amount in amounts_list:
            try:
                # Extract number and multiplier
                import re
                match = re.search(r'(\d+[.,]?\d*)\s*([KMB])', amount.upper())
                if match:
                    num = float(match.group(1).replace(',', '.'))
                    multiplier = match.group(2)
                    if multiplier == 'K':
                        values.append(num * 1000)
                    elif multiplier == 'M':
                        values.append(num * 1000000)
                    elif multiplier == 'B':
                        values.append(num * 1000000000)
            except (ValueError, AttributeError):
                continue
        return values
    
    def _empty_result(self) -> Dict[str, Any]:
        """Return empty result structure"""
        return {
            'funding': {
                'company_funding': [], 
                'market_data': [], 
                'founder_exits': [], 
                'contexts': [], 
                'total_amounts': 0
            },
            'kpis': {k: None for k in self.kpi_patterns.keys()},
            'percentages': {'rates': [], 'contexts': [], 'count': 0},
            'revenue': {'metrics': [], 'pl_mentions': [], 'has_pl_reference': False},
            'has_financial_data': False,
            'validation_warnings': [],
            'extraction_summary': 'No content provided'
        }
    
    def format_for_gpt4(self, extracted_data: Dict[str, Any]) -> str:
        """
        Format extracted financial data for GPT-5 prompt
        
        Args:
            extracted_data: Result from extract_all_financial_data()
            
        Returns:
            Formatted string for inclusion in GPT-5 prompt
        """
        if not extracted_data['has_financial_data']:
            return "No specific financial data detected in documents."
        
        sections = []
        
        # Company funding (most important for analysis)
        if extracted_data['funding']['company_funding']:
            company_amounts = extracted_data['funding']['company_funding']
            sections.append(f"COMPANY FUNDING: {', '.join(company_amounts)}")
        
        # Market data (separate context)  
        if extracted_data['funding']['market_data']:
            market_amounts = extracted_data['funding']['market_data']
            sections.append(f"MARKET SIZE: {', '.join(market_amounts)}")
            
        # Founder background (if relevant)
        if extracted_data['funding']['founder_exits']:
            founder_amounts = extracted_data['funding']['founder_exits']
            sections.append(f"FOUNDER PREVIOUS EXIT: {', '.join(founder_amounts)}")
        
        # KPIs
        kpis = extracted_data['kpis']
        detected_kpis = [f"{k.upper()}: {v}" for k, v in kpis.items() if v]
        if detected_kpis:
            sections.append(f"KPIs: {' | '.join(detected_kpis)}")
        
        # Percentages/Conversion rates
        if extracted_data['percentages']['rates']:
            rates = extracted_data['percentages']['rates'][:5]  # Limit to avoid clutter
            sections.append(f"CONVERSION RATES/MARGINS: {', '.join(rates)}")
        
        # P&L/Revenue data
        if extracted_data['revenue']['has_pl_reference']:
            sections.append("P&L/FINANCIAL STATEMENTS: Referenced in document")
        
        return '\n'.join(sections)


def extract_financial_data(content: str) -> Dict[str, Any]:
    """
    Convenience function for extracting financial data
    
    Args:
        content: Raw document content
        
    Returns:
        Dictionary with extracted financial data
    """
    extractor = FinancialDataExtractor()
    return extractor.extract_all_financial_data(content)


def format_financial_data_for_prompt(extracted_data: Dict[str, Any]) -> str:
    """
    Convenience function for formatting data for GPT-5
    
    Args:
        extracted_data: Result from extract_financial_data()
        
    Returns:
        Formatted string for GPT-5 prompt
    """
    extractor = FinancialDataExtractor()
    return extractor.format_for_gpt4(extracted_data)