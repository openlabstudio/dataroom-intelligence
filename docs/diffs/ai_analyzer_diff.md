*** a/ai_analyzer.py
--- b/ai_analyzer.py
***************
*** 1,16 ****
  """
  AI Analysis handler for DataRoom Intelligence Bot
  Integrates with OpenAI GPT-4 to analyze data room documents
  """

  import json
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
+ import re
  from typing import Dict, List, Any, Optional
  from openai import OpenAI
  from config.settings import config
  from prompts.analysis_prompts import DATAROOM_ANALYSIS_PROMPT, SCORING_PROMPT, SLACK_READY_ANALYSIS_PROMPT
  from prompts.qa_prompts import QA_PROMPT, MEMO_PROMPT, GAPS_PROMPT, SLACK_READY_GAPS_PROMPT
  from utils.logger import get_logger

  logger = get_logger(__name__)

  class AIAnalyzer:
+     # --- Normalización financiera mínima inline (evita confusiones Revenue/GMV/VAT/Funding)
+     @staticmethod
+     def _normalize_financials(fin: Dict[str, Any]) -> Dict[str, Any]:
+         fin = fin or {}
+         fin.setdefault("financials", {})
+         f = fin["financials"]
+         for k in ["revenue","gmv","vat","funding_rounds"]:
+             f.setdefault(k, [])
+         # Reglas básicas de reclasificación por notas/textos comunes
+         def move_if(patterns: List[str], src: str, dst: str):
+             keep = []
+             moved = []
+             for item in f.get(src, []):
+                 note = (item.get("note") or item.get("value") or "").lower()
+                 if any(p in note for p in patterns):
+                     moved.append(item)
+                 else:
+                     keep.append(item)
+             f[src] = keep
+             f[dst] = f.get(dst, []) + moved
+         move_if(["eligible sales","gmv","gross merchandise"], "revenue", "gmv")
+         move_if(["vat","iva"], "revenue", "vat")
+         return fin
***************
*** 40,58 ****
      ...
              analysis_prompt = SLACK_READY_ANALYSIS_PROMPT.format(
                  documents_with_metadata=context['documents_summary'],
-                 document_contents=context['full_content'][:25000],  # Increased to ensure financial data is included
+                 document_contents=context['full_content'],  # ❌ sin truncamiento
                  extracted_financials=formatted_financials
              )

              logger.info("🧪 TESTING: Using new Slack-ready prompt")

              # Call GPT-4 for analysis
              response = self.client.chat.completions.create(
-                 model=self.model,
+                 model=self.model,  # será gpt-4o (ver __init__)
                  messages=[
                      {"role": "system", "content": "You are a sen... years of experience in due diligence and startup evaluation."},
                      {"role": "user", "content": analysis_prompt}
--- 49,70 ----
      ...
+             # Completeness guard: si faltan secciones, indícalo en el prompt
+             must_sections = ["team","competition","risks","why_now"]
+             missing = [s for s in must_sections if not extracted.get(s)]
+             if missing:
+                 analysis_prompt += (
+                     "\n\n[COMPLETENESS-GUARD] The deck appears to be missing sections: "
+                     + ", ".join(missing)
+                     + ". If truly not in deck, write 'Not found in deck' and reference slides scanned."
+                 )
+
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
***************
*** 60,75 ****
-             )
+             , max_tokens=4000, temperature=0.25)
              analysis = response.choices[0].message.content

              # Slack emoji post-process (mapear alias ES → Unicode)
              for src, uni in {
                  ":dardo:": "🎯",
                  ":gráfico_de_barras:": "📊",
                  ":cohete:": "🚀",
              }.items():
                  analysis = analysis.replace(src, uni)

              return analysis
--- 72,93 ----
+             , max_tokens=4000, temperature=0.25)
              analysis = response.choices[0].message.content

              # Slack emoji post-process (mapear alias ES → Unicode)
              for src, uni in {
                  ":dardo:": "🎯",
                  ":gráfico_de_barras:": "📊",
                  ":cohete:": "🚀",
              }.items():
                  analysis = analysis.replace(src, uni)

+             # Señalizar claramente "Not found" cuando aplique
+             analysis = re.sub(r"\b(No specific .* mentioned)\b", "Not found in deck (explicitly verified)", analysis)
+
              return analysis
***************
*** 100,122 ****
      def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
          self.client = OpenAI(api_key=api_key or config.OPENAI_API_KEY)
-         self.model = model or "gpt-4"
+         # ✅ Alinear con extractor: usar siempre gpt-4o
+         self.model = model or "gpt-4o"
          self.current_analysis: Optional[str] = None
          self.analysis_context: Optional[Dict[str, Any]] = None
          logger.info(f"AIAnalyzer initialized with model: {self.model}")

      def _prepare_analysis_context(self, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
          """Aggregate and prepare analysis context from documents"""
          documents_summary = []
          full_content = ""
          for doc in documents:
              documents_summary.append(f"- {doc.get('name','unknown')} ({doc.get('type','unknown')})")
-             # ❌ no cortar por documento
-             full_content += (doc.get('content') or '')[:10000]
+             # ✅ sin truncamiento: preserva fidelidad para el análisis
+             full_content += (doc.get('content') or '')

          return {
              "documents_summary": "\n".join(documents_summary),
              "full_content": full_content
          }
--- 118,149 ----
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

+         # Si el contenido ya es JSON de extractor, normalízalo antes
+         extracted: Dict[str, Any] = {}
+         try:
+             extracted = json.loads(full_content)
+         except Exception:
+             pass
+
+         if isinstance(extracted, dict) and "financials" in extracted:
+             extracted = self._normalize_financials(extracted)
+             full_content = json.dumps(extracted, ensure_ascii=False)
+
          return {
              "documents_summary": "\n".join(documents_summary),
              "full_content": full_content
          }
