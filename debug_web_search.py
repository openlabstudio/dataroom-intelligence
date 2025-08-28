#!/usr/bin/env python3
"""
Debug script to test web search functionality
Tests both DuckDuckGo and Tavily (if API key available)
"""

import os
import sys
sys.path.append('/Users/gavalle/Documents/GitHub/dataroom-intelligence')

from utils.web_search import WebSearchEngine, TavilyProvider, DuckDuckGoProvider
from utils.logger import get_logger

logger = get_logger(__name__)

def test_tavily_connection():
    """Test if Tavily API is working"""
    print("\n🔍 TESTING TAVILY CONNECTION...")
    
    api_key = os.getenv('TAVILY_API_KEY')
    print(f"API Key configured: {'✅ YES' if api_key else '❌ NO'}")
    
    if not api_key:
        print("❌ Tavily API key not found in environment")
        return False
    
    try:
        provider = TavilyProvider()
        results = provider.search("electrochemical wastewater treatment competitors", max_results=3)
        print(f"✅ Tavily search returned {len(results)} results")
        
        for i, result in enumerate(results[:2]):
            print(f"  {i+1}. {result.get('title', 'No title')[:60]}")
            print(f"     URL: {result.get('url', 'No URL')}")
            print(f"     Snippet: {result.get('snippet', 'No snippet')[:100]}...")
            print()
        
        return len(results) > 0
        
    except Exception as e:
        print(f"❌ Tavily test failed: {e}")
        return False

def test_duckduckgo_connection():
    """Test DuckDuckGo functionality"""
    print("\n🦆 TESTING DUCKDUCKGO CONNECTION...")
    
    try:
        provider = DuckDuckGoProvider()
        results = provider.search("electrochemical wastewater treatment competitors", max_results=3)
        print(f"✅ DuckDuckGo search returned {len(results)} results")
        
        for i, result in enumerate(results[:2]):
            print(f"  {i+1}. {result.get('title', 'No title')[:60]}")
            print(f"     URL: {result.get('url', 'No URL')}")
            print(f"     Snippet: {result.get('snippet', 'No snippet')[:100]}...")
            print()
        
        return len(results) > 0
        
    except Exception as e:
        print(f"❌ DuckDuckGo test failed: {e}")
        return False

def test_web_search_engine():
    """Test the main WebSearchEngine class"""
    print("\n⚙️ TESTING WEB SEARCH ENGINE...")
    
    # Test with TEST_MODE=false to use real providers
    os.environ['TEST_MODE'] = 'false'
    
    try:
        # Test default initialization (should use Tavily if available, else DuckDuckGo)
        engine = WebSearchEngine()
        print(f"✅ WebSearchEngine initialized with provider: {engine.provider_name}")
        
        queries = [
            "electrochemical wastewater treatment competitors",
            "water treatment technology market leaders"
        ]
        
        results = engine.search_multiple(queries, max_results_per_query=2)
        
        print(f"✅ Search completed with {results.get('sources_count', 0)} total sources")
        print(f"Competitors found: {len(results.get('competitors_found', []))}")
        print(f"Expert insights: {len(results.get('expert_insights', []))}")
        
        # Show sample competitors
        competitors = results.get('competitors_found', [])[:3]
        if competitors:
            print("\n🏢 SAMPLE COMPETITORS FOUND:")
            for comp in competitors:
                print(f"  • {comp.get('name', 'Unknown')}: {comp.get('description', 'No description')[:60]}...")
        else:
            print("\n❌ NO COMPETITORS FOUND")
        
        return len(competitors) > 0
        
    except Exception as e:
        print(f"❌ WebSearchEngine test failed: {e}")
        return False
    finally:
        # Reset TEST_MODE
        os.environ['TEST_MODE'] = 'true'

def main():
    """Run all debug tests"""
    print("🔬 WEB SEARCH DEBUG TESTS")
    print("=" * 50)
    
    print(f"Current TEST_MODE: {os.getenv('TEST_MODE', 'not set')}")
    print(f"Current working dir: {os.getcwd()}")
    
    tavily_ok = test_tavily_connection()
    duckduckgo_ok = test_duckduckgo_connection()
    engine_ok = test_web_search_engine()
    
    print("\n📊 SUMMARY:")
    print(f"Tavily API: {'✅ Working' if tavily_ok else '❌ Failed'}")
    print(f"DuckDuckGo: {'✅ Working' if duckduckgo_ok else '❌ Failed'}")
    print(f"WebSearchEngine: {'✅ Working' if engine_ok else '❌ Failed'}")
    
    if not any([tavily_ok, duckduckgo_ok]):
        print("\n🚨 CRITICAL: No working search providers found!")
        
    return tavily_ok or duckduckgo_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)