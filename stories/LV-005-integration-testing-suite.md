# Story LV-005: Integration Testing Suite

**Story ID**: LV-005  
**Epic**: Lazy Vision Document Analysis Enhancement  
**Sprint**: 1  
**Story Points**: 5  
**Priority**: Must Have  
**Type**: Quality Assurance  

---

## USER STORY

**As a** developer  
**I want** comprehensive tests validating vision enhancement  
**So that** I can ensure quality and prevent regressions across all components

## BUSINESS VALUE

**Problem**: Vision enhancement involves multiple complex components that must work together flawlessly  
**Solution**: Comprehensive testing suite validates integration, performance, and quality  
**Value**: Prevents production failures, ensures 95% success rate target, validates cost and performance claims  

**Quality Assurance**: Tests prevent deployment of broken vision processing (current 0% success rate shows risk)  
**Performance Validation**: Ensures 30-second response time and SSL prevention claims are met  
**Regression Prevention**: Guards against breaking existing functionality during enhancement  

---

## DETAILED ACCEPTANCE CRITERIA

### AC1: Strategic Page Selection Tests
```gherkin
GIVEN various deck formats (15-page, 30-page, 43-page)
WHEN running strategic page selection tests
THEN correct strategic pages are identified for each format
AND selection completes in <2 seconds for all deck sizes
AND selected pages contain relevant business content (financials, competition, market)
```

**Test Cases**:
- [ ] **TC1.1**: 15-page standard pitch deck → identifies 3-5 strategic pages across categories
- [ ] **TC1.2**: 30-page comprehensive deck → identifies exactly 7 strategic pages with proper prioritization
- [ ] **TC1.3**: 43-page detailed deck → identifies 7 most strategic pages, ignores appendix content
- [ ] **TC1.4**: Text-heavy deck with minimal charts → identifies at least 3 pages using fallback patterns
- [ ] **TC1.5**: Visual-heavy deck → prioritizes financial charts and competition slides correctly
- [ ] **TC1.6**: Non-English deck → fallback patterns work correctly
- [ ] **TC1.7**: Performance test → selection completes in <2 seconds for 43-page deck

### AC2: SSL Prevention Validation
```gherkin
GIVEN a 43-page pitch deck that previously caused SSL exhaustion
WHEN vision processing runs with Lazy Vision enhancement
THEN zero SSL exhaustion errors occur
AND processing completes in <35 seconds
AND exactly 7 pages maximum are processed regardless of input size
```

**Test Cases**:
- [ ] **TC2.1**: 43-page deck processing → zero SSL errors, completes successfully
- [ ] **TC2.2**: Multiple concurrent users → no connection pool exhaustion
- [ ] **TC2.3**: Extended processing session → system remains stable without SSL issues
- [ ] **TC2.4**: Stress test with 100-page deck → processes only 7 pages, no SSL errors
- [ ] **TC2.5**: Network interruption simulation → graceful recovery without SSL corruption
- [ ] **TC2.6**: API rate limiting → proper error handling without SSL connection issues

### AC3: Data Quality Testing
```gherkin
GIVEN sample financial chart pages processed with vision
WHEN comparing extracted data to manual review
THEN extracted data matches manual review >90% accuracy
AND includes specific numbers, percentages, and trends
AND identifies visual elements correctly (charts, graphs, competitor logos)
```

**Test Cases**:
- [ ] **TC3.1**: Revenue chart extraction → extracts specific revenue figures with >90% accuracy
- [ ] **TC3.2**: Competition slide analysis → identifies competitor names and positioning correctly
- [ ] **TC3.3**: Market size chart → extracts TAM/SAM numbers accurately
- [ ] **TC3.4**: Financial dashboard → extracts multiple metrics (CAC, LTV, burn rate) correctly
- [ ] **TC3.5**: Growth metrics → identifies growth percentages and trends accurately
- [ ] **TC3.6**: Unit economics → extracts payback period, customer metrics correctly

