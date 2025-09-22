#!/usr/bin/env python3
"""
Quick test to verify valuation extraction from slide 16
"""
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from handlers.gpt4o_pdf_processor import GPT4oDirectProcessor
import re

def test_valuation_extraction():
    """Test if slide 16 valuation is being extracted"""

    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ OPENAI_API_KEY not found")
        return

    processor = GPT4oDirectProcessor(api_key)
    pdf_path = "/Users/gavalle/Documents/GitHub/dataroom-intelligence/docs/decks/Stamp_Investor Deck.pdf"

    print("=== Testing PDF Text Extraction for Valuation ===\n")

    # Process the PDF
    result = processor.process_pdf_document(pdf_path, "Stamp_Investor Deck.pdf")

    if result and 'full_text' in result:
        extracted_text = result['full_text']

        # Look for valuation-related terms
        valuation_patterns = [
            r'12M.*[Vv]aloración',
            r'[Vv]aloración.*12M',
            r'Pre.*Money.*12M',
            r'12M.*Pre.*Money',
            r'valoración.*12',
            r'12.*valoración',
            r'Valoración.*Pre.*Money'
        ]

        print("=== Searching for Valuation Patterns ===")
        found_patterns = []

        for pattern in valuation_patterns:
            matches = re.finditer(pattern, extracted_text, re.IGNORECASE)
            for match in matches:
                found_patterns.append(match.group())
                print(f"✓ Found: '{match.group()}'")

        if not found_patterns:
            print("❌ No valuation patterns found!")

            # Let's search for any mention of "12" or "valoración"
            print("\n=== Searching for '12' mentions ===")
            twelve_matches = re.finditer(r'.{0,50}12.{0,50}', extracted_text, re.IGNORECASE)
            for i, match in enumerate(twelve_matches):
                if i < 10:  # Limit to first 10
                    print(f"12 context {i+1}: '{match.group().strip()}'")

            print("\n=== Searching for 'valoración' mentions ===")
            val_matches = re.finditer(r'.{0,50}valoración.{0,50}', extracted_text, re.IGNORECASE)
            for i, match in enumerate(val_matches):
                if i < 5:  # Limit to first 5
                    print(f"Valoración context {i+1}: '{match.group().strip()}'")
        else:
            print(f"\n✅ Found {len(found_patterns)} valuation references!")

        # Check text length to see if extraction is complete
        print(f"\n=== Text Extraction Stats ===")
        print(f"Total extracted text length: {len(extracted_text)} characters")
        print(f"Number of pages likely extracted: ~{len(extracted_text) // 2000}")

        # Look for slide markers to verify slide 16 was processed
        slide_markers = re.findall(r'slide?\s*\d+', extracted_text, re.IGNORECASE)
        print(f"Slide markers found: {slide_markers}")

    else:
        print(f"❌ PDF processing failed or no full_text found")
        if result:
            print(f"Result keys: {list(result.keys())}")
        else:
            print("Result is None")

if __name__ == "__main__":
    test_valuation_extraction()