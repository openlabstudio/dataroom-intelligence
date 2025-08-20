#!/usr/bin/env python3
"""
Test script for FASE 2C: Funding Benchmarker Agent Refactor
Tests the enhanced FundingBenchmarkerAgent with integrated web search
"""

import os
import sys
import json

# Ensure TEST_MODE is enabled
os.environ['TEST_MODE'] = 'true'
os.environ['PRODUCTION_MODE'] = 'false'

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents.funding_benchmarker import FundingBenchmarkerAgent, FundingBenchmarkProfile
from agents.market_detection import MarketProfile
from utils.logger import get_logger

logger = get_logger(__name__)

def test_funding_benchmarker_refactor():
    """Test the refactored Funding Benchmarker Agent"""
    print("\n" + "="*60)
    print("TESTING FASE 2C: Funding Benchmarker Agent Refactor")
    print("="*60)
    
    # Initialize agent
    agent = FundingBenchmarkerAgent()
    
    # Create mock market profile
    market_profile = MarketProfile()
    market_profile.vertical = 'fintech'
    market_profile.sub_vertical = 'payments'
    market_profile.target_market = 'SMB merchants'
    market_profile.business_model = 'SaaS + transaction fees'
    market_profile.geo_focus = 'LATAM'
    
    processed_documents = []
    analysis_result = {
        'executive_summary': 'AI-powered invoice factoring platform targeting Series A',
        'scoring': {'financials': {'score': 7}}
    }
    
    # Test the enhanced benchmarker
    print("\n💰 Testing Funding Benchmarker with integrated web search...")
    funding_profile = agent.benchmark_funding(
        market_profile, processed_documents, None, analysis_result
    )
    
    # Get the dictionary representation
    funding_data = funding_profile.to_dict()
    
    # Check new structure
    print("\n✅ Checking new FASE 2C structure:")
    
    # 1. Check independent_analysis exists
    assert 'independent_analysis' in funding_data, "Missing independent_analysis"
    print("  ✓ independent_analysis structure present")
    
    independent = funding_data['independent_analysis']
    
    # 2. Check market funding patterns
    assert 'market_funding_patterns' in independent, "Missing market_funding_patterns"
    assert len(independent['market_funding_patterns']) > 0, "No funding patterns"
    print(f"  ✓ Found {len(independent['market_funding_patterns'])} market funding patterns")
    print(f"    First: {independent['market_funding_patterns'][0][:80]}...")
    
    # 3. Check similar deals
    assert 'similar_deals' in independent, "Missing similar_deals"
    assert len(independent['similar_deals']) > 0, "No similar deals"
    print(f"  ✓ Found {len(independent['similar_deals'])} similar deals")
    if independent['similar_deals']:
        first_deal = independent['similar_deals'][0]
        print(f"    Example: {first_deal.get('company')} - {first_deal.get('details')[:50]}...")
    
    # 4. Check investor sentiment
    assert 'investor_sentiment' in independent, "Missing investor_sentiment"
    print(f"  ✓ Found {len(independent['investor_sentiment'])} investor sentiment insights")
    
    # 5. Check funding climate
    assert 'funding_climate' in independent, "Missing funding_climate"
    print(f"  ✓ Funding climate: {independent['funding_climate']}")
    
    # 6. Check confidence level
    assert 'confidence_level' in independent, "Missing confidence_level"
    print(f"  ✓ Confidence level: {independent['confidence_level']}")
    
    # 7. Check startup claims extraction
    assert 'startup_claims_extracted' in funding_data, "Missing startup_claims_extracted"
    claims = funding_data['startup_claims_extracted']
    print(f"  ✓ Startup claims extracted:")
    print(f"    - Stage: {claims.get('claimed_stage')}")
    print(f"    - Amount: {claims.get('claimed_amount')}")
    
    # Display formatted output (as it would appear in Slack)
    print("\n" + "="*60)
    print("SLACK OUTPUT PREVIEW (FASE 2C Enhanced):")
    print("="*60)
    
    # Simulate handler formatting
    sources_count = len(independent.get('sources', []))
    confidence_level = independent.get('confidence_level', 'Unknown')
    
    if sources_count > 0:
        print(f"💰 **FUNDING BENCHMARKS** ({confidence_level} confidence - {sources_count} sources)")
    else:
        print(f"💰 **FUNDING BENCHMARKS** ({confidence_level} confidence)")
    
    # Market pattern
    if independent['market_funding_patterns']:
        pattern = str(independent['market_funding_patterns'][0])[:100]
        print(f"• **Market:** {pattern}")
    
    # Similar deal
    if independent['similar_deals']:
        deal = independent['similar_deals'][0]
        company = deal.get('company', 'Unknown')
        details = deal.get('details', '')[:50]
        print(f"• **Recent:** {company} - {details}")
    
    # Climate
    funding_climate = independent.get('funding_climate', '')
    if funding_climate:
        print(f"• **Climate:** {funding_climate}")
    
    # Calculate character count
    char_count = 0
    char_count += len(f"💰 **FUNDING BENCHMARKS** ({confidence_level} confidence - {sources_count} sources)\n")
    if independent['market_funding_patterns']:
        char_count += len(f"• **Market:** {str(independent['market_funding_patterns'][0])[:100]}\n")
    if independent['similar_deals']:
        d = independent['similar_deals'][0]
        char_count += len(f"• **Recent:** {d.get('company')} - {d.get('details', '')[:50]}\n")
    if funding_climate:
        char_count += len(f"• **Climate:** {funding_climate}\n")
    
    print(f"\n📊 Character count: {char_count} (target: <300)")
    
    print("\n" + "="*60)
    print("✅ FASE 2C TEST COMPLETED SUCCESSFULLY!")
    print("="*60)
    
    # Return the profile for further inspection if needed
    return funding_data

if __name__ == "__main__":
    try:
        result = test_funding_benchmarker_refactor()
        print("\n🎉 All tests passed! FASE 2C is working correctly.")
        print("\nNext steps:")
        print("1. Test with full /market-research command")
        print("2. Verify integration with orchestrator")
        print("3. Consider testing with TEST_MODE=false (costs money)")
        print("4. Move to FASE 2D (Critical Synthesizer Enhanced)")
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)