#!/usr/bin/env python3
"""
Direct test of market research with Tavily integration
Tests the actual agents without Slack integration
"""

import os
import sys
sys.path.append('/Users/gavalle/Documents/GitHub/dataroom-intelligence')

# Set production mode to use real Tavily
os.environ['TEST_MODE'] = 'false'
os.environ['PRODUCTION_MODE'] = 'true'

from agents.market_detection import MarketDetectionAgent, MarketProfile
from agents.competitive_intelligence import CompetitiveIntelligenceAgent
from utils.logger import get_logger

logger = get_logger(__name__)

def test_market_research_flow():
    """Test the full market research flow with Tavily"""
    print("🧪 TESTING MARKET RESEARCH WITH TAVILY")
    print("=" * 50)
    
    # Create mock market profile for water treatment startup
    market_profile = MarketProfile(
        solution="electrochemical wastewater treatment",
        sub_vertical="water treatment technology", 
        vertical="cleantech sustainability",
        industry="environmental technology",
        target_market="B2B pharmaceutical and cosmetics industries",
        geo_focus="Europe",
        business_model="Direct-to-Business, Technology Licensing",
        confidence_score=0.88
    )
    
    print(f"📊 Market Profile:")
    print(f"  • Solution: {market_profile.solution}")
    print(f"  • Sub-vertical: {market_profile.sub_vertical}")
    print(f"  • Vertical: {market_profile.vertical}")
    print(f"  • Target: {market_profile.target_market}")
    print()
    
    # Test Competitive Intelligence Agent
    print("🏢 TESTING COMPETITIVE INTELLIGENCE AGENT...")
    comp_agent = CompetitiveIntelligenceAgent()
    
    try:
        # Mock documents (not used in web search)
        mock_documents = []
        mock_summary = {'summary': 'AI-powered electrochemical wastewater treatment startup'}
        
        result = comp_agent.analyze_competitors(
            market_profile=market_profile.to_dict(),
            processed_documents=mock_documents,
            document_summary=mock_summary
        )
        
        print(f"✅ Competitive Intelligence Analysis Completed")
        
        # Test the new analyst formatter
        print("\n🎯 TESTING NEW ANALYST FORMATTER...")
        
        # Create mock market intelligence result structure
        from types import SimpleNamespace
        
        mock_result = SimpleNamespace()
        mock_result.market_profile = market_profile
        mock_result.competitive_analysis = result
        
        # Test new formatter
        from utils.analyst_formatter import format_analyst_market_research
        formatted_output = format_analyst_market_research(mock_result)
        
        print("\n" + "="*60)
        print("NEW ANALYST FORMAT OUTPUT:")
        print("="*60)
        print(formatted_output)
        print("="*60)
        
        # Also show old format for comparison
        result_dict = result.to_dict()
        independent = result_dict.get('independent_analysis', {})
        
        print(f"\n📋 OLD FORMAT COMPARISON:")
        print(f"Threat Level: {independent.get('threat_level', 'Unknown')}")
        print(f"Market Position: {independent.get('market_position', 'Unknown')}")
        print(f"Sources Count: {independent.get('sources_count', 0)}")
        print(f"Confidence: {independent.get('confidence_score', 0):.2f}")
        
        # Show competitors found
        competitors = []
        for level in ['solution_competitors', 'subvertical_competitors', 'vertical_competitors']:
            level_comps = independent.get(level, [])
            if level_comps:
                competitors.extend(level_comps)
        
        print(f"\n🏢 COMPETITORS FOUND ({len(competitors)} total):")
        for i, comp in enumerate(competitors[:5], 1):
            print(f"  {i}. {comp.get('name', 'Unknown')}")
            print(f"     Description: {comp.get('description', 'No description')[:80]}...")
            print(f"     URL: {comp.get('url', 'No URL')}")
            print()
        
        # Show web sources  
        all_sources = result_dict.get('all_sources', [])
        print(f"📚 WEB SOURCES USED ({len(all_sources)} total):")
        for i, source in enumerate(all_sources[:3], 1):
            print(f"  {i}. {source.get('title', 'Unknown')[:60]}...")
            print(f"     Domain: {source.get('domain', 'Unknown')}")
            print(f"     Type: {source.get('type', 'Unknown')}")
            print(f"     URL: {source.get('url', 'No URL')}")
            print()
        
        # Check if we have real competitor data vs empty
        if competitors and len(competitors) > 0:
            print("✅ SUCCESS: Found real competitors via Tavily")
            return True
        else:
            print("❌ FAIL: No competitors found")
            return False
            
    except Exception as e:
        print(f"❌ ERROR in competitive intelligence: {e}")
        logger.error(f"Competitive intelligence failed: {e}", exc_info=True)
        return False

def main():
    """Run the test"""
    print(f"🔧 Environment:")
    print(f"  TEST_MODE: {os.getenv('TEST_MODE')}")
    print(f"  PRODUCTION_MODE: {os.getenv('PRODUCTION_MODE')}")
    print(f"  TAVILY_API_KEY: {'✅ SET' if os.getenv('TAVILY_API_KEY') else '❌ MISSING'}")
    print()
    
    success = test_market_research_flow()
    
    print("\n📊 FINAL RESULT:")
    if success:
        print("✅ Tavily integration WORKING - Market research finds real competitors")
    else:
        print("❌ Tavily integration FAILED - No meaningful competitor data")
        
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)