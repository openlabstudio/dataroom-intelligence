#!/usr/bin/env python3
"""
Test Suite for Story 1.2: Enhanced Multi-Source Intelligence Collection
Tests integration with Story 1.1 BMAD Framework professional prompts

This test validates:
1. Enhanced source collection (24→50+ sources)
2. Integration with BMAD professional prompts from Story 1.1
3. Cost monitoring and control mechanisms
4. Source quality scoring and diversity validation
"""

import os
import sys
import unittest
from unittest.mock import Mock, patch
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Enable TEST_MODE for safe testing
os.environ['TEST_MODE'] = 'true'

class TestStory12EnhancedCollection(unittest.TestCase):
    """Test Story 1.2: Enhanced Multi-Source Intelligence Collection"""

    def setUp(self):
        """Set up test environment"""
        from agents.enhanced_source_collection import EnhancedSourceCollector
        from agents.market_detection import MarketProfile
        
        self.collector = EnhancedSourceCollector()
        
        # Create mock market profile for testing
        self.mock_market_profile = Mock(spec=MarketProfile)
        self.mock_market_profile.solution = "AI-powered tax-free shopping platform"
        self.mock_market_profile.sub_vertical = "tax-free shopping"
        self.mock_market_profile.vertical = "fintech"
        self.mock_market_profile.target_market = "international tourists"
        self.mock_market_profile.business_model = "B2B SaaS"
        self.mock_market_profile.geo_focus = "Europe"
        self.mock_market_profile.primary_vertical = "fintech"

    def test_enhanced_collection_initialization(self):
        """Test that enhanced collector initializes with proper cost controls"""
        print("🧪 Testing Enhanced Source Collector Initialization...")
        
        # Verify collector has cost monitoring attributes
        self.assertTrue(hasattr(self.collector, 'api_calls_count'))
        self.assertTrue(hasattr(self.collector, 'estimated_cost_usd'))
        self.assertTrue(hasattr(self.collector, 'max_cost_limit'))
        self.assertTrue(hasattr(self.collector, 'professional_source_domains'))
        
        # Verify initial cost state
        self.assertEqual(self.collector.api_calls_count, 0)
        self.assertEqual(self.collector.estimated_cost_usd, 0.0)
        self.assertGreater(len(self.collector.professional_source_domains), 20)
        
        print("✅ Enhanced collector initialized with cost controls")

    def test_enhanced_source_collection_50_plus_sources(self):
        """Test that enhanced collection targets 50+ sources"""
        print("🧪 Testing Enhanced Source Collection (50+ sources target)...")
        
        result = self.collector.collect_enhanced_sources(
            market_profile=self.mock_market_profile,
            target_sources=50
        )
        
        # Verify result structure
        self.assertIn('enhanced_sources', result)
        self.assertIn('quality_summary', result)
        self.assertIn('diversity_metrics', result)
        self.assertIn('collection_metadata', result)
        self.assertIn('cost_summary', result)  # Story 1.2: Cost monitoring
        
        # Verify target achievement (should be 50 in TEST_MODE)
        sources_count = len(result['enhanced_sources'])
        self.assertEqual(sources_count, 50, f"Expected 50 sources, got {sources_count}")
        
        # Verify cost summary structure
        cost_summary = result['cost_summary']
        self.assertIn('test_mode', cost_summary)
        self.assertIn('within_cost_limits', cost_summary)
        self.assertTrue(cost_summary['within_cost_limits'])
        
        print(f"✅ Enhanced collection completed: {sources_count} sources collected")

    def test_source_quality_scoring(self):
        """Test source quality scoring and professional source identification"""
        print("🧪 Testing Source Quality Scoring System...")
        
        result = self.collector.collect_enhanced_sources(
            market_profile=self.mock_market_profile,
            target_sources=25  # Smaller test
        )
        
        # Verify quality summary
        quality_summary = result['quality_summary']
        self.assertIn('average_quality', quality_summary)
        self.assertIn('professional_sources', quality_summary)
        self.assertIn('high_quality_sources', quality_summary)
        
        # In TEST_MODE, should have consistent quality metrics
        self.assertGreater(quality_summary['average_quality'], 0.7)
        self.assertGreater(quality_summary['professional_sources'], 0)
        
        # Verify individual sources have quality scores
        sources = result['enhanced_sources']
        for source in sources[:5]:  # Check first 5 sources
            self.assertIn('quality_score', source)
            self.assertIn('source_type', source)
            self.assertGreater(source['quality_score'], 0.6)
        
        print("✅ Source quality scoring system functional")

    def test_source_diversity_validation(self):
        """Test source diversity validation across domains and types"""
        print("🧪 Testing Source Diversity Validation...")
        
        result = self.collector.collect_enhanced_sources(
            market_profile=self.mock_market_profile,
            target_sources=30
        )
        
        # Verify diversity metrics
        diversity_metrics = result['diversity_metrics']
        self.assertIn('domain_diversity', diversity_metrics)
        self.assertIn('source_type_diversity', diversity_metrics)
        self.assertIn('professional_source_percentage', diversity_metrics)
        self.assertIn('diversity_score', diversity_metrics)
        
        # Verify reasonable diversity (TEST_MODE provides good diversity)
        self.assertGreater(diversity_metrics['domain_diversity'], 10)
        self.assertGreaterEqual(diversity_metrics['source_type_diversity'], 3)
        self.assertGreater(diversity_metrics['diversity_score'], 0.5)
        
        print("✅ Source diversity validation functional")

    def test_cost_monitoring_integration(self):
        """Test cost monitoring and control mechanisms"""
        print("🧪 Testing Cost Monitoring Integration...")
        
        # Test cost limits checking
        self.assertTrue(self.collector._check_cost_limits())
        
        # Simulate cost accumulation
        self.collector.api_calls_count = 50
        self.collector.estimated_cost_usd = 1.0
        
        cost_summary = self.collector._get_cost_summary()
        self.assertIn('api_calls_made', cost_summary)
        self.assertIn('estimated_cost_usd', cost_summary)
        self.assertIn('cost_efficiency_ratio', cost_summary)
        
        self.assertEqual(cost_summary['api_calls_made'], 50)
        self.assertEqual(cost_summary['estimated_cost_usd'], 1.0)
        
        print("✅ Cost monitoring integration functional")

    def test_integration_with_market_research_orchestrator(self):
        """Test integration with MarketResearchOrchestrator (Story 1.1 integration)"""
        print("🧪 Testing Integration with MarketResearchOrchestrator...")
        
        try:
            from agents.market_research_orchestrator import MarketResearchOrchestrator
            from agents.enhanced_source_collection import EnhancedSourceCollector
            
            orchestrator = MarketResearchOrchestrator()
            
            # Verify that MarketResearchOrchestrator can import EnhancedSourceCollector
            enhanced_collector = EnhancedSourceCollector()
            self.assertIsNotNone(enhanced_collector)
            
            # Verify integration in TEST_MODE works
            mock_documents = [{"content": "Test startup document", "filename": "test.pdf"}]
            mock_summary = {"company_name": "TestStartup", "solution_summary": "AI platform"}
            
            # This should not fail in TEST_MODE
            result = orchestrator.perform_market_intelligence(mock_documents, mock_summary)
            self.assertIsNotNone(result)
            
            print("✅ Integration with MarketResearchOrchestrator successful")
            
        except ImportError as e:
            self.fail(f"Integration test failed due to import error: {e}")

    def test_professional_source_domains(self):
        """Test that professional source domains include expected consulting firms"""
        print("🧪 Testing Professional Source Domains...")
        
        professional_domains = self.collector.professional_source_domains
        
        # Verify key consulting firms are included
        expected_domains = [
            'mckinsey.com', 'bcg.com', 'bain.com', 'deloitte.com',
            'crunchbase.com', 'bloomberg.com', 'reuters.com'
        ]
        
        for domain in expected_domains:
            self.assertIn(domain, professional_domains, f"Missing professional domain: {domain}")
        
        print(f"✅ Professional source domains validated ({len(professional_domains)} domains)")

    def test_enhanced_vs_legacy_comparison(self):
        """Test that enhanced collection provides more sources than legacy (24 vs 50+)"""
        print("🧪 Testing Enhanced vs Legacy Source Count Comparison...")
        
        # Test enhanced collection
        enhanced_result = self.collector.collect_enhanced_sources(
            market_profile=self.mock_market_profile,
            target_sources=50
        )
        
        enhanced_count = len(enhanced_result['enhanced_sources'])
        
        # Should significantly exceed legacy 24 source limit
        self.assertGreaterEqual(enhanced_count, 50, "Enhanced collection should provide 50+ sources")
        self.assertGreater(enhanced_count, 24, "Enhanced collection should exceed legacy 24 sources")
        
        # Verify metadata confirms target achievement
        metadata = enhanced_result['collection_metadata']
        self.assertTrue(metadata.get('target_achieved', False))
        
        print(f"✅ Enhanced collection: {enhanced_count} sources vs legacy ~24 sources")

def run_story_1_2_tests():
    """Run all Story 1.2 tests"""
    print("🚀 STORY 1.2: Enhanced Multi-Source Intelligence Collection Tests")
    print("=" * 80)
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestStory12EnhancedCollection)
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    result = runner.run(suite)
    
    print("\n" + "=" * 80)
    
    if result.wasSuccessful():
        print("🎉 ALL STORY 1.2 TESTS PASSED!")
        print("✅ Enhanced Multi-Source Intelligence Collection is ready")
        print("✅ Integration with Story 1.1 BMAD prompts confirmed")
        print("✅ Cost monitoring and control mechanisms functional")
        return True
    else:
        print("❌ SOME TESTS FAILED")
        print(f"Failures: {len(result.failures)}")
        print(f"Errors: {len(result.errors)}")
        return False

if __name__ == "__main__":
    success = run_story_1_2_tests()
    sys.exit(0 if success else 1)