### AC4: End-to-End Workflow Tests
```gherkin
GIVEN complete /analyze command with real pitch deck
WHEN executed with Lazy Vision enhancement
THEN report is generated with enhanced data quality
AND vision cache is populated for /ask optimization
AND response time is <30 seconds
AND all existing functionality continues to work
```

**Test Cases**:
- [ ] **TC4.1**: Full /analyze workflow → completes successfully with vision-enhanced data
- [ ] **TC4.2**: Report quality comparison → demonstrates improved accuracy vs text-only
- [ ] **TC4.3**: Vision cache validation → cache properly populated with strategic page data
- [ ] **TC4.4**: /ask command integration → uses cached vision data for instant responses
- [ ] **TC4.5**: Fallback functionality → graceful degradation when vision fails
- [ ] **TC4.6**: Session management → proper storage of enhanced data

---

## TECHNICAL IMPLEMENTATION REQUIREMENTS

### Test Infrastructure Setup
**File**: `tests/conftest.py`

```python
import pytest
import tempfile
import shutil
from pathlib import Path

@pytest.fixture
def test_data_dir():
    """Provide test data directory with sample pitch decks"""
    return Path(__file__).parent / "test_data"

@pytest.fixture
def sample_decks(test_data_dir):
    """Provide various sample deck formats for testing"""
    return {
        'standard_20_page': test_data_dir / "standard_pitch_deck_20p.pdf",
        'long_43_page': test_data_dir / "comprehensive_deck_43p.pdf",
        'visual_heavy': test_data_dir / "visual_heavy_deck_25p.pdf",
        'text_heavy': test_data_dir / "text_only_deck_15p.pdf",
        'financial_focus': test_data_dir / "financial_charts_deck_18p.pdf",
        'competition_focus': test_data_dir / "competition_heavy_deck_22p.pdf"
    }

@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client for testing without API calls"""
    # Mock implementation for testing without real API costs

@pytest.fixture
def temporary_session():
    """Provide clean user session for testing"""
    # Setup clean session state for each test
```

### Strategic Page Selection Tests
**File**: `tests/test_strategic_page_selection_integration.py`

```python
class TestStrategicPageSelectionIntegration:
    def test_various_deck_formats(self, sample_decks):
        """Test strategic page selection across different deck formats"""
        selector = StrategicPageSelector()
        
        for deck_name, deck_path in sample_decks.items():
            # Test page selection
            selected_pages = selector.select_strategic_pages(str(deck_path))
            
            # Validate results
            assert len(selected_pages) > 0, f"No pages selected for {deck_name}"
            total_pages = sum(len(pages) for pages in selected_pages.values())
            assert total_pages <= 7, f"Too many pages selected for {deck_name}: {total_pages}"
            assert total_pages >= 3, f"Too few pages selected for {deck_name}: {total_pages}"
            
            # Validate categories
            assert 'financials' in selected_pages or 'market' in selected_pages, \
                f"No business-critical pages selected for {deck_name}"
    
    def test_selection_performance(self, sample_decks):
        """Test selection performance meets <2 second requirement"""
        import time
        selector = StrategicPageSelector()
        
        for deck_name, deck_path in sample_decks.items():
            start_time = time.time()
            selected_pages = selector.select_strategic_pages(str(deck_path))
            selection_time = time.time() - start_time
            
            assert selection_time < 2.0, \
                f"Selection too slow for {deck_name}: {selection_time:.2f}s"
    
    def test_content_accuracy_validation(self, sample_decks):
        """Test that selected pages contain relevant business content"""
        selector = StrategicPageSelector()
        
        # Test financial focus deck
        financial_deck = sample_decks['financial_focus']
        selected_pages = selector.select_strategic_pages(str(financial_deck))
        
        # Should prioritize financial pages
        assert 'financials' in selected_pages, "Financial pages not detected in financial-focus deck"
        assert len(selected_pages['financials']) >= 2, "Insufficient financial pages selected"
```

