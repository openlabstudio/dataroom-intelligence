# PRD-002: Intelligent Pipeline V2 - Fixing the Extraction-Analysis Decoupling

**Epic:** Phase 1B: Correcting the Hybrid Pipeline Architecture
**Status:** In Development
**Author:** Claudio & Rafa
**Date:** 2025-09-22
**Supersedes:** PRD-001

---

## 1. Problem Context (Updated Understanding)

### Original Diagnosis (PRD-001) - INCORRECT
- **Believed Problem:** GPT-4o Vision extraction was slow, expensive, and unreliable
- **Proposed Solution:** Hybrid extraction with PyMuPDF + Vision fallback

### Actual Problem (Gemini Analysis) - CORRECT
- **Real Problem:** Decoupling between extraction and analysis phases
- **Root Cause:** Extraction provides unstructured `full_text` instead of `pages[]` array
- **Impact:** High-quality analysis prompt receives low-quality data structure

### Evidence
- Stamp deck: 0 native text chars (confirmed via debug_extraction.py)
- GPT-4o extracts 6,122 chars successfully but analysis shows only GAPS
- Previous working version had page-by-page citations [A·p1], [A·p2], etc.

## 2. Requirements (Revised)

### Functional Requirements

**RF-1: Intelligent PDF Classification**
- System MUST perform pre-flight check on first 3 pages
- If all pages have <20 chars → classify as "image-only"
- If any page has >20 chars → classify as "hybrid-capable"

**RF-2: Holistic Processing for Image PDFs**
- Image-only PDFs MUST use GPT-4o holistic processing
- MUST return `pages[]` array structure
- MUST preserve page boundaries for citation

**RF-3: Hybrid Processing for Text PDFs**
- Text-capable PDFs use PyMuPDF for text pages
- Fall back to Vision OCR only for image pages
- MUST return unified `pages[]` array

**RF-4: Unified Data Structure**
```python
{
    'name': str,
    'type': 'pdf',
    'pages': List[str],      # REQUIRED - array of page texts
    'content': str,          # OPTIONAL - concatenated for compatibility
    'metadata': {
        'extraction_method': str,
        'pages_count': int,
        'text_pages': int,   # For hybrid only
        'image_pages': int   # For hybrid only
    }
}
```

**RF-5: Analysis Pipeline Requirements**
- ai_analyzer MUST receive `pages[]` array
- MUST use `_generate_simple_analyst_summary` method
- MUST format with locators [A·p1], [A·p2], etc.

### Non-Functional Requirements

**RNF-1: Quality Target**
- Output quality MUST match docs/outputs analyze/gemini reference
- MUST extract: metrics, team, funding, traction, business model

**RNF-2: Performance**
- Total processing time < 60 seconds for 20-page deck
- Pre-flight check < 1 second

**RNF-3: Cost Optimization**
- Minimize Vision API calls for text-heavy documents
- Use holistic processing for image-only (better quality/cost ratio)

## 3. Implementation Plan

### Phase 1: Core Pipeline Fix (2 hours)

#### Step 1.1: Update doc_processor.py
```python
def _process_pdf(self, file_path: str, file_name: str) -> Dict[str, Any]:
    """Intelligent routing based on PDF content type"""

    # Pre-flight check
    if self._is_image_only_pdf(file_path):
        logger.info(f"📄 Detected image-only PDF, using holistic processing")
        return self._process_pdf_holistically(file_path, file_name)
    else:
        logger.info(f"📄 Detected text-capable PDF, using hybrid processing")
        return self._process_pdf_hybrid(file_path, file_name)

def _is_image_only_pdf(self, file_path: str) -> bool:
    """Check first 3 pages for native text"""
    doc = fitz.open(file_path)
    pages_to_check = min(3, len(doc))

    for i in range(pages_to_check):
        page_text = doc[i].get_text("text").strip()
        if len(page_text) > 20:
            doc.close()
            return False

    doc.close()
    return True

def _process_pdf_holistically(self, file_path: str, file_name: str) -> Dict[str, Any]:
    """Use GPT-4o for complete PDF analysis"""
    if not self.gpt4o_processor:
        raise Exception("GPT-4o processor not available")

    # GPT-4o returns pages[] structure
    result = self.gpt4o_processor.process_pdf_document(file_path, file_name)

    # Ensure consistent structure
    if 'pages' not in result and 'content' in result:
        # Fallback: split content by some delimiter if needed
        result['pages'] = [result['content']]

    return result
```

#### Step 1.2: Verify gpt4o_pdf_processor.py
- Confirm `process_pdf_document` returns `pages[]` array
- If not, update to extract text per page as per Gemini's recommendation

#### Step 1.3: Fix ai_analyzer.py data flow
- Verify `_prepare_analysis_context` handles `pages[]`
- Ensure `_generate_simple_analyst_summary` is called
- Confirm citation formatting works

### Phase 2: Testing Protocol (1 hour)

#### Test Case 1: Image-Only PDF (Stamp)
```bash
# Run analysis
/analyze [stamp-deck-url]

# Expected Output Validation:
- [ ] Full executive summary (not just GAPS)
- [ ] Metrics: €2M seed, €12M valuation
- [ ] Team: 4 founders with names
- [ ] Traction: 1,300+ merchants, 40,000+ travelers
- [ ] Citations: [A·p1], [A·p2], etc.
- [ ] Processing time < 60 seconds
```

#### Test Case 2: Text-Heavy PDF
```bash
# Use a text-based financial report
/analyze [text-heavy-pdf-url]

# Expected:
- [ ] PyMuPDF processes most pages
- [ ] Minimal Vision API calls
- [ ] Quality maintained
- [ ] Processing time < 30 seconds
```

#### Test Case 3: Debug Verification
```bash
# Check logs for:
- "Detected image-only PDF" OR "Detected text-capable PDF"
- "pages (X text, Y image)" for hybrid
- "Facts loaded: X non-empty sections"
- "Using SIMPLIFIED analysis with full text"
```

### Phase 3: Optimization (30 minutes)

1. Fine-tune pre-flight check threshold (currently 20 chars)
2. Optimize GPT-4o prompts if needed
3. Add performance logging
4. Document findings

## 4. Success Criteria

### Immediate Success (Today)
- [ ] Stamp deck produces full analysis matching Gemini quality
- [ ] Processing completes in < 60 seconds
- [ ] Citations work correctly

### Complete Success (This Week)
- [ ] 5 different PDFs tested successfully
- [ ] Hybrid routing works correctly
- [ ] Performance meets targets
- [ ] Documentation complete

## 5. Rollback Plan

If implementation fails:
1. Preserve all documentation in `docs/` folder
2. Create backup branch: `git checkout -b phase1b-backup`
3. Rollback to commit 9d789d6 if needed
4. Cherry-pick documentation commits back

## 6. Dependencies and Risks

### Dependencies
- GPT-4o API availability
- PyMuPDF functionality
- Existing `_generate_simple_analyst_summary` prompt quality

### Risks
- GPT-4o might not return pages[] structure → Need to verify/fix
- Pre-flight check might misclassify → Tunable threshold
- Performance might degrade → Monitor and optimize

## 7. Appendix: Key Code Locations

- `handlers/doc_processor.py`: Main routing logic (lines 82-140)
- `handlers/gpt4o_pdf_processor.py`: GPT-4o integration
- `handlers/ai_analyzer.py`: Analysis pipeline
- Method `_generate_simple_analyst_summary`: The high-quality prompt
- Method `_format_dataroom_text_with_locators`: Citation formatting