# Session Management Enhancement Architecture

**Component**: Enhanced Session Management System  
**Location**: `utils/session_manager.py`  
**Responsibility**: Unified session data with vision extraction and optional persistence  

## Component Overview

The Enhanced Session Management System extends the existing in-memory session structure to support hybrid text + vision extraction results while maintaining backward compatibility and adding optional Redis persistence for improved reliability.

### Enhancement Philosophy

**Backward Compatible Extension**
- **Preserve**: All existing session access patterns and data structures
- **Extend**: Session schema to include vision extraction results and processing metadata
- **Enhance**: Cross-command data sharing with unified extraction results
- **Add**: Optional Redis persistence without breaking existing in-memory functionality

**Data Structure Evolution**
```python
# Current: Simple session structure
user_sessions[user_id] = {
    'processed_documents': [...],
    'document_summary': {...}
}

# Enhanced: Unified extraction with vision data
user_sessions[user_id] = {
    # EXISTING structure preserved
    'processed_documents': [...],
    'document_summary': {...},
    
    # NEW vision-enhanced data
    'extraction_results': {...},
    'processing_metadata': {...}
}
```

## Architectural Design

### Enhanced Session Manager Structure

```python
# utils/session_manager.py
class EnhancedSessionManager:
    """Enhanced session management with vision data support and optional persistence"""
    
    def __init__(self):
        # Primary storage (existing)
        self.memory_sessions = {}
        
        # Optional persistence layer
        self.redis_client = None
        self.redis_enabled = False
        
        # Session configuration
        self.session_ttl_hours = int(os.getenv('SESSION_TTL_HOURS', '24'))
        self.max_memory_sessions = int(os.getenv('MAX_MEMORY_SESSIONS', '1000'))
        
        # Initialize Redis if available and configured
        self._initialize_redis_if_available()
        
        # Session metrics and monitoring
        self.session_metrics = SessionMetrics()
```

### Unified Session Data Schema

**Enhanced Session Structure**
```python
class EnhancedSessionData:
    """Comprehensive session data structure supporting all extraction types"""
    
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.created_at = datetime.utcnow()
        self.last_accessed = datetime.utcnow()
        
        # EXISTING data structures (preserved for backward compatibility)
        self.processed_documents = []
        self.document_summary = {}
        self.market_research_data = {}
        
        # NEW enhanced extraction data
        self.extraction_results = {}
        self.processing_metadata = {}
        self.cross_document_insights = {}
        
    def to_dict(self) -> dict:
        """Convert to dictionary for storage and serialization"""
        return {
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat(),
            'last_accessed': self.last_accessed.isoformat(),
            
            # Existing session data (backward compatible)
            'processed_documents': self.processed_documents,
            'document_summary': self.document_summary,
            'market_research_data': self.market_research_data,
            
            # Enhanced extraction data
            'extraction_results': self.extraction_results,
            'processing_metadata': self.processing_metadata,
            'cross_document_insights': self.cross_document_insights
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'EnhancedSessionData':
        """Create session from dictionary (for Redis persistence)"""
        session = cls(data['user_id'])
        session.created_at = datetime.fromisoformat(data['created_at'])
        session.last_accessed = datetime.fromisoformat(data['last_accessed'])
        
        # Restore existing data
        session.processed_documents = data.get('processed_documents', [])
        session.document_summary = data.get('document_summary', {})
        session.market_research_data = data.get('market_research_data', {})
        
        # Restore enhanced data
        session.extraction_results = data.get('extraction_results', {})
        session.processing_metadata = data.get('processing_metadata', {})
        session.cross_document_insights = data.get('cross_document_insights', {})
        
        return session
```

**Document Extraction Result Schema**
```python
@dataclass
class DocumentExtractionResult:
    """Comprehensive extraction result supporting text and vision data"""
    
    document_id: str
    filename: str
    extraction_method: str  # 'text_only', 'vision_enhanced', 'hybrid_text_vision'
    
    # Text extraction data
    text_content: str
    text_extraction_metadata: dict
    
    # Vision extraction data (optional)
    vision_extractions: List[dict] = None
    vision_processing_summary: dict = None
    
    # Combined analysis
    enhanced_content: str = None
    comprehensive_insights: List[str] = None
    confidence_scores: dict = None
    
    # Processing metadata
    processing_time: float = 0.0
    processing_cost: float = 0.0
    processing_strategy: str = 'default'
    
    # Quality metrics
    extraction_quality_score: float = 0.0
    completeness_score: float = 0.0
    
    def get_all_content(self) -> str:
        """Get comprehensive content combining text and vision"""
        if self.enhanced_content:
            return self.enhanced_content
        elif self.vision_extractions:
            vision_content = self._format_vision_content()
            return f"{self.text_content}\n\n{vision_content}"
        else:
            return self.text_content
    
    def get_extraction_summary(self) -> dict:
        """Get summary of extraction results for command usage"""
        return {
            'extraction_method': self.extraction_method,
            'has_vision_data': bool(self.vision_extractions),
            'content_length': len(self.get_all_content()),
            'quality_score': self.extraction_quality_score,
            'processing_cost': self.processing_cost,
            'insights_count': len(self.comprehensive_insights) if self.comprehensive_insights else 0
        }
```

