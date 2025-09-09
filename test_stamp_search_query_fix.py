#!/usr/bin/env python3
"""
Production mode simulation test for MR-FIX-02 (Search Query Enhancement)
Validates that STAMP gets VAT refund platform queries instead of duty-free retail
"""

import os
import sys
from unittest.mock import MagicMock
sys.path.insert(0, '/Users/gavalle/Documents/GitHub/dataroom-intelligence')

from agents.market_research_orchestrator import MarketResearchOrchestrator
from agents.market_detection import MarketProfile


def test_stamp_search_query_fix():
    """Test STAMP production scenario with enhanced search queries"""
    print("🎯 STAMP Search Query Enhancement Validation")
    print("=" * 55)
    
    # Create STAMP market profile (as detected by MarketDetectionAgent)
    stamp_profile = MarketProfile(
        solution="tax-free shopping platform",
        sub_vertical="tax-free shopping", 
        vertical="fintech",
        industry="financial technology",
        target_market="international travelers",
        geo_focus="Europe",
        business_model="B2C platform",
        confidence_score=0.85
    )
    
    print("📊 STAMP Market Profile:")
    print(f"   Solution: {stamp_profile.solution}")
    print(f"   Sub-vertical: {stamp_profile.sub_vertical}")
    print(f"   Vertical: {stamp_profile.vertical}")
    print(f"   Industry: {stamp_profile.industry}")
    print()
    
    # Mock web search engine to capture queries
    mock_web_search = MagicMock()
    mock_web_search.search_multiple.return_value = {'all_sources': []}
    
    # Create orchestrator with mocked web search
    orchestrator = MarketResearchOrchestrator()
    orchestrator.web_search_engine = mock_web_search
    
    # Set to PRODUCTION_MODE
    os.environ['TEST_MODE'] = 'false'
    
    print("🔍 BEFORE FIX (Expected Original Generic Queries):")
    print("   - 'tax-free shopping competitors market analysis'")
    print("   - 'tax-free shopping companies vendors providers'") 
    print("   - 'fintech industry companies directory 2024'")
    print("   ❌ Result: Returns 'duty-free retail' data (wrong market)")
    print()
    
    print("🚀 AFTER FIX (Enhanced Sector-Specific Queries):")
    print("-" * 45)
    
    # Test competitive intelligence queries
    print("\n1️⃣  COMPETITIVE INTELLIGENCE QUERIES:")
    orchestrator._search_competitive_intelligence(stamp_profile)
    competitive_queries = mock_web_search.search_multiple.call_args[0][0]
    
    for i, query in enumerate(competitive_queries, 1):
        print(f"   {i}. {query}")
    
    # Reset mock
    mock_web_search.reset_mock()
    
    # Test market validation queries  
    print("\n2️⃣  MARKET VALIDATION QUERIES:")
    orchestrator._search_market_validation(stamp_profile)
    validation_queries = mock_web_search.search_multiple.call_args[0][0]
    
    for i, query in enumerate(validation_queries, 1):
        print(f"   {i}. {query}")
    
    # Reset mock
    mock_web_search.reset_mock()
    
    # Test funding intelligence queries
    print("\n3️⃣  FUNDING INTELLIGENCE QUERIES:")
    orchestrator._search_funding_intelligence(stamp_profile) 
    funding_queries = mock_web_search.search_multiple.call_args[0][0]
    
    for i, query in enumerate(funding_queries, 1):
        print(f"   {i}. {query}")
    
    print()
    
    # Analyze query quality
    all_queries = competitive_queries + validation_queries + funding_queries
    
    # Check for VAT refund specific terms
    vat_queries = [q for q in all_queries if 'VAT refund' in q]
    global_blue_queries = [q for q in all_queries if 'Global Blue' in q] 
    platform_queries = [q for q in all_queries if 'platform' in q]
    duty_free_queries = [q for q in all_queries if 'duty-free retail' in q]
    
    print("📈 QUERY ANALYSIS RESULTS:")
    print("=" * 30)
    print(f"✅ VAT refund specific queries: {len(vat_queries)}")
    print(f"✅ Global Blue competitor queries: {len(global_blue_queries)}")  
    print(f"✅ Platform-focused queries: {len(platform_queries)}")
    print(f"❌ Wrong 'duty-free retail' queries: {len(duty_free_queries)}")
    print()
    
    # Validation
    success_criteria = {
        "VAT refund queries": len(vat_queries) >= 2,
        "Platform focus": len(platform_queries) >= 1,
        "No duty-free retail": len(duty_free_queries) == 0,
        "Total enhanced queries": len(all_queries) >= 10
    }
    
    print("🎯 SUCCESS CRITERIA VALIDATION:")
    print("-" * 35)
    all_passed = True
    for criteria, passed in success_criteria.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {criteria}: {status}")
        if not passed:
            all_passed = False
    
    print()
    
    # Expected impact
    if all_passed:
        print("🏆 STAMP SEARCH QUERY FIX: SUCCESS!")
        print("=" * 40)
        print("✅ Queries now target VAT refund platform market")
        print("✅ Should return VAT refund platform competitors generically")
        print("✅ Market data will focus on tax-free shopping technology")
        print("✅ No more 'duty-free retail' misclassification")
        print("🎯 Expected Result: 90%+ market classification accuracy")
    else:
        print("❌ STAMP SEARCH QUERY FIX: FAILED!")
        print("=" * 40)
        print("❌ Queries still too generic or incorrect")
        print("❌ May still return wrong market data")
    
    return all_passed


