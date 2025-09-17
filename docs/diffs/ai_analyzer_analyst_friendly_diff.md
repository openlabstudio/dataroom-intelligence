*** a/ai_analyzer.py
--- b/ai_analyzer.py
***************
*** 1,16 ****
  """
  AI Analysis handler for DataRoom Intelligence Bot
  Integrates with OpenAI GPT-4 to analyze data room documents
  """

  import json
  import re
  from typing import Dict, List, Any, Optional
  from openai import OpenAI
  from config.settings import config
  from prompts.analysis_prompts import DATAROOM_ANALYSIS_PROMPT, SCORING_PROMPT, SLACK_READY_ANALYSIS_PROMPT
  from prompts.qa_prompts import QA_PROMPT, MEMO_PROMPT, GAPS_PROMPT, SLACK_READY_GAPS_PROMPT
  from utils.logger import get_logger

  logger = get_logger(__name__)

  class AIAnalyzer:
--- 1,25 ----
  """
  AI Analysis handler for DataRoom Intelligence Bot
  Integrates with OpenAI GPT-4 to analyze data room documents
  """

  import json
  import re
  from typing import Dict, List, Any, Optional, Tuple
  from openai import OpenAI
  from config.settings import config
  from prompts.analysis_prompts import DATAROOM_ANALYSIS_PROMPT, SCORING_PROMPT, SLACK_READY_ANALYSIS_PROMPT
  from prompts.qa_prompts import QA_PROMPT, MEMO_PROMPT, GAPS_PROMPT, SLACK_READY_GAPS_PROMPT
  from utils.logger import get_logger

  logger = get_logger(__name__)

  class AIAnalyzer:
