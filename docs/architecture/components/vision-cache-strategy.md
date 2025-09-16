# Vision Cache Strategy Architecture

**Component**: Vision Result Caching System  
**Location**: Enhanced Session Management (`app.py`, session handling)  
**Responsibility**: Optimize /ask performance through strategic vision result caching  

## Component Overview

The Vision Cache Strategy implements intelligent caching of vision processing results to enable instant responses for /ask queries. By storing processed vision data in user sessions, 80% of questions can be answered in 2-3 seconds using cached results, while new questions requiring vision processing complete in 5-7 seconds.

### Core Responsibilities

**Primary Functions**
- **Vision Result Storage**: Cache vision data from 7 strategic pages in user_sessions
- **Query Optimization**: Provide instant answers for questions about cached visual content
- **On-Demand Processing**: Process 1-3 additional pages for uncached questions
- **Cache Management**: Handle cache expiration, memory management, and cleanup

**Integration Points**
- **Vision Processor**: Receives and stores vision processing results
- **Ask Command Handler**: Provides cached data for instant question answering
- **Session Manager**: Integrates with existing user session structure
- **Memory Management**: Optional Redis integration for persistence

## Architectural Design

### Enhanced Session Structure

```python
# Enhanced user_sessions structure with vision cache
user_sessions[user_id] = {
    # Existing session data (unchanged)
    'extracted_text': text_data,
    'doc_summary': summary_data,
    'pdf_path': pdf_file_path,
    'timestamp': session_timestamp,
    
    # NEW: Vision cache for lazy loading
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
        'data': {
            18: {
                'category': 'financials',
                'content': 'Revenue chart shows $2M ARR, 15% MoM growth...',
                'confidence': 0.92,
                'processed_at': '2025-09-15T10:30:15Z',
                'key_phrases': ['revenue', '$2M ARR', '15% growth', 'burn rate']
            },
            19: {
                'category': 'financials', 
                'content': 'Unit economics: CAC $150, LTV $800, payback 8 months...',
                'confidence': 0.88,
                'processed_at': '2025-09-15T10:30:18Z',
                'key_phrases': ['CAC', 'LTV', 'unit economics', 'payback']
            },
            # ... additional pages
        },
        'search_index': {
            'financials': {
                'keywords': ['revenue', 'ARR', 'growth', 'burn', 'CAC', 'LTV'],
                'pages': [18, 19],
                'summary': 'Financial metrics and unit economics data'
            },
            'competition': {
                'keywords': ['competitor', 'market share', 'positioning'],
                'pages': [11, 12],
                'summary': 'Competitive landscape and positioning'
            }
            # ... additional categories
        }
    },
    
    # NEW: On-demand processing queue
    'vision_queue': {
        'pending_pages': [],  # Pages identified but not yet processed
        'processing_requests': []  # Specific /ask requests requiring vision
    }
}
```

### Cache Population Strategy

**Stage 1: Initial Cache Population (/analyze command)**
```python
def populate_vision_cache_during_analyze(user_id: str, pdf_path: str, vision_results: Dict):
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
        'data': {},
        'search_index': {}
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
                'key_phrases': extract_key_phrases(page_data['vision_data']['content'])
            }
            
            vision_cache['pages_processed'].append(page_num)
            
        except Exception as e:
            logger.warning(f"Failed to cache vision data for page {page_num}: {e}")
    
    # Build search index for fast query matching
    vision_cache['search_index'] = build_search_index(vision_cache['data'])
    
    # Store in user session
    user_sessions[user_id]['vision_cache'] = vision_cache
    
    logger.info(f"Vision cache populated: {len(vision_cache['data'])} pages for user {user_id}")

def build_search_index(vision_data: Dict) -> Dict:
    """Build searchable index for fast question matching"""
    
    search_index = {}
    
    # Group by category
    categories = {}
    for page_num, page_data in vision_data.items():
        category = page_data['category']
        if category not in categories:
            categories[category] = {
                'keywords': set(),
                'pages': [],
                'content_snippets': []
            }
        
        categories[category]['pages'].append(page_num)
        categories[category]['keywords'].update(page_data['key_phrases'])
        categories[category]['content_snippets'].append(page_data['content'][:200])
    
    # Convert to searchable format
    for category, data in categories.items():
        search_index[category] = {
            'keywords': list(data['keywords']),
            'pages': data['pages'],
            'summary': f"{category.title()} data from {len(data['pages'])} pages"
        }
    
    return search_index
```

