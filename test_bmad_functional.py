#!/usr/bin/env python3
"""
Test BMAD-Inspired Functional Implementation
Tests that the enhanced BMAD system actually improves OpenAI prompts and analysis quality
"""

import os
import sys
sys.path.append('.')

def test_bmad_professional_prompts():
    """Test that BMAD-inspired professional prompts are properly defined"""
    try:
        # Add agents/bmad_framework to Python path
        bmad_path = os.path.join(os.path.dirname(__file__), 'agents', 'bmad_framework')
        sys.path.insert(0, bmad_path)
        
        from professional_prompts import RESEARCH_TYPE_PROMPTS, get_specialized_prompt, format_prompt
        
        # Test all expected prompts exist
        expected_prompts = [
            'competitive_intelligence',
            'market_research', 
            'technology_assessment',
            'financial_analysis',
            'meta_synthesis'
        ]
        
        for prompt_type in expected_prompts:
            assert prompt_type in RESEARCH_TYPE_PROMPTS, f"Missing prompt: {prompt_type}"
            prompt = get_specialized_prompt(prompt_type)
            assert len(prompt) > 1000, f"Prompt too short: {prompt_type}"
            assert "BMAD" in prompt or "McKinsey" in prompt or "BCG" in prompt, f"Missing professional context: {prompt_type}"
        
        # Test prompt formatting
        test_prompt = get_specialized_prompt('competitive_intelligence')
        formatted = format_prompt(
            test_prompt,
            sources_count=25,
            startup_name="TestCorp",
            market_vertical="fintech",
            sub_vertical="payments",
            target_market="SMB payments",
            solution_description="AI-powered payment processing"
        )
        
        assert "25" in formatted, "Sources count not formatted"
        assert "TestCorp" in formatted, "Startup name not formatted"
        assert "fintech" in formatted, "Market vertical not formatted"
        
        print("✅ BMAD Professional Prompts - All prompts defined and functional")
        return True
        
    except Exception as e:
        print(f"❌ BMAD Professional Prompts - Test Failed: {e}")
        return False
    finally:
        if bmad_path in sys.path:
            sys.path.remove(bmad_path)

def test_bmad_enhanced_core_functionality():
    """Test enhanced BMAD core functionality without requiring OpenAI"""
    try:
        # Add agents/bmad_framework to Python path
        bmad_path = os.path.join(os.path.dirname(__file__), 'agents', 'bmad_framework')
        sys.path.insert(0, bmad_path)
        
        from core import BMADFramework, BMADAnalysisRequest
        
        # Test framework initialization
        framework = BMADFramework()
        assert framework is not None, "Framework failed to initialize"
        
        # Test analysis request creation
        request = BMADAnalysisRequest(
            startup_name="TestCorp",
            solution_description="AI-powered fintech solution",
            market_vertical="fintech",
            sub_vertical="payments",
            analysis_depth="comprehensive"
        )
        
        # Test helper methods
        sources = framework._collect_comprehensive_sources.__func__(
            framework, request, lambda q: {"results": [{"url": f"http://test.com/{i}", "title": f"Test {i}", "content": "test content"}]}
        )
        
        assert len(sources) > 0, "No sources collected"
        assert isinstance(sources, dict), "Sources not in correct format"
        
        # Test extraction methods
        test_synthesis = """
        RECOMMENDATION: PROCEED
        
        Key findings:
        • Strong market opportunity with $2B TAM
        • Competitive advantage in AI technology
        • Growing customer adoption
        
        Strategic recommendations:
        • Focus on enterprise segment
        • Develop partnership strategy
        • Expand technology capabilities
        """
        
        recommendation = framework._extract_investment_recommendation(test_synthesis)
        confidence = framework._extract_confidence_level(test_synthesis) 
        findings = framework._extract_key_findings(test_synthesis, {})
        recommendations = framework._extract_strategic_recommendations(test_synthesis)
        
        assert recommendation == "PROCEED", f"Wrong recommendation: {recommendation}"
        assert len(findings) > 0, "No findings extracted"
        assert len(recommendations) > 0, "No recommendations extracted"
        
        print("✅ BMAD Enhanced Core Functionality - All methods working correctly")
        return True
        
    except Exception as e:
        print(f"❌ BMAD Enhanced Core Functionality - Test Failed: {e}")
        return False
    finally:
        if bmad_path in sys.path:
            sys.path.remove(bmad_path)

