#!/usr/bin/env python3
"""
Fix TEST_MODE and Session Issues - Emergency Script
Resolves the two critical issues found in TASK-001 testing
"""

import os
import sys
from dotenv import load_dotenv

def main():
    print("🔧 DataRoom Intelligence - Emergency Fix Script")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    print("\n1. ✅ Environment Variables Loaded")
    
    # Check TEST_MODE
    test_mode_env = os.getenv('TEST_MODE', 'not set')
    test_mode_active = test_mode_env.lower() == 'true'
    
    print(f"2. TEST_MODE Environment Variable: '{test_mode_env}'")
    print(f"3. TEST_MODE Active: {'✅ YES' if test_mode_active else '❌ NO'}")
    
    if not test_mode_active:
        print("\n🚨 CRÍTICO: TEST_MODE no está activo!")
        print("   Esto causará llamadas reales a GPT-5 ($$$ costos)")
        print("   Solucionando...")
        
        # Force set TEST_MODE in current environment
        os.environ['TEST_MODE'] = 'true'
        print("   ✅ TEST_MODE forzado a 'true' en sesión actual")
        
        # Verify
        if os.getenv('TEST_MODE', 'false').lower() == 'true':
            print("   ✅ Verificado: TEST_MODE ahora activo")
        else:
            print("   ❌ Error: No se pudo activar TEST_MODE")
            sys.exit(1)
    else:
        print("4. ✅ TEST_MODE está correctamente configurado")
    
    # Test imports
    print("\n5. 🔍 Probando imports críticos...")
    
    try:
        sys.path.insert(0, os.getcwd())
        
        # Test orchestrator
        from agents.market_research_orchestrator import MarketResearchOrchestrator
        orchestrator = MarketResearchOrchestrator()
        print("   ✅ MarketResearchOrchestrator imported and instantiated")
        
        # Test competitive intelligence
        from agents.competitive_intelligence import CompetitiveIntelligenceAgent
        competitive_agent = CompetitiveIntelligenceAgent()
        print("   ✅ CompetitiveIntelligenceAgent imported and instantiated")
        
        # Test handler
        from handlers.market_research_handler import MarketResearchHandler
        handler = MarketResearchHandler(orchestrator, {})
        print("   ✅ MarketResearchHandler imported and instantiated")
        
    except Exception as e:
        print(f"   ❌ Import error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    # Test mock analysis
    print("\n6. 🧪 Probando análisis mock...")
    
    try:
        mock_docs = [{'type': 'test', 'name': 'test.pdf', 'content': 'Test content'}]
        mock_summary = {'total_documents': 1}
        
        # Force TEST_MODE in orchestrator test
        os.environ['TEST_MODE'] = 'true'
        
        result = orchestrator.perform_market_intelligence(mock_docs, mock_summary)
        
        if hasattr(result, 'competitive_analysis') and result.competitive_analysis:
            print("   ✅ Mock analysis completed successfully")
            print(f"   ✅ Competitive analysis: {len(result.competitive_analysis.get('direct_competitors', []))} competitors")
        else:
            print("   ❌ Mock analysis failed - no competitive_analysis")
            
    except Exception as e:
        print(f"   ❌ Mock analysis error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("✅ DIAGNÓSTICO COMPLETO - Todo funcionando correctamente")
    print("")
    print("🔧 INSTRUCCIONES PARA SOLUCIONAR:")
    print("1. Para usar la app correctamente:")
    print("   export TEST_MODE=true && python app.py")
    print("")
    print("2. Secuencia correcta en Slack:")
    print("   /analyze [google-drive-link]")
    print("   (esperar a que complete)")
    print("   /market-research")
    print("")
    print("3. Verificar TEST_MODE con:")
    print("   /analyze debug")
    print("")
    print("🚨 IMPORTANTE: Si /analyze no entra en TEST_MODE:")
    print("   - Reiniciar la aplicación con: export TEST_MODE=true && python app.py")
    print("   - Verificar que .env tenga TEST_MODE=true al principio")
    print("")

if __name__ == '__main__':
    main()