### Cache Query Optimization

**Stage 2: Fast Query Resolution (/ask command)**
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
    
    # Analyze question to determine relevant categories
    question_analysis = analyze_question_intent(question)
    
    # Check if we have cached data for this question type
    cache_result = match_question_to_cache(question_analysis, vision_cache)
    
    if cache_result['match_found']:
        return {
            'cache_hit': True,
            'relevant_pages': cache_result['relevant_pages'],
            'cached_content': cache_result['content'],
            'confidence': cache_result['confidence'],
            'response_time_estimate': '2-3 seconds'
        }
    else:
        return {
            'cache_hit': False,
            'reason': 'content_not_cached',
            'suggested_pages': cache_result['suggested_pages'],
            'requires_processing': True,
            'response_time_estimate': '5-7 seconds'
        }

def analyze_question_intent(question: str) -> Dict:
    """Analyze question to determine what type of content is needed"""
    
    question_lower = question.lower()
    
    intent_patterns = {
        'financials': [
            'revenue', 'income', 'sales', 'arr', 'mrr', 'growth rate',
            'burn rate', 'runway', 'cash', 'funding', 'valuation',
            'cac', 'ltv', 'unit economics', 'margins', 'profitability'
        ],
        'competition': [
            'competitor', 'competitive', 'market share', 'vs', 
            'alternative', 'differentiation', 'positioning', 'landscape'
        ],
        'market': [
            'market size', 'tam', 'sam', 'som', 'opportunity',
            'addressable market', 'billion', 'million', 'market analysis'
        ],
        'traction': [
            'users', 'customers', 'growth', 'metrics', 'kpis',
            'retention', 'churn', 'engagement', 'traction'
        ],
        'team': [
            'founder', 'ceo', 'cto', 'team', 'leadership', 
            'experience', 'background', 'advisors'
        ]
    }
    
    # Score question against each category
    category_scores = {}
    for category, keywords in intent_patterns.items():
        score = sum(1 for keyword in keywords if keyword in question_lower)
        if score > 0:
            category_scores[category] = score
    
    # Determine primary intent
    if category_scores:
        primary_category = max(category_scores.keys(), key=lambda k: category_scores[k])
        return {
            'primary_category': primary_category,
            'category_scores': category_scores,
            'question_type': 'specific' if len(category_scores) == 1 else 'broad'
        }
    else:
        return {
            'primary_category': 'general',
            'category_scores': {},
            'question_type': 'general'
        }

def match_question_to_cache(question_analysis: Dict, vision_cache: Dict) -> Dict:
    """Match analyzed question to cached vision content"""
    
    primary_category = question_analysis['primary_category']
    
    # Check if we have cached data for this category
    if primary_category in vision_cache['search_index']:
        category_data = vision_cache['search_index'][primary_category]
        relevant_pages = category_data['pages']
        
        # Gather content from relevant cached pages
        cached_content = []
        total_confidence = 0
        
        for page_num in relevant_pages:
            if page_num in vision_cache['data']:
                page_data = vision_cache['data'][page_num]
                cached_content.append({
                    'page': page_num,
                    'category': page_data['category'],
                    'content': page_data['content']
                })
                total_confidence += page_data['confidence']
        
        if cached_content:
            avg_confidence = total_confidence / len(cached_content)
            return {
                'match_found': True,
                'relevant_pages': relevant_pages,
                'content': cached_content,
                'confidence': avg_confidence
            }
    
    # No cache match found
    return {
        'match_found': False,
        'suggested_pages': [],  # Could suggest pages to process
        'reason': f'No cached data for {primary_category} questions'
    }
