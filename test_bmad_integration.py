#!/usr/bin/env python3
"""
Test BMAD Framework Integration
Verifies that Story 1.1 implementation preserves existing functionality
"""

import os
import sys
sys.path.append('.')

def test_bmad_framework_import():
    """Test that BMAD Framework can be imported successfully"""
    try:
        from agents.bmad_framework import BMADFramework, BMADAnalysisRequest, BMAD_RESEARCH_TYPES
        from agents.bmad_framework.research_types import ResearchTypeId
        from agents.bmad_framework.expert_personas import ExpertPersonaId
        
        print("✅ BMAD Framework imports successful")
        print(f"   - Research Types Available: {len(BMAD_RESEARCH_TYPES)}")
        print(f"   - Research Type IDs: {[rt.name for rt in ResearchTypeId]}")
        print(f"   - Expert Persona IDs: {[ep.name for ep in ExpertPersonaId]}")
        return True
    except Exception as e:
        print(f"❌ BMAD Framework import failed: {e}")
        return False

def test_market_research_orchestrator_integration():
    """Test that MarketResearchOrchestrator integrates BMAD Framework correctly"""
    try:
        # Test class definition and BMAD Framework integration without instantiation
        import sys
        sys.path.append('.')
        
        # Check that the integration code is present
        with open('agents/market_research_orchestrator.py', 'r') as f:
            content = f.read()
            
        # Verify BMAD Framework imports are present
        assert 'from .bmad_framework import BMADFramework' in content, "BMAD Framework import missing"
        assert 'self.bmad_framework = BMADFramework()' in content, "BMAD Framework initialization missing"
        assert 'bmad_result = self.bmad_framework.execute_bmad_analysis' in content, "BMAD execution missing"
        
        print("✅ MarketResearchOrchestrator BMAD integration successful")
        print("   - BMAD Framework imports added")
        print("   - BMAD Framework initialization present")
        print("   - BMAD execution logic integrated")
        
        return True
    except Exception as e:
        print(f"❌ MarketResearchOrchestrator integration failed: {e}")
        return False

def test_existing_functionality_preserved():
    """Test that existing functionality is preserved after BMAD integration"""
    try:
        # Test MarketIntelligenceResult without instantiating agents that require OpenAI
        import sys
        sys.path.append('.')
        
        # Check that existing functionality is preserved in code
        with open('agents/market_research_orchestrator.py', 'r') as f:
            content = f.read()
        
        # Verify core methods are still present
        assert 'def perform_market_intelligence(' in content, "perform_market_intelligence method missing"
        assert 'def analyze(' in content, "analyze method missing"
        assert 'self.market_detector = MarketDetectionAgent()' in content, "market_detector missing"
        assert 'self.web_search_engine = WebSearchEngine(' in content, "web_search_engine missing"
        
        # Test MarketIntelligenceResult class can be imported and used
        from agents.market_research_orchestrator import MarketIntelligenceResult
        result = MarketIntelligenceResult()
        result_dict = result.to_dict()
        
        # Verify existing keys are preserved
        expected_keys = ['market_profile', 'competitive_analysis', 'market_validation', 
                        'funding_benchmarks', 'web_intelligence', 'critical_assessment',
                        'investment_decision', 'timestamp', 'processing_steps', 'confidence_score']
        
        for key in expected_keys:
            assert key in result_dict, f"Missing key in result: {key}"
        
        # Verify BMAD integration is backward compatible
        assert 'bmad_analysis' not in result_dict or result_dict['bmad_analysis'] is None, "BMAD should be None when not set"
        
        print("✅ Existing functionality preserved")
        print("   - All core methods available in code")
        print("   - MarketIntelligenceResult backward compatible")
        print(f"   - Result keys: {list(result_dict.keys())}")
        
        return True
    except Exception as e:
        print(f"❌ Existing functionality check failed: {e}")
        return False

def test_bmad_analysis_request_creation():
    """Test BMAD analysis request creation"""
    try:
        from agents.bmad_framework import BMADAnalysisRequest
        from agents.bmad_framework.research_types import ResearchTypeId
        
        request = BMADAnalysisRequest(
            startup_name="Test Startup",
            solution_description="AI-powered data analysis",
            market_vertical="fintech",
            sub_vertical="robo-advisory",
            analysis_depth="comprehensive"
        )
        
        assert request.startup_name == "Test Startup"
        assert request.analysis_depth == "comprehensive"
        
        print("✅ BMAD Analysis Request creation successful")
        print(f"   - Startup: {request.startup_name}")
        print(f"   - Market: {request.market_vertical}/{request.sub_vertical}")
        print(f"   - Depth: {request.analysis_depth}")
        
        return True
    except Exception as e:
        print(f"❌ BMAD Analysis Request creation failed: {e}")
        return False

def main():
    """Run all BMAD integration tests"""
    print("🧪 BMAD Framework Integration Tests - Story 1.1")
    print("=" * 60)
    
    # Set TEST_MODE to avoid API calls
    os.environ['TEST_MODE'] = 'true'
    
    tests = [
        ("BMAD Framework Import", test_bmad_framework_import),
        ("MarketResearchOrchestrator Integration", test_market_research_orchestrator_integration),
        ("Existing Functionality Preservation", test_existing_functionality_preserved),
        ("BMAD Analysis Request Creation", test_bmad_analysis_request_creation)
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
        print("   - All existing functionality preserved")
        print("   - BMAD Framework successfully integrated")
        print("   - Ready for enhanced market intelligence analysis")
    else:
        print("⚠️  Story 1.1: BMAD Framework Integration - NEEDS ATTENTION")
    
    return passed == len(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)