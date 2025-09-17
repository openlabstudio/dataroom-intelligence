"""
Tests unitarios para GPT4oDirectProcessor
"""

import json
import unittest
from unittest.mock import Mock, patch, MagicMock
from handlers.gpt4o_pdf_processor import GPT4oDirectProcessor


class TestGPT4oProcessor(unittest.TestCase):

    def setUp(self):
        """Setup para cada test"""
        self.processor = GPT4oDirectProcessor("test-key")

    def test_json_schema_prompt_contains_required_fields(self):
        """Test que el prompt del schema JSON contiene los campos requeridos"""
        prompt = self.processor._json_schema_prompt()

        # Verificar que contiene los campos críticos
        required_fields = [
            "financials", "revenue", "gmv", "vat", "burn",
            "runway_months", "funding_rounds", "traction",
            "team", "business_model", "gtm", "competition",
            "risks", "why_now", "slides_covered"
        ]

        for field in required_fields:
            self.assertIn(field, prompt)

        # Verificar reglas importantes
        self.assertIn("STRICT JSON", prompt)
        self.assertIn("slide reference", prompt)
        self.assertIn("eligible sales/GMV", prompt)

    def test_validate_json_basic(self):
        """Test validación JSON básica"""
        valid_json = '{"test": "value"}'
        result = self.processor._validate_json(valid_json)
        self.assertEqual(result, {"test": "value"})

    def test_validate_json_with_code_fences(self):
        """Test validación JSON con code fences"""
        json_with_fences = '```json\n{"test": "value"}\n```'
        result = self.processor._validate_json(json_with_fences)
        self.assertEqual(result, {"test": "value"})

    def test_merge_extractions_slides_covered(self):
        """Test merge de extracciones con slides_covered sin duplicados"""
        base = {"slides_covered": [1, 2]}
        inc = {"slides_covered": [2, 3]}

        result = self.processor._merge_extractions(base, inc)
        self.assertEqual(sorted(result["slides_covered"]), [1, 2, 3])

    def test_merge_extractions_lists(self):
        """Test merge de listas"""
        base = {"financials": {"revenue": [{"value": "100K", "slide": 1}]}}
        inc = {"financials": {"revenue": [{"value": "200K", "slide": 2}]}}

        result = self.processor._merge_extractions(base, inc)
        self.assertEqual(len(result["financials"]["revenue"]), 2)

    @patch('handlers.gpt4o_pdf_processor.OpenAI')
    def test_extract_pass_valid_response(self, mock_openai):
        """Test extracción válida con respuesta JSON"""
        # Mock response
        mock_response = Mock()
        mock_response.choices[0].message.content = json.dumps({
            "financials": {"revenue": []},
            "slides_covered": [1, 2]
        })

        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        self.processor.client = mock_client

        result = self.processor._extract_pass("test-file-id")

        # Verificar que se llama con los parámetros correctos
        mock_client.chat.completions.create.assert_called_once()
        call_args = mock_client.chat.completions.create.call_args

        self.assertEqual(call_args[1]['model'], 'gpt-4o')
        self.assertEqual(call_args[1]['max_tokens'], 6000)
        self.assertEqual(call_args[1]['response_format'], {"type": "json_object"})

        # Verificar resultado
        self.assertIn("financials", result)
        self.assertIn("slides_covered", result)

    def test_extract_pass_with_exclude_slides(self):
        """Test extracción con slides excluidos"""
        with patch.object(self.processor, 'client') as mock_client:
            mock_response = Mock()
            mock_response.choices[0].message.content = '{"slides_covered": [3]}'
            mock_client.chat.completions.create.return_value = mock_response

            result = self.processor._extract_pass("test-file-id", exclude_slides=[1, 2])

            # Verificar que el prompt incluye exclusión
            call_args = mock_client.chat.completions.create.call_args[1]
            messages = call_args['messages']
            content = messages[0]['content'][0]['text']
            self.assertIn("NOT IN [1, 2]", content)


if __name__ == '__main__':
    print("🧪 Running GPT4o Processor unit tests...")
    unittest.main(verbosity=2)