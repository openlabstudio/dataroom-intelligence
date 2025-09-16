# Story LV-003: Vision Cache Infrastructure

**Story ID**: LV-003  
**Epic**: Lazy Vision Document Analysis Enhancement  
**Sprint**: 1  
**Story Points**: 5  
**Priority**: Must Have  
**Type**: Performance Enhancement  

---

## USER STORY

**As a** VC analyst  
**I want** vision results cached in my session  
**So that** follow-up questions are answered instantly without re-processing

## BUSINESS VALUE

**Problem**: Every /ask question requires re-processing visual content, causing 5-7 second delays  
**Solution**: Cache vision results during /analyze for instant /ask responses  
**Value**: 80% of questions answered in 2-3 seconds vs 5-7 seconds, dramatically improved user experience  

**User Experience Impact**: Instant responses enable rapid investment analysis exploration  
**Cost Efficiency**: Eliminates duplicate processing costs for repeated questions  
**System Performance**: Enables sub-3-second /ask responses for cached content  

---

## DETAILED ACCEPTANCE CRITERIA

### AC1: Enhanced Session Structure
```gherkin
GIVEN a user session after /analyze command completion
WHEN vision processing completes successfully
THEN results are stored in user_sessions[user_id]['vision_cache']
AND includes: pages_processed, strategic_selection, data, search_index
AND maintains backward compatibility with existing session structure
```

**Test Cases**:
- [ ] **TC1.1**: Successful vision processing → cache populated with all required fields
- [ ] **TC1.2**: Partial vision processing (3 of 7 pages) → cache contains successful results only
- [ ] **TC1.3**: Vision processing failure → cache initialized as empty with error status
- [ ] **TC1.4**: Existing session data → vision cache added without disrupting other fields

### AC2: Searchable Index Creation
```gherkin
GIVEN vision processing results for multiple page categories
WHEN caching data in session
THEN the system creates searchable index by category and keywords
AND enables fast query matching for /ask commands
AND includes content snippets for quick relevance checking
```

**Test Cases**:
- [ ] **TC2.1**: Financial pages → index contains revenue, ARR, growth, burn rate keywords
- [ ] **TC2.2**: Competition pages → index contains competitor names and positioning keywords
- [ ] **TC2.3**: Market pages → index contains TAM, SAM, market size keywords
- [ ] **TC2.4**: Mixed categories → index properly separates and categorizes all keywords

### AC3: Cache Performance
```gherkin
GIVEN cached vision data in user session
WHEN /ask command queries cache for relevant information
THEN response is provided in <3 seconds for cache hits
AND cache hit rate is >75% for common financial/competition questions
AND cache miss gracefully falls back to on-demand processing
```

**Test Cases**:
- [ ] **TC3.1**: Question about cached financial data → response in <3 seconds
- [ ] **TC3.2**: Question about cached competition → response in <3 seconds
- [ ] **TC3.3**: Question about uncached content → graceful cache miss handling
- [ ] **TC3.4**: Complex question spanning multiple categories → combines cached data effectively

### AC4: Memory Management
```gherkin
GIVEN vision cache data accumulating in sessions
WHEN cache size exceeds 50KB per user OR 24 hours elapsed
THEN the system compacts data (keep summaries, remove full content)
AND automatically expires cache after TTL
AND logs cache management activities for monitoring
```

**Test Cases**:
- [ ] **TC4.1**: Cache under 50KB → maintains full content
- [ ] **TC4.2**: Cache over 50KB → compacts to summaries while preserving searchability
- [ ] **TC4.3**: Cache older than 24 hours → automatically expires and cleans up
- [ ] **TC4.4**: System restart → cache properly initialized for existing sessions

---

## TECHNICAL IMPLEMENTATION REQUIREMENTS

