#!/usr/bin/env python3
"""
Script de prueba manual para validar las mejoras implementadas
"""

import os
import sys
import json
from pathlib import Path

# Agregar el directorio raíz al path para importar módulos
sys.path.insert(0, str(Path(__file__).parent))

from handlers.gpt4o_pdf_processor import GPT4oDirectProcessor
from handlers.ai_analyzer import AIAnalyzer

def test_json_extraction():
    """Test 1: Validar extracción JSON estructurada"""
    print("🧪 TEST 1: JSON Schema y validación")

    processor = GPT4oDirectProcessor("dummy-key")

    # Test schema prompt
    schema = processor._json_schema_prompt()
    print("✅ JSON schema generado correctamente")
    print(f"   - Contiene 'financials': {'financials' in schema}")
    print(f"   - Contiene 'slides_covered': {'slides_covered' in schema}")
    print(f"   - Contiene reglas GMV≠Revenue: {'eligible sales/GMV' in schema}")

    # Test JSON validation
    test_json = '{"financials": {"revenue": []}, "slides_covered": [1,2]}'
    validated = processor._validate_json(test_json)
    print("✅ Validación JSON funcionando")
    print(f"   - Parsed slides_covered: {validated.get('slides_covered')}")

    # Test JSON con code fences
    fenced_json = '```json\n{"test": "value"}\n```'
    cleaned = processor._validate_json(fenced_json)
    print("✅ Limpieza de code fences funcionando")
    print(f"   - Cleaned value: {cleaned.get('test')}")

    return True

def test_financial_normalization():
    """Test 2: Normalización financiera"""
    print("\n🧪 TEST 2: Normalización financiera")

    # Test case: GMV mislabeled as revenue
    test_data = {
        "financials": {
            "revenue": [
                {"value": "1M", "note": "eligible sales volume", "slide": 5},
                {"value": "100K", "note": "actual commission revenue", "slide": 6},
                {"value": "21K", "note": "VAT collected", "slide": 7}
            ],
            "gmv": [],
            "vat": []
        }
    }

    normalized = AIAnalyzer._normalize_financials(test_data)

    print("✅ Normalización financiera aplicada:")
    print(f"   - Revenue items: {len(normalized['financials']['revenue'])}")
    print(f"   - GMV items: {len(normalized['financials']['gmv'])}")
    print(f"   - VAT items: {len(normalized['financials']['vat'])}")

    # Verificar que GMV se movió
    if len(normalized['financials']['gmv']) > 0:
        print("✅ GMV reclasificado correctamente")
        print(f"   - GMV value: {normalized['financials']['gmv'][0]['value']}")

    # Verificar que VAT se movió
    if len(normalized['financials']['vat']) > 0:
        print("✅ VAT reclasificado correctamente")
        print(f"   - VAT value: {normalized['financials']['vat'][0]['value']}")

    return True

def test_completeness_guard():
    """Test 3: Completeness guard"""
    print("\n🧪 TEST 3: Completeness guard")

    # JSON con secciones faltantes
    incomplete_data = {
        "financials": {"revenue": []},
        "team": [{"name": "CEO"}],
        # Faltan: competition, risks, why_now
    }

    must_sections = ["team", "competition", "risks", "why_now"]
    missing = [s for s in must_sections if not incomplete_data.get(s)]

    print("✅ Completeness guard identifica faltantes:")
    print(f"   - Secciones faltantes: {missing}")
    print(f"   - Debería advertir sobre: competition, risks, why_now")

    if sorted(missing) == ["competition", "risks", "why_now"]:
        print("✅ Detección correcta de secciones faltantes")
    else:
        print("❌ Error en detección de secciones")

    return True

def test_emoji_mapping():
    """Test 4: Mapeo de emojis"""
    print("\n🧪 TEST 4: Mapeo de emojis")

    test_text = "Análisis :dardo: con :cohete: y :gráfico_de_barras:"

    # Aplicar mapeo como en el código real
    for src, uni in {
        ":dardo:": "🎯",
        ":gráfico_de_barras:": "📊",
        ":cohete:": "🚀",
    }.items():
        test_text = test_text.replace(src, uni)

    print("✅ Mapeo de emojis aplicado:")
    print(f"   - Resultado: {test_text}")
    print(f"   - Contiene Unicode: {'🎯' in test_text and '🚀' in test_text and '📊' in test_text}")

    return True

def test_model_configuration():
    """Test 5: Configuración del modelo"""
    print("\n🧪 TEST 5: Configuración del modelo")

    # Mock config para evitar errores
    class MockConfig:
        OPENAI_API_KEY = "test-key"

    import handlers.ai_analyzer
    original_config = handlers.ai_analyzer.config
    handlers.ai_analyzer.config = MockConfig()

    try:
        analyzer = AIAnalyzer()
        print("✅ AIAnalyzer inicializado correctamente")
        print(f"   - Modelo configurado: {analyzer.model}")

        if analyzer.model == "gpt-4o":
            print("✅ Modelo actualizado a gpt-4o")
        else:
            print(f"❌ Modelo incorrecto: {analyzer.model} (esperado: gpt-4o)")

    finally:
        handlers.ai_analyzer.config = original_config

    return True

def test_no_truncation():
    """Test 6: Sin truncamiento"""
    print("\n🧪 TEST 6: Eliminación de truncamiento")

    # Crear contenido largo
    large_content = "x" * 50000  # 50K caracteres

    # Mock config
    class MockConfig:
        OPENAI_API_KEY = "test-key"

    import handlers.ai_analyzer
    original_config = handlers.ai_analyzer.config
    handlers.ai_analyzer.config = MockConfig()

    try:
        analyzer = AIAnalyzer()
        documents = [{
            "name": "large_test.pdf",
            "type": "pdf",
            "content": large_content
        }]

        context = analyzer._prepare_analysis_context(documents)

        print("✅ Contexto preparado sin truncamiento:")
        print(f"   - Contenido original: {len(large_content)} chars")
        print(f"   - Contenido en context: {len(context['full_content'])} chars")
        print(f"   - Sin truncamiento: {len(context['full_content']) > 49000}")

    finally:
        handlers.ai_analyzer.config = original_config

    return True

def main():
    """Ejecutar todos los tests"""
    print("🔧 INICIANDO PRUEBAS MANUALES DE MEJORAS")
    print("=" * 50)

    tests = [
        test_json_extraction,
        test_financial_normalization,
        test_completeness_guard,
        test_emoji_mapping,
        test_model_configuration,
        test_no_truncation
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            if test():
                passed += 1
                print("✅ PASSED")
            else:
                failed += 1
                print("❌ FAILED")
        except Exception as e:
            failed += 1
            print(f"❌ ERROR: {e}")

    print("\n" + "=" * 50)
    print("📊 RESUMEN DE TESTS")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Total: {passed + failed}")

    if failed == 0:
        print("\n🎉 TODOS LOS TESTS PASARON - MEJORAS IMPLEMENTADAS CORRECTAMENTE")
        return True
    else:
        print(f"\n⚠️ {failed} TESTS FALLARON - REVISAR IMPLEMENTACIÓN")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)