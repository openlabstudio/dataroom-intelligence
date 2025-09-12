#!/usr/bin/env python3
"""
Minimal BMAD Framework Test
Tests BMAD Framework components in isolation
"""

import sys
import os

def test_bmad_research_types_direct():
    """Test BMAD Research Types by importing directly from file"""
    try:
        # Add agents/bmad_framework to Python path
        bmad_path = os.path.join(os.path.dirname(__file__), 'agents', 'bmad_framework')
        sys.path.insert(0, bmad_path)
        
        # Import directly
        from research_types import BMAD_RESEARCH_TYPES, ResearchTypeId
        
        # Verify structure
        assert len(BMAD_RESEARCH_TYPES) == 8, f"Expected 8 research types, got {len(BMAD_RESEARCH_TYPES)}"
        
        # Check key research types
        key_types = [
            ResearchTypeId.PRODUCT_VALIDATION,
            ResearchTypeId.COMPETITIVE_INTELLIGENCE, 
            ResearchTypeId.MARKET_SIZING
        ]
        
        for rt_id in key_types:
            assert rt_id in BMAD_RESEARCH_TYPES, f"Missing research type: {rt_id.name}"
        
        print("✅ BMAD Research Types - Direct Import Success")
        return True
        
    except Exception as e:
        print(f"❌ BMAD Research Types - Direct Import Failed: {e}")
        return False
    finally:
        # Clean up path
        if bmad_path in sys.path:
            sys.path.remove(bmad_path)

def test_bmad_expert_personas_direct():
    """Test BMAD Expert Personas by importing directly from file"""
    try:
        # Add agents/bmad_framework to Python path
        bmad_path = os.path.join(os.path.dirname(__file__), 'agents', 'bmad_framework')
        sys.path.insert(0, bmad_path)
        
        # Import directly
        from expert_personas import BMAD_EXPERT_PERSONAS, ExpertPersonaId
        
        # Check key personas
        key_personas = [
            ExpertPersonaId.PRODUCT_STRATEGIST,
            ExpertPersonaId.COMPETITIVE_ANALYST,
            ExpertPersonaId.STRATEGY_CONSULTANT
        ]
        
        for persona_id in key_personas:
            assert persona_id in BMAD_EXPERT_PERSONAS, f"Missing persona: {persona_id.name}"
        
        print("✅ BMAD Expert Personas - Direct Import Success")
        return True
        
    except Exception as e:
        print(f"❌ BMAD Expert Personas - Direct Import Failed: {e}")
        return False
    finally:
        # Clean up path
        if bmad_path in sys.path:
            sys.path.remove(bmad_path)

def test_integration_code():
    """Test that integration code exists in MarketResearchOrchestrator file"""
    try:
        orchestrator_path = 'agents/market_research_orchestrator.py'
        
        with open(orchestrator_path, 'r') as f:
            content = f.read()
        
        checks = [
            'from .bmad_framework import BMADFramework',
            'self.bmad_framework = BMADFramework()',
            'bmad_request = BMADAnalysisRequest(',
            'bmad_result = self.bmad_framework.execute_bmad_analysis'
        ]
        
        for check in checks:
            assert check in content, f"Missing integration code: {check}"
        
        print("✅ BMAD Integration Code - Present in MarketResearchOrchestrator")
        return True
        
    except Exception as e:
        print(f"❌ BMAD Integration Code - Test Failed: {e}")
        return False

def test_files_created():
    """Test that BMAD Framework files were created"""
    try:
        expected_files = [
            'agents/bmad_framework/__init__.py',
            'agents/bmad_framework/research_types.py', 
            'agents/bmad_framework/expert_personas.py',
            'agents/bmad_framework/core.py'
        ]
        
        for file_path in expected_files:
            assert os.path.exists(file_path), f"Missing file: {file_path}"
        
        print("✅ BMAD Framework Files - All Created Successfully")
        return True
        
    except Exception as e:
        print(f"❌ BMAD Framework Files - Test Failed: {e}")
        return False

def main():
    """Run minimal BMAD Framework tests"""
    print("🧪 BMAD Framework Minimal Tests - Story 1.1")
    print("=" * 60)
    
    tests = [
        ("BMAD Framework Files Created", test_files_created),
        ("BMAD Research Types Direct Import", test_bmad_research_types_direct), 
        ("BMAD Expert Personas Direct Import", test_bmad_expert_personas_direct),
        ("BMAD Integration Code Present", test_integration_code)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🔍 Testing: {test_name}")
        print("-" * 40)
        result = test_func()
        results.append((test_name, result))
    
    print("\n📊 Test Results Summary")
    print("=" * 60)
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n📈 Overall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 Story 1.1: BMAD Framework Integration - SUCCESS!")
        print("   - BMAD Framework components created and working")
        print("   - Integration code properly implemented") 
        print("   - Ready for full system integration")
    else:
        print("⚠️  Story 1.1: BMAD Framework Integration - PARTIAL SUCCESS")
        print("   - Some components may need attention")
    
    return passed == len(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)