### Enhanced Session Structure
```python
# Enhanced user_sessions structure with vision cache
user_sessions[user_id] = {
    # Existing session data (unchanged)
    'extracted_text': text_data,
    'doc_summary': summary_data,
    'pdf_path': pdf_file_path,
    'timestamp': session_timestamp,
    'company_name': company_name,
    
    # NEW: Vision cache for lazy loading optimization
    'vision_cache': {
        'pages_processed': [18, 19, 11, 12, 8, 14, 3],  # List of processed pages
        'strategic_selection': {
            'financials': [18, 19],
            'competition': [11, 12], 
            'market': [8],
            'traction': [14],
            'team': [3]
        },
        'cached_at': '2025-09-15T10:30:00Z',
        'cache_version': 'lazy-vision-1.0',
        'data': {
            18: {
                'category': 'financials',
                'content': 'Revenue chart shows $2M ARR, 15% MoM growth...',
                'confidence': 0.92,
                'processed_at': '2025-09-15T10:30:15Z',
                'key_phrases': ['revenue', '$2M ARR', '15% growth', 'burn rate'],
                'content_summary': 'Financial metrics and growth data'
            },
            19: {
                'category': 'financials', 
                'content': 'Unit economics: CAC $150, LTV $800, payback 8 months...',
                'confidence': 0.88,
                'processed_at': '2025-09-15T10:30:18Z',
                'key_phrases': ['CAC', 'LTV', 'unit economics', 'payback'],
                'content_summary': 'Unit economics and customer metrics'
            }
            # ... additional pages
        },
        'search_index': {
            'financials': {
                'keywords': ['revenue', 'ARR', 'growth', 'burn', 'CAC', 'LTV'],
                'pages': [18, 19],
                'summary': 'Financial metrics and unit economics data',
                'confidence_avg': 0.90
            },
            'competition': {
                'keywords': ['competitor', 'market share', 'positioning'],
                'pages': [11, 12],
                'summary': 'Competitive landscape and positioning',
                'confidence_avg': 0.85
            }
            # ... additional categories
        },
        'cache_stats': {
            'total_size_kb': 45,
            'hit_count': 0,
            'miss_count': 0,
            'last_accessed': '2025-09-15T10:30:00Z'
        }
    }
}
```

### Cache Management Implementation
**File**: `handlers/vision_cache_manager.py` (New)

```python
class VisionCacheManager:
    """Manages vision result caching for instant /ask responses"""
    
    def __init__(self):
        self.cache_ttl = timedelta(hours=24)  # 24-hour cache lifetime
        self.max_cache_size_kb = 50  # 50KB per user cache limit
        self.compaction_threshold = 0.8  # Compact when 80% of max size
    
    def populate_vision_cache(self, user_id: str, vision_results: Dict):
        """Populate vision cache during /analyze command execution"""
        
    def build_search_index(self, vision_data: Dict) -> Dict:
        """Build searchable index for fast query matching"""
        
    def check_vision_cache_for_answer(self, user_id: str, question: str) -> Dict:
        """Check if question can be answered from cached vision data"""
        
    def analyze_question_intent(self, question: str) -> Dict:
        """Analyze question to determine relevant categories"""
        
    def match_question_to_cache(self, question_analysis: Dict, vision_cache: Dict) -> Dict:
        """Match analyzed question to cached vision content"""
        
    def manage_cache_memory(self):
        """Manage vision cache memory usage and cleanup old data"""
        
    def compact_vision_cache(self, vision_cache: Dict) -> Dict:
        """Compact vision cache by removing less important data"""
        
    def get_cache_performance_metrics(self, user_id: str = None) -> Dict:
        """Get vision cache performance metrics"""
```

