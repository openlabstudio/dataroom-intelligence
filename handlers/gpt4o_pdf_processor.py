"""
GPT-4o Direct PDF Processor for DataRoom Intelligence Bot
Replaces OCR pipeline with OpenAI's native PDF processing capabilities
Story: G4O-001 - GPT-4o PDF Processor Implementation
"""

import os
import time
import json
from json import JSONDecodeError
from dataclasses import dataclass
from typing import Dict, Any, Optional, List, Tuple
from openai import OpenAI
from utils.logger import get_logger

logger = get_logger(__name__)

class GPT4oDirectProcessor:
    """GPT-4o Direct PDF processor using OpenAI Files API"""

    def __init__(self, api_key: str):
        """Initialize with OpenAI API key"""
        self.client = OpenAI(api_key=api_key)
        
    def process_pdf_document(self, pdf_path: str, file_name: str) -> Dict[str, Any]:
        """
        Process PDF using GPT-4o Direct analysis
        
        Args:
            pdf_path: Path to PDF file
            file_name: Name of the file for logging/metadata
            
        Returns:
            Dictionary with structured extraction results
        """
        logger.info(f"🔵 Starting AI processing for: {file_name}")
        start_time = time.time()
        
        try:
            # Step 1: Upload PDF to OpenAI Files API
            logger.info(f"📤 Uploading {file_name} to OpenAI Files API...")
            with open(pdf_path, 'rb') as file:
                uploaded_file = self.client.files.create(
                    file=file,
                    purpose='assistants'
                )
            
            logger.info(f"✅ File uploaded successfully: {uploaded_file.id}")
            
            # Step 2: Process with GPT-4o (multi-paso con JSON estricto)
            logger.info("🧠 Processing with AI (multi-pass JSON)…")
            extraction_result = self._extract_structured_data_multi(uploaded_file.id, file_name)
            
            # Step 3: Cleanup uploaded file
            try:
                self.client.files.delete(uploaded_file.id)
                logger.info("🧹 Temporary file cleaned up")
            except Exception as cleanup_error:
                logger.warning(f"⚠️ Cleanup warning: {cleanup_error}")
            
            # Step 4: Format results
            processing_time = time.time() - start_time
            logger.info(f"✅ AI processing completed in {processing_time:.2f}s")
            
            return extraction_result
            
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"❌ GPT-4o processing failed for {file_name}: {e}")
            logger.info(f"⏱️ Failed after {processing_time:.2f}s")
            
            # Return error result for fallback handling
            return {
                'name': file_name,
                'type': 'pdf',
                'content': '',
                'structured_data': {},  # Empty dict instead of None for consistency
                'metadata': {
                    'extraction_method': 'gpt4o_failed',
                    'processing_time': processing_time,
                    'error': str(e),
                    'has_content': False,
                    'fallback_required': True,
                    'facts_count': 0
                }
            }
    
    def _json_schema_prompt(self) -> str:
        return """
You are extracting ALL INVESTMENT-GRADE facts from a startup pitch deck.
Return STRICT JSON ONLY with this schema (no prose, no comments):
{
  "financials": {
    "revenue": [{"value": "...", "currency": "...", "period": "...", "slide": 0}],
    "gmv": [{"value": "...", "currency": "...", "period": "...", "slide": 0}],
    "vat": [{"value": "...", "currency": "...", "period": "...", "slide": 0}],
    "burn": [{"value": "...", "currency": "...", "period": "...", "slide": 0}],
    "runway_months": [{"value": 0, "slide": 0}],
    "funding_rounds": [{"round": "Seed|Series A|...", "amount": "...", "currency": "...", "valuation": "...", "slide": 0}]
  },
  "unit_economics": {
    "cac": [{"value": "...", "currency": "...", "channel": "...", "slide": 0}],
    "ltv": [{"value": "...", "currency": "...", "slide": 0}],
    "payback_months": [{"value": 0, "slide": 0}],
    "gross_margin": [{"value": "...", "slide": 0}],
    "contribution_margin": [{"value": "...", "slide": 0}]
  },
  "traction": {
    "merchants": [{"value": "...", "period": "...", "growth": "...", "slide": 0}],
    "users": [{"value": "...", "period": "...", "growth": "...", "slide": 0}],
    "transactions": [{"value": "...", "period": "...", "growth": "...", "slide": 0}],
    "retention": [{"value": "...", "cohort": "...", "slide": 0}],
    "nps": [{"value": "...", "slide": 0}]
  },
  "value_proposition": [{"quote": "...", "slide": 0}],
  "differentiation": [{"quote": "...", "slide": 0}],
  "market": [{"quote": "...", "slide": 0}],
  "product": [{"quote": "...", "slide": 0}],
  "roadmap": [{"quote": "...", "slide": 0}],
  "gtm": [{"quote": "...", "slide": 0}],
  "icp": [{"quote": "...", "slide": 0}],
  "channels": [{"quote": "...", "slide": 0}],
  "pricing_model": [{"quote": "...", "slide": 0}],
  "take_rate": [{"value": "...", "slide": 0}],
  "competition": [{"quote": "...", "slide": 0}],
  "team": [{"quote": "...", "slide": 0}],
  "business_model": [{"quote": "...", "slide": 0}],
  "risks": [{"quote": "...", "slide": 0}],
  "regulatory": [{"quote": "...", "slide": 0}],
  "why_now": [{"quote": "...", "slide": 0}],
  "use_of_funds": [{"quote": "...", "slide": 0}],
  "case_studies": [{"quote": "...", "slide": 0}],
  "slides_covered": [1]
}
Rules:
- Extract EVERYTHING that is explicitly present: numbers, metrics, company names, team backgrounds, customers, competitors, channels, etc.
- For unit economics: look for CAC, LTV, payback period, gross margin, contribution margin
- For traction: look for active users/merchants, growth rates, retention, NPS
- NO INFERENCE. If a field is not present in the deck, return an EMPTY ARRAY for it.
- Every numeric datapoint MUST include `slide` when visible on slide.
- Use exact periods seen: "Q1 27", "FY2024", "TTM", "monthly", "cumulative", etc.
- Use exact currencies seen: "€", "$", "USD", "EUR", etc.
- STRICT JSON only. Do NOT include prose or comments.
        """.strip()

    def _merge_extractions(self, base: Dict[str, Any], inc: Dict[str, Any]) -> Dict[str, Any]:
        """Une merge simple por listas de objetos y lista de slides_covered sin duplicados."""
        if not base:
            return inc
        out = dict(base)
        for k, v in inc.items():
            if k == "slides_covered":
                prev = set(out.get(k, []))
                out[k] = sorted(list(prev.union(set(v))))
            elif isinstance(v, list):
                out[k] = (out.get(k, []) or []) + v
            elif isinstance(v, dict):
                out[k] = self._merge_extractions(out.get(k, {}) or {}, v)
            else:
                out[k] = v
        return out

    def _validate_json(self, raw: str) -> Dict[str, Any]:
        try:
            return json.loads(raw)
        except JSONDecodeError as e:
            # Intenta limpiar envoltorios accidentales de code fences
            raw2 = raw.strip()
            if raw2.startswith("```"):
                raw2 = raw2.strip("`")
                if raw2.startswith("json"):
                    raw2 = raw2[4:]
            return json.loads(raw2)

    def _extract_pass(self, file_id: str, exclude_slides: Optional[List[int]]=None) -> Dict[str, Any]:
        instructions = self._json_schema_prompt()
        if exclude_slides:
            instructions += f"\n\nAdditional rule: Re-scan ONLY slides NOT IN {exclude_slides}."

        resp = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": instructions},
                    {"type": "text", "text": "Extract all possible facts strictly as JSON."},
                    {"type": "file", "file": {"file_id": file_id}},
                ],
            }],
            # ⬇️ subir cobertura (antes 2500)
            max_tokens=6000,
            temperature=0.1,
            # ⬇️ fuerza JSON válido con SDK 1.6.x
            response_format={"type": "json_object"},
        )
        raw = resp.choices[0].message.content
        return self._validate_json(raw)

    def _extract_full_text(self, file_id: str) -> str:
        """Extract complete text content from the PDF for Q&A functionality"""
        logger.info("📖 Extracting full text content for Q&A...")

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": """Extract ALL text content from this pitch deck.
                        Include EVERY detail: company name, all numbers, metrics, team info,
                        product descriptions, market data, competitors, roadmap, everything.
                        Present the content slide by slide with clear headers.
                        This will be used to answer detailed questions about the deck."""},
                        {"type": "file", "file": {"file_id": file_id}}
                    ]
                }],
                max_tokens=8000,
                temperature=0.1
            )

            full_text = response.choices[0].message.content
            logger.info(f"✅ Extracted {len(full_text)} characters of text")
            return full_text

        except Exception as e:
            logger.error(f"❌ Full text extraction failed: {e}")
            return ""

    def _extract_structured_data_multi(self, file_id: str, file_name: str) -> Dict[str, Any]:
        """Hasta 3 pasadas: 1ª global + re-scan de slides no cubiertos."""

        # FIRST: Extract full text for Q&A
        full_text = self._extract_full_text(file_id)

        # THEN: Do structured extraction
        merged: Dict[str, Any] = {}
        covered: List[int] = []

        for i in range(3):
            logger.info(f"🔁 Extraction pass {i+1}/3 (excluding slides {covered})")

            # Skip if we already covered a reasonable range (likely all slides)
            if len(covered) >= 15 and i > 0:
                logger.info(f"✅ Already covered {len(covered)} slides; likely complete. Stopping.")
                break

            part = self._extract_pass(file_id, exclude_slides=covered or None)
            prev_len = len(covered)
            merged = self._merge_extractions(merged, part)
            covered = sorted(list(set(merged.get("slides_covered", []))))
            if len(covered) == prev_len:
                logger.info("✅ No new slides discovered; stopping extraction loop.")
                break

        result = {
            'name': file_name,
            'type': 'pdf',
            'content': json.dumps(merged, ensure_ascii=False),
            'structured_data': merged,  # CRITICAL: Pass as dict for ai_analyzer
            'full_text': full_text,  # NEW: Full text for Q&A
            'metadata': {
                'extraction_method': 'gpt-4o_files_api_json',
                'has_content': True,
                'has_full_text': bool(full_text),  # NEW: Track if we have full text
                'slides_covered': covered,
                'facts_count': len([k for k, v in merged.items() if v])  # Count non-empty sections
            }
        }

        # Log extraction stats for debugging
        logger.info(f"📊 Extraction stats for {file_name}:")
        logger.info(f"  - Total sections with data: {result['metadata']['facts_count']}")
        if merged.get('financials'):
            fin = merged['financials']
            logger.info(f"  - Financial metrics: GMV={len(fin.get('gmv', []))}, Revenue={len(fin.get('revenue', []))}, Funding={len(fin.get('funding_rounds', []))}")
        if merged.get('team'):
            logger.info(f"  - Team entries: {len(merged['team'])}")
        if merged.get('competition'):
            logger.info(f"  - Competition entries: {len(merged['competition'])}")

        return result

    def _extract_structured_data(self, file_id: str, file_name: str) -> Dict[str, Any]:
        """Extract structured data using GPT-4o with optimized prompt"""
        
        # Optimized prompt for startup pitch deck analysis
        extraction_prompt = """
        Analyze this startup pitch deck and extract key business information with precise slide references.

        **EXTRACT THE FOLLOWING DATA:**

        **FINANCIAL METRICS:**
        - Funding rounds, amounts, and valuations (with slide numbers AND TIME PERIODS/DATES)
        - Revenue figures and projections WITH TIME PERIODS (e.g., "€10M (2023)", "€25M (2024 projection)")
        - Market size (TAM/SAM/SOM) WITH YEAR if specified
        - Key financial KPIs WITH TIME PERIODS
        - Burn rate, runway, or cash flow data WITH TIME PERIODS

        **TRACTION DATA:**
        - User/customer numbers and growth
        - Transaction volumes and revenue metrics
        - Growth rates and retention data
        - Key partnerships and customers

        **TEAM INFORMATION:**
        - Founders with their EXACT names and roles as stated in the document (do not normalize roles)
        - Key team members with their EXACT titles and experience
        - Advisory board if mentioned (with exact titles)

        **BUSINESS MODEL:**
        - Revenue model and pricing structure
        - Target market and customer segments
        - Value proposition and competitive advantages
        - Go-to-market strategy

        **MARKET & COMPETITION:**
        - Market opportunity and addressable market
        - Competitive landscape and positioning
        - Market trends and timing

        **IMPORTANT REQUIREMENTS:**
        1. Provide specific numbers with slide references (e.g., "€2M seed round (Slide 16)")
        2. Extract ALL financial data visible in charts or tables
        3. Include slide/page numbers for each major data point
        4. Structure the response clearly with headers and bullet points
        5. If information is in a chart/graph, describe the visual data
        
        Focus on accuracy and completeness - this analysis will be used for investment decisions.
        """
        
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": extraction_prompt},
                        {"type": "file", "file": {"file_id": file_id}}
                    ]
                }
            ],
            max_tokens=2500,
            temperature=0.1  # Low temperature for factual extraction
        )
        
        raw_content = response.choices[0].message.content
        
        # Parse structured data from GPT-4o response
        structured_data = self._parse_structured_response(raw_content)
        
        # Extract slide references for metadata
        slide_references = self._extract_slide_references(raw_content)
        
        return {
            'raw_content': raw_content,
            'structured_data': structured_data,
            'slide_references': slide_references,
            'quality_score': 0.95  # GPT-4o typically provides high quality
        }
    
    def _parse_structured_response(self, content: str) -> Dict[str, Any]:
        """Parse GPT-4o response into structured data format"""
        
        # Initialize structured data dictionary
        structured = {
            'financial_metrics': {},
            'traction_data': {},
            'team_information': {},
            'business_model': {},
            'market_competition': {}
        }
        
        # Basic parsing - look for key patterns
        lines = content.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Detect section headers
            if '**FINANCIAL METRICS' in line.upper():
                current_section = 'financial_metrics'
            elif '**TRACTION DATA' in line.upper():
                current_section = 'traction_data'
            elif '**TEAM' in line.upper():
                current_section = 'team_information'
            elif '**BUSINESS MODEL' in line.upper():
                current_section = 'business_model'
            elif '**MARKET' in line.upper() or '**COMPETITION' in line.upper():
                current_section = 'market_competition'
            elif line.startswith('- ') and current_section:
                # Store bullet points in appropriate section
                if current_section not in structured:
                    structured[current_section] = []
                if isinstance(structured[current_section], dict):
                    structured[current_section] = []
                structured[current_section].append(line[2:])  # Remove "- "
        
        return structured
    
    def _extract_slide_references(self, content: str) -> list:
        """Extract slide/page references from GPT-4o response"""
        import re
        
        # Pattern to match slide references
        patterns = [
            r'Slide (\d+)',
            r'Page (\d+)',
            r'slide (\d+)',
            r'page (\d+)',
            r'\(Slide (\d+)\)',
            r'\(Page (\d+)\)'
        ]
        
        references = []
        for pattern in patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                slide_num = int(match.group(1))
                if slide_num not in references:
                    references.append(slide_num)
        
        return sorted(references)

class GPT4oFallbackProcessor:
    """Manages fallback from GPT-4o to existing OCR pipeline"""
    
    def __init__(self, gpt4o_processor: GPT4oDirectProcessor, ocr_processor):
        self.gpt4o_processor = gpt4o_processor
        self.ocr_processor = ocr_processor
        
    def process_pdf_with_fallback(self, pdf_path: str, file_name: str) -> Dict[str, Any]:
        """
        Process PDF with GPT-4o, fallback to OCR if needed
        Story: G4O-003 - Graceful Fallback to OCR Pipeline
        """
        logger.info(f"🔄 Starting PDF processing with fallback for: {file_name}")
        
        # Try GPT-4o first
        result = self.gpt4o_processor.process_pdf_document(pdf_path, file_name)
        
        if result['metadata'].get('fallback_required', False):
            logger.warning(f"⚠️ GPT-4o failed for {file_name}, falling back to OCR")
            
            # Fallback to existing OCR pipeline
            try:
                ocr_result = self.ocr_processor._process_pdf(pdf_path, file_name)
                
                # Enhance OCR result with fallback metadata
                ocr_result['metadata']['extraction_method'] = 'ocr_fallback'
                ocr_result['metadata']['gpt4o_attempted'] = True
                ocr_result['metadata']['gpt4o_error'] = result['metadata'].get('error')
                
                logger.info(f"✅ OCR fallback successful for {file_name}")
                return ocr_result
                
            except Exception as ocr_error:
                logger.error(f"❌ OCR fallback also failed for {file_name}: {ocr_error}")
                
                # Final fallback - empty result
                return {
                    'name': file_name,
                    'type': 'pdf',
                    'content': '',
                    'metadata': {
                        'extraction_method': 'failed',
                        'gpt4o_error': result['metadata'].get('error'),
                        'ocr_error': str(ocr_error),
                        'has_content': False
                    }
                }
        
        # GPT-4o succeeded
        logger.info(f"✅ GPT-4o processing successful for {file_name}")
        return result