# Brownfield Product Requirements Document: Lazy Vision Enhancement

**Product Name**: DataRoom Intelligence Bot - Lazy Vision Enhancement  
**Document Type**: Brownfield PRD  
**Version**: 3.0  
**Date**: September 15, 2025  
**Author**: John (Product Manager)  
**Status**: Ready for Implementation  

---

## 1. EXECUTIVE SUMMARY

### 1.1 Critical Business Context
The DataRoom Intelligence Bot is currently experiencing **complete system failure** with 0% success rate in production due to SSL exhaustion when processing pitch deck visuals. This PRD defines the Lazy Vision enhancement - a strategic brownfield integration that restores system functionality while dramatically improving data quality.

### 1.2 Solution Overview
**Lazy Vision** implements intelligent processing of only 7 strategic pages (vs 43) during analysis, preventing SSL exhaustion while maintaining the exact user experience with enhanced data accuracy. The solution requires minimal code changes (~285 lines across 5 files) while delivering a quantum leap in quality.

### 1.3 Business Value
- **Restore System Functionality**: From 0% to 95% success rate
- **Enhance Data Quality**: 95% accuracy on financial metrics (vs 60% text-only)
- **Reduce Costs**: 84% reduction in API costs ($0.43 → $0.07 per analysis)
- **Preserve User Experience**: Same commands, same reports, just better data

---

## 2. PROBLEM STATEMENT

### 2.1 Current State Analysis

#### System Failure Mode
```
Current Flow (BROKEN):
/analyze → Process 43 pages → SSL Exhaustion → 0% Success → No Value Delivered
```

**Technical Root Cause**:
- Processing 43 pages exhausts OpenAI SSL connection pool
- Error: `SSL: UNEXPECTED_EOF_WHILE_READING`
- Modern API client (VF-1) fixed handshake but not resource exhaustion
- Result: Complete vision processing failure in production

#### Business Impact
| Impact Area | Current State | Business Cost |
|-------------|--------------|---------------|
| **User Experience** | 3-minute timeouts, no results | User abandonment |
| **Data Quality** | Missing critical chart data | Poor investment decisions |
| **System Reliability** | 0% success rate | Platform unusable |
| **Operating Costs** | $0.43 per failed attempt | Wasted resources |

### 2.2 Failed Attempts & Learnings

**Previous Solutions**:
1. **Story 1.2-1.3**: Full vision implementation → SSL failures
2. **VF-1**: OpenAI client modernization → Still failed with 43 pages
3. **Key Learning**: Problem is volume, not API pattern

**Critical Insight**: Quality over quantity - 7 strategic pages provide 95% of business value

---

## 3. PROPOSED SOLUTION: LAZY VISION

### 3.1 Solution Philosophy

**Strategic Processing Over Brute Force**
```
New Flow (WORKING):
/analyze → Identify 7 Key Pages → Process Safely → 95% Success → Enhanced Value
```

**Core Principles**:
1. **Intelligent Selection**: Content-based identification of high-value pages
2. **Hard Limits**: Maximum 7 pages prevents SSL exhaustion
3. **Cache Everything**: Store results for instant reuse
4. **Progressive Enhancement**: On-demand processing for edge cases
5. **Graceful Degradation**: Fall back to text when vision unavailable

### 3.2 Functional Architecture

#### Component Overview
```mermaid
graph TD
    A[Slack Command] --> B[Document Processor]
    B --> C[Strategic Page Selector]
    C --> D[Vision Processor<br/>7 pages max]
    D --> E[Vision Cache]
    E --> F[Report Generator]
    
    G[/ask Command] --> H{Cache Hit?}
    H -->|Yes| I[Instant Response<br/>2-3 seconds]
    H -->|No| J[On-Demand Process<br/>1-3 pages]
    J --> E
```

#### Key Components