+     # ===================== Presentation helpers (analyst-friendly) =====================
+     _EMOJI_ES2UNICODE = {
+         # comunes
+         ":página_boca_arriba:": "📄", ":bombilla:": "💡", ":gráfico_de_barras:": "📊",
+         ":espadas_cruzadas:": "⚔️", ":autopista:": "🛣️", ":cohete:": "🚀",
+         ":bolsa_de_dinero:": "💰", ":bocadillo_de_diálogo:": "💬",
+         ":lupa:": "🔎", ":flechas_en_sentido_antihorario:": "🔄",
+         # ya mapeados previamente, se mantienen por compatibilidad
+         ":dardo:": "🎯", ":gráfico_de_pastel:": "🥧"
+     }
+
+     @staticmethod
+     def _strip_completeness_meta(text: str) -> str:
+         # elimina cualquier línea con [COMPLETENESS-GUARD] ... (prompt leak)
+         return re.sub(r"\[COMPLETENESS-GUARD][^\n]*\n?", "", text, flags=re.IGNORECASE)
+
+     @staticmethod
+     def _format_missing_sections_human(missing: List[str], slides_range: Tuple[int,int]) -> str:
+         if not missing:
+             return ""
+         pretty = ", ".join(missing)
+         a, b = slides_range
+         return (
+             f"⚠️ **Missing Sections in Deck**: {pretty}.\n"
+             f"_These were not found across slides {a}–{b}. "
+             f"Absence is unusual; treat as a diligence gap and request clarification._\n"
+         )
+
+     @classmethod
+     def _map_emojis(cls, text: str) -> str:
+         for src, uni in cls._EMOJI_ES2UNICODE.items():
+             text = text.replace(src, uni)
+         return text
+
+     @staticmethod
+     def _inject_analyst_notes(text: str) -> str:
+         """
+         Añade micro-notas de analista tras bloques principales si no existen.
+         Heurístico no intrusivo: busca headers y agrega una línea de insight.
+         """
+         def inject(after_title: str, note: str) -> str:
+             pattern = rf"({re.escape(after_title)}\s*\n)"
+             repl = r"\1" + note.strip() + "\n"
+             return re.sub(pattern, repl, text, count=1, flags=re.IGNORECASE)
+
+         t = text
+         if re.search(r"\*\*FINANCIAL HIGHLIGHTS\*\*", t, re.IGNORECASE):
+             t = inject("**FINANCIAL HIGHLIGHTS:**",
+                        "• _Analyst Note:_ GMV/VAT separation is good; request revenue recognition policy and gross margin profile to assess unit economics.")
+         if re.search(r"\*\*MARKET ANALYSIS\*\*", t, re.IGNORECASE):
+             t = inject("**MARKET ANALYSIS:**",
+                        "• _Analyst Note:_ Provide TAM/SAM/SOM with sources and sensitivity; current signals are insufficient for sizing conviction.")
+         if re.search(r"\*\*GO-TO-MARKET STRATEGY\*\*", t, re.IGNORECASE):
+             t = inject("**GO-TO-MARKET STRATEGY:**",
+                        "• _Analyst Note:_ Clarify ICP, sales motion, and partner channels; without this, ramp assumptions are speculative.")
+         if re.search(r"\*\*COMPETITORS\*\*", t, re.IGNORECASE):
+             t = inject("**COMPETITORS:**",
+                        "• _Analyst Note:_ Missing landscape; ask for top 3 comps and differentiation on product, economics, and regulatory posture.")
+         return t
+
+     @staticmethod
+     def _improve_next_steps(text: str, missing: List[str]) -> str:
+         # Reemplaza un bloque de "Next Steps" genérico por acciones concretas
+         actionable = [
+             "• Request 12–24m P&L with revenue breakdown and gross margin assumptions.",
+             "• Provide competitive landscape slide with top 3–5 comps and pricing.",
+             "• Share GTM plan: ICP, channels, quota assumptions, pipeline math.",
+             "• Provide cap table and runway post-seed; outline next raise triggers.",
+         ]
+         if "team" in missing:
+             actionable.append("• Add management bios with relevant domain/regulatory expertise.")
+         if "risks" in missing:
+             actionable.append("• Provide key execution/regulatory risks with mitigations.")
+
+         # Normaliza el header (Next Steps / NEXT STEPS / **Next Steps:** ...)
+         header_regex = r"(\*\*Next Steps\*\*:|\*\*NEXT STEPS\*\*:|\*\*Next Steps:\*\*|\*\*NEXT STEPS:\*\*)"
+         if re.search(header_regex, text, re.IGNORECASE):
+             text = re.sub(
+                 header_regex + r"([\s\S]*?)(?=\n\*\*|$)",
+                 "**Next Steps:**\n" + "\n".join(actionable) + "\n",
+                 text,
+                 flags=re.IGNORECASE
+             )
+         else:
+             # si no existía, lo añadimos al final
+             text = text.rstrip() + "\n\n**Next Steps:**\n" + "\n".join(actionable) + "\n"
+         return text
***************
*** 40,75 ****
      ...
              # Completeness guard: si faltan secciones, indícalo en el prompt
              must_sections = ["team","competition","risks","why_now"]
              missing = [s for s in must_sections if not extracted.get(s)]
              if missing:
                  analysis_prompt += (
                      "\n\n[COMPLETENESS-GUARD] The deck appears to be missing sections: "
                      + ", ".join(missing)
                      + ". If truly not in deck, write 'Not found in deck' and reference slides scanned."
                  )

              analysis_prompt = SLACK_READY_ANALYSIS_PROMPT.format(
                  documents_with_metadata=context['documents_summary'],
                  document_contents=context['full_content'],  # ❌ sin truncamiento
                  extracted_financials=formatted_financials
              )

              logger.info("🧪 TESTING: Using new Slack-ready prompt")

              # Call GPT-4 for analysis
              response = self.client.chat.completions.create(
                  model=self.model,  # será gpt-4o (ver __init__)
                  messages=[
                      {"role": "system", "content": "You are a sen... years of experience in due diligence and startup evaluation."},
                      {"role": "user", "content": analysis_prompt}
-             , max_tokens=4000, temperature=0.25)
+             , max_tokens=4000, temperature=0.25)
              analysis = response.choices[0].message.content

