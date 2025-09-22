# Test Case Suite 002: Intelligent Pipeline V2

**Epic:** Phase 1B - Pipeline Correction
**Date:** 2025-09-22
**Status:** Ready for Execution

---

## Test Environment Setup

### Prerequisites
1. Stamp deck available at: `./temp/Stamp_Investor-Deck.pdf`
2. Debug script available: `debug_extraction.py`
3. Slack workspace connected
4. Logging level set to DEBUG

### Test Data
- **Image-Only PDF:** Stamp_Investor-Deck.pdf (0 chars native text)
- **Text-Heavy PDF:** [To be identified - financial report or pitch deck]
- **Mixed PDF:** [To be identified - deck with both text and images]

---

## Test Case 1: Pre-Implementation Baseline

**Objective:** Document current broken state for comparison

### Steps:
1. Run current system with Stamp deck
2. Capture Slack output
3. Capture full logs
4. Note processing time

### Expected Current State (Broken):
- [ ] Slack shows only GAPS
- [ ] No metrics extracted
- [ ] No team information
- [ ] Processing time ~3 minutes
- [ ] 18 Vision API calls

### Actual Results:
```
Date/Time: ___________
Processing Time: ___________
Vision API Calls: ___________
Slack Output: [Paste here]
Key Missing Data: ___________
```

---

## Test Case 2: Debug Data Flow

**Objective:** Trace where data gets lost

### Steps:
1. Add debug logging at key points:
   - After doc_processor returns
   - When ai_analyzer receives data
   - Before calling analysis methods

2. Run with Stamp deck

3. Check for:
   - [ ] Does `processed_documents` contain `pages[]`?
   - [ ] Does `ai_analyzer` receive the pages?
   - [ ] Is `_generate_simple_analyst_summary` called?
   - [ ] What's in `full_text` variable?

### Debug Points to Add:
```python
# In perform_dataroom_analysis (app.py)
logger.debug(f"PIPELINE_DEBUG: processed_documents keys: {processed_documents[0].keys()}")
logger.debug(f"PIPELINE_DEBUG: pages present: {'pages' in processed_documents[0]}")

# In ai_analyzer.analyze_dataroom
logger.debug(f"ANALYZER_DEBUG: Received docs with keys: {[doc.keys() for doc in processed_documents]}")
logger.debug(f"ANALYZER_DEBUG: full_text length: {len(self.full_text)}")
```

---

## Test Case 3: Pre-Flight Check Validation

**Objective:** Verify PDF classification works correctly

### Test Script:
```python
# test_preflight.py
import fitz

def check_pdf(file_path):
    doc = fitz.open(file_path)
    for i in range(min(3, len(doc))):
        text = doc[i].get_text("text").strip()
        print(f"Page {i+1}: {len(text)} chars")
        print(f"  Preview: {text[:50]}...")
    doc.close()

# Test with different PDFs
check_pdf("./temp/Stamp_Investor-Deck.pdf")  # Should be ~0 chars
check_pdf("./temp/text-heavy.pdf")          # Should be >20 chars
```

### Expected Results:
- [ ] Stamp: All pages < 20 chars → Image-only classification
- [ ] Text PDF: Some pages > 20 chars → Hybrid classification

---

## Test Case 4: GPT-4o Pages Structure

**Objective:** Verify GPT-4o returns correct structure

### Manual Test:
1. Call `gpt4o_processor.process_pdf_document()` directly
2. Inspect returned structure

### Validation Checklist:
```python
result = gpt4o_processor.process_pdf_document(file_path, file_name)
assert 'pages' in result, "Missing pages array"
assert isinstance(result['pages'], list), "Pages not a list"
assert len(result['pages']) > 0, "Empty pages array"
assert all(isinstance(p, str) for p in result['pages']), "Pages not strings"
```

---

## Test Case 5: End-to-End Success Validation

**Objective:** Verify complete pipeline produces quality output

### Success Criteria for Stamp Deck:

#### Executive Summary
- [ ] Contains: "platform for real-time tax-free shopping"
- [ ] Contains: "€2M seed round"
- [ ] Contains: "1,300+ merchants"

#### Company Section
- [ ] Contains: "instant VAT-free"
- [ ] Contains: "Milan, Madrid, Valencia"

#### Business Model
- [ ] Contains: "B2B"
- [ ] Contains pricing or revenue model

#### Metrics & Traction
- [ ] Contains: "1,300+ merchants"
- [ ] Contains: "40,000+ travelers"
- [ ] Contains: "100,000+ invoices"
- [ ] Contains: "€77M tax-free eligible"
- [ ] Contains: "€14M VAT/GMV"
- [ ] Contains: "250% growth"

#### Team & Funding
- [ ] Contains: "Abel Navajas"
- [ ] Contains: "Álvaro Fortaneda"
- [ ] Contains: "Javier Castillo"
- [ ] Contains: "Sebastián Perez"
- [ ] Contains: "€2M seed"
- [ ] Contains: "€12M valuation"

#### Citations
- [ ] Format: [A·p1], [A·p2], etc.
- [ ] Citations reference correct pages

---

## Test Case 6: Performance Benchmarks

**Objective:** Ensure performance meets targets

### Metrics to Capture:
```
PDF Type          | Target | Actual | Pass/Fail
------------------|--------|--------|----------
Image-Only (18p)  | <60s   | ____   | ____
Text-Heavy (20p)  | <30s   | ____   | ____
Mixed (15p)       | <45s   | ____   | ____
```

### API Call Count:
```
PDF Type          | PyMuPDF | Vision | Total Cost
------------------|---------|--------|------------
Image-Only        | ____    | ____   | $____
Text-Heavy        | ____    | ____   | $____
Mixed            | ____    | ____   | $____
```

---

## Test Case 7: Regression Tests

**Objective:** Ensure no functionality breaks

### Commands to Test:
- [ ] `/analyze [url]` - Main analysis
- [ ] `/analyze debug` - Session debugging
- [ ] `/ask [question]` - Q&A on analyzed docs
- [ ] `/reset` - Clear session
- [ ] `/health` - System health

### Each Should:
- [ ] Complete without error
- [ ] Return expected format
- [ ] Log appropriately

---

## Test Execution Log

### Round 1: Baseline (Current Broken State)
```
Date: _______
Tester: _______
Result: _______
Notes: _______
```

### Round 2: After Core Fix
```
Date: _______
Tester: _______
Result: _______
Notes: _______
```

### Round 3: After Optimization
```
Date: _______
Tester: _______
Result: _______
Notes: _______
```

---

## Sign-off Criteria

Before marking as complete:
- [ ] All test cases pass
- [ ] Quality matches Gemini reference
- [ ] Performance within targets
- [ ] No regressions identified
- [ ] Documentation updated
- [ ] Code reviewed

**Sign-off:**
- Developer: _______ Date: _______
- Reviewer: _______ Date: _______