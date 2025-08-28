#!/usr/bin/env python3
"""
Simple test to verify geography removal from web searches
"""

import re

def check_file_for_geo_references(filepath):
    """Check if a file contains geo references in queries"""
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Look for patterns that might use geography in queries
    # Exclude comments by checking if line starts with #
    patterns = [
        (r'\{geo\}', lambda line: not line.strip().startswith('#')),  # Direct {geo} usage, not in comments
        (r'geo =.*market_profile\.get.*geo_focus', lambda line: 'queries' in content[max(0, content.find(line)-200):content.find(line)+200]),  # Getting geo near queries
        (r'f".*\{geo\}.*"', lambda line: not '#' in line),  # f-strings with {geo}, not comments
    ]
    
    issues = []
    lines = content.split('\n')
    
    for i, line in enumerate(lines, 1):
        for pattern, filter_func in patterns:
            if re.search(pattern, line):
                # Apply filter to exclude false positives
                if filter_func(line):
                    # Check if it's in a query context
                    context_start = max(0, i-3)
                    context_end = min(len(lines), i+3)
                    context = lines[context_start:context_end]
                    
                    # Check if it's near "queries = [" 
                    if any('queries' in ctx_line for ctx_line in context):
                        # Skip if it's a comment line
                        if not line.strip().endswith('# Removed {geo}'):
                            issues.append(f"Line {i}: {line.strip()}")
    
    return issues

def main():
    print("=" * 60)
    print("CHECKING GEOGRAPHY REMOVAL FROM WEB SEARCHES")
    print("=" * 60)
    
    agents_to_check = [
        'agents/competitive_intelligence.py',
        'agents/market_validation.py', 
        'agents/funding_benchmarker.py'
    ]
    
    all_good = True
    
    for agent_file in agents_to_check:
        print(f"\n📋 Checking {agent_file}...")
        issues = check_file_for_geo_references(agent_file)
        
        if issues:
            print(f"  ❌ Found {len(issues)} potential geography references in queries:")
            for issue in issues:
                print(f"    - {issue}")
            all_good = False
        else:
            print(f"  ✅ No geography references in queries!")
    
    # Also check for "Removed {geo}" comments to confirm changes
    print("\n📝 Checking for removal confirmations...")
    confirmations = []
    
    for agent_file in agents_to_check:
        with open(agent_file, 'r') as f:
            lines = f.readlines()
            for i, line in enumerate(lines, 1):
                if "Removed {geo}" in line or "NO GEOGRAPHY" in line:
                    confirmations.append(f"{agent_file}:{i} - {line.strip()}")
    
    if confirmations:
        print(f"  ✅ Found {len(confirmations)} removal confirmations:")
        for conf in confirmations:
            print(f"    - {conf}")
    
    print("\n" + "=" * 60)
    if all_good:
        print("✅ ALL CHECKS PASSED! Geography successfully removed from web searches.")
        print("\nNext steps:")
        print("1. Test with full /market-research command")
        print("2. Consider implementing hierarchical search (solution → vertical)")
        print("3. Update TASKS.md with progress")
    else:
        print("❌ Some issues found. Please review and fix.")
    print("=" * 60)

if __name__ == "__main__":
    main()