-             # Slack emoji post-process (mapear alias ES → Unicode)
-             for src, uni in {
-                 ":dardo:": "🎯",
-                 ":gráfico_de_barras:": "📊",
-                 ":cohete:": "🚀",
-             }.items():
-                 analysis = analysis.replace(src, uni)
-
-             # Señalizar claramente "Not found" cuando aplique
-             analysis = re.sub(r"\b(No specific .* mentioned)\b", "Not found in deck (explicitly verified)", analysis)
-
-             return analysis
+             # ---------- PRESENTATION LAYER ----------
+             # 1) Ocultar meta y añadir nota humana de secciones faltantes
+             analysis = self._strip_completeness_meta(analysis)
+
+             # 2) Emojis 100% Unicode
+             analysis = self._map_emojis(analysis)
+
+             # 3) Sustituir mensajes genéricos por “Not found in deck (…)”
+             analysis = re.sub(r"\b(No specific .*? mentioned\.)", "Not found in deck (explicitly verified).", analysis, flags=re.IGNORECASE)
+
+             # 4) Nota “Missing Sections” arriba del todo si aplica
+             slides_range = (1, max(extracted.get("slides_covered", [1])) if isinstance(extracted.get("slides_covered"), list) else 20)
+             human_missing = self._format_missing_sections_human(missing, slides_range if isinstance(slides_range, tuple) else (1,20))
+             if human_missing:
+                 analysis = human_missing + "\n" + analysis
+
+             # 5) Añadir “Analyst Notes” heurísticas por sección (no intrusivas)
+             analysis = self._inject_analyst_notes(analysis)
+
+             # 6) Re-escribir “Next Steps” a acciones concretas para VC
+             analysis = self._improve_next_steps(analysis, missing)
+
+             return analysis
***************
*** 118,149 ****
      def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
          self.client = OpenAI(api_key=api_key or config.OPENAI_API_KEY)
          # ✅ Alinear con extractor: usar siempre gpt-4o
          self.model = model or "gpt-4o"
          self.current_analysis: Optional[str] = None
          self.analysis_context: Optional[Dict[str, Any]] = None
          logger.info(f"AIAnalyzer initialized with model: {self.model}")

      def _prepare_analysis_context(self, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
          """Aggregate and prepare analysis context from documents"""
          documents_summary = []
          full_content = ""
          for doc in documents:
              documents_summary.append(f"- {doc.get('name','unknown')} ({doc.get('type','unknown')})")
              # ✅ sin truncamiento: preserva fidelidad para el análisis
              full_content += (doc.get('content') or '')

          # Si el contenido ya es JSON de extractor, normalízalo antes
          extracted: Dict[str, Any] = {}
          try:
              extracted = json.loads(full_content)
          except Exception:
              pass

          if isinstance(extracted, dict) and "financials" in extracted:
              extracted = self._normalize_financials(extracted)
              full_content = json.dumps(extracted, ensure_ascii=False)

          return {
              "documents_summary": "\n".join(documents_summary),
              "full_content": full_content
          }
--- 138,174 ----
      def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
          self.client = OpenAI(api_key=api_key or config.OPENAI_API_KEY)
          # ✅ Alinear con extractor: usar siempre gpt-4o
          self.model = model or "gpt-4o"
          self.current_analysis: Optional[str] = None
          self.analysis_context: Optional[Dict[str, Any]] = None
          logger.info(f"AIAnalyzer initialized with model: {self.model}")

      def _prepare_analysis_context(self, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
          """Aggregate and prepare analysis context from documents"""
          documents_summary = []
          full_content = ""
          for doc in documents:
              documents_summary.append(f"- {doc.get('name','unknown')}: {doc.get('type','unknown')}")
              # ✅ sin truncamiento: preserva fidelidad para el análisis
              full_content += (doc.get('content') or '')

          # Si el contenido ya es JSON de extractor, normalízalo antes
          extracted: Dict[str, Any] = {}
          try:
              extracted = json.loads(full_content)
          except Exception:
              pass

          if isinstance(extracted, dict) and "financials" in extracted:
              extracted = self._normalize_financials(extracted)
              full_content = json.dumps(extracted, ensure_ascii=False)

          return {
              "documents_summary": "\n".join(documents_summary),
              "full_content": full_content
          }
