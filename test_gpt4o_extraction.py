#!/usr/bin/env python3
"""
Test what GPT-4o actually extracts from Stamp PDF
"""
import os
import sys
import json
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from handlers.gpt4o_pdf_processor import GPT4oDirectProcessor

def test_extraction():
    """Test GPT-4o extraction to see what's captured"""

    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ OPENAI_API_KEY not found")
        return

    processor = GPT4oDirectProcessor(api_key)
    pdf_path = "./docs/decks/Stamp_Investor Deck.pdf"

    print("=== GPT-4o Extraction Test ===\n")
    print("Processing Stamp PDF...")

    result = processor.process_pdf_document(pdf_path, "Stamp_Investor Deck.pdf")

    if not result:
        print("❌ Processing failed")
        return

    print(f"✅ Processing complete\n")

    # Check structured data
    if 'structured_data' in result:
        data = result['structured_data']

        print("=== Financial Data Extracted ===")
        if 'financials' in data:
            financials = data['financials']

            # Check funding rounds
            if 'funding_rounds' in financials:
                rounds = financials['funding_rounds']
                print(f"\n📊 Funding Rounds Found: {len(rounds)}")
                for r in rounds:
                    print(f"  • Round: {r.get('round', 'N/A')}")
                    print(f"    Amount: {r.get('currency', '')} {r.get('amount', 'N/A')}")
                    print(f"    Valuation: {r.get('valuation', 'NOT CAPTURED')}")
                    print(f"    Slide: {r.get('slide', 'N/A')}")
            else:
                print("❌ No funding_rounds in financials")

            # Check other financial metrics
            for metric in ['revenue', 'gmv', 'burn', 'runway_months']:
                if metric in financials and financials[metric]:
                    print(f"\n📈 {metric.upper()}: {len(financials[metric])} entries")
                    for entry in financials[metric][:2]:  # First 2 entries
                        print(f"  • {entry}")
        else:
            print("❌ No financials section found")

        # Check slides covered
        if 'slides_covered' in data:
            slides = data['slides_covered']
            print(f"\n📄 Slides Covered: {slides}")
            if 16 in slides:
                print("  ✅ Slide 16 was processed")
            else:
                print("  ❌ Slide 16 NOT in covered slides!")

    # Check full text extraction
    if 'full_text' in result:
        text = result['full_text']
        print(f"\n=== Full Text Analysis ===")
        print(f"Total length: {len(text)} characters")

        # Search for valuation mentions
        import re

        # Search for 12M
        twelve_patterns = re.findall(r'.{0,50}12M.{0,50}', text, re.IGNORECASE)
        if twelve_patterns:
            print(f"\n✅ Found '12M' {len(twelve_patterns)} times:")
            for p in twelve_patterns[:3]:
                print(f"  • {p.strip()}")
        else:
            # Try with spaces
            twelve_patterns = re.findall(r'.{0,50}12\s*M.{0,50}', text, re.IGNORECASE)
            if twelve_patterns:
                print(f"\n✅ Found '12 M' {len(twelve_patterns)} times:")
                for p in twelve_patterns[:3]:
                    print(f"  • {p.strip()}")
            else:
                print("\n❌ No '12M' found in full text")

        # Search for valoración
        val_patterns = re.findall(r'.{0,50}valorac.{0,50}', text, re.IGNORECASE)
        if val_patterns:
            print(f"\n✅ Found 'valoración' {len(val_patterns)} times:")
            for p in val_patterns[:3]:
                print(f"  • {p.strip()}")
        else:
            print("\n❌ No 'valoración' found in full text")

        # Search for Pre-Money
        pre_patterns = re.findall(r'.{0,50}pre.?money.{0,50}', text, re.IGNORECASE)
        if pre_patterns:
            print(f"\n✅ Found 'Pre-Money' {len(pre_patterns)} times:")
            for p in pre_patterns[:3]:
                print(f"  • {p.strip()}")

    else:
        print("\n❌ No full_text in result")

    # Save result for inspection
    output_file = "stamp_extraction_result.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"\n💾 Full result saved to {output_file}")

if __name__ == "__main__":
    test_extraction()