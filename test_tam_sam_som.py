#!/usr/bin/env python3
"""
Test script to verify TAM/SAM/SOM and competitor extraction
"""

import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from handlers.doc_processor import DocumentProcessor

def search_content_for_info(content):
    """Search extracted content for specific business information"""
    content_lower = content.lower()
    
    print("🔍 SEARCHING FOR KEY BUSINESS INFORMATION:")
    print("=" * 60)
    
    # Search for TAM/SAM/SOM
    tam_indicators = ['tam', 'total addressable market', 'mercado total', '70b', '€70b']
    sam_indicators = ['sam', 'serviceable addressable market', 'mercado disponible', '35b', '€35b']
    som_indicators = ['som', 'serviceable obtainable market', 'mercado obtenible', '1.5b', '€1.5b']
    
    print("📊 TAM/SAM/SOM METRICS:")
    tam_found = any(indicator in content_lower for indicator in tam_indicators)
    sam_found = any(indicator in content_lower for indicator in sam_indicators)
    som_found = any(indicator in content_lower for indicator in som_indicators)
    
    print(f"   • TAM: {'✅ FOUND' if tam_found else '❌ NOT FOUND'}")
    print(f"   • SAM: {'✅ FOUND' if sam_found else '❌ NOT FOUND'}")
    print(f"   • SOM: {'✅ FOUND' if som_found else '❌ NOT FOUND'}")
    
    # Search for competitors
    competitors = ['woonivers', 'global blue', 'jtu', 'planet', 'bfeel', 'b.feel', 'zapp', 'vatfree', 'safety tax free']
    
    print("\n🏢 COMPETITOR INFORMATION:")
    competitors_found = []
    for competitor in competitors:
        if competitor in content_lower:
            competitors_found.append(competitor)
    
    print(f"   • Competitors found: {len(competitors_found)}/8")
    if competitors_found:
        print(f"   • Found: {', '.join(competitors_found)}")
    else:
        print("   • No competitors detected")
    
    # Search for market opportunity keywords
    market_keywords = ['turismo', 'comercio', 'fintech', 'oportunidad', 'mercado']
    
    print("\n🎯 MARKET OPPORTUNITY KEYWORDS:")
    market_found = []
    for keyword in market_keywords:
        if keyword in content_lower:
            market_found.append(keyword)
    
    print(f"   • Keywords found: {', '.join(market_found) if market_found else 'None'}")
    
    # Show relevant excerpts
    print(f"\n📄 CONTENT EXCERPTS WITH NUMBERS:")
    lines = content.split('\n')
    number_lines = [line.strip() for line in lines if any(char.isdigit() for char in line) and any(char in line for char in ['€', '$', 'B', 'M', '%'])]
    
    if number_lines:
        for i, line in enumerate(number_lines[:5]):  # Show first 5 lines with numbers
            print(f"   {i+1}. {line}")
    else:
        print("   • No lines with financial metrics found")
    
    return {
        'tam_sam_som': tam_found or sam_found or som_found,
        'competitors': len(competitors_found),
        'market_keywords': len(market_found)
    }

def main():
    """Main test function"""
    pdf_path = "./temp/Stamp_Investor Deck.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"❌ PDF file not found: {pdf_path}")
        return False
    
    print("🧪 TAM/SAM/SOM & Competitor Analysis Test")
    print("=" * 60)
    
    # Process with enhanced OCR
    processor = DocumentProcessor()
    result = processor._process_pdf(pdf_path, os.path.basename(pdf_path))
    
    print(f"📊 OCR EXTRACTION RESULTS:")
    print(f"   • Pages processed: {result['metadata'].get('pages_processed', 0)}")
    print(f"   • Characters extracted: {result['metadata'].get('total_chars_extracted', 0)}")
    print(f"   • Extraction method: {result['metadata'].get('extraction_method', 'unknown')}")
    
    if result['content']:
        # Search for business information
        analysis = search_content_for_info(result['content'])
        
        print(f"\n🎯 ANALYSIS SUMMARY:")
        print(f"   • TAM/SAM/SOM detected: {'✅ YES' if analysis['tam_sam_som'] else '❌ NO'}")
        print(f"   • Competitors detected: {analysis['competitors']}/8")
        print(f"   • Market keywords: {analysis['market_keywords']}/5")
        
        # Show success rate
        success_score = 0
        if analysis['tam_sam_som']: success_score += 40
        if analysis['competitors'] >= 3: success_score += 40
        if analysis['market_keywords'] >= 2: success_score += 20
        
        print(f"\n📈 SUCCESS SCORE: {success_score}/100")
        
        return success_score >= 60
    else:
        print("❌ No content extracted")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print(f"\n✅ TEST PASSED: Business information successfully extracted!")
    else:
        print(f"\n❌ TEST FAILED: Critical business information missing")