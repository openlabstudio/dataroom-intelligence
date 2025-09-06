"""
Financial Data Extractor for DataRoom Intelligence

This module provides deterministic extraction of financial data from document content
before passing to GPT-4 for analysis. It uses pattern matching to identify funding amounts,
KPIs, percentages, and other financial metrics that GPT-4 might miss due to formatting.
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
        
        # Determine if we have meaningful financial data
        has_financial_data = any([
            funding_data['amounts'],
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
            'extraction_summary': self._create_summary(funding_data, kpi_data, percentage_data, revenue_data)
        }
        
        logger.info(f"   💰 Financial data found: {has_financial_data}")
        logger.info(f"   📊 Funding amounts: {len(funding_data['amounts'])}")
        logger.info(f"   📈 KPIs detected: {sum(1 for v in kpi_data.values() if v)}")
        logger.info(f"   📉 Percentages: {len(percentage_data['rates'])}")
        
        return result
    
    def _extract_funding_amounts(self, content: str) -> Dict[str, Any]:
        """Extract funding amounts and investment needs"""
        amounts = []
        contexts = []
        
        for pattern in self.funding_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                # Extract context around the match
                start = max(0, match.start() - 50)
                end = min(len(content), match.end() + 50)
                context = content[start:end].strip()
                
                amount_text = match.group(0)
                amounts.append(amount_text)
                contexts.append(context)
        
        return {
            'amounts': list(set(amounts)),  # Remove duplicates
            'contexts': contexts,
            'count': len(set(amounts))
        }
    
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
        
        if funding_data['amounts']:
            amounts_text = ', '.join(funding_data['amounts'][:3])  # Max 3 amounts
            summary_parts.append(f"Funding: {amounts_text}")
        
        detected_kpis = [k.upper() for k, v in kpi_data.items() if v]
        if detected_kpis:
            summary_parts.append(f"KPIs: {', '.join(detected_kpis)}")
        
        if percentage_data['rates']:
            rates_text = ', '.join(percentage_data['rates'][:5])  # Max 5 percentages
            summary_parts.append(f"Metrics: {rates_text}")
        
        if revenue_data['has_pl_reference']:
            summary_parts.append("P&L data referenced")
        
        return ' | '.join(summary_parts) if summary_parts else "No financial data detected"
    
    def _empty_result(self) -> Dict[str, Any]:
        """Return empty result structure"""
        return {
            'funding': {'amounts': [], 'contexts': [], 'count': 0},
            'kpis': {k: None for k in self.kpi_patterns.keys()},
            'percentages': {'rates': [], 'contexts': [], 'count': 0},
            'revenue': {'metrics': [], 'pl_mentions': [], 'has_pl_reference': False},
            'has_financial_data': False,
            'extraction_summary': 'No content provided'
        }
    
    def format_for_gpt4(self, extracted_data: Dict[str, Any]) -> str:
        """
        Format extracted financial data for GPT-4 prompt
        
        Args:
            extracted_data: Result from extract_all_financial_data()
            
        Returns:
            Formatted string for inclusion in GPT-4 prompt
        """
        if not extracted_data['has_financial_data']:
            return "No specific financial data detected in documents."
        
        sections = []
        
        # Funding information
        if extracted_data['funding']['amounts']:
            amounts = extracted_data['funding']['amounts']
            sections.append(f"FUNDING: {', '.join(amounts)}")
        
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
    Convenience function for formatting data for GPT-4
    
    Args:
        extracted_data: Result from extract_financial_data()
        
    Returns:
        Formatted string for GPT-4 prompt
    """
    extractor = FinancialDataExtractor()
    return extractor.format_for_gpt4(extracted_data)