```

### On-Demand Processing Strategy

**Stage 3: Smart On-Demand Processing**
```python
def process_on_demand_for_question(user_id: str, question: str, pdf_path: str) -> Dict:
    """
    Process 1-3 additional pages on-demand for specific questions
    Only called when cache miss occurs
    """
    try:
        # Analyze question to find relevant pages not yet processed
        question_analysis = analyze_question_intent(question)
        vision_cache = user_sessions[user_id].get('vision_cache', {})
        processed_pages = vision_cache.get('pages_processed', [])
        
        # Find pages that might contain relevant content
        candidate_pages = find_pages_for_question(
            pdf_path, question_analysis, exclude_pages=processed_pages
        )
        
        # Limit to 3 pages maximum for on-demand processing
        pages_to_process = candidate_pages[:3]
        
        if not pages_to_process:
            return {
                'success': False,
                'reason': 'no_additional_pages_found',
                'cached_response': True
            }
        
        logger.info(f"Processing {len(pages_to_process)} additional pages on-demand for question")
        
        # Process additional pages with vision
        vision_processor = LazyVisionProcessor()
        on_demand_results = {}
        
        for page_num in pages_to_process:
            try:
                category = question_analysis['primary_category']
                vision_result = vision_processor._process_single_page_strategic(
                    pdf_path, page_num, category
                )
                
                on_demand_results[page_num] = {
                    'category': category,
                    'content': vision_result['content'],
                    'confidence': vision_result['confidence'],
                    'processed_at': datetime.utcnow().isoformat(),
                    'key_phrases': extract_key_phrases(vision_result['content'])
                }
                
            except Exception as e:
                logger.error(f"On-demand processing failed for page {page_num}: {e}")
                continue
        
        # Update vision cache with new results
        if on_demand_results:
            vision_cache['data'].update(on_demand_results)
            vision_cache['pages_processed'].extend(on_demand_results.keys())
            vision_cache['search_index'] = build_search_index(vision_cache['data'])
            user_sessions[user_id]['vision_cache'] = vision_cache
        
        return {
            'success': True,
            'pages_processed': list(on_demand_results.keys()),
            'new_content': on_demand_results,
            'total_cached_pages': len(vision_cache['data'])
        }
        
    except Exception as e:
        logger.error(f"On-demand processing failed: {e}")
        return {
            'success': False,
            'reason': str(e),
            'fallback': 'text_only_response'
        }

def find_pages_for_question(pdf_path: str, question_analysis: Dict, exclude_pages: List[int]) -> List[int]:
    """Find pages that might contain relevant content for the specific question"""
    
    # Use strategic page selector to find additional relevant pages
    page_selector = StrategicPageSelector()
    
    # Get full document analysis (not just strategic pages)
    all_page_scores = page_selector._analyze_all_pages_for_content(pdf_path)
    
    primary_category = question_analysis['primary_category']
    
    # Find pages with content matching the question category
    relevant_pages = []
    for page_data in all_page_scores:
        page_num = page_data['page_number']
        
        # Skip already processed pages
        if page_num in exclude_pages:
            continue
        
        # Check if page has relevant content
        if primary_category in page_data['category_scores']:
            score = page_data['category_scores'][primary_category]['weighted_score']
            if score > 0.5:  # Threshold for relevance
                relevant_pages.append({
                    'page_num': page_num,
                    'score': score
                })
    
    # Sort by relevance score and return page numbers
    relevant_pages.sort(key=lambda x: x['score'], reverse=True)
    return [p['page_num'] for p in relevant_pages]
