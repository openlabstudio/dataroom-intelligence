#!/usr/bin/env python3
"""
Smoke Test Refactor para validar la capa analyst-friendly
"""

import sys
import os
import json
from pathlib import Path

# Agregar el directorio raíz al path para importar módulos
sys.path.insert(0, str(Path(__file__).parent.parent))

from handlers.ai_analyzer import AIAnalyzer

# ----------------------------
# Helpers de MOCK
# ----------------------------
# Nota: este parche añade verificaciones de la capa analyst-friendly.

class _DummyChoices:
    def __init__(self, content: str):
        self.message = type("M", (), {"content": content})

class _DummyResp:
    def __init__(self, content: str):
        self.choices = [_DummyChoices(content)]

def _setup_analyzer_mock(analyzer):
    """Setup mock para AIAnalyzer sin API calls"""

    def _fake_cc_create(*args, **kwargs):
        content = (
            "🔎 Análisis (MOCK)\n\n"
            "[COMPLETENESS-GUARD] The deck appears to be missing sections: team, competition, risks, why_now.\n"
            "**VALUE PROPOSITION:**\n"
            ":bombilla: Clear merchant value through automated tax compliance\n"
            "**FINANCIAL HIGHLIGHTS:**\n"
            ":dardo: €75M GMV mentioned in slide 7\n"
            "**MARKET ANALYSIS:**\n"
            "No specific market size mentioned.\n"
            ":gráfico_de_barras: Crecimiento positivo en merchants.\n"
            "**COMPETITORS:**\n"
            "No specific competitors mentioned.\n"
            "**GO-TO-MARKET STRATEGY:**\n"
            "Direct sales approach mentioned.\n"
            "**PRODUCT ROADMAP:**\n"
            ":cohete: API integration milestones outlined.\n"
            "\n**Next Steps:**\n"
            "• Placeholder pasos técnicos (/ask, /gaps, /reset)\n"
        )
        return _DummyResp(content)

    analyzer.client.chat.completions.create = _fake_cc_create  # type: ignore

def _create_mock_document():
    """Crea documento mock con JSON estructurado"""
    mock_data = {
        "financials": {
            "revenue": [],
            "gmv": [{"value": "€75M GMV", "slide": 7}],
            "vat": [{"value": "€14M VAT", "slide": 8}],
            "funding_rounds": [{"round": "Seed", "amount": "€2M", "currency": "EUR", "valuation": "€12M", "slide": 15}],
        },
        "team": [],  # Faltante
        "competition": [],  # Faltante
        "risks": [],  # Faltante
        "why_now": [],  # Faltante
        "slides_covered": list(range(1, 19))
    }

    return {
        "name": "test_deck.pdf",
        "type": "pdf",
        "content": json.dumps(mock_data),
        "metadata": {"extraction_method": "gpt4o_mock"}
    }

def _assert_emojis_unicode(text: str):
    """Verifica que no hay emojis sin renderizar"""
    problematic_emojis = [":dardo:", ":gráfico_de_barras:", ":cohete:", ":página_boca_arriba:",
                         ":bombilla:", ":espadas_cruzadas:", ":autopista:", ":bolsa_de_dinero:",
                         ":carpeta_de_archivos:", ":libreta_de_notas:", ":martillo:",
                         ":page_facing_up:", ":bulb:", ":bar_chart:", ":crossed_swords:",
                         ":motorway:", ":rocket:", ":moneybag:", ":speech_balloon:", ":mag:",
                         ":arrows_counterclockwise:"]

    for emoji in problematic_emojis:
        assert emoji not in text, f"Emoji sin renderizar encontrado: {emoji}"

    # Verificación adicional: no debe quedar ningún patrón :algo:
    import re
    remaining_aliases = re.findall(r':([a-z0-9_+-]+):', text)
    assert not remaining_aliases, f"Alias emoji residuales encontrados: {remaining_aliases}"

def _assert_not_found_substitution(text: str):
    """Verifica que mensajes genéricos se cambiaron por 'Not found in deck'"""
    assert "Not found in deck" in text, "No se aplicó la sustitución 'Not found in deck'"

