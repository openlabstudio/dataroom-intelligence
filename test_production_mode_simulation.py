#!/usr/bin/env python3
"""
Production mode simulation test for MR-FIX-01
This simulates the scenario where GPT-4 doesn't cite [1] properly
"""

import os
import sys
sys.path.insert(0, '/Users/gavalle/Documents/GitHub/dataroom-intelligence')

from utils.expert_formatter import _extract_cited_references

def test_production_simulation():
    """Simulate the actual STAMP production scenario"""
    print("🎯 STAMP Production Scenario Simulation")
    print("="*50)
    
    # Simulate STAMP references (like what Tavily would return)
    stamp_references = {
        'https://fortune.com/duty-free-retail-market': {
            'number': 1, 
            'title': 'Global VAT Refund Market Size Analysis 2024'
        },
        'https://mordor.com/tax-free-shopping': {
            'number': 2, 
            'title': 'Tax-Free Shopping Industry Growth Report'
        },
        'https://cbinsights.com/global-blue': {
            'number': 3, 
            'title': 'Global Blue Market Leadership Analysis'
        },
        'https://cbinsights.com/fintech-funding': {
            'number': 4, 
            'title': 'FinTech Startup Funding Trends Q3 2024'
        }
    }
    
    # Simulate GPT-4 text that DOESN'T cite [1] (the bug scenario)
    gpt4_synthesis_missing_1 = """
    The tax-free shopping platform market presents compelling opportunities [2]. 
    
    COMPETITIVE LANDSCAPE:
    The market includes established players like Global Blue and emerging fintech solutions [3]. 
    Investment activity shows strong momentum with recent funding rounds [4].
    
    INVESTMENT RECOMMENDATION: PROCEED (Medium Risk) - Market fundamentals strong 
    but requires deeper competitive analysis.
    """
    
    print(f"📄 GPT-4 Synthesis Text (Missing [1]):")
    print(f"   Citations found: [2][3][4]")
    print(f"   Missing citation: [1] ❌")
    print()
    
    # Test BEFORE fix (original behavior)
    print("BEFORE FIX (Original Behavior):")
    print("-" * 30)
    
    # Simulate original function behavior (only cited refs)
    original_cited_numbers = {2, 3, 4}  # What would be found
    original_result = {}
    for url, ref_data in stamp_references.items():
        if ref_data['number'] in original_cited_numbers:
            original_result[ref_data['number']] = (url, ref_data)
    original_result = dict(sorted(original_result.items()))
    
    print(f"   References returned: {list(original_result.keys())}")
    print(f"   Missing [1]: {'❌ YES - BUG!' if 1 not in original_result else '✅ NO'}")
    print()
    
    # Test AFTER fix (our implementation) 
    print("AFTER FIX (Our Implementation):")
    print("-" * 30)
    
    # Set to PRODUCTION_MODE
    os.environ['TEST_MODE'] = 'false'
    
    # Run our fixed function
    fixed_result = _extract_cited_references(gpt4_synthesis_missing_1, stamp_references)
    
    print(f"   References returned: {list(fixed_result.keys())}")
    print(f"   Includes [1]: {'✅ YES - FIXED!' if 1 in fixed_result else '❌ NO - STILL BROKEN'}")
    print(f"   Sequential numbering: {'✅ YES' if list(fixed_result.keys()) == [1, 2, 3, 4] else '❌ NO'}")
    print()
    
    # Verify the fix worked
    success = (1 in fixed_result and 
               2 in fixed_result and 
               3 in fixed_result and 
               4 in fixed_result and
               list(fixed_result.keys()) == [1, 2, 3, 4])
    
    print("🏆 SIMULATION RESULTS:")
    print("=" * 25)
    if success:
        print("✅ STAMP Production Fix: SUCCESS!")
        print("✅ References now start at [1] as expected")
        print("✅ VC analysts will see proper reference numbering")
    else:
        print("❌ STAMP Production Fix: FAILED!")
        print("❌ References still missing [1]")
    
    return success

if __name__ == "__main__":
    success = test_production_simulation()
    print(f"\n🎯 Overall Result: {'SUCCESS' if success else 'FAILURE'}")
    sys.exit(0 if success else 1)