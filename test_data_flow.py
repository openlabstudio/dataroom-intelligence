#!/usr/bin/env python
"""
Quick test to check data flow structure
"""

import os
import fitz  # PyMuPDF
from handlers.doc_processor import DocumentProcessor

def test_data_structure():
    """Check what structure _process_pdf returns"""

    test_file = "./temp/Stamp_Investor-Deck.pdf"
    if not os.path.exists(test_file):
        print(f"❌ File not found: {test_file}")
        return

    # Test PyMuPDF directly
    print("1. TESTING PyMuPDF DIRECTLY:")
    doc = fitz.open(test_file)
    for i in range(min(3, len(doc))):
        page_text = doc[i].get_text("text").strip()
        print(f"   Page {i+1}: {len(page_text)} chars")
    doc.close()

    # Test doc_processor
    print("\n2. TESTING DOC_PROCESSOR:")
    processor = DocumentProcessor()

    # Call internal _process_pdf method
    result = processor._process_pdf(test_file, "Stamp_Investor-Deck.pdf")

    print(f"   Result keys: {list(result.keys())}")
    if 'pages' in result:
        print(f"   ✅ Has 'pages' array with {len(result['pages'])} pages")
    else:
        print(f"   ❌ Missing 'pages' array!")

    if 'full_text' in result:
        print(f"   Has 'full_text' with {len(result['full_text'])} chars")
    if 'content' in result:
        print(f"   Has 'content' with {len(result['content'])} chars")

if __name__ == "__main__":
    test_data_structure()