### SSL Prevention Tests
**File**: `tests/test_ssl_prevention_integration.py`

```python
class TestSSLPreventionIntegration:
    def test_43_page_deck_ssl_prevention(self, sample_decks, mock_openai_client):
        """Test 43-page deck doesn't cause SSL errors"""
        processor = VisionProcessor()
        long_deck = sample_decks['long_43_page']
        
        # This should not cause SSL errors
        result = processor.process_pdf_with_vision(str(long_deck))
        
        # Validate SSL prevention
        assert result['success'] == True, "Processing failed on 43-page deck"
        assert result['processing_summary']['ssl_safe'] == True, "SSL safety not maintained"
        assert result['processing_summary']['pages_processed'] <= 7, "Too many pages processed"
        
        # Should complete within time limit
        assert result['processing_summary']['processing_time'] < 35, "Processing took too long"
    
    def test_concurrent_processing_stability(self, sample_decks, mock_openai_client):
        """Test multiple users don't cause connection pool exhaustion"""
        import threading
        import time
        
        processor = VisionProcessor()
        results = []
        errors = []
        
        def process_deck(deck_path, user_id):
            try:
                result = processor.process_pdf_with_vision(str(deck_path))
                results.append((user_id, result))
            except Exception as e:
                errors.append((user_id, e))
        
        # Simulate 5 concurrent users
        threads = []
        for i in range(5):
            deck_path = sample_decks['standard_20_page']
            thread = threading.Thread(target=process_deck, args=(deck_path, f"user_{i}"))
            threads.append(thread)
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join(timeout=60)  # 60 second timeout
        
        # Validate no SSL errors occurred
        assert len(errors) == 0, f"SSL errors occurred: {errors}"
        assert len(results) == 5, "Not all processing completed"
    
    def test_processing_time_limits(self, sample_decks):
        """Test processing completes within 35-second limit"""
        processor = VisionProcessor()
        
        for deck_name, deck_path in sample_decks.items():
            start_time = time.time()
            result = processor.process_pdf_with_vision(str(deck_path))
            processing_time = time.time() - start_time
            
            assert processing_time < 35, \
                f"Processing too slow for {deck_name}: {processing_time:.2f}s"
```

### Data Quality Tests
**File**: `tests/test_data_quality_integration.py`

```python
class TestDataQualityIntegration:
    def test_financial_data_extraction_accuracy(self, sample_decks):
        """Test accuracy of financial data extraction"""
        processor = VisionProcessor()
        financial_deck = sample_decks['financial_focus']
        
        # Expected financial data (from manual review)
        expected_data = {
            'revenue': ['$2M', '2M', '2.0M'],  # Various formats
            'growth_rate': ['15%', '15', 'fifteen percent'],
            'burn_rate': ['$200K', '200K', '200,000'],
            'runway': ['12 months', '12M', 'one year']
        }
        
        result = processor.process_pdf_with_vision(str(financial_deck))
        
        # Extract financial pages content
        financial_content = []
        for page_num, page_data in result['vision_cache'].items():
            if page_data['category'] == 'financials':
                financial_content.append(page_data['content'].lower())
        
        # Validate financial data extraction
        financial_text = ' '.join(financial_content)
        
        accuracy_score = 0
        total_checks = 0
        
        for metric, possible_values in expected_data.items():
            total_checks += 1
            for value in possible_values:
                if value.lower() in financial_text:
                    accuracy_score += 1
                    break
        
        accuracy_percentage = (accuracy_score / total_checks) * 100
        assert accuracy_percentage >= 90, \
            f"Financial extraction accuracy too low: {accuracy_percentage}%"
    
    def test_competition_detection_accuracy(self, sample_decks):
        """Test accuracy of competitor identification"""
        processor = VisionProcessor()
        competition_deck = sample_decks['competition_focus']
        
        # Expected competitors (from manual review)
        expected_competitors = ['slack', 'microsoft teams', 'zoom', 'discord']
        
        result = processor.process_pdf_with_vision(str(competition_deck))
        
        # Extract competition pages content
        competition_content = []
        for page_num, page_data in result['vision_cache'].items():
            if page_data['category'] == 'competition':
                competition_content.append(page_data['content'].lower())
        
        competition_text = ' '.join(competition_content)
        
        # Count detected competitors
        detected_competitors = 0
        for competitor in expected_competitors:
            if competitor in competition_text:
                detected_competitors += 1
        
        detection_rate = (detected_competitors / len(expected_competitors)) * 100
        assert detection_rate >= 85, \
            f"Competition detection rate too low: {detection_rate}%"
```