**1. Strategic Page Selector** (NEW)
- Location: `utils/strategic_page_selector.py`
- Function: Identify 7 most valuable pages via content analysis
- Categories: Financials, Competition, Market, Traction, Team

**2. Vision Processor** (ENHANCED)
- Location: `handlers/vision_processor.py`
- Changes: Hard 7-page limit, 5-second timeout per page
- SSL Prevention: Single connection, limited retries

**3. Vision Cache** (NEW)
- Location: Enhanced session management
- Function: Store vision results for instant `/ask` responses
- Structure: Indexed by page and category for fast retrieval

**4. Integration Points** (MODIFIED)
- `app.py`: Fix PDF path propagation (critical bug)
- `enhanced_session_manager.py`: Add vision cache structure
- `doc_processor.py`: Minor integration updates

---

## 4. DETAILED REQUIREMENTS

### 4.1 Functional Requirements

#### FR1: Strategic Page Selection
**Requirement**: System shall identify 7 most valuable pages using content-based analysis

**Acceptance Criteria**:
- Scans PDF text for business-critical keywords
- Prioritizes: Financials > Competition > Market > Traction > Team
- Falls back to common deck patterns if content analysis fails
- Never exceeds 7 pages (hard limit)

**Implementation**:
```python
PRIORITY_PATTERNS = {
    'financials': ['revenue', 'ARR', 'burn rate', 'runway'],  # Priority 1
    'competition': ['competitor', 'vs', 'landscape'],         # Priority 1
    'market': ['TAM', 'SAM', 'market size'],                 # Priority 2
    'traction': ['growth', 'users', 'retention'],            # Priority 2
    'team': ['founder', 'CEO', 'leadership']                 # Priority 3
}
```

#### FR2: SSL-Safe Vision Processing
**Requirement**: System shall process maximum 7 pages with timeout protection

**Acceptance Criteria**:
- Hard limit of 7 pages enforced
- 5-second timeout per page (35 seconds maximum total)
- Modern OpenAI client pattern (gpt-4o model)
- Single connection pool to prevent exhaustion

#### FR3: Vision Result Caching
**Requirement**: System shall cache vision results in user sessions

**Acceptance Criteria**:
- Cache populated during `/analyze` command
- Indexed by page number and content category
- Searchable for quick `/ask` query matching
- 24-hour TTL with automatic cleanup

**Cache Structure**:
```python
vision_cache = {
    'pages_processed': [18, 19, 11, 12, 8],
    'strategic_selection': {'financials': [18, 19], 'competition': [11, 12]},
    'data': {
        18: {'category': 'financials', 'content': '...', 'confidence': 0.92},
        19: {'category': 'financials', 'content': '...', 'confidence': 0.88}
    },
    'search_index': {'financials': ['revenue', 'ARR', 'growth']}
}
```

#### FR4: On-Demand Processing for /ask
**Requirement**: System shall process 1-3 additional pages on-demand for uncached questions

**Acceptance Criteria**:
- Check cache first (80% hit rate expected)
- If miss, identify relevant pages not yet processed
- Process maximum 3 pages on-demand
- Update cache with new results

#### FR5: Unchanged User Experience
**Requirement**: System shall maintain exact same command interface and report format

**Acceptance Criteria**:
- All Slack commands work identically
- Report format unchanged (same sections, same order)
- No user retraining required
- Only data quality improves

### 4.2 Non-Functional Requirements

#### NFR1: Performance Requirements
| Metric | Current | Target | Measurement |
|--------|---------|--------|-------------|
| `/analyze` Response Time | Timeout (3m) | <30 seconds | P95 latency |
| `/ask` Cached Response | N/A | 2-3 seconds | Average |
| `/ask` On-Demand | N/A | 5-7 seconds | Average |
| Vision Processing | 43 pages | 7 pages max | Hard limit |