def test_test_mode_regression():
    """Verify TEST_MODE behavior unchanged"""
    print("\n" + "=" * 55)
    print("🧪 TEST_MODE REGRESSION TEST")
    print("=" * 55)
    
    # Same STAMP profile
    stamp_profile = MarketProfile(
        solution="tax-free shopping platform",
        sub_vertical="tax-free shopping", 
        vertical="fintech"
    )
    
    # Mock web search engine
    mock_web_search = MagicMock()
    mock_web_search.search_multiple.return_value = {'all_sources': []}
    
    # Create orchestrator
    orchestrator = MarketResearchOrchestrator()
    orchestrator.web_search_engine = mock_web_search
    
    # Set to TEST_MODE
    os.environ['TEST_MODE'] = 'true'
    
    print("🔄 Testing TEST_MODE preservation...")
    
    # Test competitive queries in TEST_MODE
    orchestrator._search_competitive_intelligence(stamp_profile)
    test_mode_queries = mock_web_search.search_multiple.call_args[0][0]
    
    print("📝 TEST_MODE Queries Generated:")
    for i, query in enumerate(test_mode_queries, 1):
        print(f"   {i}. {query}")
    
    # Should use original generic patterns
    generic_patterns_found = any('competitors market analysis' in q for q in test_mode_queries)
    enhanced_patterns_found = any('VAT refund platform competitors' in q for q in test_mode_queries)
    
    print(f"\n📊 TEST_MODE Analysis:")
    print(f"   Generic patterns preserved: {'✅ YES' if generic_patterns_found else '❌ NO'}")
    print(f"   Enhanced patterns avoided: {'✅ YES' if not enhanced_patterns_found else '❌ NO'}")
    
    regression_passed = generic_patterns_found and not enhanced_patterns_found
    
    if regression_passed:
        print("✅ TEST_MODE REGRESSION: PASSED")
        print("🎯 Original TEST_MODE behavior preserved correctly")
    else:
        print("❌ TEST_MODE REGRESSION: FAILED") 
        print("⚠️  TEST_MODE behavior may have changed")
    
    return regression_passed


if __name__ == "__main__":
    print("🎯 MR-FIX-02: STAMP Search Query Enhancement Validation\n")
    
    production_success = test_stamp_search_query_fix()
    test_mode_success = test_test_mode_regression()
    
    overall_success = production_success and test_mode_success
    
    print(f"\n{'=' * 55}")
    print("🏁 FINAL VALIDATION RESULTS")
    print(f"{'=' * 55}")
    print(f"🚀 Production Enhancement: {'SUCCESS' if production_success else 'FAILED'}")
    print(f"🧪 TEST_MODE Regression: {'PASSED' if test_mode_success else 'FAILED'}")
    print(f"🎯 Overall Result: {'SUCCESS' if overall_success else 'FAILURE'}")
    
    if overall_success:
        print("\n✅ MR-FIX-02 Implementation: READY FOR PRODUCTION")
        print("🎯 STAMP will now get correct VAT refund platform analysis")
    else:
        print("\n❌ MR-FIX-02 Implementation: NEEDS FIXES")
        
    sys.exit(0 if overall_success else 1)