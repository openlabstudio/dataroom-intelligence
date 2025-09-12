#!/usr/bin/env python3
"""
Test Vision Integration Story 1.2 Completion

Validates that GPT Vision infrastructure is properly integrated into main application workflow
and all Integration Verification Points are working correctly.
"""

import os
import sys
import json
from datetime import datetime
from typing import Dict, Any

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from handlers.vision_integration_coordinator import vision_integration_coordinator
from handlers.enhanced_session_manager import EnhancedSessionManager
from utils.logger import get_logger

logger = get_logger(__name__)

def test_vision_coordinator_initialization():
    """Test that vision integration coordinator initializes correctly"""
    print("🔧 Testing Vision Integration Coordinator initialization...")
    
    # Check if coordinator is properly initialized
    assert vision_integration_coordinator is not None, "Vision coordinator should be initialized"
    
    # Check if all components are initialized
    assert hasattr(vision_integration_coordinator, 'vision_processor'), "Vision processor should be available"
    assert hasattr(vision_integration_coordinator, 'complexity_analyzer'), "Complexity analyzer should be available"
    assert hasattr(vision_integration_coordinator, 'image_processor'), "Image processor should be available"
    assert hasattr(vision_integration_coordinator, 'cost_controller'), "Cost controller should be available"
    assert hasattr(vision_integration_coordinator, 'session_manager'), "Session manager should be available"
    
    print("✅ Vision Integration Coordinator initialization: PASSED")
    return True

def test_enhanced_session_creation():
    """Test enhanced session creation without vision processing"""
    print("📊 Testing Enhanced Session creation...")
    
    session_manager = EnhancedSessionManager()
    
    # Create mock basic session data
    basic_session_data = {
        'analysis_result': {'mock': 'analysis'},
        'document_summary': {'total_documents': 1, 'successful_processing': 1},
        'processed_documents': {'doc1': {'name': 'test.pdf', 'type': 'pdf'}},
        'drive_link': 'https://drive.google.com/test',
        'analysis_timestamp': datetime.now().isoformat()
    }
    
    # Test enhanced session creation without vision results
    enhanced_session = session_manager.create_enhanced_session(
        'test_user_123', basic_session_data, None
    )
    
    # Validate enhanced session structure
    assert 'extraction_metadata' in enhanced_session, "Enhanced session should have extraction metadata"
    assert 'unified_extraction' in enhanced_session, "Enhanced session should have unified extraction"
    assert 'command_data' in enhanced_session, "Enhanced session should have command data"
    
    # Check command data availability
    command_data = enhanced_session['command_data']
    assert 'ask' in command_data, "Ask command data should be available"
    assert 'gaps' in command_data, "Gaps command data should be available"
    assert 'scoring' in command_data, "Scoring command data should be available"
    assert 'memo' in command_data, "Memo command data should be available"
    
    # Check backward compatibility
    assert 'analysis_result' in enhanced_session, "Should maintain backward compatibility"
    assert 'document_summary' in enhanced_session, "Should maintain backward compatibility"
    assert 'processed_documents' in enhanced_session, "Should maintain backward compatibility"
    
    print("✅ Enhanced Session creation: PASSED")
    return True

def test_vision_processing_pipeline_mock():
    """Test vision processing pipeline with mock data (no real API calls)"""
    print("🔍 Testing Vision Processing Pipeline (mock mode)...")
    
    # Create mock basic session data
    basic_session_data = {
        'analysis_result': {'mock': 'analysis'},
        'document_summary': {'total_documents': 1, 'successful_processing': 1},
        'processed_documents': {'doc1': {'name': 'test.pdf', 'type': 'pdf'}},
        'drive_link': 'https://drive.google.com/test',
        'analysis_timestamp': datetime.now().isoformat()
    }
    
    # Test with no PDF path (should fallback gracefully)
    enhanced_session, vision_results = vision_integration_coordinator.process_document_with_vision(
        None, 'test_user_456', basic_session_data
    )
    
    # Should create enhanced session even without vision processing
    assert enhanced_session is not None, "Enhanced session should be created"
    assert 'extraction_metadata' in enhanced_session, "Should have extraction metadata"
    assert enhanced_session['extraction_metadata']['text_extraction_complete'], "Text extraction should be marked complete"
    
    # Vision results should be empty but handled gracefully
    assert vision_results == {}, "Vision results should be empty for null PDF path"
    
    print("✅ Vision Processing Pipeline (mock mode): PASSED")
    return True

