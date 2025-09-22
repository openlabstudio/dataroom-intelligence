#!/usr/bin/env python3
"""
Quick test to see what GPT4o extracts from first pass
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from handlers.gpt4o_pdf_processor import GPT4oDirectProcessor

def test_quick():
    """Quick extraction test"""

    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ OPENAI_API_KEY not found")
        return

    processor = GPT4oDirectProcessor(api_key)
    pdf_path = "./docs/decks/Stamp_Investor Deck.pdf"

    print("=== Quick GPT4o Extraction Test ===\n")

    # Just get the full text extraction
    with open(pdf_path, 'rb') as f:
        file_obj = processor.client.files.create(file=f, purpose='assistants')
        print(f"✅ File uploaded: {file_obj.id}")

    # Extract text only
    extraction_prompt = """Extract all readable text from this PDF document.
Focus on preserving ALL financial information, valuations, and numbers.
Include slide 16 content completely."""

    print("📖 Extracting text...")
    response = processor.client.chat.completions.create(
        model='gpt-4o',
        messages=[{
            'role': 'user',
            'content': [
                {'type': 'text', 'text': extraction_prompt},
                {'type': 'image_url', 'image_url': {'url': f'file://{file_obj.id}'}}
            ]
        }],
        max_tokens=4096,
        temperature=0
    )

    text = response.choices[0].message.content
    print(f"✅ Extracted {len(text)} characters")

    # Search for valuation
    import re
    print("\n=== Searching for Valuation ===")

    # Look for 12M
    twelve_matches = re.findall(r'.{0,30}12.{0,30}', text, re.IGNORECASE)
    if twelve_matches:
        print(f"Found {len(twelve_matches)} mentions of '12':")
        for match in twelve_matches[:5]:
            print(f"  • {match.strip()}")
    else:
        print("❌ No '12' found in extraction")

    # Look for valoración
    val_matches = re.findall(r'.{0,30}valorac.{0,30}', text, re.IGNORECASE)
    if val_matches:
        print(f"\nFound {len(val_matches)} mentions of 'valoración':")
        for match in val_matches[:5]:
            print(f"  • {match.strip()}")
    else:
        print("❌ No 'valoración' found in extraction")

    # Clean up
    processor.client.files.delete(file_obj.id)
    print(f"\n🗑️ Cleaned up file {file_obj.id}")

if __name__ == "__main__":
    test_quick()