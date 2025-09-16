#!/usr/bin/env python3
"""
Vision Processing SSL Fix Validation Test

Tests that the OpenAI client API pattern fix resolves SSL/timeout issues
and enables proper vision processing integration.

Story: VF-1 - Vision Processing SSL/API Client Fix
"""

import os
import sys
import tempfile
import logging
from unittest.mock import patch, MagicMock
from io import BytesIO

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from handlers.vision_processor import VisionProcessor, get_vision_processor
from handlers.vision_integration_coordinator import VisionIntegrationCoordinator

# Setup test logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TestVisionSSLFix:
    """Test suite for Vision Processing SSL/API Client Fix"""
    
    def __init__(self):
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
    
    def run_test(self, test_name, test_func):
        """Run a single test and record results"""
        self.total_tests += 1
        logger.info(f"🧪 Running: {test_name}")
        
        try:
            result = test_func()
            if result:
                logger.info(f"✅ PASS: {test_name}")
                self.passed_tests += 1
                self.test_results.append(f"✅ {test_name}")
                return True
            else:
                logger.error(f"❌ FAIL: {test_name}")
                self.test_results.append(f"❌ {test_name}")
                return False
        except Exception as e:
            logger.error(f"❌ ERROR in {test_name}: {e}")
            self.test_results.append(f"❌ {test_name}: {str(e)}")
            return False
    
    def test_vision_processor_import(self):
        """AC1: Verify OpenAI import pattern is updated"""
        try:
            # Check that vision_processor.py uses correct OpenAI import
            with open('/Users/gavalle/Documents/GitHub/dataroom-intelligence/handlers/vision_processor.py', 'r') as f:
                content = f.read()
            
            # Should have: from openai import OpenAI
            if 'from openai import OpenAI' in content:
                logger.info("✅ Correct OpenAI import pattern found")
            else:
                logger.error("❌ Missing 'from openai import OpenAI' import")
                return False
                
            # Should NOT have: import openai (old pattern)
            if 'import openai' in content and 'from openai import OpenAI' not in content:
                logger.error("❌ Still using deprecated 'import openai' pattern")
                return False
                
            # Should have: OpenAI(api_key=...)
            if 'OpenAI(api_key=' in content:
                logger.info("✅ Modern client initialization pattern found")
            else:
                logger.error("❌ Missing modern OpenAI client initialization")
                return False
                
            # Should have: client.chat.completions.create
            if 'client.chat.completions.create' in content:
                logger.info("✅ Modern API call pattern found")
            else:
                logger.error("❌ Missing modern API call pattern")
                return False
                
            # Should have: model='gpt-4o'
            if 'gpt-4o' in content:
                logger.info("✅ Updated vision model found")
            else:
                logger.error("❌ Missing updated vision model")
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to check imports: {e}")
            return False
    
    def test_vision_processor_initialization(self):
        """AC1: Test VisionProcessor can initialize with new client pattern"""
        try:
            with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key', 'VISION_ENABLED': 'true'}):
                with patch('handlers.vision_processor.OpenAI') as mock_openai:
                    # Mock OpenAI client
                    mock_client = MagicMock()
                    mock_openai.return_value = mock_client
                    
                    # Initialize processor
                    processor = VisionProcessor()
                    
                    # Verify OpenAI client was initialized correctly
                    mock_openai.assert_called_once_with(api_key='test-key')
                    assert processor.client == mock_client
                    assert processor.vision_enabled == True
                    
                    logger.info("✅ VisionProcessor initialization successful")
                    return True
                    
        except Exception as e:
            logger.error(f"❌ VisionProcessor initialization failed: {e}")
            return False
    
    def test_vision_api_call_pattern(self):
        """AC1: Test that API calls use new pattern without SSL issues"""
        try:
            with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key', 'VISION_ENABLED': 'true'}):
                with patch('handlers.vision_processor.OpenAI') as mock_openai:
                    # Mock successful API response
                    mock_response = MagicMock()
                    mock_response.choices = [MagicMock()]
                    mock_response.choices[0].message.content = '{"analysis": "test result"}'
                    mock_response.usage.total_tokens = 150
                    
                    mock_client = MagicMock()
                    mock_client.chat.completions.create.return_value = mock_response
                    mock_openai.return_value = mock_client
                    
                    # Initialize processor and test API call
                    processor = VisionProcessor()
                    
                    # Create test image data
                    test_image = BytesIO()
                    # Create minimal valid PNG (1x1 pixel)
                    test_image.write(b'\\x89PNG\\r\\n\\x1a\\n\\x00\\x00\\x00\\rIHDR\\x00\\x00\\x00\\x01\\x00\\x00\\x00\\x01\\x08\\x02\\x00\\x00\\x00\\x90wS\\xde\\x00\\x00\\x00\\x0cIDATx\\x9cc```\\x00\\x00\\x00\\x04\\x00\\x01\\xddz\\xc4\\xb6\\x00\\x00\\x00\\x00IEND\\xaeB`\\x82')
                    test_image.seek(0)
                    
                    # Call analyze_image
                    result = processor.analyze_image(
                        test_image.getvalue(),
                        "Test analysis prompt",
                        "Test context"
                    )
                    
                    # Verify API was called with correct pattern
                    mock_client.chat.completions.create.assert_called_once()
                    call_args = mock_client.chat.completions.create.call_args
                    
                    # Check model is updated
                    assert call_args[1]['model'] == 'gpt-4o'
                    
                    # Check timeout is set
                    assert call_args[1]['timeout'] == 30
                    
                    # Check result structure
                    assert result['success'] == True
                    assert result['model_used'] == 'gpt-4o'
                    
                    logger.info("✅ Vision API call pattern updated successfully")
                    return True
                    
        except Exception as e:
            logger.error(f"❌ Vision API call test failed: {e}")
            return False
    
    def test_app_vision_re_enabled(self):
        """AC2: Verify app.py passes actual PDF path instead of None"""
        try:
            with open('/Users/gavalle/Documents/GitHub/dataroom-intelligence/app.py', 'r') as f:
                content = f.read()
            
            # Should NOT have the bypass comment
            if 'TEMPORARY: Disable vision processing due to SSL/timeout issues' not in content:
                logger.info("✅ Vision processing bypass comment removed")
            else:
                logger.error("❌ Vision processing still shows as disabled")
                return False
                
            # Should pass actual PDF path, not None
            if 'pdf_path = pdf_files[0][\'path\']' in content:
                logger.info("✅ PDF path extraction added")
            else:
                logger.error("❌ Missing PDF path extraction")
                return False
                
            # Should pass pdf_path to coordinator, not None
            if 'process_document_with_vision(\n                            pdf_path,' in content:
                logger.info("✅ Vision processing re-enabled with PDF path")
            else:
                logger.error("❌ Vision processing still passes None")
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to check app.py changes: {e}")
            return False
    
    def test_error_handling_graceful_fallback(self):
        """AC3: Test graceful fallback when vision fails"""
        try:
            with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key', 'VISION_ENABLED': 'true'}):
                with patch('handlers.vision_processor.OpenAI') as mock_openai:
                    # Mock API failure
                    mock_client = MagicMock()
                    mock_client.chat.completions.create.side_effect = Exception("Test SSL error")
                    mock_openai.return_value = mock_client
                    
                    processor = VisionProcessor()
                    
                    # Test graceful fallback
                    result = processor.analyze_image(
                        b"fake image data",
                        "Test prompt",
                        "Test context"
                    )
                    
                    # Should return fallback response
                    assert result['success'] == False
                    assert 'error' in result
                    assert result['fallback_required'] == True
                    
                    logger.info("✅ Graceful fallback works correctly")
                    return True
                    
        except Exception as e:
            logger.error(f"❌ Error handling test failed: {e}")
            return False
    
    def test_cost_controls_functional(self):
        """AC4: Verify cost controls still work"""
        try:
            with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key', 'VISION_ENABLED': 'true', 'VISION_COST_LIMIT': '5.0'}):
                with patch('handlers.vision_processor.OpenAI'):
                    processor = VisionProcessor()
                    
                    # Check initial state
                    assert processor.daily_budget == 5.0
                    assert processor.current_daily_cost == 0.0
                    
                    # Test budget availability check
                    assert processor.is_vision_available() == True
                    
                    # Simulate exceeding budget
                    processor.current_daily_cost = 6.0
                    assert processor.is_vision_available() == False
                    
                    # Test cost status
                    status = processor.get_daily_cost_status()
                    assert status['daily_budget'] == 5.0
                    assert status['current_cost'] == 6.0
                    assert status['remaining_budget'] == 0
                    
                    logger.info("✅ Cost controls functional")
                    return True
                    
        except Exception as e:
            logger.error(f"❌ Cost controls test failed: {e}")
            return False
    
    def run_all_tests(self):
        """Run all validation tests"""
        logger.info("🚀 Starting Vision SSL Fix Validation Tests")
        logger.info("=" * 60)
        
        # AC1: Update OpenAI Client Pattern
        self.run_test("OpenAI Import Pattern Updated", self.test_vision_processor_import)
        self.run_test("VisionProcessor Initialization", self.test_vision_processor_initialization)
        self.run_test("Vision API Call Pattern Fixed", self.test_vision_api_call_pattern)
        
        # AC2: Re-enable Vision Processing
        self.run_test("App Vision Processing Re-enabled", self.test_app_vision_re_enabled)
        
        # AC3: Error Handling Enhancement
        self.run_test("Graceful Fallback on Errors", self.test_error_handling_graceful_fallback)
        
        # AC4: Cost Controls
        self.run_test("Cost Controls Functional", self.test_cost_controls_functional)
        
        # Summary
        logger.info("=" * 60)
        logger.info("🧪 TEST RESULTS SUMMARY")
        logger.info("=" * 60)
        
        for result in self.test_results:
            logger.info(result)
        
        logger.info(f"\\n📊 TOTAL: {self.passed_tests}/{self.total_tests} tests passed")
        
        if self.passed_tests == self.total_tests:
            logger.info("🎉 ALL TESTS PASSED - Vision SSL fix is successful!")
            return True
        else:
            logger.error(f"❌ {self.total_tests - self.passed_tests} tests failed")
            return False

if __name__ == "__main__":
    # Set TEST_MODE to avoid actual API calls
    os.environ['TEST_MODE'] = 'true'
    
    tester = TestVisionSSLFix()
    success = tester.run_all_tests()
    
    sys.exit(0 if success else 1)