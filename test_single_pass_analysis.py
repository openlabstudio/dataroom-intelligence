#!/usr/bin/env python3
"""
Option A: Single-pass analysis that processes PDF directly to VC analyst summary
Avoiding the extract-then-analyze pattern that loses information
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from openai import OpenAI

def single_pass_analysis():
    """Process PDF directly to analyst summary in one pass"""

    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ OPENAI_API_KEY not found")
        return

    client = OpenAI(api_key=api_key)
    pdf_path = "./docs/decks/Stamp_Investor Deck.pdf"

    print("=== Single-Pass Analysis (Option A) ===\n")

    # Upload file
    print("📤 Uploading PDF...")
    with open(pdf_path, 'rb') as f:
        file_obj = client.files.create(file=f, purpose='assistants')
    print(f"✅ File uploaded: {file_obj.id}\n")

    # Single comprehensive prompt based on Gemini's output format
    analyst_prompt = """You are a senior venture capital analyst. Analyze this startup pitch deck and produce a comprehensive investment analysis.

REQUIREMENTS:
1. Extract EVERY piece of financial data, especially valuations (pre-money, post-money)
2. Include ALL metrics with specific numbers and time periods
3. Reference slide/page numbers for each fact
4. Use the exact format below

OUTPUT FORMAT:

EXECUTIVE SUMMARY
[One paragraph with company description, key traction metric, and current funding round WITH VALUATION]

COMPANY
• [What the company does] [Page X]
• [Vision/Mission] [Page X]
• [Locations if stated] [Page X]

BUSINESS MODEL
• [Type: B2B/B2C/etc.] [Page X]
• [Revenue model with specific pricing] [Page X]
• [Key offerings: freemium/premium details] [Page X]

METRICS & TRACTION
• [TAM/SAM/SOM with specific amounts] [Page X]
• [Growth metrics with percentages] [Page X]
• [User/merchant/transaction numbers] [Page X]
• [GMV/Revenue with amounts and periods] [Page X]
• [Any other KPIs] [Page X]

TEAM & FUNDING
• [Current round: amount and valuation - MUST INCLUDE VALUATION IF PRESENT] [Page X]
• [Team size] [Page X]
• [Founders with backgrounds] [Page X]
• [Projections post-funding] [Page X]

CUSTOMERS / LOGOS
• [List of notable customers] [Page X]

CRITICAL GAPS
• [Missing information that would be needed for investment decision]

IMPORTANT:
- Extract the €12M pre-money valuation from slide 16 if present
- Include ALL financial figures with currency symbols
- Use exact numbers from the deck, don't round or approximate"""

    print("🧠 Processing with single-pass analysis...")
    response = client.chat.completions.create(
        model='gpt-4o',
        messages=[{
            'role': 'user',
            'content': [
                {'type': 'text', 'text': analyst_prompt},
                {'type': 'file', 'file': {'file_id': file_obj.id}}
            ]
        }],
        max_tokens=4000,
        temperature=0.1
    )

    analysis = response.choices[0].message.content
    print("✅ Analysis complete\n")

    # Save output
    with open('docs/outputs analyze/option_a_single_pass.txt', 'w', encoding='utf-8') as f:
        f.write(analysis)
    print("💾 Output saved to docs/outputs analyze/option_a_single_pass.txt\n")

    # Check for valuation
    import re
    print("=== Checking for Valuation ===")
    valuation_found = False

    # Search for 12M valuation
    if re.search(r'12M.*valuation|valuation.*12M|12M.*pre-money|pre-money.*12M', analysis, re.IGNORECASE):
        print("✅ Found €12M valuation in output!")
        valuation_found = True
    else:
        print("❌ €12M valuation NOT found in output")

    # Search for any mention of valuation
    val_matches = re.findall(r'.{0,50}valuation.{0,50}', analysis, re.IGNORECASE)
    if val_matches:
        print(f"\nValuation mentions ({len(val_matches)}):")
        for match in val_matches[:3]:
            print(f"  • {match.strip()}")

    # Print first part of analysis
    print("\n=== Analysis Preview (first 1500 chars) ===")
    print(analysis[:1500])
    if len(analysis) > 1500:
        print("...")

    # Clean up
    client.files.delete(file_obj.id)
    print(f"\n🗑️ Cleaned up file {file_obj.id}")

    return analysis, valuation_found

if __name__ == "__main__":
    analysis, has_valuation = single_pass_analysis()

    print("\n" + "="*60)
    print("SUMMARY:")
    print(f"✅ Single-pass analysis complete")
    print(f"{'✅' if has_valuation else '❌'} €12M valuation {'captured' if has_valuation else 'missing'}")
    print("="*60)