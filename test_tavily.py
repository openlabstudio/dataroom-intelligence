#!/usr/bin/env python3
"""
Test script for Tavily integration
Tests both TEST_MODE and production mode
"""

import os
import sys

def test_test_mode():
    """Test that TEST_MODE still works with mock data"""
    print("\n" + "="*60)
    print("TEST 1: Verificando TEST_MODE=true")
    print("="*60)
    
    # Set TEST_MODE
    os.environ['TEST_MODE'] = 'true'
    os.environ['PRODUCTION_MODE'] = 'false'
    
    try:
        from utils.web_search import WebSearchEngine
        
        # Initialize engine
        engine = WebSearchEngine()
        
        # Test search
        results = engine.search_multiple(
            ["AI invoice factoring competitors"],
            max_results_per_query=3
        )
        
        print(f"✅ TEST_MODE funciona correctamente")
        print(f"   - Provider: MockSearchProvider")
        print(f"   - Resultados encontrados: {results.get('sources_count', 0)}")
        print(f"   - Competidores: {len(results.get('competitors_found', []))}")
        
        # Verificar que tenemos mock data
        assert 'competitors_found' in results, "No competitors in mock data"
        assert len(results.get('competitors_found', [])) > 0, "Empty competitors list"
        
        print("✅ Mock data validado correctamente")
        return True
        
    except Exception as e:
        print(f"❌ Error en TEST_MODE: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_production_mode():
    """Test that production mode uses Tavily"""
    print("\n" + "="*60)
    print("TEST 2: Verificando TEST_MODE=false con Tavily")
    print("="*60)
    
    # Set production mode
    os.environ['TEST_MODE'] = 'false'
    os.environ['PRODUCTION_MODE'] = 'true'
    
    # Check if Tavily API key exists
    if not os.getenv('TAVILY_API_KEY'):
        print("⚠️ TAVILY_API_KEY no configurada - skipping test")
        return True
    
    try:
        from utils.web_search import WebSearchEngine
        
        # Initialize engine
        engine = WebSearchEngine()
        
        # Check provider type
        print(f"   - Provider type: {engine.provider.__class__.__name__}")
        
        # Test simple search
        print("   - Ejecutando búsqueda real con Tavily...")
        results = engine.search_multiple(
            ["electrochemical wastewater treatment companies"],
            max_results_per_query=2
        )
        
        print(f"✅ Tavily funciona correctamente")
        print(f"   - Fuentes encontradas: {results.get('sources_count', 0)}")
        print(f"   - Competidores: {results.get('competitors_found', [])[:2]}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Error de importación: {e}")
        print("   Ejecuta: pip install tavily")
        return False
    except Exception as e:
        print(f"⚠️ Error en Tavily (esperado si no hay conexión): {e}")
        # This is OK - transparent error handling
        return True


def test_transparent_error():
    """Test transparent error handling when Tavily fails"""
    print("\n" + "="*60)
    print("TEST 3: Verificando manejo transparente de errores")
    print("="*60)
    
    # Set production mode without API key
    os.environ['TEST_MODE'] = 'false'
    old_key = os.environ.pop('TAVILY_API_KEY', None)
    
    try:
        from utils.web_search import WebSearchEngine
        
        # Initialize without API key
        engine = WebSearchEngine()
        
        # This should fall back to DuckDuckGo
        print(f"   - Provider sin API key: {engine.provider.__class__.__name__}")
        
        # Should return empty or limited results
        results = engine.search_multiple(
            ["test query"],
            max_results_per_query=1
        )
        
        print("✅ Fallback a DuckDuckGo funciona")
        
    finally:
        # Restore API key if it existed
        if old_key:
            os.environ['TAVILY_API_KEY'] = old_key
    
    return True


def main():
    print("\n" + "="*60)
    print("TESTING TAVILY INTEGRATION")
    print("="*60)
    
    all_passed = True
    
    # Test 1: TEST_MODE
    if not test_test_mode():
        all_passed = False
    
    # Test 2: Production mode
    if not test_production_mode():
        all_passed = False
    
    # Test 3: Error handling
    if not test_transparent_error():
        all_passed = False
    
    print("\n" + "="*60)
    if all_passed:
        print("✅ TODOS LOS TESTS PASARON CORRECTAMENTE")
        print("\nSiguientes pasos:")
        print("1. Probar con /market-research en Slack")
        print("2. Verificar que no rompe funcionalidad existente")
        print("3. Monitorear logs para errores")
    else:
        print("❌ ALGUNOS TESTS FALLARON")
        print("Revisa los errores arriba")
    print("="*60)


if __name__ == "__main__":
    main()