### End-to-End Workflow Tests
**File**: `tests/test_end_to_end_workflow.py`

```python
class TestEndToEndWorkflow:
    def test_complete_analyze_workflow(self, sample_decks, temporary_session):
        """Test complete /analyze workflow with vision enhancement"""
        from app import handle_analyze
        from unittest.mock import Mock
        
        # Setup mock Slack objects
        ack = Mock()
        body = {'user_id': 'test_user', 'text': 'https://drive.google.com/test'}
        client = Mock()
        
        # Mock Google Drive extraction
        with patch('app.extract_documents_from_drive') as mock_extract:
            mock_extract.return_value = [{
                'pdf_path': str(sample_decks['standard_20_page']),
                'content': 'Sample content'
            }]
            
            # Execute workflow
            result = handle_analyze(ack, body, client)
            
            # Validate workflow completion
            assert ack.called, "Slack acknowledgment not sent"
            
            # Validate session was updated
            user_sessions = get_user_sessions()
            assert 'test_user' in user_sessions, "User session not created"
            
            session_data = user_sessions['test_user']
            assert 'vision_cache' in session_data, "Vision cache not populated"
            assert 'pdf_path' in session_data, "PDF path not stored"
    
    def test_vision_cache_ask_integration(self, sample_decks, temporary_session):
        """Test /ask command uses vision cache for instant responses"""
        # First, populate cache with /analyze
        # ... (analyze workflow setup)
        
        # Then test /ask with cached question
        from handlers.ask_handler import handle_ask
        
        question = "What is the revenue growth rate?"
        start_time = time.time()
        response = handle_ask('test_user', question)
        response_time = time.time() - start_time
        
        # Should be instant cache hit
        assert response_time < 3.0, f"Cache hit too slow: {response_time:.2f}s"
        assert 'cache_hit' in response, "Cache hit not indicated"
        assert response['cache_hit'] == True, "Should be cache hit"
    
    def test_fallback_functionality(self, sample_decks):
        """Test graceful fallback when vision processing fails"""
        # Simulate vision processing failure
        with patch('handlers.vision_processor.VisionProcessor.process_pdf_with_vision') as mock_vision:
            mock_vision.side_effect = Exception("Simulated vision failure")
            
            # Should fall back to text-only processing
            result = handle_analyze(ack, body, client)
            
            # Should complete successfully despite vision failure
            assert result['status'] == 'success', "Fallback processing failed"
            assert result['processing_mode'] == 'text_only', "Fallback mode not set"
```

---

## TEST DATA REQUIREMENTS

### Sample Pitch Decks
**Directory**: `tests/test_data/`

Required test documents:
- [ ] **standard_pitch_deck_20p.pdf**: Typical 20-page pitch deck with financial charts
- [ ] **comprehensive_deck_43p.pdf**: Large deck for SSL prevention testing
- [ ] **visual_heavy_deck_25p.pdf**: Deck with many charts and graphs
- [ ] **text_only_deck_15p.pdf**: Minimal visual content for fallback testing
- [ ] **financial_charts_deck_18p.pdf**: Focus on revenue, growth, burn rate charts
- [ ] **competition_heavy_deck_22p.pdf**: Multiple competitor slides and positioning

### Expected Results Database
**File**: `tests/test_data/expected_results.json`