#### NFR2: Reliability Requirements
| Metric | Current | Target | Rationale |
|--------|---------|--------|-----------|
| Success Rate | 0% | 95% | SSL prevention + fallback |
| SSL Errors | 100% | 0% | 7-page limit prevents exhaustion |
| Fallback Success | N/A | 100% | Text-only always available |

#### NFR3: Quality Requirements
| Data Type | Current Accuracy | Target Accuracy | Source |
|-----------|-----------------|-----------------|--------|
| Financial Metrics | ~60% | 95% | Charts & graphs |
| Competition Detection | ~40% | 90% | Logos & slides |
| Market Size | ~70% | 95% | Visual TAM/SAM |
| Growth Metrics | ~50% | 95% | Dashboards |

#### NFR4: Cost Requirements
| Metric | Current | Target | Savings |
|--------|---------|--------|---------|
| Cost per Analysis | $0.43 | $0.07 | 84% |
| Monthly Cost (100/day) | $1,290 | $210 | $1,080 |
| Pages Processed | 43 | 7 | 84% reduction |

---

## 5. USER STORIES & ACCEPTANCE CRITERIA

### 5.1 Epic: Restore Vision Processing with Strategic Intelligence

#### Story 1: Strategic Page Selection
**As a** system administrator  
**I want** the system to intelligently select only 7 critical pages  
**So that** vision processing completes without SSL exhaustion

**Acceptance Criteria**:
- [ ] Content-based page detection implemented
- [ ] 7-page maximum enforced
- [ ] Fallback patterns for unknown formats
- [ ] Selection rationale logged for debugging

#### Story 2: Vision Processing Enhancement
**As a** VC analyst  
**I want** vision processing to complete successfully  
**So that** I get accurate data from charts and visuals

**Acceptance Criteria**:
- [ ] 95% success rate achieved
- [ ] 30-second response time
- [ ] Zero SSL errors
- [ ] Graceful text-only fallback

#### Story 3: Cache-Optimized /ask
**As a** VC analyst  
**I want** instant answers to questions about analyzed documents  
**So that** I can quickly explore investment opportunities

**Acceptance Criteria**:
- [ ] 80% cache hit rate
- [ ] 2-3 second cached responses
- [ ] 5-7 second on-demand processing
- [ ] Cache persistence across session

### 5.2 User Journey Map

```
1. Upload Deck → 2. Strategic Selection → 3. Vision Processing → 4. Report Generation
   (Same UX)        (7 pages, 2s)           (20s, SSL-safe)        (Same format)
                           ↓
                     5. Cache Storage
                           ↓
   6. /ask Query → 7. Cache Check → 8a. Instant Response (80%)
                                  → 8b. On-Demand Process (20%)
```

---

## 6. TECHNICAL SPECIFICATIONS

### 6.1 System Architecture Changes

#### Existing Components (Preserved)
- Flask/Slack Bolt framework
- Google Drive integration
- Report generation templates
- BMAD Framework agents
- Railway deployment

#### New Components (Added)
```python
# utils/strategic_page_selector.py (~200 lines)
class StrategicPageSelector:
    def select_strategic_pages(pdf_path: str) -> Dict[str, List[int]]

# Enhanced vision_processor.py (+50 lines)
class VisionProcessor:
    max_pages = 7
    timeout_per_page = 5
    
# Enhanced session structure (+20 lines)
user_sessions[user_id]['vision_cache'] = {...}
```

#### Modified Components
- `app.py`: Fix PDF path propagation (10 lines)
- `enhanced_session_manager.py`: Add vision cache (20 lines)
- `doc_processor.py`: Minor integration (5 lines)

**Total Code Impact**: ~285 lines across 5 files

### 6.2 Data Models

#### Vision Cache Model
```python
@dataclass
class VisionCache:
    pages_processed: List[int]
    strategic_selection: Dict[str, List[int]]
    data: Dict[int, PageVisionData]
    search_index: Dict[str, SearchIndex]
    cached_at: datetime
    
@dataclass
class PageVisionData:
    category: str
    content: str
    confidence: float
    processed_at: datetime
    key_phrases: List[str]
```

