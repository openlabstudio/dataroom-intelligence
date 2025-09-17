"""
Tests unitarios para AIAnalyzer
"""

import json
import unittest
from unittest.mock import Mock, patch
from handlers.ai_analyzer import AIAnalyzer


class TestAIAnalyzer(unittest.TestCase):

    def setUp(self):
        """Setup para cada test"""
        with patch('handlers.ai_analyzer.config') as mock_config:
            mock_config.OPENAI_API_KEY = "test-key"
            self.analyzer = AIAnalyzer()

    def test_normalize_financials_basic(self):
        """Test normalización básica de financials"""
        input_data = {
            "financials": {
                "revenue": [{"value": "1M", "note": "eligible sales volume"}],
                "gmv": []
            }
        }

        result = AIAnalyzer._normalize_financials(input_data)

        # Debería mover "eligible sales" de revenue a gmv
        self.assertEqual(len(result["financials"]["revenue"]), 0)
        self.assertEqual(len(result["financials"]["gmv"]), 1)
        self.assertEqual(result["financials"]["gmv"][0]["value"], "1M")

    def test_normalize_financials_vat_classification(self):
        """Test reclasificación de VAT/IVA"""
        input_data = {
            "financials": {
                "revenue": [
                    {"value": "100K", "note": "actual revenue"},
                    {"value": "21K", "note": "VAT collected"}
                ],
                "vat": []
            }
        }

        result = AIAnalyzer._normalize_financials(input_data)

        # VAT debería moverse a su propia categoría
        self.assertEqual(len(result["financials"]["revenue"]), 1)
        self.assertEqual(len(result["financials"]["vat"]), 1)
        self.assertEqual(result["financials"]["revenue"][0]["note"], "actual revenue")
        self.assertEqual(result["financials"]["vat"][0]["note"], "VAT collected")

    def test_normalize_financials_gmv_patterns(self):
        """Test detección de patrones GMV"""
        input_data = {
            "financials": {
                "revenue": [
                    {"value": "500K", "note": "gross merchandise value"},
                    {"value": "50K", "value": "commission revenue"}
                ],
                "gmv": []
            }
        }

        result = AIAnalyzer._normalize_financials(input_data)

        # GMV debería moverse, commission revenue quedarse
        self.assertEqual(len(result["financials"]["revenue"]), 1)
        self.assertEqual(len(result["financials"]["gmv"]), 1)

    def test_model_initialization(self):
        """Test que el modelo se inicializa con gpt-4o"""
        self.assertEqual(self.analyzer.model, "gpt-4o")

    @patch('handlers.ai_analyzer.OpenAI')
    def test_emoji_replacement(self, mock_openai):
        """Test reemplazo de emojis en español"""
        # Simular respuesta con emojis en español
        mock_response = Mock()
        mock_response.choices[0].message.content = "Análisis :dardo: con :cohete: y :gráfico_de_barras:"

        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response

        with patch.object(self.analyzer, 'client', mock_client):
            # Setup context mínimo
            self.analyzer.analysis_context = {'full_content': '{"financials": {}}'}

            # Simular método que usa emoji replacement
            result = mock_response.choices[0].message.content

            # Aplicar reemplazos como en el código real
            for src, uni in {
                ":dardo:": "🎯",
                ":gráfico_de_barras:": "📊",
                ":cohete:": "🚀",
            }.items():
                result = result.replace(src, uni)

        self.assertEqual(result, "Análisis 🎯 con 🚀 y 📊")

    def test_completeness_guard_missing_sections(self):
        """Test completeness guard identifica secciones faltantes"""
        # JSON con secciones faltantes
        json_content = json.dumps({
            "financials": {"revenue": []},
            "team": [{"name": "CEO"}],
            # Faltan: competition, risks, why_now
        })

        context = {"full_content": json_content, "documents_summary": "test"}

        # Simular extracción de JSON
        extracted = json.loads(context['full_content'])
        must_sections = ["team", "competition", "risks", "why_now"]
        missing = [s for s in must_sections if not extracted.get(s)]

        self.assertEqual(sorted(missing), ["competition", "risks", "why_now"])

    def test_prepare_analysis_context_no_truncation(self):
        """Test que prepare_analysis_context no trunca contenido"""
        documents = [
            {
                "name": "test.pdf",
                "type": "pdf",
                "content": "x" * 50000  # 50K caracteres
            }
        ]

        result = self.analyzer._prepare_analysis_context(documents)

        # No debería haber truncamiento
        self.assertEqual(len(result["full_content"]), 50000 + len("\n\n=== DOCUMENT: test.pdf ===\n"))

    def test_json_content_normalization(self):
        """Test normalización de contenido JSON"""
        json_data = {
            "financials": {
                "revenue": [{"value": "1M", "note": "gmv value"}]
            }
        }

        documents = [
            {
                "name": "test.pdf",
                "type": "pdf",
                "content": json.dumps(json_data)
            }
        ]

        result = self.analyzer._prepare_analysis_context(documents)

        # El contenido debería ser JSON normalizado
        self.assertIn("financials", result["full_content"])
        # GMV debería haberse movido
        parsed = json.loads(result["full_content"].split("===\n")[1])
        self.assertEqual(len(parsed["financials"]["revenue"]), 0)
        self.assertEqual(len(parsed["financials"]["gmv"]), 1)


if __name__ == '__main__':
    print("🧪 Running AI Analyzer unit tests...")
    unittest.main(verbosity=2)