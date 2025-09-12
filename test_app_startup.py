#!/usr/bin/env python3
"""
Test that the app can start gracefully even without vision dependencies installed
"""

import os
import sys

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_app_startup():
    """Test that app.py can be imported without crashing due to vision dependencies"""
    print("🚀 Testing app.py startup with graceful vision fallback...")
    
    try:
        # This should work even without vision dependencies
        import app
        
        # Check that vision_integration_available variable exists and is correctly set
        assert hasattr(app, 'vision_integration_available'), "Should have vision_integration_available variable"
        
        vision_available = app.vision_integration_available
        print(f"📊 Vision integration available: {'✅' if vision_available else '❌'}")
        
        if not vision_available:
            print("✅ App gracefully handles missing vision dependencies")
        else:
            print("✅ Vision dependencies are installed and working")
            
        print("✅ App startup test: PASSED")
        return True
        
    except ImportError as e:
        print(f"❌ App import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error during app startup: {e}")
        return False

def main():
    """Run app startup test"""
    print("🔧 Story 1.2 Vision Integration - App Startup Test")
    print("=" * 50)
    
    success = test_app_startup()
    
    print("=" * 50)
    if success:
        print("🎉 App startup test PASSED!")
        print("💡 Application can start gracefully with or without vision dependencies")
    else:
        print("❌ App startup test FAILED!")
        print("💡 Integration may need fixes for graceful degradation")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)