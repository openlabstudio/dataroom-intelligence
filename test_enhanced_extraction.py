#!/usr/bin/env python3
"""
Test script for enhanced Tavily extraction with URLs and metadata
SPRINT 1 - FASE 2D: Verify we're getting proper URLs and meeting minimum requirements
"""

import os
import sys
from utils.web_search import WebSearchEngine
from utils.logger import get_logger

logger = get_logger(__name__)

def test_enhanced_extraction():
    """Test that we get proper URLs and metadata from Tavily searches"""
    
    # Force test mode off to test real Tavily if available
    original_test_mode = os.getenv('TEST_MODE')
    os.environ['TEST_MODE'] = 'false'
    
    try:
        # Initialize search engine
        search_engine = WebSearchEngine(provider='tavily')
        
        # Test case: Electrochemical wastewater treatment (from previous test)
        test_queries = [
            "Electrochemical wastewater treatment competitors market analysis 2024",
            "wastewater treatment regulatory requirements EU US compliance",
            "electrochemical water treatment companies funding raised"
        ]
        
        print("\n" + "="*80)
        print("TESTING ENHANCED TAVILY EXTRACTION - SPRINT 1")
        print("="*80)
        
        # Execute searches
        results = search_engine.search_multiple(test_queries, max_results_per_query=5)
        
        # Check results structure
        print(f"\n✅ Total sources found: {results.get('sources_count', 0)}")
        print(f"✅ Search completed in: {results.get('search_time_seconds', 0)} seconds")
        
        # Check competitors with URLs
        competitors = results.get('competitors_found', [])
        print(f"\n📊 COMPETITORS FOUND: {len(competitors)}")
        for i, comp in enumerate(competitors[:5], 1):
            if isinstance(comp, dict):
                print(f"\n  {i}. {comp.get('name', 'Unknown')}")
                print(f"     Description: {comp.get('description', '')[:100]}")
                print(f"     URL: {comp.get('url', 'NO URL!')}")
                print(f"     Domain: {comp.get('source_domain', 'NO DOMAIN!')}")
            else:
                print(f"\n  {i}. {comp} (STRING FORMAT - NO URL!)")
        
        # Check expert insights with URLs
        insights = results.get('expert_insights', [])
        print(f"\n🧠 EXPERT INSIGHTS: {len(insights)}")
        for i, insight in enumerate(insights[:3], 1):
            if isinstance(insight, dict):
                print(f"\n  {i}. Insight: {insight.get('insight', '')[:100]}...")
                print(f"     Source: {insight.get('source', 'NO SOURCE!')}")
                print(f"     URL: {insight.get('url', 'NO URL!')}")
                print(f"     Type: {insight.get('source_type', 'general')}")
            else:
                print(f"\n  {i}. {str(insight)[:100]}... (STRING FORMAT - NO URL!)")
        
        # Check regulatory insights
        regulatory = results.get('regulatory_insights', [])
        print(f"\n⚖️ REGULATORY INSIGHTS: {len(regulatory)}")
        for i, reg in enumerate(regulatory[:2], 1):
            if isinstance(reg, dict):
                print(f"\n  {i}. Regulation: {reg.get('regulation', '')[:100]}...")
                print(f"     Source: {reg.get('source', 'NO SOURCE!')}")
                print(f"     URL: {reg.get('url', 'NO URL!')}")
                print(f"     Jurisdiction: {reg.get('jurisdiction', 'Unknown')}")
        
        # Check all sources for citation
        all_sources = results.get('all_sources', [])
        print(f"\n📚 ALL SOURCES FOR CITATION: {len(all_sources)}")
        for i, source in enumerate(all_sources[:5], 1):
            print(f"\n  {i}. {source.get('title', 'NO TITLE!')}")
            print(f"     URL: {source.get('url', 'NO URL!')}")
            print(f"     Domain: {source.get('domain', 'NO DOMAIN!')}")
            print(f"     Type: {source.get('type', 'general')}")
            print(f"     Score: {source.get('relevance_score', 0)}")
        
        # Check source quality breakdown
        quality = results.get('source_quality_breakdown', {})
        print(f"\n📊 SOURCE QUALITY BREAKDOWN:")
        print(f"  Academic: {quality.get('academic', 0)}")
        print(f"  Industry Reports: {quality.get('industry_report', 0)}")
        print(f"  Financial: {quality.get('financial', 0)}")
        print(f"  Regulatory: {quality.get('regulatory', 0)}")
        
        # CHECK MINIMUM REQUIREMENTS
        print("\n" + "="*80)
        print("MINIMUM REQUIREMENTS CHECK:")
        print("="*80)
        
        min_sources_met = len(all_sources) >= 10
        min_competitors_met = len(competitors) >= 5
        
        print(f"\n✅ Sources: {len(all_sources)}/10 required - {'✅ MET' if min_sources_met else '❌ NOT MET'}")
        print(f"✅ Competitors: {len(competitors)}/5 required - {'✅ MET' if min_competitors_met else '❌ NOT MET'}")
        
        # Check if we have URLs
        sources_with_urls = sum(1 for s in all_sources if s.get('url'))
        competitors_with_urls = sum(1 for c in competitors if isinstance(c, dict) and c.get('url'))
        
        print(f"\n🔗 Sources with URLs: {sources_with_urls}/{len(all_sources)}")
        print(f"🔗 Competitors with URLs: {competitors_with_urls}/{len(competitors)}")
        
        if min_sources_met and min_competitors_met and sources_with_urls >= 10:
            print("\n🎉 SUCCESS! Enhanced extraction meets all requirements!")
        else:
            print("\n⚠️ WARNING: Not all requirements met. Need to adjust search queries or increase limits.")
        
    except Exception as e:
        print(f"\n❌ ERROR during test: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Restore original test mode
        if original_test_mode:
            os.environ['TEST_MODE'] = original_test_mode
        elif 'TEST_MODE' in os.environ:
            del os.environ['TEST_MODE']

if __name__ == "__main__":
    test_enhanced_extraction()