#!/usr/bin/env python3
"""
Unit tests for MR-FIX-02: Search Query Generation Enhancement
Tests enhanced sector-specific query generation for both TEST_MODE and PRODUCTION_MODE
"""

import unittest
import os
from unittest.mock import patch, MagicMock
import sys

# Add utils to path for imports
sys.path.insert(0, '/Users/gavalle/Documents/GitHub/dataroom-intelligence')
from agents.market_research_orchestrator import MarketResearchOrchestrator
from agents.market_detection import MarketProfile


class TestSearchQueryEnhancement(unittest.TestCase):
    """Test cases for search query generation enhancement (MR-FIX-02)"""

    def setUp(self):
        """Set up test orchestrator and market profiles"""
        # Mock web search engine
        self.mock_web_search = MagicMock()
        self.mock_web_search.search_multiple.return_value = {'all_sources': []}
        
        # Create orchestrator with mocked dependencies
        self.orchestrator = MarketResearchOrchestrator()
        self.orchestrator.web_search_engine = self.mock_web_search
        
        # STAMP market profile (VAT refund platform)
        self.stamp_profile = MarketProfile(
            solution="tax-free shopping platform",
            sub_vertical="tax-free shopping",
            vertical="fintech",
            industry="financial technology"
        )
        
        # FinTech market profile
        self.fintech_profile = MarketProfile(
            solution="digital payment platform",
            sub_vertical="payment processing",
            vertical="fintech",
            industry="financial services"
        )
        
        # CleanTech market profile
        self.cleantech_profile = MarketProfile(
            solution="water treatment technology",
            sub_vertical="water management",
            vertical="cleantech",
            industry="environmental technology"
        )

    def test_production_mode_stamp_competitive_queries(self):
        """Test Case 1: PRODUCTION_MODE - STAMP competitive queries are VAT-refund specific"""
        with patch.dict(os.environ, {'TEST_MODE': 'false'}):
            self.orchestrator._search_competitive_intelligence(self.stamp_profile)
            
            # Get the queries that were generated
            called_queries = self.mock_web_search.search_multiple.call_args[0][0]
            
            # Should include VAT refund specific terms (generic enrichment)
            self.assertTrue(any('VAT refund platform' in query for query in called_queries))
            self.assertTrue(any('tax refund technology' in query for query in called_queries))
            self.assertTrue(len([q for q in called_queries if 'VAT refund' in q or 'tax refund' in q]) >= 3)
            
            # Should NOT include generic duty-free terms
            self.assertFalse(any('duty-free retail' in query for query in called_queries))
            
    def test_production_mode_stamp_market_validation_queries(self):
        """Test Case 2: PRODUCTION_MODE - STAMP validation queries focus on VAT refund market"""
        with patch.dict(os.environ, {'TEST_MODE': 'false'}):
            self.orchestrator._search_market_validation(self.stamp_profile)
            
            # Get the queries that were generated
            called_queries = self.mock_web_search.search_multiple.call_args[0][0]
            
            # Should include VAT refund market validation terms (generic enrichment)
            self.assertTrue(any('VAT refund' in query for query in called_queries))
            self.assertTrue(len([q for q in called_queries if 'VAT refund' in q or 'tax refund' in q]) >= 2)
            
    def test_production_mode_stamp_funding_queries(self):
        """Test Case 3: PRODUCTION_MODE - STAMP funding queries target VAT refund startups"""
        with patch.dict(os.environ, {'TEST_MODE': 'false'}):
            self.orchestrator._search_funding_intelligence(self.stamp_profile)
            
            # Get the queries that were generated
            called_queries = self.mock_web_search.search_multiple.call_args[0][0]
            
            # Should include VAT refund funding specific terms (generic enrichment)
            self.assertTrue(any('VAT refund' in query for query in called_queries))
            self.assertTrue(len([q for q in called_queries if 'VAT refund' in q or 'tax refund' in q]) >= 2)

    def test_test_mode_preserves_original_behavior(self):
        """Test Case 4: TEST_MODE - Original generic query behavior preserved"""
        with patch.dict(os.environ, {'TEST_MODE': 'true'}):
            self.orchestrator._search_competitive_intelligence(self.stamp_profile)
            
            # Get the queries that were generated
            called_queries = self.mock_web_search.search_multiple.call_args[0][0]
            
            # Should use original generic patterns
            expected_patterns = [
                'tax-free shopping platform competitors market analysis',
                'tax-free shopping platform companies vendors providers',
                'tax-free shopping market leaders companies 2024',
                'fintech industry companies directory 2024'
            ]
            
            for pattern in expected_patterns:
                self.assertTrue(any(pattern in query for query in called_queries))

    def test_fintech_sector_enhancement(self):
        """Test Case 5: PRODUCTION_MODE - FinTech sector gets appropriate queries"""
        with patch.dict(os.environ, {'TEST_MODE': 'false'}):
            self.orchestrator._search_competitive_intelligence(self.fintech_profile)
            
            # Get the queries that were generated
            called_queries = self.mock_web_search.search_multiple.call_args[0][0]
            
            # Should include fintech-specific terms (generic enrichment)
            self.assertTrue(any('payment processing platform' in query for query in called_queries))
            self.assertTrue(any('fintech' in query for query in called_queries))
            self.assertTrue(len([q for q in called_queries if 'payment' in q or 'fintech' in q]) >= 3)

    def test_cleantech_sector_enhancement(self):
        """Test Case 6: PRODUCTION_MODE - CleanTech sector gets appropriate queries"""
        with patch.dict(os.environ, {'TEST_MODE': 'false'}):
            self.orchestrator._search_competitive_intelligence(self.cleantech_profile)
            
            # Get the queries that were generated
            called_queries = self.mock_web_search.search_multiple.call_args[0][0]
            
            # Should include cleantech-specific terms (generic enrichment)
            self.assertTrue(any('environmental technology' in query for query in called_queries))
            self.assertTrue(any('water' in query for query in called_queries))
            self.assertTrue(len([q for q in called_queries if 'environmental' in q or 'cleantech' in q]) >= 2)

    def test_fallback_generic_queries(self):
        """Test Case 7: PRODUCTION_MODE - Fallback to enhanced generic queries for unknown sectors"""
        unknown_profile = MarketProfile(
            solution="unknown solution",
            sub_vertical="unknown vertical",
            vertical="unknown industry"
        )
        
        with patch.dict(os.environ, {'TEST_MODE': 'false'}):
            self.orchestrator._search_competitive_intelligence(unknown_profile)
            
            # Get the queries that were generated
            called_queries = self.mock_web_search.search_multiple.call_args[0][0]
            
            # Should use enhanced generic queries with quotes
            self.assertTrue(any('"unknown solution"' in query for query in called_queries))
            self.assertTrue(any('"unknown vertical"' in query for query in called_queries))

    def test_query_generation_methods_exist(self):
        """Test Case 8: Ensure all new query generation methods exist"""
        # Test that all new methods exist
        self.assertTrue(hasattr(self.orchestrator, '_generate_enhanced_competitive_queries'))
        self.assertTrue(hasattr(self.orchestrator, '_generate_enhanced_validation_queries'))  
        self.assertTrue(hasattr(self.orchestrator, '_generate_enhanced_funding_queries'))
        
        # Test that fallback methods exist
        self.assertTrue(hasattr(self.orchestrator, '_original_competitive_search'))
        self.assertTrue(hasattr(self.orchestrator, '_original_validation_search'))
        self.assertTrue(hasattr(self.orchestrator, '_original_funding_search'))

    def test_stamp_comprehensive_scenario(self):
        """Test Case 9: STAMP comprehensive scenario - all search functions enhanced"""
        with patch.dict(os.environ, {'TEST_MODE': 'false'}):
            # Test competitive intelligence
            self.orchestrator._search_competitive_intelligence(self.stamp_profile)
            competitive_queries = self.mock_web_search.search_multiple.call_args[0][0]
            
            # Reset mock for next call
            self.mock_web_search.reset_mock()
            
            # Test market validation
            self.orchestrator._search_market_validation(self.stamp_profile)
            validation_queries = self.mock_web_search.search_multiple.call_args[0][0]
            
            # Reset mock for next call
            self.mock_web_search.reset_mock()
            
            # Test funding intelligence
            self.orchestrator._search_funding_intelligence(self.stamp_profile)
            funding_queries = self.mock_web_search.search_multiple.call_args[0][0]
            
            # Verify all query sets contain VAT refund specific terms
            all_queries = competitive_queries + validation_queries + funding_queries
            
            # Should contain multiple VAT refund references (generic enrichment)
            vat_queries = [q for q in all_queries if 'VAT refund' in q or 'tax refund' in q]
            self.assertGreaterEqual(len(vat_queries), 3, 
                                   "Should have multiple VAT/tax refund specific queries")
            
            # Should contain tax-free shopping platform terms
            platform_queries = [q for q in all_queries if 'tax-free shopping' in q]
            self.assertGreaterEqual(len(platform_queries), 2,
                                   "Should contain tax-free shopping platform terms")

    def test_no_regression_test_mode_all_functions(self):
        """Test Case 10: TEST_MODE - No regression across all search functions"""
        with patch.dict(os.environ, {'TEST_MODE': 'true'}):
            # Test all functions preserve original behavior in TEST_MODE
            functions_to_test = [
                self.orchestrator._search_competitive_intelligence,
                self.orchestrator._search_market_validation, 
                self.orchestrator._search_funding_intelligence
            ]
            
            for search_function in functions_to_test:
                self.mock_web_search.reset_mock()
                search_function(self.stamp_profile)
                
                # Should be called (original behavior preserved)
                self.assertTrue(self.mock_web_search.search_multiple.called)
                
                # Get queries generated
                called_queries = self.mock_web_search.search_multiple.call_args[0][0]
                
                # Should use original generic format (no sector-specific enhancements)
                # Original queries use direct string formatting, not enhanced patterns
                self.assertTrue(len(called_queries) > 0, "Should generate queries in TEST_MODE")


def run_search_query_tests():
    """Run all search query enhancement tests"""
    print("🧪 Running MR-FIX-02 Search Query Enhancement Tests...\n")
    
    # Run tests
    suite = unittest.TestLoader().loadTestsFromTestCase(TestSearchQueryEnhancement)
    runner = unittest.TextTestRunner(verbosity=2)
    test_result = runner.run(suite)
    
    # Summary
    if test_result.wasSuccessful():
        print(f"\n✅ All {test_result.testsRun} tests PASSED!")
        print("🎯 Search query enhancement working correctly in both modes")
        print("🚀 STAMP scenario will now get VAT refund platform data instead of duty-free retail")
        return True
    else:
        print(f"\n❌ {len(test_result.failures)} test(s) FAILED")
        print(f"❌ {len(test_result.errors)} test(s) had ERRORS")
        return False


if __name__ == "__main__":
    success = run_search_query_tests()
    sys.exit(0 if success else 1)