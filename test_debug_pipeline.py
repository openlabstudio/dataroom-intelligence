#!/usr/bin/env python
"""
Test script to debug the extraction-analysis pipeline
"""

import os
import sys
import logging
from handlers.doc_processor import DocumentProcessor
from handlers.ai_analyzer import AIAnalyzer

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_pipeline():
    """Test the pipeline with debug output"""

    # Test file
    test_file = "./temp/Stamp_Investor-Deck.pdf"

    if not os.path.exists(test_file):
        logger.error(f"Test file not found: {test_file}")
        return

    logger.info("=" * 80)
    logger.info("STARTING PIPELINE DEBUG TEST")
    logger.info("=" * 80)

    # Initialize processors
    doc_processor = DocumentProcessor()
    ai_analyzer = AIAnalyzer()

    # Process document
    logger.info(f"\n1. PROCESSING DOCUMENT: {test_file}")
    # The method expects a list of dicts with 'path', 'name', and 'mime_type' keys
    files = [{
        'path': test_file,
        'name': 'Stamp_Investor-Deck.pdf',
        'mime_type': 'application/pdf'
    }]
    processed_documents = doc_processor.process_dataroom_documents(files)

    # Debug output
    logger.info(f"\n2. PROCESSED DOCUMENTS STRUCTURE:")
    for i, doc in enumerate(processed_documents):
        logger.info(f"   Doc {i}: {doc['name']}")
        logger.info(f"   - Keys: {list(doc.keys())}")
        if 'pages' in doc:
            logger.info(f"   - Pages: {len(doc['pages'])} pages")
            if doc['pages']:
                logger.info(f"   - First page preview: {doc['pages'][0][:100]}...")
        if 'content' in doc:
            logger.info(f"   - Content length: {len(doc.get('content', ''))} chars")
        if 'full_text' in doc:
            logger.info(f"   - Full text length: {len(doc.get('full_text', ''))} chars")

    # Get summary
    logger.info(f"\n3. GETTING CONTENT SUMMARY:")
    document_summary = doc_processor.get_content_summary(processed_documents)
    logger.info(f"   - Summary keys: {list(document_summary.keys())}")

    # Analyze
    logger.info(f"\n4. RUNNING AI ANALYSIS:")
    analysis_result = ai_analyzer.analyze_dataroom(processed_documents, document_summary)

    # Show result preview
    logger.info(f"\n5. ANALYSIS RESULT:")
    if 'deck_summary' in analysis_result:
        deck_summary = analysis_result['deck_summary']
        logger.info(f"   - Deck summary length: {len(deck_summary)} chars")
        logger.info(f"   - First 500 chars: {deck_summary[:500]}...")
    else:
        logger.info(f"   - Keys in result: {list(analysis_result.keys())}")

    logger.info("=" * 80)
    logger.info("PIPELINE DEBUG TEST COMPLETE")
    logger.info("=" * 80)

if __name__ == "__main__":
    test_pipeline()