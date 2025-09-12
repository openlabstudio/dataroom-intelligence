#!/usr/bin/env python3
"""
Test BMAD Framework Standalone Components
Tests BMAD Framework without dependencies on OpenAI or other external services
"""

import os
import sys
sys.path.append('.')

def test_bmad_research_types():
    """Test BMAD Research Types are properly defined"""
    try:
        from agents.bmad_framework.research_types import BMAD_RESEARCH_TYPES, ResearchTypeId, ResearchType
        
        # Test all 8 research types are present
        assert len(BMAD_RESEARCH_TYPES) == 8, f"Expected 8 research types, got {len(BMAD_RESEARCH_TYPES)}"
        
        # Test specific research types exist
        expected_types = [
            ResearchTypeId.PRODUCT_VALIDATION,
            ResearchTypeId.COMPETITIVE_INTELLIGENCE,
            ResearchTypeId.MARKET_SIZING,
            ResearchTypeId.TECHNOLOGY_ASSESSMENT,
            ResearchTypeId.REGULATORY_ANALYSIS,
            ResearchTypeId.CUSTOMER_DEVELOPMENT,
            ResearchTypeId.FUNDING_INTELLIGENCE,
            ResearchTypeId.STRATEGIC_POSITIONING
        ]
        
        for rt_id in expected_types:
            assert rt_id in BMAD_RESEARCH_TYPES, f"Missing research type: {rt_id.name}"
            rt = BMAD_RESEARCH_TYPES[rt_id]
            assert isinstance(rt, ResearchType), f"Invalid type for {rt_id.name}"
            assert len(rt.focus_areas) > 0, f"No focus areas for {rt_id.name}"
            assert len(rt.search_strategies) > 0, f"No search strategies for {rt_id.name}"
        
        print("✅ BMAD Research Types test successful")
        print(f"   - All 8 research types present: {[rt.name for rt in expected_types]}")
        return True
    except Exception as e:
        print(f"❌ BMAD Research Types test failed: {e}")
        return False

def test_bmad_expert_personas():
    """Test BMAD Expert Personas are properly defined"""
    try:
        from agents.bmad_framework.expert_personas import BMAD_EXPERT_PERSONAS, ExpertPersonaId, ExpertPersona
        
        # Test key expert personas exist
        key_personas = [
            ExpertPersonaId.PRODUCT_STRATEGIST,
            ExpertPersonaId.MARKET_RESEARCHER,
            ExpertPersonaId.COMPETITIVE_ANALYST,
            ExpertPersonaId.FINANCIAL_ANALYST,
            ExpertPersonaId.STRATEGY_CONSULTANT,
            ExpertPersonaId.INVESTMENT_ANALYST
        ]
        
        for persona_id in key_personas:
            assert persona_id in BMAD_EXPERT_PERSONAS, f"Missing expert persona: {persona_id.name}"
            persona = BMAD_EXPERT_PERSONAS[persona_id]
            assert isinstance(persona, ExpertPersona), f"Invalid type for {persona_id.name}"
            assert len(persona.expertise_areas) > 0, f"No expertise areas for {persona_id.name}"
            assert len(persona.analysis_frameworks) > 0, f"No analysis frameworks for {persona_id.name}"
            assert len(persona.key_questions) > 0, f"No key questions for {persona_id.name}"
        
        print("✅ BMAD Expert Personas test successful")
        print(f"   - Key personas present: {[p.name for p in key_personas]}")
        return True
    except Exception as e:
        print(f"❌ BMAD Expert Personas test failed: {e}")
        return False

def test_bmad_core_structure():
    """Test BMAD Framework core structure without instantiation"""
    try:
        from agents.bmad_framework.core import BMADFramework, BMADAnalysisRequest, BMADSynthesisResult, BMADResearchResult
        
        # Test that classes can be imported
        assert BMADFramework is not None, "BMADFramework class not found"
        assert BMADAnalysisRequest is not None, "BMADAnalysisRequest class not found"
        assert BMADSynthesisResult is not None, "BMADSynthesisResult class not found"
        assert BMADResearchResult is not None, "BMADResearchResult class not found"
        
        # Test BMADAnalysisRequest creation
        request = BMADAnalysisRequest(
            startup_name="Test Company",
            solution_description="AI-powered analytics",
            market_vertical="fintech",
            sub_vertical="data analytics"
        )
        
        assert request.startup_name == "Test Company"
        assert request.analysis_depth == "comprehensive"  # default value
        
        print("✅ BMAD Core Structure test successful")
        print("   - All core classes importable")
        print("   - BMADAnalysisRequest creation works")
        return True
    except Exception as e:
        print(f"❌ BMAD Core Structure test failed: {e}")
        return False

def test_integration_code_presence():
    """Test that integration code is present in MarketResearchOrchestrator"""
    try:
        with open('agents/market_research_orchestrator.py', 'r') as f:
            content = f.read()
        
        integration_checks = [
            ('BMAD Import', 'from .bmad_framework import BMADFramework'),
            ('BMAD Initialization', 'self.bmad_framework = BMADFramework()'),
            ('BMAD Request Creation', 'bmad_request = BMADAnalysisRequest('),
            ('BMAD Execution', 'bmad_result = self.bmad_framework.execute_bmad_analysis'),
            ('BMAD Result Storage', "result.bmad_analysis = {"),
            ('Result Enhancement', "result['bmad_analysis'] = self.bmad_analysis")
        ]
        
        for check_name, pattern in integration_checks:
            assert pattern in content, f"Missing {check_name}: '{pattern}'"
        
        print("✅ Integration Code Presence test successful")
        print("   - All integration patterns found")
        return True
    except Exception as e:
        print(f"❌ Integration Code Presence test failed: {e}")
        return False

def main():
    """Run BMAD Framework standalone tests"""
    print("🧪 BMAD Framework Standalone Tests - Story 1.1")
    print("=" * 60)
    
    tests = [
        ("BMAD Research Types", test_bmad_research_types),
        ("BMAD Expert Personas", test_bmad_expert_personas),
        ("BMAD Core Structure", test_bmad_core_structure),
        ("Integration Code Presence", test_integration_code_presence)
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
        print("🎉 Story 1.1: BMAD Framework Integration - CORE SUCCESS!")
        print("   - BMAD Framework components working correctly")
        print("   - Integration code properly placed")
        print("   - Ready for full system testing with dependencies")
    else:
        print("⚠️  Story 1.1: BMAD Framework Integration - NEEDS ATTENTION")
    
    return passed == len(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)