def test_command_enhancement_integration():
    """Test that command enhancement methods work correctly"""
    print("🎯 Testing Command Enhancement Integration...")
    
    # Create mock enhanced session
    mock_session = {
        'vision_analysis': {
            'processing_summary': {
                'total_pages_analyzed': 5,
                'successful_analyses': 4,
                'total_cost_usd': 0.15
            }
        },
        'command_data': {
            'ask': {'searchable_content': {}, 'visual_references': {}},
            'gaps': {'missing_categories': [], 'completeness_assessment': {'completeness_score': 0.8}},
            'scoring': {'scoring_metrics': {}, 'financial_indicators': {}},
            'memo': {'supporting_evidence': {}}
        }
    }
    
    # Test ask command enhancement
    ask_enhancement = vision_integration_coordinator.enhance_ask_command(mock_session, "What is the revenue?")
    assert 'enhanced_context' in ask_enhancement, "Ask enhancement should have enhanced context"
    assert 'answer_sources' in ask_enhancement, "Ask enhancement should have answer sources"
    
    # Test gaps command enhancement
    gaps_enhancement = vision_integration_coordinator.enhance_gaps_command(mock_session)
    assert 'comprehensive_gap_analysis' in gaps_enhancement, "Gaps enhancement should have comprehensive analysis"
    assert 'completeness_assessment' in gaps_enhancement, "Gaps enhancement should have completeness assessment"
    
    # Test scoring command enhancement
    scoring_enhancement = vision_integration_coordinator.enhance_scoring_command(mock_session)
    assert 'comprehensive_metrics' in scoring_enhancement, "Scoring enhancement should have comprehensive metrics"
    assert 'scoring_confidence' in scoring_enhancement, "Scoring enhancement should have confidence scores"
    
    # Test memo command enhancement
    memo_enhancement = vision_integration_coordinator.enhance_memo_command(mock_session)
    assert 'comprehensive_evidence' in memo_enhancement, "Memo enhancement should have comprehensive evidence"
    assert 'investment_thesis_strength' in memo_enhancement, "Memo enhancement should have thesis strength"
    
    print("✅ Command Enhancement Integration: PASSED")
    return True

def test_vision_processing_status():
    """Test vision processing status reporting"""
    print("📋 Testing Vision Processing Status...")
    
    # Create mock session with vision data
    mock_session_with_vision = {
        'vision_analysis': {
            'processing_summary': {
                'total_pages_analyzed': 3,
                'successful_analyses': 3,
                'total_cost_usd': 0.08
            },
            'processing_metadata': {
                'total_pages_analyzed': 3,
                'cost_optimization_savings': 15.0
            }
        },
        'extraction_metadata': {
            'vision_extraction_complete': True,
            'hybrid_processing_used': True
        }
    }
    
    # Test vision processing status
    status = vision_integration_coordinator.get_vision_processing_status(mock_session_with_vision)
    
    assert 'vision_processing_complete' in status, "Status should include processing completion"
    assert 'enhancement_status' in status, "Status should include enhancement status"
    assert 'processing_metadata' in status, "Status should include processing metadata"
    
    # Check enhancement status for all commands
    enhancement_status = status['enhancement_status']
    assert 'ask_enhanced' in enhancement_status, "Should report ask enhancement status"
    assert 'gaps_enhanced' in enhancement_status, "Should report gaps enhancement status"
    assert 'scoring_enhanced' in enhancement_status, "Should report scoring enhancement status"
    assert 'memo_enhanced' in enhancement_status, "Should report memo enhancement status"
    
    print("✅ Vision Processing Status: PASSED")
    return True

def validate_integration_verification_points():
    """Validate all Integration Verification Points"""
    print("🎯 Validating Integration Verification Points...")
    
    # IV1: /gaps command should access enhanced extraction data
    print("   IV1: Testing /gaps command enhanced data access...")
    mock_session = {'command_data': {'gaps': {'missing_categories': ['financials']}}}
    gaps_data = vision_integration_coordinator.enhance_gaps_command(mock_session)
    assert gaps_data is not None, "IV1: /gaps should access enhanced data"
    print("   ✅ IV1: PASSED")
    
    # IV2: /ask command should access both text and visual content
    print("   IV2: Testing /ask command text+visual access...")
    ask_data = vision_integration_coordinator.enhance_ask_command(mock_session, "test question")
    assert ask_data is not None, "IV2: /ask should access enhanced data"
    assert 'enhanced_context' in ask_data, "IV2: Should have enhanced context"
    print("   ✅ IV2: PASSED")
    
    # IV3: All commands should have access to vision results when available
    print("   IV3: Testing universal vision access...")
    commands = ['ask', 'gaps', 'scoring', 'memo']
    for cmd in commands:
        method_name = f'enhance_{cmd}_command'
        assert hasattr(vision_integration_coordinator, method_name), f"IV3: Should have {method_name} method"
    print("   ✅ IV3: PASSED")
    
    print("✅ All Integration Verification Points: PASSED")
    return True

def main():
    """Run all integration tests"""
    print("🚀 Starting Vision Integration Tests for Story 1.2 Completion")
    print("=" * 60)
    
    test_results = []
    
    try:
        # Test 1: Initialization
        test_results.append(("Vision Coordinator Init", test_vision_coordinator_initialization()))
        
        # Test 2: Enhanced Session Creation
        test_results.append(("Enhanced Session Creation", test_enhanced_session_creation()))
        
        # Test 3: Vision Processing Pipeline
        test_results.append(("Vision Processing Pipeline", test_vision_processing_pipeline_mock()))
        
        # Test 4: Command Enhancement
        test_results.append(("Command Enhancement", test_command_enhancement_integration()))
        
        # Test 5: Status Reporting
        test_results.append(("Status Reporting", test_vision_processing_status()))
        
        # Test 6: Integration Verification Points
        test_results.append(("Integration Verification", validate_integration_verification_points()))
        
    except Exception as e:
        logger.error(f"❌ Test failed with error: {e}")
        test_results.append(("Error", False))
    
    # Print results summary
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY:")
    print("=" * 60)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "PASSED" if result else "FAILED"
        emoji = "✅" if result else "❌"
        print(f"{emoji} {test_name}: {status}")
        if result:
            passed += 1
    
    print("=" * 60)
    print(f"🎯 OVERALL RESULT: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED - Story 1.2 Integration Complete!")
        return True
    else:
        print("❌ Some tests failed - Integration needs attention")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)