### Cache Population During /analyze
```python
def populate_vision_cache_during_analyze(user_id: str, vision_results: Dict):
    """
    Populate vision cache during /analyze command execution
    Stores results from 7 strategic pages for future /ask optimization
    """
    if user_id not in user_sessions:
        logger.error(f"No session found for user {user_id}")
        return
    
    # Initialize vision cache structure
    vision_cache = {
        'pages_processed': [],
        'strategic_selection': vision_results.get('strategic_selection', {}),
        'cached_at': datetime.utcnow().isoformat(),
        'cache_version': 'lazy-vision-1.0',
        'data': {},
        'search_index': {},
        'cache_stats': {
            'total_size_kb': 0,
            'hit_count': 0,
            'miss_count': 0,
            'last_accessed': datetime.utcnow().isoformat()
        }
    }
    
    # Process and store each vision result
    for page_num, page_data in vision_results.get('vision_results', {}).items():
        try:
            # Store core vision data
            vision_cache['data'][page_num] = {
                'category': page_data['category'],
                'content': page_data['vision_data']['content'],
                'confidence': page_data['vision_data']['confidence'],
                'processed_at': datetime.utcnow().isoformat(),
                'key_phrases': self._extract_key_phrases(page_data['vision_data']['content']),
                'content_summary': self._create_content_summary(page_data['vision_data']['content'])
            }
            
            vision_cache['pages_processed'].append(page_num)
            
        except Exception as e:
            logger.warning(f"Failed to cache vision data for page {page_num}: {e}")
    
    # Build search index for fast query matching
    vision_cache['search_index'] = self._build_search_index(vision_cache['data'])
    
    # Calculate cache size
    cache_size_kb = len(str(vision_cache).encode('utf-8')) / 1024
    vision_cache['cache_stats']['total_size_kb'] = round(cache_size_kb, 2)
    
    # Store in user session
    user_sessions[user_id]['vision_cache'] = vision_cache
    
    logger.info(f"Vision cache populated: {len(vision_cache['data'])} pages for user {user_id}")
```

### Fast Query Resolution
```python
def check_vision_cache_for_answer(user_id: str, question: str) -> Dict:
    """
    Check if question can be answered from cached vision data
    Returns cache hit with instant data or cache miss requiring processing
    """
    if user_id not in user_sessions:
        return {'cache_hit': False, 'reason': 'no_session'}
    
    vision_cache = user_sessions[user_id].get('vision_cache', {})
    if not vision_cache.get('data'):
        return {'cache_hit': False, 'reason': 'no_vision_cache'}
    
    # Update cache access stats
    vision_cache['cache_stats']['last_accessed'] = datetime.utcnow().isoformat()
    
    # Analyze question to determine relevant categories
    question_analysis = self._analyze_question_intent(question)
    
    # Check if we have cached data for this question type
    cache_result = self._match_question_to_cache(question_analysis, vision_cache)
    
    if cache_result['match_found']:
        # Update hit stats
        vision_cache['cache_stats']['hit_count'] += 1
        
        return {
            'cache_hit': True,
            'relevant_pages': cache_result['relevant_pages'],
            'cached_content': cache_result['content'],
            'confidence': cache_result['confidence'],
            'response_time_estimate': '2-3 seconds',
            'cache_source': 'vision_analysis'
        }
    else:
        # Update miss stats
        vision_cache['cache_stats']['miss_count'] += 1
        
        return {
            'cache_hit': False,
            'reason': 'content_not_cached',
            'suggested_pages': cache_result['suggested_pages'],
            'requires_processing': True,
            'response_time_estimate': '5-7 seconds'
        }
```

### Integration Points
**Files to modify**:
- `app.py` - Call cache population during /analyze
- `handlers/ask_handler.py` - Use cache for instant responses
- `handlers/enhanced_session_manager.py` - Include cache in session management

---

## TESTING REQUIREMENTS

### Unit Tests
**File**: `tests/test_vision_cache_manager.py`

```python
class TestVisionCacheManager:
    def test_cache_population(self):
        """Test vision cache population during /analyze"""
        
    def test_search_index_creation(self):
        """Test searchable index building"""
        
    def test_cache_hit_performance(self):
        """Test cache hit response time <3 seconds"""
        
    def test_memory_management(self):
        """Test cache compaction and TTL expiration"""
        
    def test_question_intent_analysis(self):
        """Test question categorization accuracy"""
        
    def test_cache_miss_handling(self):
        """Test graceful cache miss behavior"""
```

### Integration Tests
**File**: `tests/test_vision_cache_integration.py`

