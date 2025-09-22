#!/usr/bin/env python3
"""
Test the ai_analyzer directly with STAMP data to see if it extracts valuation
"""
import sys
import os
import json

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from handlers.ai_analyzer import AIAnalyzer
from handlers.gpt4o_pdf_processor import GPT4oDirectProcessor

def test_ai_analyzer_valuation():
    """Test if AI analyzer extracts valuation from processed STAMP data"""

    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ OPENAI_API_KEY not found")
        return

    print("=== Testing AI Analyzer Valuation Extraction ===\n")

    # Step 1: Get processed documents like the system would
    processor = GPT4oDirectProcessor(api_key)
    pdf_path = "/Users/gavalle/Documents/GitHub/dataroom-intelligence/docs/decks/Stamp_Investor Deck.pdf"

    print("📄 Processing PDF...")
    result = processor.process_pdf_document(pdf_path, "Stamp_Investor Deck.pdf")

    if not result or 'structured_data' not in result:
        print("❌ Failed to get structured data from PDF processor")
        return

    # Step 2: Test AI analyzer
    analyzer = AIAnalyzer()
    processed_documents = [result]

    # Create a document summary for the analyzer
    document_summary = {
        'total_documents': 1,
        'document_types': {'pdf': 1},
        'total_pages': 18,
        'documents': [{'name': 'Stamp_Investor Deck.pdf', 'type': 'pdf', 'pages': 18}]
    }

    print("🧠 Running AI analyzer...")
    analysis_result = analyzer.analyze_dataroom(processed_documents, document_summary)

    print("\n=== AI Analyzer Results ===")
    print(f"Analysis success: {analysis_result.get('ok', False)}")

    if analysis_result.get('ok'):
        summary = analysis_result.get('slack_ready_content', '')
        print(f"Summary length: {len(summary)} characters")

        # Look for valuation patterns in the output
        valuation_patterns = [
            r'12M.*[Vv]aloración',
            r'[Vv]aloración.*12M',
            r'Pre.*Money.*12M',
            r'12M.*Pre.*Money',
            r'valoración.*12',
            r'12.*valoración',
            r'Valoración.*Pre.*Money',
            r'\€12M',
            r'12.*million.*valuation',
            r'valuation.*12.*million'
        ]

        print("\n=== Searching for Valuation in AI Analyzer Output ===")
        import re
        found_patterns = []

        for pattern in valuation_patterns:
            matches = re.finditer(pattern, summary, re.IGNORECASE)
            for match in matches:
                found_patterns.append(match.group())
                print(f"✓ Found: '{match.group()}'")

        if not found_patterns:
            print("❌ No valuation patterns found in AI analyzer output!")

            # Let's search for any "12" mention
            twelve_matches = re.finditer(r'.{0,50}12.{0,50}', summary, re.IGNORECASE)
            print("\n=== Any '12' mentions in output ===")
            for i, match in enumerate(twelve_matches):
                if i < 5:
                    print(f"12 context {i+1}: '{match.group().strip()}'")

            # Print first 1000 chars of summary for debugging
            print(f"\n=== First 1000 chars of AI output ===")
            print(summary[:1000])
            print("...")
        else:
            print(f"\n✅ Found {len(found_patterns)} valuation references in AI output!")

    else:
        print(f"❌ AI analyzer failed: {analysis_result.get('error', 'Unknown error')}")

    # Step 3: Check what's actually in the structured data
    print(f"\n=== Structured Data Debug ===")
    structured_data = result.get('structured_data', {})

    # Look for funding/financial data in structured extraction
    if 'financials' in structured_data:
        print("Financial data found:")
        financials = structured_data['financials']
        for key, value in financials.items():
            print(f"  {key}: {value}")
    else:
        print("No 'financials' section in structured data")

    # Print all top-level keys
    print(f"Structured data keys: {list(structured_data.keys())}")

if __name__ == "__main__":
    test_ai_analyzer_valuation()