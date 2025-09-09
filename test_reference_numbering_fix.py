#!/usr/bin/env python3
"""
Unit tests for MR-FIX-01: Reference Numbering Fix
Tests _extract_cited_references function for both TEST_MODE and PRODUCTION_MODE
"""

import unittest
import os
from unittest.mock import patch
import sys
import tempfile

# Add utils to path for imports
sys.path.insert(0, '/Users/gavalle/Documents/GitHub/dataroom-intelligence')
from utils.expert_formatter import _extract_cited_references


class TestReferenceNumberingFix(unittest.TestCase):
    """Test cases for reference numbering fix (MR-FIX-01)"""

    def setUp(self):
        """Set up test references data"""
        self.sample_references = {
            'https://example.com/ref1': {'number': 1, 'title': 'Market Analysis Report'},
            'https://example.com/ref2': {'number': 2, 'title': 'Competitor Landscape'},
            'https://example.com/ref3': {'number': 3, 'title': 'Funding Report'},
            'https://example.com/ref4': {'number': 4, 'title': 'Industry Trends'}
        }

    def test_production_mode_missing_ref_1_fix(self):
        """Test Case 1: PRODUCTION_MODE - Fix missing [1] reference"""
        # Simulate GPT-4 text that doesn't cite [1] but cites others
        gpt4_text_missing_1 = "Market analysis shows growth [2][3]. Competitors include [4]."
        
        with patch.dict(os.environ, {'TEST_MODE': 'false'}):
            result = _extract_cited_references(gpt4_text_missing_1, self.sample_references)
        
        # Should include [1] even though not cited by GPT-4 (PRODUCTION FIX)
        self.assertIn(1, result)
        self.assertIn(2, result)  
        self.assertIn(3, result)
        self.assertIn(4, result)
        
        # Verify proper sorting
        result_keys = list(result.keys())
        self.assertEqual(result_keys, [1, 2, 3, 4])

    def test_production_mode_with_ref_1_cited(self):
        """Test Case 2: PRODUCTION_MODE - [1] already cited (no interference)"""
        gpt4_text_with_1 = "Market analysis [1] shows growth [2][3]. Competitors [4]."
        
        with patch.dict(os.environ, {'TEST_MODE': 'false'}):
            result = _extract_cited_references(gpt4_text_with_1, self.sample_references)
        
        # Should work normally when [1] is already cited
        self.assertIn(1, result)
        self.assertIn(2, result)
        self.assertIn(3, result)
        self.assertIn(4, result)

    def test_production_mode_no_references_no_fix(self):
        """Test Case 3: PRODUCTION_MODE - No references at all (edge case)"""
        gpt4_text_no_refs = "Market analysis shows strong growth potential."
        
        with patch.dict(os.environ, {'TEST_MODE': 'false'}):
            result = _extract_cited_references(gpt4_text_no_refs, self.sample_references)
        
        # Should be empty when no references cited
        self.assertEqual(len(result), 0)

    def test_production_mode_single_ref_1_only(self):
        """Test Case 4: PRODUCTION_MODE - Only [1] cited"""
        gpt4_text_only_1 = "Market analysis [1] shows strong fundamentals."
        
        with patch.dict(os.environ, {'TEST_MODE': 'false'}):
            result = _extract_cited_references(gpt4_text_only_1, self.sample_references)
        
        # Should include only [1] when it's the only one cited
        self.assertEqual(list(result.keys()), [1])
        self.assertEqual(result[1][1]['title'], 'Market Analysis Report')

    def test_test_mode_unchanged_behavior(self):
        """Test Case 5: TEST_MODE - No changes to existing behavior"""
        # This simulates TEST_MODE behavior (should not trigger production fix)
        gpt4_text_missing_1 = "Market analysis shows growth [2][3]. Competitors include [4]."
        
        with patch.dict(os.environ, {'TEST_MODE': 'true'}):
            result = _extract_cited_references(gpt4_text_missing_1, self.sample_references)
        
        # In TEST_MODE, should NOT include [1] if not cited (preserve original behavior)
        self.assertNotIn(1, result)
        self.assertIn(2, result)
        self.assertIn(3, result)
        self.assertIn(4, result)

    def test_test_mode_with_all_refs_cited(self):
        """Test Case 6: TEST_MODE - All references cited (normal case)"""
        # TEST_MODE typically has hardcoded [1][2][3][4][5][6] citations
        test_mode_text = "Market growth [1][2] with competitors [3][4] and funding [5][6]."
        test_refs_extended = {
            **self.sample_references,
            'https://example.com/ref5': {'number': 5, 'title': 'Startup Funding'},
            'https://example.com/ref6': {'number': 6, 'title': 'Series A Analysis'}
        }
        
        with patch.dict(os.environ, {'TEST_MODE': 'true'}):
            result = _extract_cited_references(test_mode_text, test_refs_extended)
        
        # Should include all cited references in TEST_MODE
        expected_refs = [1, 2, 3, 4, 5, 6]
        self.assertEqual(list(result.keys()), expected_refs)

    def test_empty_references_dict(self):
        """Test Case 7: Edge case - empty references dictionary"""
        gpt4_text = "Market analysis [1][2] shows growth."
        empty_refs = {}
        
        with patch.dict(os.environ, {'TEST_MODE': 'false'}):
            result = _extract_cited_references(gpt4_text, empty_refs)
        
        # Should handle empty references gracefully
        self.assertEqual(len(result), 0)

    def test_reference_data_structure(self):
        """Test Case 8: Verify returned data structure is correct"""
        gpt4_text = "Market analysis [2] shows growth."
        
        with patch.dict(os.environ, {'TEST_MODE': 'false'}):
            result = _extract_cited_references(gpt4_text, self.sample_references)
        
        # Should include [1] (production fix) and [2] (cited)
        self.assertIn(1, result)
        self.assertIn(2, result)
        
        # Verify data structure: {ref_num: (url, ref_data)}
        self.assertIsInstance(result[1], tuple)
        self.assertEqual(len(result[1]), 2)  # (url, ref_data)
        
        url, ref_data = result[1]
        self.assertEqual(url, 'https://example.com/ref1')
        self.assertEqual(ref_data['number'], 1)
        self.assertEqual(ref_data['title'], 'Market Analysis Report')

    def test_stamp_scenario_production_fix(self):
        """Test Case 9: STAMP scenario - realistic production case"""
        # Simulate STAMP startup analysis where GPT-4 doesn't cite [1]
        stamp_gpt4_text = """
        The tax-free shopping market analysis [2] shows strong fundamentals.
        Key competitors include Global Blue and Planet Payment [3][4].
        Recent funding activity [5] indicates investor interest.
        """
        
        stamp_references = {
            'https://fortune.com/vat-refund-market': {'number': 1, 'title': 'VAT Refund Market Analysis'},
            'https://mordor.com/tax-free-shopping': {'number': 2, 'title': 'Tax-Free Shopping Growth Report'},
            'https://cb.com/global-blue-analysis': {'number': 3, 'title': 'Global Blue Competition'},
            'https://cb.com/planet-payment': {'number': 4, 'title': 'Planet Payment Analysis'},
            'https://pitchbook.com/fintech-funding': {'number': 5, 'title': 'FinTech Funding 2024'}
        }
        
        with patch.dict(os.environ, {'TEST_MODE': 'false'}):
            result = _extract_cited_references(stamp_gpt4_text, stamp_references)
        
        # Should include [1] despite not being cited (PRODUCTION FIX)
        expected_refs = [1, 2, 3, 4, 5]
        self.assertEqual(list(result.keys()), expected_refs)
        
        # Verify [1] points to VAT refund market analysis
        self.assertEqual(result[1][1]['title'], 'VAT Refund Market Analysis')


def run_reference_tests():
    """Run all reference numbering tests"""
    print("🧪 Running MR-FIX-01 Reference Numbering Tests...\n")
    
    # Run tests
    suite = unittest.TestLoader().loadTestsFromTestCase(TestReferenceNumberingFix)
    runner = unittest.TextTestRunner(verbosity=2)
    test_result = runner.run(suite)
    
    # Summary
    if test_result.wasSuccessful():
        print(f"\n✅ All {test_result.testsRun} tests PASSED!")
        print("🎯 Reference numbering fix working correctly in both modes")
        return True
    else:
        print(f"\n❌ {len(test_result.failures)} test(s) FAILED")
        print(f"❌ {len(test_result.errors)} test(s) had ERRORS")
        return False


if __name__ == "__main__":
    success = run_reference_tests()
    sys.exit(0 if success else 1)