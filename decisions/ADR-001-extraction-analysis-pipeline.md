# ADR-001: Extraction and Analysis Pipeline Architecture

**Date:** 2025-09-22
**Status:** Proposed
**Author:** Claudio & Rafa

## Context and Problem Statement

We have implemented a hybrid extraction pipeline (PHASE_1) that technically works but produces poor quality analysis results. The system currently:
- Uses PyMuPDF + GPT-4o Vision fallback for extraction
- Loses critical page-by-page structure during processing
- Produces only GAPS without actual content in Slack output
- Takes 3 minutes for processing vs. seconds expected

The root cause identified: **Decoupling between extraction and analysis phases**, not the extraction method itself.

## Decision Drivers

1. **Quality Target**: Match Gemini web output quality (rich metrics, accurate citations, complete analysis)
2. **Performance**: Maintain reasonable processing time (<1 minute)
3. **Cost Efficiency**: Minimize GPT-4o API calls where possible
4. **Maintainability**: Simple, debuggable architecture
5. **Incremental Development**: Ability to test and validate each step

## Considered Options

### Option 1: Complete Rollback to GPT-4o Direct
- Revert to commit 9d789d6
- Lose all PHASE_1 improvements
- Return to known working state

### Option 2: Fix Current Hybrid Implementation
- Keep PyMuPDF extraction for text-heavy PDFs
- Fix data flow between extraction and analysis
- Preserve page structure throughout pipeline

### Option 3: Intelligent Hybrid with Holistic Analysis (Recommended)
- Pre-flight check for image-only PDFs
- Route image PDFs to GPT-4o holistic processing
- Route text PDFs to PyMuPDF with page preservation
- Ensure pages[] structure flows to ai_analyzer

## Decision Outcome

**Chosen option: Option 3 - Intelligent Hybrid with Holistic Analysis**

### Rationale
- Preserves cost optimization for text-heavy PDFs
- Maintains quality for image-only PDFs like Stamp deck
- Aligns with Gemini's identified solution (page-by-page structure)
- Allows incremental testing and validation

## Implementation Strategy

### Phase 1: Documentation and Planning (CURRENT)
1. Create this ADR
2. Update PRD with corrections
3. Define test cases
4. Preserve documentation

### Phase 2: Core Pipeline Fix
1. Implement pre-flight check in doc_processor
2. Ensure GPT-4o returns pages[] structure
3. Fix data flow to ai_analyzer
4. Verify _generate_simple_analyst_summary usage

### Phase 3: Testing and Validation
1. Test with Stamp deck (image-only)
2. Test with text-heavy PDF
3. Compare output with Gemini quality target
4. Measure performance metrics

### Phase 4: Optimization
1. Fine-tune heuristics
2. Optimize prompts
3. Add caching where appropriate

## Consequences

### Positive
- Achieves quality target
- Maintains cost efficiency
- Preserves work done in PHASE_1
- Clear debugging path

### Negative
- More complex than pure GPT-4o Direct
- Requires careful testing of routing logic
- Two code paths to maintain

## Technical Specifications

### Key Changes Required

1. **doc_processor.py**
```python
def _process_pdf(self, file_path, file_name):
    # Pre-flight check
    if is_image_only_pdf(file_path):
        return self.gpt4o_processor.process_pdf_document(file_path, file_name)
    else:
        return self._process_pdf_hybrid(file_path, file_name)
```

2. **Data Structure**
```python
{
    'name': str,
    'type': 'pdf',
    'pages': List[str],  # CRITICAL: Must be present
    'content': str,      # Concatenated for compatibility
    'metadata': dict
}
```

3. **ai_analyzer.py**
- Must receive pages[] array
- Use _generate_simple_analyst_summary with proper formatting
- Maintain citation structure [A·p1], [A·p2], etc.

## Verification Criteria

1. Stamp deck produces full analysis (not just GAPS)
2. Quality matches Gemini reference output
3. Processing time < 1 minute
4. Citations correctly reference page numbers
5. All metrics and team info extracted

## References

- Original working commit: 9d789d6
- Gemini analysis: docs/How to improve analyze/gemini-decoupling-extraction-analysys
- Target quality: docs/outputs analyze/gemini
- Current PRD: docs/prd/01_Hybrid_Extraction_Pipeline.md