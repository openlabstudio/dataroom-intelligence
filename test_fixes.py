#!/usr/bin/env python3
"""
Quick test to verify our fixes work
"""

import os
import sys

# Set TEST_MODE for safety
os.environ['TEST_MODE'] = 'true'

def test_syntax():
    """Test that all modules can be imported without syntax errors"""
    print("\n" + "="*60)
    print("TESTING SYNTAX FIXES")
    print("="*60)
    
    try:
        print("\n1. Testing competitive_intelligence.py...")
        from agents.competitive_intelligence import CompetitiveIntelligenceAgent
        print("   ✅ No syntax errors")
        
        print("\n2. Testing market_validation.py...")
        from agents.market_validation import MarketValidationAgent
        print("   ✅ No syntax errors")
        
        print("\n3. Testing funding_benchmarker.py...")
        from agents.funding_benchmarker import FundingBenchmarkerAgent
        print("   ✅ No syntax errors")
        
        print("\n4. Testing market_research_orchestrator.py...")
        from agents.market_research_orchestrator import MarketResearchOrchestrator
        print("   ✅ No syntax errors")
        
        print("\n" + "="*60)
        print("✅ ALL MODULES LOAD SUCCESSFULLY")
        print("="*60)
        return True
        
    except Exception as e:
        print(f"\n❌ Error loading modules: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_value_proposition():
    """Test that value proposition builds correctly from market profile"""
    print("\n" + "="*60)
    print("TESTING VALUE PROPOSITION FIX")
    print("="*60)
    
    try:
        from agents.competitive_intelligence import CompetitiveIntelligenceAgent
        
        agent = CompetitiveIntelligenceAgent()
        
        # Test with water treatment profile (what we expect)
        market_profile = {
            'solution': 'Electrochemical wastewater treatment',
            'sub_vertical': 'Water treatment technology',
            'vertical': 'Cleantech sustainability',
            'target_market': 'B2B pharmaceutical and cosmetics industries'
        }
        
        value_prop = agent._build_value_proposition_from_profile(market_profile, {})
        print(f"   Value proposition: {value_prop}")
        
        # Should NOT contain "healthtech" or "AI-powered GLOBAL"
        assert 'healthtech' not in value_prop.lower(), "Should not contain healthtech"
        assert 'GLOBAL' not in value_prop, "Should not contain GLOBAL"
        assert 'Electrochemical wastewater treatment' in value_prop, "Should contain actual solution"
        
        print("   ✅ Value proposition correctly uses market profile")
        return True
        
    except Exception as e:
        print(f"\n❌ Error testing value proposition: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    all_passed = True
    
    # Test 1: Syntax
    if not test_syntax():
        all_passed = False
    
    # Test 2: Value proposition
    if not test_value_proposition():
        all_passed = False
    
    print("\n" + "="*60)
    if all_passed:
        print("✅ ALL FIXES WORK CORRECTLY")
        print("\nNext steps:")
        print("1. Run the full /market-research command again")
        print("2. Verify it searches for 'water treatment' not 'healthtech'")
        print("3. Check that competitive analysis doesn't fail")
    else:
        print("❌ SOME FIXES HAVE ISSUES")
    print("="*60)

if __name__ == "__main__":
    main()