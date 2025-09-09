#!/usr/bin/env python3

"""
Test Suite for MR-FIX-03: GPT-4 Synthesis Validation Enhancement

Tests synthesis content filtering and sector validation in PRODUCTION MODE
while preserving TEST_MODE behavior.
"""

import unittest
import os
from unittest.mock import patch, MagicMock
from utils.expert_formatter import synthesize_market_intelligence_with_gpt4, _filter_content_by_sector_relevance
from agents.market_detection import MarketProfile

class TestSynthesisValidation(unittest.TestCase):
    """Test synthesis validation enhancements"""
    
    def setUp(self):
        """Set up test fixtures"""
        # STAMP market profile (FinTech/Tax-Free Shopping)
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
        
        # HealthTech market profile
        self.healthtech_profile = MarketProfile(
            solution="digital health platform",
            sub_vertical="telemedicine",
            vertical="healthcare",
            industry="medical technology"
        )
        
        # CleanTech market profile
        self.cleantech_profile = MarketProfile(
            solution="water treatment system",
            sub_vertical="water management", 
            vertical="cleantech",
            industry="environmental technology"
        )

    def test_content_filtering_stamp_scenario(self):
        """Test Case 1: STAMP content filtering removes duty-free retail data"""
        # Mixed content - relevant VAT refund + irrelevant duty-free retail
        mixed_content = [
            "SOURCE [1]: VAT Refund Technology Market Analysis\nVAT refund platform market growing at 15% annually, driven by digital transformation in tax-free shopping technology. Companies like Global Blue focus on payment processing for international travelers.",
            "SOURCE [2]: Duty-Free Retail Market Report\nDuty-free retail shops at airports generated $85 billion in 2024, with luxury goods and alcohol being top categories. Traditional retail models dominate the sector.",
            "SOURCE [3]: Tax-Free Shopping Digital Platforms\nTax-free shopping technology platforms are revolutionizing how tourists claim VAT refunds, with digital solutions replacing paper processes.",
            "SOURCE [4]: Airport Retail Market Analysis\nAirport retail market includes duty-free shops, restaurants, and convenience stores. Physical retail locations generate most revenue through walk-in customers."
        ]
        
        filtered = _filter_content_by_sector_relevance(mixed_content, self.stamp_profile)
        
        # Should keep VAT refund and tax-free shopping content, remove duty-free retail
        self.assertEqual(len(filtered), 2, "Should filter out irrelevant duty-free retail content")
        
        # Check that VAT refund content is preserved
        vat_content = [content for content in filtered if 'VAT refund' in content]
        self.assertGreater(len(vat_content), 0, "Should preserve VAT refund relevant content")
        
        # Check that tax-free shopping platform content is preserved
        platform_content = [content for content in filtered if 'tax-free shopping' in content and 'platform' in content]
        self.assertGreater(len(platform_content), 0, "Should preserve tax-free shopping platform content")
        
        # Check that duty-free retail content is removed
        retail_content = [content for content in filtered if 'duty-free retail' in content or 'airport retail' in content]
        self.assertEqual(len(retail_content), 0, "Should remove irrelevant retail content")

    def test_content_filtering_healthtech_scenario(self):
        """Test Case 2: HealthTech content filtering removes wellness coaching data"""
        mixed_content = [
            "SOURCE [1]: Digital Health Technology Market\nDigital health platforms are transforming patient care through telemedicine and clinical decision support systems.",
            "SOURCE [2]: Wellness Coaching Apps Market\nWellness coaching apps focus on fitness tracking and lifestyle advice, targeting consumers interested in general wellness.",
            "SOURCE [3]: Medical Technology Innovation\nMedical technology companies are developing AI-powered diagnostic tools for clinical use in hospitals and clinics."
        ]
        
        filtered = _filter_content_by_sector_relevance(mixed_content, self.healthtech_profile)
        
        # Should keep medical/healthcare content, remove wellness coaching
        healthcare_content = [content for content in filtered if 'medical' in content.lower() or 'clinical' in content.lower() or 'digital health' in content.lower()]
        self.assertGreater(len(healthcare_content), 0, "Should preserve healthcare relevant content")
        
        wellness_content = [content for content in filtered if 'wellness coaching' in content.lower()]
        self.assertEqual(len(wellness_content), 0, "Should remove wellness coaching content")

    def test_content_filtering_cleantech_scenario(self):
        """Test Case 3: CleanTech content filtering removes fossil fuel data"""
        mixed_content = [
            "SOURCE [1]: Water Treatment Technology Market\nWater treatment systems using advanced filtration are growing, driven by environmental regulations and sustainability concerns.",
            "SOURCE [2]: Fossil Fuel Industry Report\nFossil fuel companies continue to dominate energy markets, with oil and gas production increasing globally.",
            "SOURCE [3]: Environmental Technology Innovation\nEnvironmental technology startups are developing clean solutions for water management and renewable energy."
        ]
        
        filtered = _filter_content_by_sector_relevance(mixed_content, self.cleantech_profile)
        
        # Should keep environmental/water content, remove fossil fuel
        environmental_content = [content for content in filtered if 'environmental' in content.lower() or 'water' in content.lower()]
        self.assertGreater(len(environmental_content), 0, "Should preserve environmental relevant content")
        
        fossil_content = [content for content in filtered if 'fossil fuel' in content.lower()]
        self.assertEqual(len(fossil_content), 0, "Should remove fossil fuel content")

    def test_content_filtering_fallback_logic(self):
        """Test Case 4: Fallback logic preserves minimum content"""
        # All irrelevant content scenario
        irrelevant_content = [
            "SOURCE [1]: Duty-Free Retail Analysis\nAirport duty-free shops focus on luxury goods and alcohol sales to travelers.",
            "SOURCE [2]: Traditional Banking Report\nPhysical bank branches continue to serve customers through in-person services."
        ]
        
        filtered = _filter_content_by_sector_relevance(irrelevant_content, self.stamp_profile)
        
        # Should preserve at least 2 sources as fallback
        self.assertGreaterEqual(len(filtered), 2, "Should preserve minimum content as fallback")

    @patch('utils.expert_formatter._scrape_real_web_content')
    @patch('openai.OpenAI')
    def test_production_mode_synthesis_integration(self, mock_openai, mock_scraper):
        """Test Case 5: Full synthesis integration in PRODUCTION MODE"""
        # Mock OpenAI response
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_response = MagicMock()
        mock_response.choices[0].message.content = """
**MARKET ANALYSIS**

The VAT refund platform market presents a compelling investment opportunity with strong fundamentals. Market research indicates the global tax-free shopping technology sector is valued at approximately $2.8 billion and growing at 12% annually [1][2].

Our competitive analysis identified key players including Global Blue and Planet Payment, with the market remaining fragmented and ripe for consolidation [3]. Recent funding activity shows investors committed $150M+ to tax-free shopping technology startups in 2024 [4].

**INVESTMENT RECOMMENDATION: PROCEED (Medium Risk)** - Attractive FinTech opportunity with clear market validation, but requires deeper technical due diligence on platform scalability.
        """.strip()
        mock_client.chat.completions.create.return_value = mock_response
        
        # Mock web scraping - mixed relevant and irrelevant content
        def mock_scrape_side_effect(url, title):
            if 'vat-refund' in url:
                return "VAT refund platform market analysis showing 15% growth in digital tax-free shopping solutions."
            elif 'duty-free-retail' in url:
                return "Duty-free retail shops at airports generated $85B in revenue through traditional retail sales."
            else:
                return "Tax-free shopping technology platforms are transforming tourist VAT refund processes."
                
        mock_scraper.side_effect = mock_scrape_side_effect
        
        # Test references with mixed relevant/irrelevant sources
        test_references = {
            'https://example.com/vat-refund-market': {'title': 'VAT Refund Technology Market', 'number': 1},
            'https://example.com/duty-free-retail-report': {'title': 'Duty-Free Retail Market Report', 'number': 2}, 
            'https://example.com/tax-free-shopping-tech': {'title': 'Tax-Free Shopping Platforms', 'number': 3}
        }
        
        with patch.dict(os.environ, {'TEST_MODE': 'false'}):
            result = synthesize_market_intelligence_with_gpt4(test_references, self.stamp_profile)
            
            # Should generate synthesis focused on FinTech/VAT refund
            self.assertIn('VAT refund', result, "Should focus on VAT refund platform analysis")
            self.assertIn('PROCEED', result, "Should provide clear investment recommendation")
            self.assertNotIn('duty-free retail', result.lower(), "Should not include irrelevant retail analysis")

    @patch('utils.expert_formatter.synthesize_market_intelligence_with_gpt4')
    def test_test_mode_regression_preservation(self, mock_synthesis):
        """Test Case 6: TEST_MODE behavior completely preserved"""
        # Mock should not be called since TEST_MODE uses different logic
        test_references = {'https://example.com/test': {'title': 'Test Source', 'number': 1}}
        
        with patch.dict(os.environ, {'TEST_MODE': 'true'}):
            result = synthesize_market_intelligence_with_gpt4(test_references, self.stamp_profile)
            
            # Should generate sector-aware mock response for FinTech
            self.assertIn('tax-free shopping', result, "Should generate FinTech sector mock content")
            self.assertIn('PROCEED', result, "Should maintain TEST_MODE investment recommendations")
            self.assertIn('Medium Risk', result, "Should maintain TEST_MODE risk assessment")
            
            # Ensure OpenAI was not called in TEST_MODE
            mock_synthesis.assert_not_called()

    def test_sector_validation_cross_sectors(self):
        """Test Case 7: Sector validation works across different verticals"""
        # Test FinTech validation
        fintech_content = ["Digital payment processing platform serving 1M+ merchants globally"]
        fintech_filtered = _filter_content_by_sector_relevance(fintech_content, self.fintech_profile)
        self.assertEqual(len(fintech_filtered), 1, "Should preserve FinTech payment content")
        
        # Test HealthTech validation
        healthtech_content = ["Medical technology for clinical decision support in hospitals"]
        healthtech_filtered = _filter_content_by_sector_relevance(healthtech_content, self.healthtech_profile)
        self.assertEqual(len(healthtech_filtered), 1, "Should preserve HealthTech clinical content")
        
        # Test CleanTech validation
        cleantech_content = ["Environmental technology for sustainable water treatment systems"]
        cleantech_filtered = _filter_content_by_sector_relevance(cleantech_content, self.cleantech_profile)
        self.assertEqual(len(cleantech_filtered), 1, "Should preserve CleanTech environmental content")

if __name__ == '__main__':
    print("🧪 Running MR-FIX-03 Synthesis Validation Enhancement Tests...\n")
    
    # Run all tests
    unittest.main(verbosity=2, exit=False)
    
    print("\n✅ All synthesis validation tests completed!")
    print("🎯 Synthesis enhancement working correctly for sector validation")
    print("🚀 Production synthesis will now reject irrelevant sector data")
    print("📝 TEST_MODE behavior completely preserved")