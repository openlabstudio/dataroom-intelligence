# Implementation Plan: Intelligent Pipeline V2

**Start Date:** 2025-09-22
**Target Completion:** 2025-09-23
**Mode:** Incremental with validation checkpoints

---

## 🎯 Objective

Fix the extraction-analysis decoupling to achieve Gemini-level quality output for the Stamp deck analysis.

---

## 📋 Pre-Implementation Checklist

### Documentation Created
- [x] ADR-001: Architecture Decision Record
- [x] PRD-002: Intelligent Pipeline V2
- [x] TC-002: Test Cases Suite
- [x] This Implementation Plan
- [x] debug_extraction.py script

### Backup Created
```bash
# Create backup branch with current state
git add docs/decisions/ docs/prd/ docs/test-cases/ IMPLEMENTATION_PLAN.md
git commit -m "📚 DOCS: Complete project documentation for Pipeline V2"
git checkout -b phase1b-implementation-backup
```

---

## 🚀 Phase 1: Baseline and Debugging (30 min)

### Step 1.1: Document Current State
```bash
# Run current broken system
python app.py

# In Slack:
/analyze [stamp-deck-url]

# Document:
- Slack output (copy/paste)
- Processing time
- Log errors/warnings
```

### Step 1.2: Add Debug Logging
Add these debug statements to trace data flow:

```python
# app.py - line ~147 (after process_dataroom_documents)
logger.debug(f"DEBUG_PIPELINE: Processed {len(processed_documents)} docs")
for i, doc in enumerate(processed_documents):
    logger.debug(f"DEBUG_PIPELINE: Doc {i} keys: {doc.keys()}")
    if 'pages' in doc:
        logger.debug(f"DEBUG_PIPELINE: Doc {i} has {len(doc['pages'])} pages")
    if 'content' in doc:
        logger.debug(f"DEBUG_PIPELINE: Doc {i} content length: {len(doc.get('content', ''))}")
```

```python
# ai_analyzer.py - in analyze_dataroom method
logger.debug(f"DEBUG_ANALYZER: Received {len(processed_documents)} documents")
logger.debug(f"DEBUG_ANALYZER: full_text length: {len(self.full_text)}")
logger.debug(f"DEBUG_ANALYZER: Using method: {'simple' if self.full_text else 'canonical'}")
```

### Step 1.3: Run Debug Test
```bash
python app.py
# Run /analyze again
# Capture debug output
```

### CHECKPOINT 1: Data Flow Understanding
- [ ] Identified where pages[] gets lost
- [ ] Confirmed ai_analyzer receives empty/wrong structure
- [ ] Documented exact failure point

---

## 🔧 Phase 2: Core Fix Implementation (1 hour)

### Step 2.1: Fix doc_processor.py

```python
# handlers/doc_processor.py

def _is_image_only_pdf(self, file_path: str) -> bool:
    """Check if PDF is image-only by sampling first 3 pages"""
    try:
        doc = fitz.open(file_path)
        pages_to_check = min(3, len(doc))

        for i in range(pages_to_check):
            page_text = doc[i].get_text("text").strip()
            if len(page_text) > 20:  # Found substantial text
                doc.close()
                return False

        doc.close()
        return True
    except Exception as e:
        logger.warning(f"Error checking PDF type: {e}")
        return False  # Default to hybrid processing

def _process_pdf(self, file_path: str, file_name: str) -> Dict[str, Any]:
    """Process PDF with intelligent routing"""

    # Check PDF type
    is_image_only = self._is_image_only_pdf(file_path)

    if is_image_only:
        logger.info(f"📄 Image-only PDF detected: {file_name}")
        # Use GPT-4o holistic processing
        if self.gpt4o_processor:
            result = self.gpt4o_processor.process_pdf_document(file_path, file_name)
            # Ensure pages structure
            if 'pages' not in result and 'content' in result:
                # Split content into pages if needed
                result['pages'] = [result['content']]
            return result
        else:
            logger.error("GPT-4o processor not available for image PDF")
            return {'name': file_name, 'type': 'error', 'pages': []}
    else:
        logger.info(f"📄 Text-capable PDF detected: {file_name}")
        # Use existing hybrid processing
        return self._process_pdf_hybrid_existing(file_path, file_name)

# Rename current _process_pdf to _process_pdf_hybrid_existing
```

### Step 2.2: Verify GPT-4o Structure

Check what `process_pdf_document` returns:
```python
# Test script: test_gpt4o_structure.py
from handlers.gpt4o_pdf_processor import GPT4oDirectProcessor
from config.settings import config

processor = GPT4oDirectProcessor(config.OPENAI_API_KEY)
result = processor.process_pdf_document("./temp/Stamp_Investor-Deck.pdf", "test.pdf")

print("Keys:", result.keys())
print("Has pages?", 'pages' in result)
print("Has content?", 'content' in result)
if 'pages' in result:
    print(f"Pages count: {len(result['pages'])}")
```

