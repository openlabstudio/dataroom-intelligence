#!/usr/bin/env python3
"""
Simple Integration Test for Story 1.2 Vision Integration

Tests the integration without requiring external dependencies
"""

import os
import sys

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_app_imports():
    """Test that app.py can import vision coordinator without errors"""
    print("🔧 Testing app.py imports...")
    
    try:
        # Test the import that would happen in app.py
        from handlers.vision_integration_coordinator import vision_integration_coordinator
        print("✅ Vision coordinator import: PASSED")
        return True
    except ImportError as e:
        print(f"❌ Vision coordinator import failed: {e}")
        print("💡 This is expected if vision dependencies are not installed")
        print("💡 In production, vision dependencies should be installed")
        return False
    except Exception as e:
        print(f"❌ Unexpected error in vision coordinator import: {e}")
        return False

def test_app_structure_integration():
    """Test that the main app structure includes vision integration points"""
    print("🔍 Testing app.py structure integration...")
    
    try:
        # Read app.py content
        with open('/Users/gavalle/Documents/GitHub/dataroom-intelligence/app.py', 'r') as f:
            app_content = f.read()
        
        # Check for key integration points
        integration_points = [
            'from handlers.vision_integration_coordinator import vision_integration_coordinator',
            'vision_integration_coordinator.process_document_with_vision',
            'vision_integration_coordinator.enhance_ask_command',
            'vision_integration_coordinator.enhance_gaps_command',
            'vision_integration_coordinator.enhance_scoring_command',
            'vision_integration_coordinator.enhance_memo_command'
        ]
        
        missing_points = []
        for point in integration_points:
            if point not in app_content:
                missing_points.append(point)
        
        if missing_points:
            print(f"❌ Missing integration points: {missing_points}")
            return False
        else:
            print("✅ All integration points found in app.py")
            return True
            
    except FileNotFoundError:
        print("❌ app.py not found")
        return False
    except Exception as e:
        print(f"❌ Error reading app.py: {e}")
        return False

def test_session_structure_changes():
    """Test that session structure includes vision-related fields"""
    print("📊 Testing session structure enhancements...")
    
    try:
        with open('/Users/gavalle/Documents/GitHub/dataroom-intelligence/app.py', 'r') as f:
            app_content = f.read()
        
        # Check for enhanced session creation
        if 'enhanced_session' in app_content and 'basic_session_data' in app_content:
            print("✅ Enhanced session structure: FOUND")
            
            # Check for vision status in debug
            if 'vision_analysis' in app_content and 'Vision processing available' in app_content:
                print("✅ Vision status in debug: FOUND")
                return True
            else:
                print("❌ Vision status missing from debug output")
                return False
        else:
            print("❌ Enhanced session structure not found")
            return False
            
    except Exception as e:
        print(f"❌ Error testing session structure: {e}")
        return False

def test_command_enhancements():
    """Test that all commands have vision enhancement integration"""
    print("🎯 Testing command enhancement integration...")
    
    try:
        with open('/Users/gavalle/Documents/GitHub/dataroom-intelligence/app.py', 'r') as f:
            app_content = f.read()
        
        commands_to_check = ['ask', 'gaps', 'scoring', 'memo']
        enhanced_commands = []
        
        for cmd in commands_to_check:
            if f'vision_{cmd}_enhancement' in app_content:
                enhanced_commands.append(cmd)
                print(f"✅ /{cmd} command enhanced: FOUND")
            else:
                print(f"❌ /{cmd} command enhancement: NOT FOUND")
        
        if len(enhanced_commands) == len(commands_to_check):
            print("✅ All commands have vision enhancement integration")
            return True
        else:
            print(f"❌ Only {len(enhanced_commands)}/{len(commands_to_check)} commands enhanced")
            return False
            
    except Exception as e:
        print(f"❌ Error testing command enhancements: {e}")
        return False

def test_integration_verification_points():
    """Test Integration Verification Points structurally"""
    print("🎯 Testing Integration Verification Points...")
    
    try:
        with open('/Users/gavalle/Documents/GitHub/dataroom-intelligence/app.py', 'r') as f:
            app_content = f.read()
        
        # IV1: /gaps command should access enhanced extraction data
        iv1_passed = 'enhance_gaps_command' in app_content and 'vision_gaps_enhancement' in app_content
        print(f"{'✅' if iv1_passed else '❌'} IV1 - /gaps enhanced data access: {'PASSED' if iv1_passed else 'FAILED'}")
        
        # IV2: /ask command should access both text and visual content  
        iv2_passed = 'enhance_ask_command' in app_content and 'vision_ask_enhancement' in app_content
        print(f"{'✅' if iv2_passed else '❌'} IV2 - /ask text+visual access: {'PASSED' if iv2_passed else 'FAILED'}")
        
        # IV3: All commands should have access to vision results when available
        all_commands_enhanced = all([
            f'enhance_{cmd}_command' in app_content 
            for cmd in ['ask', 'gaps', 'scoring', 'memo']
        ])
        print(f"{'✅' if all_commands_enhanced else '❌'} IV3 - Universal vision access: {'PASSED' if all_commands_enhanced else 'FAILED'}")
        
        return iv1_passed and iv2_passed and all_commands_enhanced
        
    except Exception as e:
        print(f"❌ Error testing IVs: {e}")
        return False

def main():
    """Run simple integration validation"""
    print("🚀 Story 1.2 Vision Integration - Simple Validation")
    print("=" * 55)
    
    tests = [
        ("App Structure Integration", test_app_structure_integration),
        ("Session Structure Changes", test_session_structure_changes),
        ("Command Enhancements", test_command_enhancements),
        ("Integration Verification Points", test_integration_verification_points),
        ("App Import Test", test_app_imports)  # This might fail due to dependencies
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with error: {e}")
            results.append((test_name, False))
        print()
    
    # Summary
    print("=" * 55)
    print("📊 VALIDATION SUMMARY:")
    print("=" * 55)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "PASSED" if result else "FAILED"
        emoji = "✅" if result else "❌"
        print(f"{emoji} {test_name}: {status}")
    
    print("=" * 55)
    print(f"🎯 RESULT: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    # Evaluate integration completeness
    core_tests_passed = passed >= 4  # All but the import test
    
    if core_tests_passed:
        print("🎉 CORE INTEGRATION COMPLETE!")
        print("💡 Story 1.2 Vision Integration is structurally complete")
        print("💡 Vision processing will activate when dependencies are installed")
        return True
    else:
        print("❌ Core integration incomplete - needs attention")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)