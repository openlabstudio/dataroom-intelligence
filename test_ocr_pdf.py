#!/usr/bin/env python3
"""
Test script for OCR PDF extraction
Tests the new OCR functionality with problematic PDFs
"""

import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from handlers.doc_processor import DocumentProcessor

def test_pdf_extraction(pdf_path: str):
    """Test PDF extraction with all available methods"""
    
    if not os.path.exists(pdf_path):
        print(f"❌ PDF file not found: {pdf_path}")
        return False
    
    print(f"🔍 Testing PDF extraction: {os.path.basename(pdf_path)}")
    print(f"📏 File size: {os.path.getsize(pdf_path)} bytes")
    print("=" * 60)
    
    # Initialize processor
    processor = DocumentProcessor()
    
    # Test extraction
    try:
        result = processor._process_pdf(pdf_path, os.path.basename(pdf_path))
        
        # Display results
        print(f"📊 EXTRACTION RESULTS:")
        print(f"   • Method used: {result['metadata'].get('extraction_method', 'unknown')}")
        print(f"   • Characters extracted: {result['metadata'].get('total_chars_extracted', 0)}")
        print(f"   • Pages processed: {result['metadata'].get('pages', 0)}")
        print(f"   • Pages with text: {result['metadata'].get('pages_with_text', 0)}")
        print(f"   • Content length: {len(result['content'])}")
        
        if 'error' in result['metadata']:
            print(f"   • Error: {result['metadata']['error']}")
        
        # Show sample content
        if result['content']:
            print(f"\n📄 SAMPLE CONTENT (first 300 chars):")
            print("-" * 40)
            sample = result['content'][:300].replace('\n', ' ').strip()
            print(f"{sample}...")
            print("-" * 40)
            
            # Count meaningful content
            words = result['content'].split()
            meaningful_words = [w for w in words if len(w) > 2 and w.isalpha()]
            print(f"   • Total words: {len(words)}")
            print(f"   • Meaningful words: {len(meaningful_words)}")
            
            return len(meaningful_words) > 10  # Success if more than 10 meaningful words
        else:
            print(f"   • No content extracted")
            return False
            
    except Exception as e:
        print(f"❌ EXTRACTION FAILED: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 OCR PDF Extraction Test")
    print("=" * 60)
    
    # Look for PDF files in temp directory
    temp_dir = "./temp"
    if os.path.exists(temp_dir):
        pdf_files = [f for f in os.listdir(temp_dir) if f.endswith('.pdf')]
        
        if pdf_files:
            print(f"Found {len(pdf_files)} PDF file(s) in temp directory:")
            for pdf_file in pdf_files:
                print(f"  • {pdf_file}")
            
            # Test the first PDF
            pdf_path = os.path.join(temp_dir, pdf_files[0])
            success = test_pdf_extraction(pdf_path)
            
            if success:
                print(f"\n✅ SUCCESS: OCR extraction working!")
            else:
                print(f"\n❌ FAILED: OCR extraction not working properly")
                
        else:
            print(f"⚠️ No PDF files found in {temp_dir}")
            print("Please run /analyze command first to download a PDF")
    else:
        print(f"⚠️ Temp directory not found: {temp_dir}")
        print("Please run /analyze command first to create temp directory")

if __name__ == "__main__":
    main()