```

### Cache Management and Performance

**Memory Management and Cleanup**
```python
def manage_vision_cache_memory():
    """Manage vision cache memory usage and cleanup old data"""
    
    current_time = datetime.utcnow()
    cache_ttl = timedelta(hours=24)  # 24-hour cache lifetime
    
    for user_id in list(user_sessions.keys()):
        try:
            session = user_sessions[user_id]
            vision_cache = session.get('vision_cache', {})
            
            if not vision_cache.get('cached_at'):
                continue
            
            cached_at = datetime.fromisoformat(vision_cache['cached_at'].replace('Z', '+00:00'))
            
            # Clean up expired cache
            if current_time - cached_at > cache_ttl:
                logger.info(f"Cleaning up expired vision cache for user {user_id}")
                del session['vision_cache']
                continue
            
            # Clean up large cache data if memory pressure
            vision_data_size = len(str(vision_cache.get('data', {})))
            if vision_data_size > 50000:  # 50KB threshold
                logger.info(f"Compacting large vision cache for user {user_id}")
                session['vision_cache'] = compact_vision_cache(vision_cache)
                
        except Exception as e:
            logger.error(f"Cache cleanup error for user {user_id}: {e}")

def compact_vision_cache(vision_cache: Dict) -> Dict:
    """Compact vision cache by removing less important data"""
    
    compacted = {
        'pages_processed': vision_cache['pages_processed'],
        'strategic_selection': vision_cache['strategic_selection'],
        'cached_at': vision_cache['cached_at'],
        'data': {},
        'search_index': vision_cache['search_index']
    }
    
    # Keep only high-confidence, recent data
    for page_num, page_data in vision_cache['data'].items():
        if page_data['confidence'] > 0.8:  # Keep high-confidence results
            # Keep summary instead of full content
            compacted['data'][page_num] = {
                'category': page_data['category'],
                'content': page_data['content'][:500] + '...' if len(page_data['content']) > 500 else page_data['content'],
                'confidence': page_data['confidence'],
                'processed_at': page_data['processed_at'],
                'key_phrases': page_data['key_phrases'][:10]  # Limit key phrases
            }
    
    return compacted
```

### Cache Performance Metrics

**Performance Monitoring**
```python
def get_cache_performance_metrics(user_id: str = None) -> Dict:
    """Get vision cache performance metrics"""
    
    if user_id:
        # Single user metrics
        session = user_sessions.get(user_id, {})
        vision_cache = session.get('vision_cache', {})
        
        return {
            'user_id': user_id,
            'pages_cached': len(vision_cache.get('data', {})),
            'categories_covered': list(vision_cache.get('search_index', {}).keys()),
            'cache_age_hours': calculate_cache_age_hours(vision_cache.get('cached_at')),
            'estimated_response_speedup': calculate_response_speedup(vision_cache)
        }
    else:
        # System-wide metrics
        total_sessions_with_cache = 0
        total_cached_pages = 0
        cache_hit_potential = 0
        
        for session in user_sessions.values():
            vision_cache = session.get('vision_cache', {})
            if vision_cache.get('data'):
                total_sessions_with_cache += 1
                total_cached_pages += len(vision_cache['data'])
                cache_hit_potential += estimate_cache_hit_rate(vision_cache)
        
        return {
            'total_sessions_with_cache': total_sessions_with_cache,
            'average_pages_per_cache': total_cached_pages / max(total_sessions_with_cache, 1),
            'estimated_system_cache_hit_rate': cache_hit_potential / max(total_sessions_with_cache, 1),
            'memory_savings_estimate': f"{total_cached_pages * 0.5:.1f}MB saved from caching"
        }

def calculate_response_speedup(vision_cache: Dict) -> str:
    """Calculate estimated response time improvement from caching"""
    
    cached_pages = len(vision_cache.get('data', {}))
    if cached_pages == 0:
        return "No speedup (no cache)"
    
    # Estimate: Each cached page saves ~5 seconds of processing
    time_saved = cached_pages * 5
    return f"{time_saved}s saved for cache hits, 2-3s response vs 5-7s processing"
```

---

*This Vision Cache Strategy architecture enables instant responses for 80% of /ask questions while maintaining cost efficiency through strategic caching and on-demand processing for uncached queries.*