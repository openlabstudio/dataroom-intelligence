# Product Requirements Document: Lazy Vision Enhancement

**Product Name**: DataRoom Intelligence Bot  
**Document Version**: 2.0 - Lazy Vision  
**Last Updated**: September 15, 2025  
**Document Owner**: John (Product Manager)  

---

## Executive Summary

This PRD defines the Lazy Vision enhancement - a strategic approach to fix critical SSL failures in GPT Vision processing by implementing intelligent page selection that processes only 7 strategic pages instead of 43, maintaining the same user experience while dramatically improving data quality.

## Current State & Problem

### System Status: CRITICAL FAILURE
- **Success Rate**: 0% - All vision processing fails with SSL errors
- **Error**: `SSL: UNEXPECTED_EOF_WHILE_READING` when processing 43 pages
- **User Impact**: No visual analysis available, missing critical financial data from charts
- **Root Cause**: Processing 43 pages exhausts SSL connections and resources

### What We've Tried
1. **Story 1.2 & 1.3**: Implemented but failed in production
2. **VF-1**: Fixed OpenAI client pattern - still failed with 43 pages
3. **Discovery**: Problem is resource exhaustion, not API pattern

## Solution: Lazy Vision Hybrid

### Core Concept
Process only **7 strategic pages** during `/analyze` and **1-3 pages on-demand** for `/ask`:

```python
KEY_PAGES = {
    'financials': [18, 19, 20],      # Revenue, burn, runway charts
    'traction': [14, 15],            # Growth metrics, retention
    'market': [8, 9],                # TAM/SAM visual analysis
    'competition': [11, 12, 13],     # Competitive landscape
    'team': [3, 4],                  # Leadership backgrounds
}
```

### Key Decision: Minimal Code, Maximum Impact
- **KEEP** existing `/analyze` report format (users familiar)
- **ENHANCE** data accuracy with vision (charts, financials, competition)
- **MAINTAIN** current UX with better data quality
- **TOUCH** minimum code while delivering quantum leap in quality

## Functional Requirements

### FR1: Strategic Page Selection
The system shall identify and process only 7 strategic pages containing business-critical visual information (financials, competition, market, traction).

### FR2: Content-Based Detection
The system shall use content analysis (not fixed page numbers) to find strategic pages dynamically across different deck formats.

### FR3: Vision Processing with Hard Limits
The system shall enforce a hard limit of 7 pages maximum for vision processing, with 5-second timeout per page (35 seconds total).

### FR4: Vision Result Caching
The system shall cache vision analysis results in user_sessions for immediate reuse by subsequent commands.

### FR5: /analyze Enhancement (Same Format)
The system shall maintain the EXACT same report format while enhancing data quality with vision-extracted information.

### FR6: /ask On-Demand Processing
The system shall check cached vision data first, then process 1-3 relevant pages on-demand if needed for specific questions.

### FR7: Graceful Fallback
The system shall fall back to text-only extraction if vision processing fails, ensuring service continuity.

## Non-Functional Requirements

### NFR1: Performance
- Response time: <30 seconds for `/analyze` (down from 3-minute timeout)
- Cache response: 2-3 seconds for cached `/ask` questions

### NFR2: Reliability
- Success rate: 95% (up from 0%)
- SSL errors: Zero connection exhaustion errors

### NFR3: Cost Efficiency
- 84% reduction in API costs (7 pages vs 43)
- Cost per analysis: <$0.10

### NFR4: Data Quality
- Financial accuracy: 95% (up from 60%)
- Competition detection: 90% (up from 40%)
- Market size accuracy: 95% (up from 70%)

## Success Metrics

| Metric | Current (Broken) | Target (Lazy Vision) |
|--------|-----------------|----------------------|
| **Success Rate** | 0% | 95% |
| **Response Time** | Timeout (3m) | 30 seconds |
| **Cost per Analysis** | $0.43 (fails) | $0.07 |
| **Pages Processed** | 43 (attempted) | 7 strategic |
| **Financial Accuracy** | ~60% | 95% |
| **Competition Detection** | ~40% | 90% |

## User Journey

1. VC Analyst uploads deck via `/analyze`
2. System identifies 7 strategic pages (financials, competition, market)
3. Vision processes only these pages (30 seconds)
4. Report appears in SAME format with ACCURATE data
5. Financial numbers match charts exactly
6. Competition section lists actual competitors from slides
7. `/ask` uses cached vision or processes 1-3 pages on-demand

## Technical Architecture

### Components
1. **Strategic Page Selector** - Content-based identification of key pages
2. **Vision Processor** - Hard limit of 7 pages, 5-second timeout each
3. **Cache Manager** - Store/retrieve vision results in user_sessions
4. **Integration Layer** - Seamless integration with existing commands

### Data Flow
```
/analyze → Text Extraction (10s) → Strategic Page Selection (2s) 
         → Vision Processing (20s) → Cache Results → Generate Report
         
/ask → Check Cache → [If miss] Find Relevant Pages (1-3) 
     → Process On-Demand → Update Cache → Generate Answer
```

## Implementation Plan

### Week 1: Core Implementation
- Day 1-2: Strategic page selector (content-based)
- Day 3-4: Vision processor with 7-page limit
- Day 5: Integration testing

### Week 2: Refinement
- Day 1-2: /ask on-demand processing
- Day 3: Cache optimization
- Day 4-5: Production testing

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Fixed page numbers don't work | Content-based detection |
| 7 pages miss important content | /ask provides on-demand processing |
| Vision still fails with 7 pages | Progressive processing, graceful fallback |
| Cache becomes stale | Timestamp tracking, session management |

## What Users Will Notice

### ✅ Improvements
- Reports complete successfully (vs timeouts)
- Financial numbers match deck charts exactly
- Competition section lists actual competitors
- Market size reflects visual TAM/SAM slides
- /ask can answer about specific charts

### 🔒 No Changes (Good!)
- Same report format
- Same command structure
- Same Slack interface
- Just works better

## Acceptance Criteria

1. Vision processing completes in <30 seconds without SSL errors
2. Strategic page selector identifies 7 most valuable pages
3. Vision results cached and reusable across commands
4. /analyze report format unchanged
5. 95% success rate achieved
6. 84% cost reduction verified

## Dependencies

- VF-1 implementation (OpenAI client fix) ✅ COMPLETED
- Access to sample pitch decks for testing
- Production environment for validation

---

**Recommendation**: PROCEED with Lazy Vision implementation. This approach solves the critical SSL failure with minimal code changes while delivering maximum quality improvement. Users get the same familiar interface with dramatically better data accuracy.