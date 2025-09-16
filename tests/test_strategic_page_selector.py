"""
Comprehensive unit tests for Strategic Page Selector
Tests all acceptance criteria and edge cases from LV-001 story
"""

import unittest
import tempfile
import os
import time
from unittest.mock import patch, mock_open, MagicMock
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.strategic_page_selector import StrategicPageSelector


class TestStrategicPageSelector(unittest.TestCase):
    """Test Strategic Page Selector functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.selector = StrategicPageSelector()
        
        # Sample PDF content for testing
        self.financial_content = """
        Revenue Growth and Financial Metrics
        Annual Recurring Revenue (ARR): $2.5M
        Monthly Recurring Revenue (MRR): $208K
        Burn Rate: $150K/month
        Cash Runway: 18 months
        Gross Margin: 85%
        Unit Economics: CAC $50, LTV $500
        EBITDA: $100K positive
        """
        
        self.competition_content = """
        Competitive Landscape Analysis
        Key competitors: CompanyA, CompanyB, CompanyC
        Our competitive advantage vs alternatives
        Market positioning and differentiation
        Competitive analysis shows 3x better performance
        """
        
        self.market_content = """
        Market Opportunity
        Total Addressable Market (TAM): $15 billion
        Serviceable Addressable Market (SAM): $2.5 billion
        Serviceable Obtainable Market (SOM): $300 million
        Market size analysis and opportunity
        """
        
        self.traction_content = """
        Growth Metrics and Traction
        Monthly Active Users (MAU): 50,000
        Daily Active Users (DAU): 15,000
        User retention rate: 85%
        Conversion rate: 3.2%
        Customer churn: 2% monthly
        Growth rate: 15% month-over-month
        """
        
        self.team_content = """
        Leadership Team
        CEO: John Smith, former Google VP
        CTO: Jane Doe, ex-Facebook engineer
        Founder background and experience
        Advisory board includes industry experts
        """
    
    def test_content_pattern_detection(self):
        """Test AC1: Content Pattern Detection"""
        # Test financial content detection
        score_data = self.selector._score_page_content(1, self.financial_content)
        self.assertIn('financials', score_data['category_scores'])
        self.assertEqual(score_data['primary_category'], 'financials')
        self.assertGreater(score_data['total_score'], 0)
        
        # Test competition content detection
        score_data = self.selector._score_page_content(2, self.competition_content)
        self.assertIn('competition', score_data['category_scores'])
        self.assertEqual(score_data['primary_category'], 'competition')
        
        # Test market content detection
        score_data = self.selector._score_page_content(3, self.market_content)
        self.assertIn('market', score_data['category_scores'])
        self.assertEqual(score_data['primary_category'], 'market')
        
        # Test traction content detection
        score_data = self.selector._score_page_content(4, self.traction_content)
        self.assertIn('traction', score_data['category_scores'])
        self.assertEqual(score_data['primary_category'], 'traction')
        
        # Test team content detection
        score_data = self.selector._score_page_content(5, self.team_content)
        self.assertIn('team', score_data['category_scores'])
        self.assertEqual(score_data['primary_category'], 'team')
    
    def test_priority_based_selection(self):
        """Test AC2: Priority-Based Selection"""
        # Create mock page scores with different priorities
        mock_pages = [
            {'page_number': 1, 'primary_category': 'financials', 'total_score': 10},
            {'page_number': 2, 'primary_category': 'financials', 'total_score': 9},
            {'page_number': 3, 'primary_category': 'competition', 'total_score': 8},
            {'page_number': 4, 'primary_category': 'competition', 'total_score': 7},
            {'page_number': 5, 'primary_category': 'market', 'total_score': 6},
            {'page_number': 6, 'primary_category': 'traction', 'total_score': 5},
            {'page_number': 7, 'primary_category': 'team', 'total_score': 4},
            {'page_number': 8, 'primary_category': 'financials', 'total_score': 3},
            {'page_number': 9, 'primary_category': 'market', 'total_score': 2},
            {'page_number': 10, 'primary_category': 'traction', 'total_score': 1}
        ]
        
        # Test TC2.1: Deck with 10 potential pages → selects exactly 7 highest-priority
        selected = self.selector._select_optimal_pages(mock_pages, max_pages=7)
        total_selected = sum(len(pages) for pages in selected.values())
        self.assertEqual(total_selected, 7)
        
        # Test priority ordering - financials and competition should be prioritized
        self.assertIn('financials', selected)
        self.assertIn('competition', selected)
        
        # Test TC2.2: Fewer pages than max → selects all available
        short_pages = mock_pages[:3]
        selected = self.selector._select_optimal_pages(short_pages, max_pages=7)
        total_selected = sum(len(pages) for pages in selected.values())
        self.assertEqual(total_selected, 3)
        
        # Test category limits
        financials_selected = len(selected.get('financials', []))
        self.assertLessEqual(financials_selected, 3)  # Max 3 financial pages
    
    def test_fallback_pattern_matching(self):
        """Test AC3: Fallback Pattern Matching"""
        # Test TC3.1: Create a temporary PDF path for fallback
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
            tmp_path = tmp_file.name
        
        try:
            # Mock page count for different scenarios
            with patch.object(self.selector, '_get_page_count') as mock_count:
                # Test with 43-page deck
                mock_count.return_value = 43
                result = self.selector._fallback_page_selection(tmp_path)
                
                # Should use 'long' pattern and select exactly 7 pages
                pages = result.get('general', [])
                self.assertGreaterEqual(len(pages), 3)  # Minimum 3 pages
                self.assertLessEqual(len(pages), 7)     # Maximum 7 pages
                
                # Test with 15-page deck
                mock_count.return_value = 15
                result = self.selector._fallback_page_selection(tmp_path)
                pages = result.get('general', [])
                self.assertGreaterEqual(len(pages), 3)
                
                # Test with very small deck
                mock_count.return_value = 5
                result = self.selector._fallback_page_selection(tmp_path)
                pages = result.get('general', [])
                self.assertEqual(len(pages), 5)  # Should select all pages
        
        finally:
            # Clean up temp file
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    
    def test_selection_rationale_logging(self):
        """Test AC4: Selection Rationale Logging"""
        with patch('utils.strategic_page_selector.logger') as mock_logger:
            # Test successful selection logging
            selected_pages = {
                'financials': [18, 19],
                'competition': [11, 12],
                'market': [8]
            }
            
            self.selector._log_selection_rationale(selected_pages, 43, 1.5)
            
            # Verify logging calls
            mock_logger.info.assert_called()
            call_args = [call[0][0] for call in mock_logger.info.call_args_list]
            
            # Check that key information is logged
            info_text = ' '.join(call_args)
            self.assertIn('Total pages in document: 43', info_text)
            self.assertIn('Pages selected for vision: 5', info_text)
            self.assertIn('Selection time: 1.50 seconds', info_text)
            self.assertIn('financials: pages [18, 19]', info_text)
            self.assertIn('competition: pages [11, 12]', info_text)
            self.assertIn('market: pages [8]', info_text)
    
    def test_performance_requirements(self):
        """Test that selection completes in <2 seconds"""
        # Create a temporary PDF file
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
            tmp_path = tmp_file.name
        
        try:
            # Mock PDF processing to avoid actual PDF dependency
            with patch.object(self.selector, '_extract_page_contents') as mock_extract:
                mock_extract.return_value = [self.financial_content] * 20
                
                with patch.object(self.selector, '_get_page_count') as mock_count:
                    mock_count.return_value = 20
                    
                    # Time the selection process
                    start_time = time.time()
                    result = self.selector.select_strategic_pages(tmp_path)
                    end_time = time.time()
                    
                    selection_time = end_time - start_time
                    self.assertLess(selection_time, 2.0, "Selection should complete in <2 seconds")
                    
                    # Verify result is valid
                    self.assertIsInstance(result, dict)
                    total_pages = sum(len(pages) for pages in result.values())
                    self.assertGreaterEqual(total_pages, 3)  # Minimum coverage
                    self.assertLessEqual(total_pages, 7)     # Maximum limit
        
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    
    def test_various_deck_formats(self):
        """Test with different deck formats and sizes"""
        test_cases = [
            (15, "15-page standard deck"),
            (30, "30-page comprehensive deck"), 
            (43, "43-page full deck"),
            (8, "8-page minimal deck")
        ]
        
        for page_count, description in test_cases:
            with self.subTest(description=description):
                with patch.object(self.selector, '_get_page_count') as mock_count:
                    mock_count.return_value = page_count
                    
                    with patch.object(self.selector, '_extract_page_contents') as mock_extract:
                        # Mix different content types
                        content_types = [
                            self.financial_content,
                            self.competition_content,
                            self.market_content,
                            self.traction_content,
                            self.team_content
                        ]
                        mock_extract.return_value = (content_types * (page_count // 5 + 1))[:page_count]
                        
                        # Create temporary file
                        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
                            tmp_path = tmp_file.name
                        
                        try:
                            result = self.selector.select_strategic_pages(tmp_path)
                            
                            # Verify constraints
                            total_selected = sum(len(pages) for pages in result.values())
                            
                            if page_count <= 7:
                                # Small deck: should select all or most pages
                                self.assertLessEqual(total_selected, page_count)
                            else:
                                # Large deck: should respect limits
                                self.assertLessEqual(total_selected, 7)
                                self.assertGreaterEqual(total_selected, 3)
                            
                            # All page numbers should be valid
                            for pages in result.values():
                                for page_num in pages:
                                    self.assertGreaterEqual(page_num, 1)
                                    self.assertLessEqual(page_num, page_count)
                        
                        finally:
                            if os.path.exists(tmp_path):
                                os.unlink(tmp_path)
    
    def test_edge_cases(self):
        """Test edge cases and error handling"""
        # Test with non-existent file
        result = self.selector.select_strategic_pages("/non/existent/file.pdf")
        self.assertIsInstance(result, dict)
        self.assertIn('general', result)
        
        # Test with empty content
        with patch.object(self.selector, '_extract_page_contents') as mock_extract:
            mock_extract.return_value = []
            
            with patch.object(self.selector, '_get_page_count') as mock_count:
                mock_count.return_value = 20  # Mock a valid page count
                
                with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
                    tmp_path = tmp_file.name
                
                try:
                    result = self.selector.select_strategic_pages(tmp_path)
                    self.assertIsInstance(result, dict)
                    # Should fall back to general selection
                    total_pages = sum(len(pages) for pages in result.values())
                    self.assertGreaterEqual(total_pages, 3)
                
                finally:
                    if os.path.exists(tmp_path):
                        os.unlink(tmp_path)
        
        # Test with very poor content (no keywords match)
        poor_content = "Lorem ipsum dolor sit amet, consectetur adipiscing elit."
        score_data = self.selector._score_page_content(1, poor_content)
        self.assertEqual(score_data['total_score'], 0)
        self.assertIsNone(score_data['primary_category'])
    
    def test_configuration_validation(self):
        """Test selector configuration and stats"""
        stats = self.selector.get_selection_stats()
        
        # Verify configuration
        self.assertEqual(stats['max_pages'], 7)
        self.assertEqual(stats['min_pages'], 3)
        self.assertIn('financials', stats['categories'])
        self.assertIn('competition', stats['categories'])
        self.assertIn('market', stats['categories'])
        self.assertIn('traction', stats['categories'])
        self.assertIn('team', stats['categories'])
        
        # Verify patterns exist
        self.assertGreater(stats['total_keywords'], 50)  # Should have many keywords
        self.assertIn('standard', stats['fallback_patterns'])
        self.assertIn('short', stats['fallback_patterns'])
        self.assertIn('long', stats['fallback_patterns'])


class TestStrategicPageSelectorIntegration(unittest.TestCase):
    """Integration tests for Strategic Page Selector"""
    
    def setUp(self):
        self.selector = StrategicPageSelector()
    
    def test_real_deck_simulation(self):
        """Simulate processing a real pitch deck"""
        # Simulate a 25-page pitch deck with realistic content distribution
        deck_content = [
            "Title Slide - Company Name",  # Page 1
            "Problem Statement",           # Page 2
            "Solution Overview",           # Page 3
            "Market Opportunity TAM SAM SOM $15 billion market", # Page 4 - Market
            "Product Demo",                # Page 5
            "Business Model",             # Page 6
            "Go-to-Market Strategy",      # Page 7
            "Competitive Landscape competitors vs alternatives", # Page 8 - Competition
            "Traction growth users MAU 50000 retention", # Page 9 - Traction
            "Technology Stack",           # Page 10
            "Competitive advantage vs CompanyA CompanyB", # Page 11 - Competition
            "Market Positioning",         # Page 12
            "Team founder CEO CTO leadership experience", # Page 13 - Team
            "Advisory Board",             # Page 14
            "Revenue Model",              # Page 15
            "Unit Economics CAC LTV", # Page 16
            "Financial Projections",      # Page 17
            "Revenue ARR MRR burn rate runway", # Page 18 - Financials
            "Financial Metrics EBITDA gross margin", # Page 19 - Financials
            "Funding Ask",                # Page 20
            "Use of Funds",              # Page 21
            "Milestones",                # Page 22
            "Investment Terms",          # Page 23
            "Thank You",                 # Page 24
            "Appendix"                   # Page 25
        ]
        
        with patch.object(self.selector, '_extract_page_contents') as mock_extract:
            mock_extract.return_value = deck_content
            
            with patch.object(self.selector, '_get_page_count') as mock_count:
                mock_count.return_value = len(deck_content)
                
                with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
                    tmp_path = tmp_file.name
                
                try:
                    result = self.selector.select_strategic_pages(tmp_path)
                    
                    # Verify realistic selection
                    total_selected = sum(len(pages) for pages in result.values())
                    self.assertGreaterEqual(total_selected, 5)
                    self.assertLessEqual(total_selected, 7)
                    
                    # Should identify key strategic pages
                    all_selected = [page for pages in result.values() for page in pages]
                    
                    # Market page (4) should likely be selected
                    if 'market' in result:
                        self.assertIn(4, result['market'])
                    
                    # Financial pages (18, 19) should be prioritized
                    if 'financials' in result:
                        self.assertTrue(18 in result['financials'] or 19 in result['financials'])
                    
                    # Competition pages (8, 11) should be considered
                    if 'competition' in result:
                        self.assertTrue(8 in result['competition'] or 11 in result['competition'])
                
                finally:
                    if os.path.exists(tmp_path):
                        os.unlink(tmp_path)


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)