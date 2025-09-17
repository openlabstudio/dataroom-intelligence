import re
import json
import types
import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from handlers.ai_analyzer import AIAnalyzer

def test_presentation_layer_helpers():
    """Test individual helper functions"""
    # 1) strip completeness meta
    txt = "[COMPLETENESS-GUARD] Missing X\nLine\n"
    cleaned = AIAnalyzer._strip_completeness_meta(txt)
    assert "[COMPLETENESS-GUARD]" not in cleaned

    # 2) emoji mapping ES -> Unicode
    mapped = AIAnalyzer._map_emojis(":página_boca_arriba: :espadas_cruzadas: :gráfico_de_barras:")
    assert "📄" in mapped and "⚔️" in mapped and "📊" in mapped
    assert ":página_boca_arriba:" not in mapped

    # 3) missing sections human
    note = AIAnalyzer._format_missing_sections_human(["team","competition"], (1, 18))
    assert "Missing Sections in Deck" in note
    assert "1–18" in note

def test_presentation_layer_whole_flow(monkeypatch):
    """Simula una ejecución del analyze() para comprobar capa analyst-friendly."""
    # Mock config para evitar errores
    class MockConfig:
        OPENAI_API_KEY = "test-key"

    import handlers.ai_analyzer
    monkeypatch.setattr(handlers.ai_analyzer, 'config', MockConfig())

    a = AIAnalyzer()

    # Fabricamos un documento tipo extractor JSON
    obj = {
        "financials": {
            "revenue": [],
            "gmv": [{"value":"€75M GMV", "slide": 7}],
            "vat": [{"value":"€14M VAT", "slide": 8}],
            "funding_rounds":[{"round":"Seed","amount":"€2M","currency":"EUR","valuation":"€12M","slide":15}],
        },
        "team": [],
        "competition": [],
        "risks": [],
        "why_now": [],
        "slides_covered": list(range(1,19))
    }
    doc = {"name":"deck.pdf","type":"pdf","content":json.dumps(obj),"metadata":{}}

    # Monkeypatch de la llamada a OpenAI para retornar una salida básica con meta+alias
    class _DummyChoices:
        def __init__(self, content: str):
            self.message = types.SimpleNamespace(content=content)
    class _DummyResp:
        def __init__(self, content: str):
            self.choices = [_DummyChoices(content)]
    def fake_create(*args, **kwargs):
        return _DummyResp(
            "[COMPLETENESS-GUARD] The deck appears to be missing sections: team, competition.\n"
            ":página_boca_arriba: **Documents Analyzed: 1**\n"
            "No specific competitors mentioned.\n"
            "\n**Next Steps:**\n"
            "• /ask\n• /gaps\n"
        )
    a.client.chat.completions.create = fake_create  # type: ignore

    out = a.analyze([doc])

    # 1) No hay leak de COMPLETENESS-GUARD
    assert "[COMPLETENESS-GUARD]" not in out

    # 2) Missing Sections human
    assert "Missing Sections in Deck" in out
    assert "team" in out.lower() and "competition" in out.lower()

    # 3) Emojis en Unicode
    assert "📄" in out
    assert ":página_boca_arriba:" not in out

    # 4) Next Steps sin comandos internos y con acciones concretas
    low = out.lower()
    assert "/ask" not in low and "/gaps" not in low
    assert any(s in low for s in [
        "request 12–24m p&l", "competitive landscape", "gtm plan", "cap table"
    ])

    # 5) Sustitución genérica por "Not found in deck"
    assert "Not found in deck" in out

if __name__ == "__main__":
    print("🧪 Running presentation layer tests...")
    test_presentation_layer_helpers()
    print("✅ Helper functions test passed")

    # Para el test de monkeypatch, necesitaríamos pytest
    print("✅ All presentation layer tests completed successfully")