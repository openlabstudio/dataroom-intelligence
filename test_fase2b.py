#!/usr/bin/env python3
"""
Test script for FASE 2B: Market Validation Agent Refactor
Tests the enhanced MarketValidationAgent with integrated web search
"""

import os
import sys
import json

# Ensure TEST_MODE is enabled
os.environ['TEST_MODE'] = 'true'
os.environ['PRODUCTION_MODE'] = 'false'

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents.market_validation import MarketValidationAgent, MarketValidationProfile
from utils.logger import get_logger

logger = get_logger(__name__)

def test_market_validation_refactor():
    """Test the refactored Market Validation Agent"""
    print("\n" + "="*60)
    print("TESTING FASE 2B: Market Validation Agent Refactor")
    print("="*60)
    
    # Initialize agent
    agent = MarketValidationAgent()
    
    # Create mock inputs
    market_profile = {
        'vertical': 'fintech',
        'sub_vertical': 'payments',
        'target_market': 'SMB merchants',
        'business_model': 'SaaS + transaction fees',
        'geo_focus': 'LATAM'
    }
    
    processed_documents = []
    document_summary = {
        'total_documents': 5,
        'document_types': {'pitch_deck': 1, 'financial_model': 1},
        'summary': 'AI-powered invoice factoring platform with 48-hour approval guarantee'
    }
    
    # Test the enhanced validation
    print("\n📈 Testing Market Validation with integrated web search...")
    validation_profile = agent.validate_market_opportunity(
        market_profile, processed_documents, document_summary
    )
    
    # Get the dictionary representation
    validation_data = validation_profile.to_dict()
    
    # Check new structure
    print("\n✅ Checking new FASE 2B structure:")
    
    # 1. Check independent_analysis exists
    assert 'independent_analysis' in validation_data, "Missing independent_analysis"
    print("  ✓ independent_analysis structure present")
    
    independent = validation_data['independent_analysis']
    
    # 2. Check expert consensus
    assert 'expert_consensus' in independent, "Missing expert_consensus"
    assert len(independent['expert_consensus']) > 0, "No expert opinions"
    print(f"  ✓ Found {len(independent['expert_consensus'])} expert opinions")
    print(f"    First: {independent['expert_consensus'][0][:80]}...")
    
    # 3. Check precedent analysis
    assert 'precedent_analysis' in independent, "Missing precedent_analysis"
    assert len(independent['precedent_analysis']) > 0, "No precedents"
    print(f"  ✓ Found {len(independent['precedent_analysis'])} precedent cases")
    if independent['precedent_analysis']:
        first_precedent = independent['precedent_analysis'][0]
        print(f"    Example: {first_precedent.get('company')} - {first_precedent.get('outcome')}")
    
    # 4. Check regulatory assessment
    assert 'regulatory_assessment' in independent, "Missing regulatory_assessment"
    print(f"  ✓ Found {len(independent['regulatory_assessment'])} regulatory insights")
    
    # 5. Check feasibility assessment
    assert 'feasibility_assessment' in independent, "Missing feasibility_assessment"
    print(f"  ✓ Feasibility: {independent['feasibility_assessment']}")
    
    # 6. Check confidence level
    assert 'confidence_level' in independent, "Missing confidence_level"
    print(f"  ✓ Confidence level: {independent['confidence_level']}")
    
    # 7. Check startup claims extraction
    assert 'startup_claims_extracted' in validation_data, "Missing startup_claims_extracted"
    claims = validation_data['startup_claims_extracted']
    print(f"  ✓ Startup claims extracted:")
    print(f"    - TAM: {claims.get('claimed_tam')}")
    print(f"    - Timeline: {claims.get('claimed_timeline')}")
    
    # Display formatted output (as it would appear in Slack)
    print("\n" + "="*60)
    print("SLACK OUTPUT PREVIEW (FASE 2B Enhanced):")
    print("="*60)
    
    # Simulate handler formatting
    sources_count = len(independent.get('sources', []))
    confidence_level = independent.get('confidence_level', 'Unknown')
    
    if sources_count > 0:
        print(f"📈 **MARKET VALIDATION** ({confidence_level} confidence - {sources_count} sources)")
    else:
        print(f"📈 **MARKET VALIDATION** ({confidence_level} confidence)")
    
    # Expert consensus
    if independent['expert_consensus']:
        expert = str(independent['expert_consensus'][0])[:100]
        print(f"• **Expert:** {expert}")
    
    # Precedent
    if independent['precedent_analysis']:
        precedent = independent['precedent_analysis'][0]
        company = precedent.get('company', 'Unknown')
        outcome = precedent.get('outcome', '')
        print(f"• **Precedent:** {company} - {outcome}")
    
    # Assessment
    feasibility = independent.get('feasibility_assessment', '')
    if feasibility:
        print(f"• **Assessment:** {feasibility[:80]}")
    
    # Calculate character count
    char_count = 0
    char_count += len(f"📈 **MARKET VALIDATION** ({confidence_level} confidence - {sources_count} sources)\n")
    if independent['expert_consensus']:
        char_count += len(f"• **Expert:** {str(independent['expert_consensus'][0])[:100]}\n")
    if independent['precedent_analysis']:
        p = independent['precedent_analysis'][0]
        char_count += len(f"• **Precedent:** {p.get('company')} - {p.get('outcome')}\n")
    if feasibility:
        char_count += len(f"• **Assessment:** {feasibility[:80]}\n")
    
    print(f"\n📊 Character count: {char_count} (target: <300)")
    
    print("\n" + "="*60)
    print("✅ FASE 2B TEST COMPLETED SUCCESSFULLY!")
    print("="*60)
    
    # Return the profile for further inspection if needed
    return validation_data

if __name__ == "__main__":
    try:
        result = test_market_validation_refactor()
        print("\n🎉 All tests passed! FASE 2B is working correctly.")
        print("\nNext steps:")
        print("1. Test with full /market-research command")
        print("2. Verify integration with orchestrator")
        print("3. Consider testing with TEST_MODE=false (costs money)")
        print("4. Move to FASE 2C (Funding Intelligence refactor)")
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)