### Step 2.3: Fix Data Structure if Needed

If GPT-4o doesn't return pages[], fix it:
```python
# In gpt4o_pdf_processor.py - process_pdf_document method
# After getting response from GPT-4o:

# Convert to pages structure
if 'pages' not in result:
    if 'content' in result:
        # Try to split by page markers or use as single page
        content = result['content']
        # Look for page breaks or treat as single page
        result['pages'] = content.split('[PAGE_BREAK]') if '[PAGE_BREAK]' in content else [content]
```

### CHECKPOINT 2: Structure Fixed
- [ ] doc_processor returns pages[] for image PDFs
- [ ] doc_processor returns pages[] for hybrid PDFs
- [ ] Verified with debug logging

---

## 🧪 Phase 3: Testing and Validation (45 min)

### Step 3.1: Unit Test - PDF Classification
```bash
python debug_extraction.py ./temp/Stamp_Investor-Deck.pdf
# Should show 0 chars → Image-only classification
```

### Step 3.2: Integration Test - Full Pipeline
```bash
python app.py

# In Slack:
/analyze [stamp-deck-url]

# Validation Checklist:
- [ ] Processing time < 60 seconds
- [ ] Slack output contains actual data (not just GAPS)
- [ ] Metrics present (€2M, €12M, 1300+, 40000+)
- [ ] Team names present
- [ ] Citations formatted correctly [A·p1]
```

### Step 3.3: Compare with Target Quality
```
Side-by-side comparison:
- Our Output: [paste here]
- Gemini Target: docs/outputs analyze/gemini
- Quality Score: ___/10
```

### CHECKPOINT 3: Quality Achieved
- [ ] Output matches Gemini quality level
- [ ] All key information extracted
- [ ] Citations work correctly

---

## 🎨 Phase 4: Optimization (30 min)

### Step 4.1: Performance Tuning
- Adjust pre-flight check pages (3 → 5?)
- Tune character threshold (20 → 30?)
- Add caching for repeated analyses

### Step 4.2: Error Handling
- Add graceful fallbacks
- Improve error messages
- Add retry logic for API failures

### Step 4.3: Logging Cleanup
- Remove debug statements
- Set appropriate log levels
- Add performance metrics

### CHECKPOINT 4: Production Ready
- [ ] Performance optimized
- [ ] Error handling robust
- [ ] Logs clean and informative

---

## 📝 Phase 5: Documentation and Commit (15 min)

### Step 5.1: Update Documentation
- Update PROJECT_MANIFEST.yaml
- Mark PRD-002 as completed
- Update test results in TC-002

### Step 5.2: Final Commit
```bash
git add -A
git commit -m "$(cat <<'EOF'
🚀 FIX: Intelligent Pipeline V2 - Extraction-Analysis Coupling

Implemented intelligent PDF routing with holistic processing for image-only PDFs.
Fixed data flow to preserve page structure through the pipeline.

Key Changes:
• Added pre-flight check for PDF classification
• Image-only PDFs use GPT-4o holistic processing
• Text PDFs use hybrid PyMuPDF + Vision fallback
• Fixed pages[] structure flow to ai_analyzer
• Restored citation functionality [A·p1], [A·p2]

Results:
• Stamp deck: Full analysis with all metrics extracted
• Quality: Matches Gemini reference output
• Performance: <60 seconds for 18-page deck
• Cost: Optimized with intelligent routing

Fixes: ADR-001, PRD-002, TC-002
References: docs/How to improve analyze/gemini-decoupling-extraction-analysys

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

### CHECKPOINT 5: Complete
- [ ] All documentation updated
- [ ] Code committed with proper message
- [ ] Ready for production

---

## 🚨 Rollback Plan

If things go wrong:
```bash
# Save documentation first
git add docs/ IMPLEMENTATION_PLAN.md
git stash

# Rollback code
git checkout 9d789d6

# Restore documentation
git stash pop
```

---

## 📊 Success Metrics

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| Stamp Analysis Quality | 9/10 | ___ | ___ |
| Processing Time | <60s | ___ | ___ |
| Metrics Extracted | 100% | ___ | ___ |
| Team Info Extracted | 100% | ___ | ___ |
| Citations Working | Yes | ___ | ___ |
| No Regressions | Yes | ___ | ___ |

---

## ✅ Final Sign-off

- [ ] All checkpoints passed
- [ ] Quality target achieved
- [ ] Performance acceptable
- [ ] Documentation complete
- [ ] Code reviewed

**Developer:** _____________ **Date:** _____________
**Reviewer:** _____________ **Date:** _____________