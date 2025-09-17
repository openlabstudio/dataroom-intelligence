*** a/scripts/smoke_test_refactor.py
--- b/scripts/smoke_test_refactor.py
***************
*** 21,26 ****
--- 21,28 ----
  from ai_analyzer import AIAnalyzer

  # ----------------------------
  # Helpers de MOCK
  # ----------------------------
+ # Nota: este parche añade verificaciones de la capa analyst-friendly.

  class _DummyChoices:
      def __init__(self, content: str):
          self.message = type("M", (), {"content": content})
***************
*** 68,78 ****
      def _fake_cc_create(*args, **kwargs):
          content = (
              "🔎 Análisis (MOCK)\n\n"
              ":dardo: Foco en mercado B2B\n"
              "No specific competitors mentioned.\n"
              ":gráfico_de_barras: Crecimiento positivo.\n"
              ":cohete: Próximos pasos: levantar ronda.\n"
          )
          return _DummyResp(content)

      analyzer.client.chat.completions.create = _fake_cc_create  # type: ignore
--- 70,85 ----
      def _fake_cc_create(*args, **kwargs):
          content = (
              "🔎 Análisis (MOCK)\n\n"
+             "[COMPLETENESS-GUARD] The deck appears to be missing sections: team, competition, risks, why_now.\n"
              ":dardo: Foco en mercado B2B\n"
              "No specific competitors mentioned.\n"
              ":gráfico_de_barras: Crecimiento positivo.\n"
              ":cohete: Próximos pasos: levantar ronda.\n"
+             "\n**Next Steps:**\n"
+             "• Placeholder pasos técnicos (/ask, /gaps, /reset)\n"
          )
          return _DummyResp(content)

      analyzer.client.chat.completions.create = _fake_cc_create  # type: ignore
***************
*** 112,117 ****
--- 119,153 ----
      print("✅ Análisis generado")

      print("🎨 Verificando emojis Unicode…")
      _assert_emojis_unicode(analysis_text)
      print("✅ Emojis Unicode OK")
+
+     # ---- NUEVAS VERIFICACIONES ANALYST-FRIENDLY ----
+     print("🧼 Verificando que no hay leak de COMPLETENESS-GUARD…")
+     assert "[COMPLETENESS-GUARD]" not in analysis_text, "Quedó el bloque de meta [COMPLETENESS-GUARD]"
+     print("✅ Sin meta prompt leaks")
+
+     print("⚠️ Verificando bloque de Missing Sections humano…")
+     assert "Missing Sections in Deck" in analysis_text, "Falta el bloque humano de secciones faltantes"
+     assert "team" in analysis_text.lower() and "competition" in analysis_text.lower(), "No lista las secciones faltantes esperadas"
+     print("✅ Bloque Missing Sections presente")
+
+     print("📝 Verificando Analyst Notes…")
+     # Buscamos un patrón de Analyst Note inyectado (heurístico)
+     assert "Analyst Note" in analysis_text, "No se inyectó Analyst Note"
+     print("✅ Analyst Notes presentes")
+
+     print("🧭 Verificando Next Steps accionables…")
+     lower = analysis_text.lower()
+     assert "/ask" not in lower and "/gaps" not in lower and "/reset" not in lower, "Siguen apareciendo comandos internos en Next Steps"
+     # Esperamos frases típicas del parche
+     expected_snippets = [
+         "request 12–24m p&l", "competitive landscape", "gtm plan", "cap table",
+     ]
+     assert any(s in lower for s in expected_snippets), "Next Steps no contiene acciones concretas esperadas"
+     print("✅ Next Steps accionables OK")

      print("🧩 Verificando completeness-guard…")
      _assert_not_found_substitution(analysis_text)
      print("✅ 'Not found in deck' presente cuando falta sección")