def main():
    """Ejecuta el smoke test completo"""
    print("🔧 INICIANDO SMOKE TEST ANALYST-FRIENDLY")
    print("=" * 50)

    # Setup analyzer con mock
    print("⚙️ Setup de AIAnalyzer con mock...")
    analyzer = AIAnalyzer()
    _setup_analyzer_mock(analyzer)

    # Crear documento mock
    print("📄 Creando documento mock...")
    mock_doc = _create_mock_document()

    # Ejecutar análisis
    print("🧠 Ejecutando análisis...")
    analysis_text = analyzer.analyze_dataroom([mock_doc], {"total_documents": 1})
    print("✅ Análisis generado")

    print("🎨 Verificando emojis Unicode…")
    _assert_emojis_unicode(analysis_text)
    print("✅ Emojis Unicode OK")

    # ---- NUEVAS VERIFICACIONES ANALYST-FRIENDLY ----
    print("🧼 Verificando que no hay leak de COMPLETENESS-GUARD…")
    assert "[COMPLETENESS-GUARD]" not in analysis_text, "Quedó el bloque de meta [COMPLETENESS-GUARD]"
    print("✅ Sin meta prompt leaks")

    print("⚠️ Verificando bloque de Missing Sections humano…")
    assert "Missing Sections in Deck" in analysis_text, "Falta el bloque humano de secciones faltantes"
    assert "team" in analysis_text.lower() and "competition" in analysis_text.lower(), "No lista las secciones faltantes esperadas"
    print("✅ Bloque Missing Sections presente")

    print("🎯 Verificando Executive Summary…")
    assert "🎯 **EXECUTIVE SUMMARY**" in analysis_text, "Falta el bloque Executive Summary autogenerado"
    # Debe tener 3-5 bullets
    exec_bullets = [line for line in analysis_text.split('\n') if line.strip().startswith('• ') and 'EXECUTIVE SUMMARY' not in line]
    assert len(exec_bullets) >= 3, f"Executive Summary tiene {len(exec_bullets)} bullets, se esperan al menos 3"
    print("✅ Executive Summary presente con bullets suficientes")

    print("📝 Verificando Analyst Notes mejoradas…")
    # Verifica que hay notas para las secciones principales
    analyst_note_count = analysis_text.count("_Analyst Note:_")
    assert analyst_note_count >= 1, f"No se encontraron Analyst Notes, se esperan al menos 1"
    print(f"✅ Analyst Notes presentes ({analyst_note_count} encontradas)")

    print("🔍 Verificando inferencias marcadas…")
    inference_count = analysis_text.count("_Inference:_")
    action_count = analysis_text.count("_Action:_")
    if inference_count > 0:
        print(f"✅ Inferencias detectadas ({inference_count} _Inference:_, {action_count} _Action:_)")
    else:
        print("⚠️ No se detectaron inferencias (puede ser normal si todas las secciones están presentes)")

    print("🧭 Verificando Next Steps accionables…")
    lower = analysis_text.lower()
    assert "/ask" not in lower and "/gaps" not in lower and "/reset" not in lower, "Siguen apareciendo comandos internos en Next Steps"
    # Esperamos frases típicas del parche
    expected_snippets = [
        "request 12–24m p&l", "competitive landscape", "gtm plan", "cap table",
    ]
    assert any(s in lower for s in expected_snippets), "Next Steps no contiene acciones concretas esperadas"
    print("✅ Next Steps accionables OK")

    print("🧩 Verificando completeness-guard…")
    _assert_not_found_substitution(analysis_text)
    print("✅ 'Not found in deck' presente cuando falta sección")

    # NUEVAS: Executive Summary y ausencia de alias conocidos
    print("🎯 Verificando EXECUTIVE SUMMARY…")
    assert "EXECUTIVE SUMMARY" in analysis_text, "Falta EXECUTIVE SUMMARY"
    print("✅ Executive Summary presente")

    print("🚫 Verificando ausencia de alias conocidos …")
    # Toleramos alias desconocidos; pero los alias ES/EN conocidos deben haberse convertido a Unicode
    KNOWN = [
        ":página_boca_arriba:", ":bombilla:", ":gráfico_de_barras:", ":espadas_cruzadas:", ":autopista:",
        ":cohete:", ":bolsa_de_dinero:", ":bocadillo_de_diálogo:", ":lupa:", ":flechas_en_sentido_antihorario:",
        ":page_facing_up:", ":bulb:", ":bar_chart:", ":crossed_swords:", ":motorway:", ":rocket:",
        ":moneybag:", ":speech_balloon:", ":mag:", ":arrows_counterclockwise:", ":dardo:", ":gráfico_de_pastel:"
    ]
    assert not any(alias in analysis_text for alias in KNOWN), "Persisten alias conocidos; faltó mapeo a Unicode"
    print("✅ Alias conocidos mapeados a Unicode")

    print("\n" + "=" * 50)
    print("🎉 TODOS LOS TESTS ANALYST-FRIENDLY PASARON")
    print("📝 Muestra del análisis:")
    print("-" * 30)
    print(analysis_text[:500] + "..." if len(analysis_text) > 500 else analysis_text)
    print("-" * 30)

    return True

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\n✅ SMOKE TEST COMPLETADO EXITOSAMENTE")
            sys.exit(0)
        else:
            print("\n❌ SMOKE TEST FALLÓ")
            sys.exit(1)
    except Exception as e:
        print(f"\n💥 ERROR EN SMOKE TEST: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)