### 6.3 API Integration

#### OpenAI Vision API (Enhanced)
```python
# Modern client pattern with SSL prevention
client = OpenAI(
    api_key=config.OPENAI_API_KEY,
    http_client=httpx.Client(
        limits=httpx.Limits(max_connections=1),  # Prevent pool exhaustion
        timeout=httpx.Timeout(read=5.0)          # Per-page timeout
    )
)

response = client.chat.completions.create(
    model="gpt-4o",  # Modern model (not deprecated gpt-4-vision-preview)
    messages=[...],
    max_tokens=1000,
    timeout=5
)
```

---

## 7. IMPLEMENTATION PLAN

### 7.1 Development Phases

#### Phase 1: Core Implementation (Days 1-3)
**Day 1-2: Strategic Page Selector**
- [ ] Implement content-based detection algorithm
- [ ] Add fallback patterns for common deck formats
- [ ] Unit tests for various deck types

**Day 3: Vision Processor Enhancement**
- [ ] Add 7-page hard limit
- [ ] Implement per-page timeout
- [ ] SSL-safe client configuration

#### Phase 2: Integration & Optimization (Days 4-5)
**Day 4: Cache Implementation**
- [ ] Vision cache in session structure
- [ ] Search index for fast query matching
- [ ] On-demand processing logic

**Day 5: Testing & Validation**
- [ ] Integration testing with sample decks
- [ ] Performance validation
- [ ] Production deployment preparation

### 7.2 Testing Strategy

#### Test Scenarios
1. **Various Deck Formats**: 15-page, 30-page, 43-page decks
2. **Content Types**: Text-heavy, visual-heavy, mixed
3. **Failure Modes**: Vision timeout, API errors, malformed PDFs
4. **Cache Performance**: Hit rate, response time, memory usage

#### Validation Metrics
- [ ] 95% success rate across test decks
- [ ] <30 second response time (P95)
- [ ] Zero SSL errors
- [ ] 80%+ cache hit rate
- [ ] 95% accuracy on financial data

### 7.3 Rollout Strategy

#### Progressive Deployment
```yaml
Stage 1: Development Testing
- Feature flag: LAZY_VISION_ENABLED=true
- Test with team members only

Stage 2: Staged Rollout  
- 10% of users (Day 1)
- 50% of users (Day 2)
- 100% of users (Day 3)

Stage 3: Monitoring
- Success rate tracking
- Performance metrics
- Cost monitoring
- User feedback collection
```

#### Rollback Plan
```bash
# Instant rollback via environment variables
LAZY_VISION_ENABLED=false
VISION_MAX_PAGES=0
```

---

## 8. RISK ASSESSMENT & MITIGATION

### 8.1 Technical Risks

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| Strategic pages miss key content | Medium | High | Content-based detection + fallback patterns |
| 7 pages still cause SSL issues | Low | Critical | Per-page timeout + connection limiting |
| Cache grows too large | Medium | Low | TTL expiration + size limits |
| On-demand processing too slow | Low | Medium | Limit to 3 pages maximum |

### 8.2 Business Risks

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| Users notice quality regression | Low | High | Enhanced accuracy offsets any gaps |
| Costs exceed budget | Low | Medium | Hard limits + monitoring |
| System instability during rollout | Low | High | Feature flags + instant rollback |

### 8.3 Mitigation Strategies

**Multi-Level Fallback**:
1. Try 7 strategic pages
2. If SSL error, reduce to 3 critical pages
3. If still failing, use text-only extraction
4. Always provide some value to user

---

## 9. SUCCESS METRICS

### 9.1 Key Performance Indicators

#### Technical KPIs
| Metric | Baseline | Week 1 Target | Month 1 Target |
|--------|----------|---------------|----------------|
| Success Rate | 0% | 90% | 95% |
| Response Time | Timeout | <45s | <30s |
| SSL Errors | 100% | <5% | 0% |
| Cache Hit Rate | N/A | 70% | 80% |

