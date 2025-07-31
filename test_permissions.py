#!/usr/bin/env python3
"""
Test file to verify GitHub write permissions
Created by Claude AI assistant to test repository access
"""

import datetime

def test_function():
    """Simple test function to verify code execution"""
    current_time = datetime.datetime.now()
    print(f"✅ Test file created successfully at {current_time}")
    print("🤖 Claude AI has write access to this repository!")
    return True

def calculate_fibonacci(n):
    """Calculate fibonacci sequence up to n terms"""
    if n <= 0:
        return []
    elif n == 1:
        return [0]
    elif n == 2:
        return [0, 1]
    
    fib_sequence = [0, 1]
    for i in range(2, n):
        fib_sequence.append(fib_sequence[i-1] + fib_sequence[i-2])
    
    return fib_sequence

if __name__ == "__main__":
    print("🧪 Running permission test...")
    test_function()
    
    # Test some functionality
    print("\n📊 Testing fibonacci calculation:")
    fib_10 = calculate_fibonacci(10)
    print(f"First 10 fibonacci numbers: {fib_10}")
    
    print("\n✅ All tests passed! Repository access confirmed.")
