#!/usr/bin/env python3
"""
Test script specifically for the problematic Stamp_Investor Deck.pdf
"""

import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from handlers.doc_processor import DocumentProcessor

def test_stamp_pdf():
    """Test the specific problematic PDF"""
    
    pdf_path = "./temp/Stamp_Investor Deck.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"❌ PDF file not found: {pdf_path}")
        return False
    
    print(f"🔍 Testing problematic PDF: {os.path.basename(pdf_path)}")
    print(f"📏 File size: {os.path.getsize(pdf_path)} bytes")
    print("=" * 60)
    
    # Initialize processor
    processor = DocumentProcessor()
    
    # Test extraction with detailed logging
    try:
        print("🔄 Starting extraction process...")
        result = processor._process_pdf(pdf_path, os.path.basename(pdf_path))
        
        # Display detailed results
        print(f"\n📊 FINAL RESULTS:")
        print(f"   • Method used: {result['metadata'].get('extraction_method', 'unknown')}")
        print(f"   • Characters extracted: {result['metadata'].get('total_chars_extracted', 0)}")
        print(f"   • Pages processed: {result['metadata'].get('pages', 0)}")
        print(f"   • Pages with text: {result['metadata'].get('pages_with_text', 0)}")
        print(f"   • Content length: {len(result['content'])}")
        
        # Show all metadata
        print(f"\n🔍 METADATA:")
        for key, value in result['metadata'].items():
            print(f"   • {key}: {value}")
        
        if result['content']:
            print(f"\n📄 EXTRACTED CONTENT:")
            print("-" * 40)
            print(result['content'][:500])
            print("-" * 40)
            return True
        else:
            print(f"\n❌ NO CONTENT EXTRACTED")
            return False
            
    except Exception as e:
        print(f"❌ EXTRACTION FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_stamp_pdf()