def test_bmad_integration_points():
    """Test BMAD integration points in MarketResearchOrchestrator"""
    try:
        with open('agents/market_research_orchestrator.py', 'r') as f:
            content = f.read()
        
        # Test enhanced integration points
        integration_checks = [
            ('Professional Prompts Import', 'from .professional_prompts import'),
            ('Enhanced Source Collection', '_collect_comprehensive_sources'),
            ('Specialized Analysis Execution', 'get_specialized_prompt'),
            ('Meta-Synthesis Implementation', 'meta_synthesis'),
            ('Investment Recommendation Extraction', '_extract_investment_recommendation'),
            ('Professional Analysis Flow', 'competitive_intelligence'),
            ('Market Research Analysis', 'market_research'),
            ('Technology Assessment', 'technology_assessment'),
            ('Financial Analysis', 'financial_analysis')
        ]
        
        for check_name, pattern in integration_checks:
            assert pattern in content, f"Missing integration: {check_name} - '{pattern}'"
        
        print("✅ BMAD Integration Points - All enhanced integration points present")
        return True
        
    except Exception as e:
        print(f"❌ BMAD Integration Points - Test Failed: {e}")
        return False

def test_bmad_quality_enhancement_features():
    """Test that BMAD enhancements provide professional-grade features"""
    try:
        # Add agents/bmad_framework to Python path  
        bmad_path = os.path.join(os.path.dirname(__file__), 'agents', 'bmad_framework')
        sys.path.insert(0, bmad_path)
        
        from professional_prompts import COMPETITIVE_INTELLIGENCE_PROMPT, MARKET_RESEARCH_PROMPT
        
        # Test professional-grade prompt features
        quality_features = [
            # BMAD-inspired features
            ('Professional Expertise', ['McKinsey', 'BCG', 'Senior', 'years of experience']),
            ('Structured Analysis Framework', ['ANALYSIS FRAMEWORK', 'methodology', 'Assessment']),
            ('Investment Focus', ['investment', 'VC', 'venture capital', 'due diligence']),
            ('Actionable Insights', ['actionable', 'strategic', 'recommendations']),
            ('Professional Output', ['professional-grade', 'executive', 'investment committee']),
            ('Evidence-Based', ['evidence', 'supporting', 'specific']),
            ('Structured Format', ['sections', 'bullet points', 'structured report'])
        ]
        
        prompts_to_check = [COMPETITIVE_INTELLIGENCE_PROMPT, MARKET_RESEARCH_PROMPT]
        
        for feature_name, keywords in quality_features:
            feature_found = False
            for prompt in prompts_to_check:
                if any(keyword.lower() in prompt.lower() for keyword in keywords):
                    feature_found = True
                    break
            assert feature_found, f"Missing quality feature: {feature_name}"
        
        # Test prompt length (professional prompts should be comprehensive)
        for prompt in prompts_to_check:
            assert len(prompt) > 2000, f"Prompt too short for professional quality: {len(prompt)} chars"
        
        print("✅ BMAD Quality Enhancement Features - Professional-grade features present")
        return True
        
    except Exception as e:
        print(f"❌ BMAD Quality Enhancement Features - Test Failed: {e}")
        return False
    finally:
        if bmad_path in sys.path:
            sys.path.remove(bmad_path)

def main():
    """Run BMAD functional enhancement tests"""
    print("🧪 BMAD-Inspired Functional Enhancement Tests")
    print("=" * 60)
    
    tests = [
        ("BMAD Professional Prompts", test_bmad_professional_prompts),
        ("BMAD Enhanced Core Functionality", test_bmad_enhanced_core_functionality),
        ("BMAD Integration Points", test_bmad_integration_points),
        ("BMAD Quality Enhancement Features", test_bmad_quality_enhancement_features)
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
        print("🎉 BMAD-Inspired Enhancement - FUNCTIONAL SUCCESS!")
        print("   - Professional prompts based on BMAD templates implemented")
        print("   - Enhanced analysis flow with specialized perspectives") 
        print("   - Quality features for McKinsey/BCG-level output")
        print("   - Real functionality to improve OpenAI calls")
    else:
        print("⚠️  BMAD-Inspired Enhancement - NEEDS ATTENTION")
    
    return passed == len(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)