```json
{
  "standard_pitch_deck_20p.pdf": {
    "strategic_pages": {
      "financials": [18, 19],
      "competition": [11, 12],
      "market": [8, 9]
    },
    "expected_financial_data": {
      "revenue": "$2M ARR",
      "growth_rate": "15% MoM",
      "burn_rate": "$200K/month"
    },
    "expected_competitors": ["Slack", "Microsoft Teams", "Zoom"]
  }
}
```

---

## PERFORMANCE REQUIREMENTS

| Test Category | Requirement | Test Method |
|---------------|-------------|-------------|
| **Page Selection** | <2 seconds any deck size | Performance timing tests |
| **Vision Processing** | <35 seconds for 7 pages | End-to-end timing tests |
| **SSL Prevention** | 0% SSL errors | Stress testing with large decks |
| **Data Accuracy** | >90% financial extraction | Manual validation comparison |
| **Cache Performance** | <3 seconds cache hits | /ask response timing |

---

## DEFINITION OF DONE

### Test Implementation Complete
- [ ] Strategic page selection test suite implemented
- [ ] SSL prevention validation tests implemented
- [ ] Data quality accuracy tests implemented
- [ ] End-to-end workflow tests implemented
- [ ] Performance tests for all critical paths

### Test Data Prepared
- [ ] 6+ sample pitch decks in various formats
- [ ] Expected results database for validation
- [ ] Mock OpenAI responses for API testing
- [ ] Test fixtures for session management

### Test Execution Validated
- [ ] All tests pass with >95% success rate
- [ ] Performance tests meet timing requirements
- [ ] SSL prevention tests confirm 0% error rate
- [ ] Data accuracy tests achieve >90% accuracy

### CI/CD Integration
- [ ] Tests integrated into continuous integration pipeline
- [ ] Performance benchmarks established
- [ ] Test reporting and metrics collection
- [ ] Automated test execution on code changes

### Documentation Complete
- [ ] Test suite documentation and usage guide
- [ ] Performance baseline documentation
- [ ] Test data management procedures
- [ ] Troubleshooting guide for test failures

---

## DEPENDENCIES

### Blocking Dependencies
- **LV-001**: Strategic Page Selector (component to test)
- **LV-002**: Vision Processor (component to test)
- **LV-003**: Vision Cache (component to test)
- **LV-004**: Bug Fixes (integration to test)

### External Dependencies
- Sample pitch deck documents for testing
- OpenAI API access (or mocking capability)
- Testing infrastructure (pytest, fixtures)
- Performance monitoring tools

---

## RISKS & MITIGATION

### Risk: Test Data Quality
**Probability**: Medium  
**Impact**: High (poor tests don't catch real issues)  
**Mitigation**: Manual validation of test data, multiple deck formats, regular test data updates

### Risk: API Testing Costs
**Probability**: High  
**Impact**: Medium (expensive to run tests)  
**Mitigation**: Mock OpenAI responses, cached test responses, limited real API testing

### Risk: Test Environment Differences
**Probability**: Medium  
**Impact**: Medium (tests pass but production fails)  
**Mitigation**: Production-like test environment, real data validation, staging tests

---

## SUCCESS METRICS

### Test Coverage Metrics
- [ ] >95% code coverage for vision processing components
- [ ] 100% of critical user workflows tested
- [ ] All performance requirements validated by tests
- [ ] All error scenarios covered by tests

### Quality Validation Metrics
- [ ] SSL prevention: 0% errors in testing
- [ ] Data accuracy: >90% in extraction tests
- [ ] Performance: All timing requirements met
- [ ] Regression: 0% breaking changes to existing functionality

### Test Reliability Metrics
- [ ] <1% flaky test rate
- [ ] Test execution time <10 minutes for full suite
- [ ] 100% test automation (no manual testing required)
- [ ] Clear pass/fail criteria for all tests

---

*Story prepared by Bob (Scrum Master) for immediate developer assignment. Comprehensive testing ensures quality and prevents production failures.*