```python
class TestVisionCacheIntegration:
    def test_analyze_to_ask_workflow(self):
        """Test /analyze populates cache, /ask uses cache"""
        
    def test_cache_performance_targets(self):
        """Test 80% cache hit rate for common questions"""
        
    def test_session_compatibility(self):
        """Test backward compatibility with existing sessions"""
        
    def test_concurrent_cache_access(self):
        """Test multiple users accessing cache simultaneously"""
```

### Performance Tests
```python
class TestCachePerformance:
    def test_cache_hit_response_time(self):
        """Test cached responses <3 seconds"""
        
    def test_cache_memory_usage(self):
        """Test cache stays under 50KB per user"""
        
    def test_cache_hit_rate(self):
        """Test >75% hit rate for common questions"""
```

---

## PERFORMANCE REQUIREMENTS

| Metric | Requirement | Test Method |
|--------|-------------|-------------|
| **Cache Hit Response** | <3 seconds | Time /ask responses for cached content |
| **Cache Hit Rate** | >75% for common questions | Statistical analysis of question patterns |
| **Memory Usage** | <50KB per user cache | Memory measurement during cache operations |
| **Cache Population Time** | <2 seconds addition to /analyze | Timing comparison with/without caching |

---

## DEFINITION OF DONE

### Implementation Complete
- [ ] Enhanced session structure with vision_cache field
- [ ] VisionCacheManager class implemented
- [ ] Cache population during /analyze command
- [ ] Search index generation for fast queries
- [ ] Question intent analysis for cache matching
- [ ] Memory management with TTL and size limits

### Performance Validated
- [ ] Cache hit responses consistently <3 seconds
- [ ] Cache hit rate >75% for financial/competition questions
- [ ] Memory usage stays under 50KB per user
- [ ] No performance regression in /analyze command

### Integration Complete
- [ ] Integration with /analyze command for cache population
- [ ] Integration with /ask command for cache queries
- [ ] Backward compatibility with existing session structure
- [ ] Error handling for cache failures

### Testing Complete
- [ ] Unit tests for cache operations (>90% coverage)
- [ ] Integration tests for analyze→ask workflow
- [ ] Performance tests validate timing requirements
- [ ] Memory management tests validate cleanup

### Documentation Complete
- [ ] Cache architecture documentation
- [ ] Performance characteristics documented
- [ ] Troubleshooting guide for cache issues
- [ ] Memory management procedures

---

## DEPENDENCIES

### Blocking Dependencies
- **LV-002**: Vision Processor (provides vision results to cache)

### Consuming Dependencies
- **LV-006**: /ask Enhancement will use this cache for instant responses

### External Dependencies
- Existing session management system
- /ask command infrastructure (existing)
- Memory monitoring capabilities

---

## RISKS & MITIGATION

### Risk: Memory Growth
**Probability**: Medium  
**Impact**: Medium (system performance degradation)  
**Mitigation**: TTL-based expiration, size limits, compaction algorithms, monitoring

### Risk: Cache Inconsistency
**Probability**: Low  
**Impact**: Medium (wrong answers from stale cache)  
**Mitigation**: Cache versioning, TTL expiration, cache invalidation on new analysis

### Risk: Cache Miss Performance
**Probability**: Medium  
**Impact**: Low (falls back to processing)  
**Mitigation**: Comprehensive keyword indexing, question analysis improvement

---

## SUCCESS METRICS

### Performance Metrics
- [ ] 80% of /ask questions answered in <3 seconds (cache hits)
- [ ] 20% of /ask questions processed on-demand in <7 seconds (cache misses)
- [ ] Cache hit rate >75% for financial and competition questions
- [ ] Memory usage <50KB per active user session

### User Experience Metrics
- [ ] Dramatic improvement in /ask response time
- [ ] Enables rapid investment analysis exploration
- [ ] Eliminates frustrating re-processing delays
- [ ] Supports complex multi-question analysis workflows

### Technical Metrics
- [ ] Zero cache-related system crashes
- [ ] Proper memory cleanup and TTL expiration
- [ ] Cache population adds <2 seconds to /analyze
- [ ] Backward compatibility maintained

---

*Story prepared by Bob (Scrum Master) for immediate developer assignment. Enables instant /ask responses for superior user experience.*