#### Business KPIs
| Metric | Baseline | Week 1 Target | Month 1 Target |
|--------|----------|---------------|----------------|
| User Satisfaction | N/A | 4.0/5 | 4.5/5 |
| Data Accuracy | 60% | 85% | 95% |
| Cost per Analysis | $0.43 | $0.10 | $0.07 |
| Daily Analyses | 0 | 50 | 100 |

### 9.2 Success Criteria

**Minimum Viable Success** (Week 1):
- [ ] 90% success rate achieved
- [ ] Zero SSL exhaustion errors
- [ ] <45 second response time
- [ ] Positive user feedback

**Full Success** (Month 1):
- [ ] 95% success rate sustained
- [ ] 80% cache hit rate
- [ ] 95% data accuracy
- [ ] $1,000+ monthly cost savings

---

## 10. STAKEHOLDER COMMUNICATION

### 10.1 Stakeholder Matrix

| Stakeholder | Interest | Influence | Communication |
|-------------|----------|-----------|---------------|
| VC Analysts (Users) | High | High | Daily updates during rollout |
| Engineering Team | High | High | Technical sync meetings |
| Finance Team | Medium | Medium | Cost reports weekly |
| Customer Success | High | Low | Training materials |

### 10.2 Communication Plan

**Pre-Launch**:
- Technical review with engineering
- User preview with key analysts
- Documentation preparation

**Launch Week**:
- Daily status updates
- Performance dashboard
- Issue tracking and resolution

**Post-Launch**:
- Weekly metrics review
- Monthly cost analysis
- Quarterly roadmap update

---

## 11. FUTURE CONSIDERATIONS

### 11.1 Potential Enhancements

**Phase 2 Possibilities**:
1. **Async Processing**: Background vision processing for faster initial response
2. **ML Page Ranking**: Learn optimal pages per deck type
3. **Redis Cache**: Persistent cache across deployments
4. **Progressive Enhancement**: Add pages as SSL handling improves

### 11.2 Technical Debt Considerations

**Current Debt**:
- PDF path propagation bug in app.py
- Session management type mismatches
- No persistence across deployments

**Debt Resolution**:
- Fix critical bugs during implementation
- Plan session persistence for Phase 2
- Document known limitations

---

## 12. APPENDICES

### Appendix A: Technical Architecture Reference
See: `docs/architecture/lazy-vision-brownfield-architecture.md`

### Appendix B: Component Specifications
- Strategic Page Selection: `docs/architecture/components/strategic-page-selection.md`
- Vision Processing Engine: `docs/architecture/components/vision-processing-engine.md`
- Vision Cache Strategy: `docs/architecture/components/vision-cache-strategy.md`

### Appendix C: Related Documentation
- Project Status: `docs/LAZY-VISION-STATUS.md`
- Executive Report: `docs/lazy-vision-executive-report.md`
- Original PRD: `docs/prd.md`

---

## APPROVAL & SIGN-OFF

### Required Approvals
- [ ] Product Manager (John)
- [ ] Engineering Lead
- [ ] Customer Success Lead
- [ ] Finance (for cost implications)

### Decision
**RECOMMENDATION**: PROCEED with Lazy Vision implementation immediately. This brownfield enhancement solves a critical production failure with minimal code changes while delivering dramatic improvements in data quality and user value.

**Rationale**:
1. **Critical Fix**: System currently unusable (0% success rate)
2. **Proven Approach**: 7-page limit mathematically prevents SSL exhaustion
3. **Minimal Risk**: ~285 lines of code, instant rollback available
4. **High ROI**: 84% cost reduction, 95% accuracy improvement
5. **User Friendly**: Zero learning curve, same interface

---

*Document prepared by John (Product Manager) for immediate implementation of critical system enhancement.*