### Session Storage and Retrieval

**Hybrid Persistence Strategy**
```python
def store_enhanced_session(self, user_id: str, session_data: dict):
    """Store session with enhanced data and optional Redis persistence"""
    
    try:
        # Create enhanced session object
        enhanced_session = self._create_enhanced_session(user_id, session_data)
        
        # Primary storage: Memory (fast access)
        self.memory_sessions[user_id] = enhanced_session
        
        # Update session metrics
        self.session_metrics.record_session_update(user_id, enhanced_session)
        
        # Secondary storage: Redis (persistence)
        if self.redis_enabled:
            self._store_session_in_redis(user_id, enhanced_session)
        
        # Memory management
        self._manage_memory_sessions()
        
        logger.debug(f"Enhanced session stored for user {user_id}")
        
    except Exception as e:
        logger.error(f"Failed to store enhanced session for {user_id}: {e}")
        # Fallback to basic session storage
        self._store_basic_session_fallback(user_id, session_data)

def get_enhanced_session(self, user_id: str) -> Optional[EnhancedSessionData]:
    """Retrieve session with fallback strategy"""
    
    # Primary: Check memory first (fastest)
    if user_id in self.memory_sessions:
        session = self.memory_sessions[user_id]
        session.last_accessed = datetime.utcnow()
        return session
    
    # Secondary: Check Redis if available
    if self.redis_enabled:
        session = self._retrieve_session_from_redis(user_id)
        if session:
            # Restore to memory for fast subsequent access
            self.memory_sessions[user_id] = session
            session.last_accessed = datetime.utcnow()
            return session
    
    # No session found
    return None
```

**Redis Integration Implementation**
```python
def _initialize_redis_if_available(self):
    """Initialize Redis connection if available and configured"""
    
    redis_url = os.getenv('REDIS_URL')
    if not redis_url:
        logger.info("Redis not configured, using memory-only session storage")
        return
    
    try:
        import redis
        self.redis_client = redis.from_url(
            redis_url,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5,
            retry_on_timeout=True
        )
        
        # Test connection
        self.redis_client.ping()
        self.redis_enabled = True
        logger.info("Redis session persistence enabled")
        
    except ImportError:
        logger.warning("Redis package not available, using memory-only storage")
    except Exception as e:
        logger.warning(f"Redis connection failed, using memory-only storage: {e}")

def _store_session_in_redis(self, user_id: str, session: EnhancedSessionData):
    """Store session in Redis with TTL"""
    
    try:
        session_key = f"session:{user_id}"
        session_data = json.dumps(session.to_dict(), default=str)
        
        # Store with TTL
        ttl_seconds = self.session_ttl_hours * 3600
        self.redis_client.setex(session_key, ttl_seconds, session_data)
        
        logger.debug(f"Session stored in Redis for user {user_id}")
        
    except Exception as e:
        logger.warning(f"Redis session storage failed for {user_id}: {e}")

def _retrieve_session_from_redis(self, user_id: str) -> Optional[EnhancedSessionData]:
    """Retrieve session from Redis"""
    
    try:
        session_key = f"session:{user_id}"
        session_data = self.redis_client.get(session_key)
        
        if session_data:
            session_dict = json.loads(session_data)
            session = EnhancedSessionData.from_dict(session_dict)
            logger.debug(f"Session retrieved from Redis for user {user_id}")
            return session
        
    except Exception as e:
        logger.warning(f"Redis session retrieval failed for {user_id}: {e}")
    
    return None
```

### Cross-Command Data Access

