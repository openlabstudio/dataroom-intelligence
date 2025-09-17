*** a/gpt4o_pdf_processor.py
--- b/gpt4o_pdf_processor.py
***************
*** 1,12 ****
  """
  GPT-4o Direct PDF Processor for DataRoom Intelligence Bot
  Replaces OCR pipeline with OpenAI's native PDF processing capabilities
  Story: G4O-001 - GPT-4o PDF Processor Implementation
  """

  import os
  import time
- from typing import Dict, Any, Optional
+ from typing import Dict, Any, Optional, List, Tuple
  from openai import OpenAI
  from utils.logger import get_logger

  logger = get_logger(__name__)

  class GPT4oDirectProcessor:
      """GPT-4o Direct PDF processor using OpenAI Files API"""
--- 1,17 ----
  """
  GPT-4o Direct PDF Processor for DataRoom Intelligence Bot
  Replaces OCR pipeline with OpenAI's native PDF processing capabilities
  Story: G4O-001 - GPT-4o PDF Processor Implementation
  """

  import os
  import time
+ import json
+ from json import JSONDecodeError
+
+ from dataclasses import dataclass
+
  from typing import Dict, Any, Optional, List, Tuple
  from openai import OpenAI
  from utils.logger import get_logger

  logger = get_logger(__name__)

  class GPT4oDirectProcessor:
      """GPT-4o Direct PDF processor using OpenAI Files API"""
***************
*** 90,163 ****
-             # Step 2: Process with GPT-4o
-             logger.info("🧠 Processing with AI...")
-             extraction_result = self._extract_structured_data(uploaded_file.id, file_name)
+             # Step 2: Process with GPT-4o (multi-paso con JSON estricto)
+             logger.info("🧠 Processing with AI (multi-pass JSON)…")
+             extraction_result = self._extract_structured_data_multi(uploaded_file.id, file_name)

              # Step 3: Cleanup uploaded file
              try:
                  self.client.files.delete(uploaded_file.id)
                  logger.info("🧹 Temporary file cleaned up")
              except Exception as cleanup_error:
                  logger.warning(f"⚠️ Cleanup warning: {cleanup_error}")

-
              # GPT-4o succeeded
              logger.info(f"✅ GPT-4o processing successful for {file_name}")
              return result
--- 95,209 ----
+
+     def _json_schema_prompt(self) -> str:
+         return """
+ You are extracting INVESTMENT-GRADE facts from a startup pitch deck.
+ Return STRICT JSON ONLY with this schema (no prose):
+ {
+   "financials": {
+     "revenue": [{"value": "...", "currency": "...", "period": "...", "slide": 0}],
+     "gmv": [{"value": "...", "currency": "...", "period": "...", "slide": 0}],
+     "vat": [{"value": "...", "currency": "...", "period": "...", "slide": 0}],
+     "burn": [{"value": "...", "currency": "...", "period": "...", "slide": 0}],
+     "runway_months": [{"value": 0, "slide": 0}],
+     "funding_rounds": [{"round": "Seed|Series A|...", "amount": "...", "currency": "...", "valuation": "...", "slide": 0}]
+   },
+   "traction": [],
+   "team": [],
+   "business_model": [],
+   "gtm": [],
+   "competition": [],
+   "risks": [{"text":"...", "slide":0}],
+   "why_now": [{"text":"...", "slide":0}],
+   "slides_covered": [1]
+ }
+ Rules:
+ - Every numeric datapoint MUST include a `slide` reference.
+ - 'eligible sales/GMV' ≠ 'revenue'; 'VAT/IVA' ≠ revenue.
+ - If a field isn't present in the deck, return an empty array for it.
+ - STRICT JSON. Do NOT include commentary.
+         """.strip()
+
+     def _merge_extractions(self, base: Dict[str, Any], inc: Dict[str, Any]) -> Dict[str, Any]:
+         """Une merge simple por listas de objetos y lista de slides_covered sin duplicados."""
+         if not base:
+             return inc
+         out = dict(base)
+         for k, v in inc.items():
+             if k == "slides_covered":
+                 prev = set(out.get(k, []))
+                 out[k] = sorted(list(prev.union(set(v))))
+             elif isinstance(v, list):
+                 out[k] = (out.get(k, []) or []) + v
+             elif isinstance(v, dict):
+                 out[k] = self._merge_extractions(out.get(k, {}) or {}, v)
+             else:
+                 out[k] = v
+         return out
+
+     def _validate_json(self, raw: str) -> Dict[str, Any]:
+         try:
+             return json.loads(raw)
+         except JSONDecodeError as e:
+             # Intenta limpiar envoltorios accidentales de code fences
+             raw2 = raw.strip()
+             if raw2.startswith("```"):
+                 raw2 = raw2.strip("`")
+                 if raw2.startswith("json"):
+                     raw2 = raw2[4:]
+             return json.loads(raw2)
+
+     def _extract_pass(self, file_id: str, exclude_slides: Optional[List[int]]=None) -> Dict[str, Any]:
+         instructions = self._json_schema_prompt()
+         if exclude_slides:
+             instructions += f"\n\nAdditional rule: Re-scan ONLY slides NOT IN {exclude_slides}."
+
+         resp = self.client.chat.completions.create(
+             model="gpt-4o",
+             messages=[{
+                 "role": "user",
+                 "content": [
+                     {"type": "text", "text": instructions},
+                     {"type": "input_text", "text": "Extract all possible facts strictly as JSON."},
+                     {"type": "input_file", "input_file": {"file_id": file_id}},
+                 ],
+             }],
+             # ⬇️ subir cobertura (antes 2500)
+             max_tokens=6000,
+             temperature=0.1,
+             # ⬇️ fuerza JSON válido con SDK 1.6.x
+             response_format={"type": "json_object"},
+         )
+         raw = resp.choices[0].message.content
+         return self._validate_json(raw)
+
+     def _extract_structured_data_multi(self, file_id: str, file_name: str) -> Dict[str, Any]:
+         """Hasta 3 pasadas: 1ª global + re-scan de slides no cubiertos."""
+         merged: Dict[str, Any] = {}
+         covered: List[int] = []
+
+         for i in range(3):
+             logger.info(f"🔁 Extraction pass {i+1}/3 (excluding slides {covered})")
+             part = self._extract_pass(file_id, exclude_slides=covered or None)
+             prev_len = len(covered)
+             merged = self._merge_extractions(merged, part)
+             covered = sorted(list(set(merged.get("slides_covered", []))))
+             if len(covered) == prev_len:
+                 logger.info("✅ No new slides discovered; stopping extraction loop.")
+                 break
+
+         result = {
+             'name': file_name,
+             'type': 'pdf',
+             'content': json.dumps(merged, ensure_ascii=False),
+             'metadata': {
+                 'extraction_method': 'gpt-4o_files_api_json',
+                 'has_content': True,
+                 'slides_covered': covered,
+             }
+         }
+         return result
