"""
Tests unitarios para validar seguridad y robustez de la capa analyst-friendly
Enfoque en emojis, Executive Summary y validaciones básicas
"""

import re
import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from handlers.ai_analyzer import AIAnalyzer


def test_known_emoji_mapping_no_alias_left():
    """Verifica que el mapeo de emojis conocidos funciona correctamente"""
    test_text = ":página_boca_arriba: :bar_chart: :rocket: :bombilla: :gráfico_de_barras:"
    mapped = AIAnalyzer._map_emojis(test_text)

    # Debe contener Unicode
    assert "📄" in mapped, "Falta emoji 📄 para :página_boca_arriba:"
    assert "📊" in mapped, "Falta emoji 📊 para :bar_chart:"
    assert "🚀" in mapped, "Falta emoji 🚀 para :rocket:"
    assert "💡" in mapped, "Falta emoji 💡 para :bombilla:"

    # No debe contener aliases originales
    assert ":página_boca_arriba:" not in mapped, "Alias :página_boca_arriba: no fue mapeado"
    assert ":bar_chart:" not in mapped, "Alias :bar_chart: no fue mapeado"
    assert ":rocket:" not in mapped, "Alias :rocket: no fue mapeado"
    assert ":bombilla:" not in mapped, "Alias :bombilla: no fue mapeado"


def test_executive_summary_generation():
    """Verifica que _inject_exec_summary_top funciona con datos mock"""
    mock_text = "**VALUE PROPOSITION:**\nTest content\n**FINANCIAL HIGHLIGHTS:**\nMore content"
    mock_extracted = {
        "financials": {
            "gmv": [{"value": "€75M GMV", "slide": 7}],
            "vat": [{"value": "€14M VAT", "slide": 8}],
            "funding_rounds": [{"round": "Seed", "amount": "€2M", "slide": 15}]
        }
    }

    result = AIAnalyzer._inject_exec_summary_top(mock_text, mock_extracted)

    # Debe contener Executive Summary
    assert "🎯 **EXECUTIVE SUMMARY**" in result, "Falta el header Executive Summary"

    # Debe estar al inicio
    assert result.startswith("🎯 **EXECUTIVE SUMMARY**"), "Executive Summary no está al inicio"

    # Debe contener bullets basados en los datos
    assert "• " in result, "No hay bullets en Executive Summary"


def test_strip_completeness_meta():
    """Verifica que _strip_completeness_meta elimina correctamente los leaks"""
    test_text = """
    [COMPLETENESS-GUARD] The deck appears to be missing sections: team.
    **FINANCIAL HIGHLIGHTS:**
    Some content here
    [COMPLETENESS-GUARD] Another guard message.
    More content
    """

    cleaned = AIAnalyzer._strip_completeness_meta(test_text)

    assert "[COMPLETENESS-GUARD]" not in cleaned, "No se eliminaron los COMPLETENESS-GUARD"
    assert "**FINANCIAL HIGHLIGHTS:**" in cleaned, "Se eliminó contenido válido"
    assert "Some content here" in cleaned, "Se eliminó contenido válido"


def test_format_missing_sections_human():
    """Verifica el formateo humano de secciones faltantes"""
    missing = ["team", "competition", "risks"]
    slides_range = (1, 18)

    result = AIAnalyzer._format_missing_sections_human(missing, slides_range)

    assert "⚠️ **Missing Sections in Deck**" in result, "Falta el header de secciones faltantes"
    assert "team, competition, risks" in result, "No lista todas las secciones faltantes"
    assert "1–18" in result, "No muestra el rango de slides correcto"
    assert "diligence gap" in result, "Falta el mensaje de gap de diligencia"


def test_emoji_dictionary_completeness():
    """Verifica que el diccionario de emojis tiene cobertura ES/EN"""
    emoji_dict = AIAnalyzer._EMOJI_ES2UNICODE

    # Verificar algunos emojis clave en español
    assert ":página_boca_arriba:" in emoji_dict, "Falta emoji español :página_boca_arriba:"
    assert ":gráfico_de_barras:" in emoji_dict, "Falta emoji español :gráfico_de_barras:"
    assert ":cohete:" in emoji_dict, "Falta emoji español :cohete:"

    # Verificar algunos emojis clave en inglés
    assert ":page_facing_up:" in emoji_dict, "Falta emoji inglés :page_facing_up:"
    assert ":bar_chart:" in emoji_dict, "Falta emoji inglés :bar_chart:"
    assert ":rocket:" in emoji_dict, "Falta emoji inglés :rocket:"

    # Verificar que todos mapean a Unicode
    for alias, unicode_char in emoji_dict.items():
        assert len(unicode_char) >= 1, f"Emoji {alias} mapea a string vacío"
        assert not unicode_char.startswith(":"), f"Emoji {alias} mapea a otro alias {unicode_char}"


if __name__ == "__main__":
    print("🧪 Running anchor and safety tests...")

    test_known_emoji_mapping_no_alias_left()
    print("✅ Emoji mapping test passed")

    test_executive_summary_generation()
    print("✅ Executive summary generation test passed")

    test_strip_completeness_meta()
    print("✅ Completeness meta stripping test passed")

    test_format_missing_sections_human()
    print("✅ Missing sections formatting test passed")

    test_emoji_dictionary_completeness()
    print("✅ Emoji dictionary completeness test passed")

    print("✅ All anchor and safety tests passed!")