**Unified Data Access for All Commands**
```python
def get_comprehensive_analysis_data(self, user_id: str) -> dict:
    """Get comprehensive analysis data for any command"""
    
    session = self.get_enhanced_session(user_id)
    if not session:
        return {'error': 'No session found for user'}
    
    # Compile comprehensive data for command usage
    analysis_data = {
        'user_id': user_id,
        'session_created': session.created_at.isoformat(),
        'last_accessed': session.last_accessed.isoformat(),
        
        # Document extraction results
        'documents': self._format_document_data(session.extraction_results),
        'document_summary': session.document_summary,
        
        # Vision analysis data
        'vision_insights': self._extract_vision_insights(session.extraction_results),
        'processing_summary': self._compile_processing_summary(session.processing_metadata),
        
        # Market research data
        'market_research': session.market_research_data,
        
        # Cross-document insights
        'cross_document_insights': session.cross_document_insights,
        
        # Session quality metrics
        'session_quality': self._assess_session_quality(session)
    }
    
    return analysis_data

def get_vision_specific_data(self, user_id: str) -> dict:
    """Get vision-specific data for commands that need visual analysis"""
    
    session = self.get_enhanced_session(user_id)
    if not session:
        return {'has_vision_data': False, 'vision_insights': []}
    
    vision_data = {
        'has_vision_data': self._has_vision_extractions(session),
        'vision_insights': [],
        'visual_elements_summary': {},
        'cost_summary': {'total_cost': 0.0, 'pages_processed': 0}
    }
    
    # Extract vision insights from all documents
    for doc_id, extraction_result in session.extraction_results.items():
        if extraction_result.get('vision_extractions'):
            vision_data['vision_insights'].extend(
                self._format_vision_insights(extraction_result['vision_extractions'])
            )
            
            # Update cost summary
            processing_summary = extraction_result.get('vision_processing_summary', {})
            vision_data['cost_summary']['total_cost'] += processing_summary.get('total_estimated_cost', 0)
            vision_data['cost_summary']['pages_processed'] += processing_summary.get('pages_analyzed', 0)
    
    return vision_data
```

### Session Quality and Optimization

**Session Quality Assessment**
```python
def _assess_session_quality(self, session: EnhancedSessionData) -> dict:
    """Assess session data quality for optimization"""
    
    quality_metrics = {
        'document_count': len(session.extraction_results),
        'has_enhanced_extraction': any(
            result.get('extraction_method') in ['vision_enhanced', 'hybrid_text_vision']
            for result in session.extraction_results.values()
        ),
        'average_extraction_quality': self._calculate_average_extraction_quality(session),
        'total_processing_cost': self._calculate_total_processing_cost(session),
        'session_completeness': self._assess_session_completeness(session)
    }
    
    # Overall quality score
    quality_score = (
        min(1.0, quality_metrics['document_count'] / 5) * 0.2 +  # Document completeness
        (1.0 if quality_metrics['has_enhanced_extraction'] else 0.5) * 0.3 +  # Enhancement usage
        quality_metrics['average_extraction_quality'] * 0.3 +  # Extraction quality
        quality_metrics['session_completeness'] * 0.2  # Data completeness
    )
    
    quality_metrics['overall_quality_score'] = quality_score
    
    return quality_metrics

def _calculate_average_extraction_quality(self, session: EnhancedSessionData) -> float:
    """Calculate average extraction quality across all documents"""
    
    if not session.extraction_results:
        return 0.0
    
    quality_scores = []
    for extraction_result in session.extraction_results.values():
        quality_score = extraction_result.get('extraction_quality_score', 0.7)  # Default reasonable score
        quality_scores.append(quality_score)
    
    return sum(quality_scores) / len(quality_scores) if quality_scores else 0.0
```

### Memory Management and Performance

**Session Lifecycle Management**
```python
def _manage_memory_sessions(self):
    """Manage memory usage by cleaning up old sessions"""
    
    if len(self.memory_sessions) <= self.max_memory_sessions:
        return
    
    # Sort sessions by last access time
    session_items = [
        (user_id, session) 
        for user_id, session in self.memory_sessions.items()
    ]
    session_items.sort(key=lambda x: x[1].last_accessed)
    
    # Remove oldest sessions
    sessions_to_remove = len(self.memory_sessions) - self.max_memory_sessions
    for i in range(sessions_to_remove):
        user_id, session = session_items[i]
        
        # Store in Redis before removing from memory (if Redis available)
        if self.redis_enabled:
            self._store_session_in_redis(user_id, session)
        
        del self.memory_sessions[user_id]
        logger.debug(f"Removed session from memory for user {user_id}")

class SessionMetrics:
    """Monitor session usage and performance"""
    
    def __init__(self):
        self.session_stats = {
            'total_sessions_created': 0,
            'sessions_with_vision_data': 0,
            'total_processing_cost': 0.0,
            'average_session_size': 0.0
        }
    
    def record_session_update(self, user_id: str, session: EnhancedSessionData):
        """Record session metrics for monitoring"""
        
        self.session_stats['total_sessions_created'] += 1
        
        if self._session_has_vision_data(session):
            self.session_stats['sessions_with_vision_data'] += 1
        
        processing_cost = self._calculate_session_processing_cost(session)
        self.session_stats['total_processing_cost'] += processing_cost
        
        session_size = self._estimate_session_size(session)
        self.session_stats['average_session_size'] = (
            (self.session_stats['average_session_size'] * (self.session_stats['total_sessions_created'] - 1) + session_size) /
            self.session_stats['total_sessions_created']
        )
```

---

*This Enhanced Session Management architecture provides unified data access for all commands while maintaining backward compatibility and adding optional persistence, enabling comprehensive document analysis across the entire DataRoom Intelligence system.*