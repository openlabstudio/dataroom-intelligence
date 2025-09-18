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

# Import analyst schema constants
from constants.analyst_schema import (
    SECTIONS_ORDER,
    SECTION_TITLE,
    FIELDS,
    FIELD_ALIASES,
    CRITICAL_SECTIONS,
    NICE_TO_HAVE_SECTIONS,
    BULLETS_LIMITS,
    DEFAULT_BULLET_LIMIT,
    MAX_TOTAL_BULLETS
)

logger = get_logger(__name__)

class AIAnalyzer:
    """Handles AI-powered analysis of data room documents using OpenAI GPT-4"""

    # ===================== Feature flags (configurables) =====================
    try:
        from config.settings import config as _cfg
        STRICT_EXTRACTION: bool = getattr(_cfg, "STRICT_EXTRACTION", True)
        ENABLE_INFERENCE: bool = getattr(_cfg, "ENABLE_INFERENCE", False)
        SHOW_CITATIONS: bool = getattr(_cfg, "SHOW_CITATIONS", False)  # por defecto OFF
        MAX_SUMMARY_BULLETS: int = int(getattr(_cfg, "MAX_SUMMARY_BULLETS", 12))
        GAP_MODE: str = getattr(_cfg, "GAP_MODE", "smart")  # "section", "field", or "smart"
        MAX_GAP_SUBFIELDS: int = int(getattr(_cfg, "MAX_GAP_SUBFIELDS", 3))
    except Exception:
        STRICT_EXTRACTION = True
        ENABLE_INFERENCE = False
        SHOW_CITATIONS = False
        MAX_SUMMARY_BULLETS = 12
        GAP_MODE = "smart"
        MAX_GAP_SUBFIELDS = 3

    # ===================== Coverage rubric (usando analyst_schema) =====================
    # Now imported from constants.analyst_schema
    # CRITICAL_SECTIONS and NICE_TO_HAVE_SECTIONS are imported above

    # Regex para detectar contenido relevante para VCs
    NUMERIC_PATTERNS = re.compile(r'(\b\d[\d,\.]*\s?(%|€|\$|M|K)\b|GMV|ARR|MRR|CAC|LTV|runway|burn|seed|valuation|take rate)', re.I)
    TEAM_PATTERNS = re.compile(r'\b(founded?|co-?founder|ex-|former|CEO|CTO|CFO|CMO|VP)\b', re.I)
    COMPETITOR_PATTERNS = re.compile(r'\b(vs\.|competitor|alternative to|compared to)\b', re.I)
    FUNDING_PATTERNS = re.compile(r'\b(raised|funding|valuation|burn|runway|investors)\b', re.I)
    _NOISE_PATTERNS = re.compile(r'\b(thank you|confidential|agenda|appendix)\b', re.I)
    FIN_METRICS = {"gmv", "revenue", "vat", "burn", "runway", "runway_months", "funding_rounds"}

    # ===================== Presentation helpers (analyst-friendly) =====================
    _EMOJI_ES2UNICODE = {
        # comunes (ES)
        ":página_boca_arriba:": "📄", ":bombilla:": "💡", ":gráfico_de_barras:": "📊",
        ":espadas_cruzadas:": "⚔️", ":autopista:": "🛣️", ":cohete:": "🚀",
        ":bolsa_de_dinero:": "💰", ":bocadillo_de_diálogo:": "💬",
        ":lupa:": "🔎", ":flechas_en_sentido_antihorario:": "🔄",
        ":carpeta_de_archivos:": "🗂️", ":libreta_de_notas:": "📒", ":martillo:": "🔨",
        # comunes (EN)
        ":page_facing_up:": "📄", ":bulb:": "💡", ":bar_chart:": "📊",
        ":crossed_swords:": "⚔️", ":motorway:": "🛣️", ":rocket:": "🚀",
        ":moneybag:": "💰", ":speech_balloon:": "💬", ":mag:": "🔎", ":arrows_counterclockwise:": "🔄",
        # previos
        ":dardo:": "🎯", ":gráfico_de_pastel:": "🥧"
    }

    # Headers usados para inyecciones
    _H_VALUE = "**VALUE PROPOSITION:**"
    _H_MARKET = "**MARKET ANALYSIS:**"
    _H_COMPETITORS = "**COMPETITORS:**"
    _H_ROADMAP = "**PRODUCT ROADMAP:**"
    _H_GTM = "**GO-TO-MARKET STRATEGY:**"
    _H_FIN = "**FINANCIAL HIGHLIGHTS:**"

    @staticmethod
    def _strip_completeness_meta(text: str) -> str:
        # elimina cualquier línea con [COMPLETENESS-GUARD] ... (prompt leak)
        return re.sub(r"\[COMPLETENESS-GUARD][^\n]*\n?", "", text, flags=re.IGNORECASE)

    @staticmethod
    def _format_missing_sections_human(missing: List[str], slides_range: Tuple[int,int]) -> str:
        if not missing:
            return ""
        pretty = ", ".join(missing)
        a, b = slides_range
        return (
            f"⚠️ **Missing Sections in Deck**: {pretty}.\n"
            f"_These were not found across slides {a}–{b}. "
            f"Absence is unusual; treat as a diligence gap and request clarification._\n"
        )

    @classmethod
    def _map_emojis(cls, text: str) -> str:
        for src, uni in cls._EMOJI_ES2UNICODE.items():
            text = text.replace(src, uni)
        return text

    def _contains_raw_dicts(self, s: str) -> bool:
        """Check if string contains raw dict/list patterns"""
        # Check for common dict patterns that shouldn't appear in final output
        patterns = [
            "{'value':",
            "{'quote':",
            "[{'value':",
            "[{'quote':",
            "'slide':",
            "'currency':",
            "'period':",
            "{'round':",
            "{'amount':"
        ]
        return any(pattern in s for pattern in patterns)

    def _sanitize_raw_dicts(self, s: str) -> str:
        """Replace raw dicts with safe placeholder"""
        import re
        # Replace dict patterns with placeholder
        s = re.sub(r"\{'[^']+':.*?\}", "• [unformatted entry omitted]", s)
        # Replace list of dicts patterns
        s = re.sub(r"\[\{'.*?\}\]", "• [unformatted entry omitted]", s)
        # Clean up any remaining dict-like patterns
        s = re.sub(r"'(value|quote|slide|currency|period|round|amount)':\s*[^,}\]]+", "[data]", s)
        logger.warning(f"Sanitized raw dicts from output")
        return s

    @staticmethod
    def _inject_exec_summary_top(text: str, extracted: Dict[str, Any]) -> str:
        """Inserta EXECUTIVE SUMMARY (3–5 bullets) al inicio usando señales del JSON."""
        bullets: List[str] = []
        fin = (extracted.get("financials") or {}) if isinstance(extracted, dict) else {}
        gmv = fin.get("gmv") or []
        vat = fin.get("vat") or []
        funding = fin.get("funding_rounds") or []

        if re.search(r"\*\*VALUE PROPOSITION\*\*:", text, re.IGNORECASE):
            bullets.append("• Clear value proposition articulated; confirm evidence of merchant demand.")
        if gmv:
            bullets.append(f"• Demonstrates traction via GMV datapoints ({len(gmv)} mentions); verify conversion to revenue and margins.")
        if vat:
            bullets.append("• Operates in regulated tax/VAT domain; diligence on compliance and government alignment required.")
        bullets.append("• Competitive landscape absent in deck; request top comps and differentiation matrix.")
        if funding:
            fr = funding[0]
            round_s = fr.get("round", "Seed")
            bullets.append(f"• {round_s} round present; request runway, use of funds, and next raise triggers.")

        if not bullets:
            return text
        exec_block = "🎯 **EXECUTIVE SUMMARY**\n" + "\n".join(bullets[:5]) + "\n\n"
        return exec_block + text

    @staticmethod
    def _inject_analyst_notes(text: str) -> str:
        """Añade micro-notas de analista tras bloques principales (forzado)."""
        def inject(after_title: str, note: str) -> str:
            pattern = rf"({re.escape(after_title)})\n"
            repl = r"\1\n" + note.strip() + "\n"
            return re.sub(pattern, repl, text, count=1, flags=re.IGNORECASE)

        t = text
        t = inject("**FINANCIAL HIGHLIGHTS:**",
                   "• _Analyst Note:_ GMV/VAT ≠ revenue. Request revenue model, gross margin profile, and unit economics clarity.")
        t = inject("**MARKET ANALYSIS:**",
                   "• _Analyst Note:_ Provide TAM/SAM/SOM with sources; current evidence is insufficient for sizing conviction.")
        t = inject("**GO-TO-MARKET STRATEGY:**",
                   "• _Analyst Note:_ Clarify ICP, sales motion, and partner channels; without this, ramp assumptions are speculative.")
        t = inject("**COMPETITORS:**",
                   "• _Analyst Note:_ Missing landscape; ask for top 3–5 comps and differentiation on product, pricing, and regulatory posture.")
        t = inject("**PRODUCT ROADMAP:**",
                   "• _Analyst Note:_ Outline milestones, regulatory checkpoints, and defensibility (data, integrations, gov links).")
        return t

    @staticmethod
    def _augment_inference(text: str, extracted: Dict[str, Any]) -> str:
        """Si faltan COMPETITORS/GTM/ROADMAP, inyecta un bloque inferido (marcado)."""
        def add_after(header: str, lines: List[str]) -> str:
            pattern = rf"({re.escape(header)}\s*\n)"
            repl = r"\1" + "\n".join(lines).strip() + "\n"
            return re.sub(pattern, repl, text, count=1, flags=re.IGNORECASE)

        t = text
        if not (extracted.get("competition") or []):
            t = add_after(AIAnalyzer._H_COMPETITORS, [
                "• _Inference:_ Likely comps include Global Blue, Planet (tax-free solutions).",
                "• _Action:_ Provide a differentiation matrix (product, take rate, compliance posture)."
            ])
        if not (extracted.get("gtm") or []):
            t = add_after(AIAnalyzer._H_GTM, [
                "• _Inference:_ Expect ICP: mid/large retailers; channels: direct sales + POS/ERP partners.",
                "• _Action:_ Share pipeline math (win rates, quotas) and partner agreements status."
            ])
        # Si existe el bloque Roadmap, añadimos guía; si no existe, no lo creamos de la nada
        if re.search(r"\*\*PRODUCT ROADMAP\*\*:", t, re.IGNORECASE):
            t = add_after(AIAnalyzer._H_ROADMAP, [
                "• _Inference:_ Milestones should cover certifications, gov integrations, and merchant onboarding automation.",
                "• _Action:_ Provide quarterly roadmap with measurable deliverables."
            ])
        return t

    @staticmethod
    def _improve_next_steps(text: str, missing: List[str]) -> str:
        # Reemplaza un bloque de "Next Steps" genérico por acciones concretas
        actionable = [
            "• Request 12–24m P&L with revenue breakdown and gross margin assumptions.",
            "• Provide competitive landscape slide with top 3–5 comps and pricing.",
            "• Share GTM plan: ICP, channels, quota assumptions, pipeline math.",
            "• Provide cap table and runway post-seed; outline next raise triggers.",
        ]
        if "team" in missing:
            actionable.append("• Add management bios with relevant domain/regulatory expertise.")
        if "risks" in missing:
            actionable.append("• Provide key execution/regulatory risks with mitigations.")

        # Normaliza el header (Next Steps / NEXT STEPS / **Next Steps:** ...)
        header_regex = r"(\*\*Next Steps\*\*:|\*\*NEXT STEPS\*\*:|\*\*Next Steps:\*\*|\*\*NEXT STEPS:\*\*)"
        if re.search(header_regex, text, re.IGNORECASE):
            text = re.sub(
                header_regex + r"([\s\S]*?)(?=\n\*\*|$)",
                "**Next Steps:**\n" + "\n".join(actionable) + "\n",
                text,
                flags=re.IGNORECASE
            )
        else:
            # si no existía, lo añadimos al final
            text = text.rstrip() + "\n\n**Next Steps:**\n" + "\n".join(actionable) + "\n"
        return text

    # --- Normalización financiera mínima inline (evita confusiones Revenue/GMV/VAT/Funding)
    @staticmethod
    def _normalize_financials(fin: Dict[str, Any]) -> Dict[str, Any]:
        fin = fin or {}
        fin.setdefault("financials", {})
        f = fin["financials"]
        for k in ["revenue","gmv","vat","funding_rounds"]:
            f.setdefault(k, [])
        # Reglas básicas de reclasificación por notas/textos comunes
        def move_if(patterns: List[str], src: str, dst: str):
            keep = []
            moved = []
            for item in f.get(src, []):
                note = (item.get("note") or item.get("value") or "").lower()
                if any(p in note for p in patterns):
                    moved.append(item)
                else:
                    keep.append(item)
            f[src] = keep
            f[dst] = f.get(dst, []) + moved
        move_if(["eligible sales","gmv","gross merchandise"], "revenue", "gmv")
        move_if(["vat","iva"], "revenue", "vat")
        return fin

    def __init__(self):
        self.client = OpenAI(api_key=config.OPENAI_API_KEY)
        # ✅ Alinear con extractor: usar siempre gpt-4o
        self.model = "gpt-4o"
        self.current_analysis = None
        self.analysis_context = None
        self.full_text = ""  # Store full text for Q&A
        self.processed_documents = []  # Store processed docs

    # ===================== NEW SIMPLIFIED ANALYSIS METHOD =====================

    def _generate_document_map(self, processed_documents: list) -> str:
        """Generate document map for citations"""
        doc_map = []
        for i, doc in enumerate(processed_documents):
            doc_code = chr(ord('A') + i)  # A, B, C, etc.
            filename = doc.get('filename', f'Document_{i+1}')
            doc_map.append(f"[{doc_code}] {filename}")
        return "\n".join(doc_map)

    def _format_dataroom_text_with_locators(self, processed_documents: list, full_text: str) -> str:
        """Format dataroom text with citation locators"""
        formatted_text = ""

        # For each document, add locators
        for i, doc in enumerate(processed_documents):
            doc_code = chr(ord('A') + i)  # A, B, C, etc.
            doc_text = doc.get('full_text', '')

            # Split into chunks and add locators
            if 'pages' in doc and doc['pages']:
                # PDF with pages
                for page_num, page_text in enumerate(doc['pages'], 1):
                    formatted_text += f"[{doc_code}·p{page_num}] {page_text}\n\n"
            else:
                # Single document or fallback
                # Split into chunks of ~500 chars for locators
                chunks = [doc_text[i:i+500] for i in range(0, len(doc_text), 500)]
                for chunk_num, chunk in enumerate(chunks, 1):
                    formatted_text += f"[{doc_code}·S{chunk_num}] {chunk}\n\n"

        return formatted_text

    def _generate_simple_analyst_summary(self, full_text: str, facts: dict = None) -> str:
        """Generate evidence-based analyst summary with citations"""
        try:
            # Extract market taxonomy if available
            market_taxonomy = ""
            if facts and 'market_detection' in facts:
                market = facts['market_detection']
                vertical = market.get('vertical', '')
                sub_vertical = market.get('sub_vertical', '')
                solution = market.get('solution', '')
                if vertical and sub_vertical:
                    market_taxonomy = f"MARKET VERTICAL: {vertical}\nSUB-VERTICAL: {sub_vertical}\nSOLUTION: {solution}\n\n"

            # Generate document map and formatted text
            doc_map = self._generate_document_map(self.processed_documents)
            dataroom_text = self._format_dataroom_text_with_locators(self.processed_documents, full_text)

            prompt = f"""ROLE
You are a senior venture capital analyst. Produce a FACTS-ONLY summary of the startup's data room based strictly on the literal text provided.

INPUTS
1) DOCUMENT MAP (legend for citations):
{doc_map}

2) CORPUS (document text marked with per-document locators):
{dataroom_text[:15000]}

LANGUAGE & RENDERING (MANDATORY)
- Output MUST be in ENGLISH, regardless of the source language.
- Translate non-English to concise, natural English. Keep proper nouns (company, people, brands) and currency symbols.
- Terminology: GMV, Revenue, VAT, Burn, Runway, Merchants, Travelers, Invoices.
- Numeric normalization:
  • Use thousands separators with commas (e.g., 40,000).
  • Convert decimal commas to decimal points (e.g., 3,5 → 3.5).
  • Preserve units/symbols (€, %, M/K). Don't invent conversions.

EVIDENCE RULES (STRICT)
1) DO NOT invent anything. Use ONLY text present in the CORPUS.
2) Every numeric fact MUST end with a citation:
   - Single doc: [S#] is OK.
   - Multi-doc: use the legend and a locator, e.g., [A·S12], [B·p4], [C·Summary!C12]. If the exact locator is unknown, OMIT the bullet.
3) Label financial metrics precisely using the literal concept and period if present:
   - GMV: €… (Qx 'YY / FY / TTM / cumulative)
   - Revenue: €… (period)
   - VAT: €… (period)
   - Burn / Runway: … (period)
   If the concept label is ambiguous (e.g., can't tell if it's VAT vs GMV), OMIT it.
4) Disambiguation:
   - "Tax-free eligible sales" (or similar) is MARKET OPPORTUNITY, NOT company revenue/GMV. Label it as such.
   - Do NOT call "market share" a breakdown like "not issued / not reimbursed".
5) Deduplication:
   - Merge bilingual near-duplicates by number: merchants/comerciantes; users/travelers/viajeros; invoices/facturas.
   - If the same metric+value appears with different periods, keep the more specific period; include both only if clearly distinct and each has its own citation.
6) No opinions or scoring. No "7/10", no "Strengths/Weaknesses", no "Next steps". Only facts and GAPS.

STYLE & LENGTH
- Max ~3,000 characters total.
- Section titles in UPPERCASE. Bullets start with "• " (bullet + space). No bold, no italics.
- If a section has no evidenced content, keep it minimal or omit the empty bullets.
- Prefer short, auditably true bullets over long prose.

REQUIRED OUTPUT (exact skeleton)

EXECUTIVE SUMMARY
[A one-line summary with company, what it does, one key traction fact, and current round — ONLY using items that have citations. If not all elements are evidenced, write with what is evidenced.]

COMPANY
• [What the company does / value proposition] [DocCode·Locator]
• [Location(s), if stated] [DocCode·Locator]
• [Year founded, if stated] [DocCode·Locator]

BUSINESS MODEL
• [Type: B2B/B2C/Marketplace/SaaS… as stated] [DocCode·Locator]
• [Revenue streams — literal from corpus] [DocCode·Locator]
• [Pricing model / who pays, if stated] [DocCode·Locator]

METRICS & TRACTION
• [Merchants: X] [DocCode·Locator]
• [Travelers/Users: X] [DocCode·Locator]
• [Invoices: X] [DocCode·Locator]
• [Tax-free eligible sales (market): €… (period)] [DocCode·Locator]
• [GMV: €… (period)] [DocCode·Locator]
• [VAT: €… (period)] [DocCode·Locator]
• [Growth: …% (period, and of what)] [DocCode·Locator]
• [Logo clients/partners, if listed] [DocCode·Locator]

TEAM & FUNDING
• [Founders: full names and roles] [DocCode·Locator]
• [Team size, if stated] [DocCode·Locator]
• [Current round: type and amount] [DocCode·Locator]
• [Valuation (pre/post), if stated] [DocCode·Locator]
• [Runway/Burn, if stated] [DocCode·Locator]

CUSTOMERS / LOGOS (optional)
• [Notable customers/brands] [DocCode·Locator]

CRITICAL GAPS
• [Up to 3 truly missing facts that matter to diligence, e.g., current revenue, CAC/LTV/Payback, competitive pricing/coverage — only list if absent in the corpus]
• [Gap 2]
• [Gap 3]

SOURCES
[List unique citations in ascending order, grouped by document code. Example:
[A·S12, S13, S16] [B·Summary!C12] [C·p4]
And include the legend up top — the DOCUMENT MAP provided in the input.]"""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,  # Lower temperature for more factual output
                max_tokens=2000   # More tokens for detailed analysis
            )

            summary = response.choices[0].message.content

            # Add market taxonomy at the beginning
            final_output = market_taxonomy + summary

            # Ensure it's under 3500 chars for Slack
            if len(final_output) > 3500:
                final_output = final_output[:3497] + "..."

            logger.info(f"✅ Generated evidence-based analyst summary ({len(final_output)} chars)")
            return final_output

        except Exception as e:
            logger.error(f"❌ Failed to generate evidence-based summary: {e}")
            # Fallback to basic formatting
            return "❌ Error generating evidence-based analysis. Please try again."

    # ===================== New Canonical Formatting Methods =====================

    def _format_field_value(self, field: str, data: dict) -> Optional[str]:
        """Format field value based on type for clean output"""
        if not isinstance(data, dict):
            return str(data).strip() if data else None

        # Financial fields with currency
        if field in ["revenue", "gmv", "vat", "burn"]:
            value = str(data.get("value", "")).strip()
            currency = str(data.get("currency", "")).strip()
            period = str(data.get("period", "")).strip()

            if not value:
                return None

            # Normalize currency format
            if currency:
                formatted = f"{currency}{value}" if currency in "€$£" else f"{value} {currency}"
            else:
                formatted = value

            if period and period.lower() not in ["", "n/a", "unknown"]:
                formatted += f" ({period})"
            return formatted

        # Funding rounds special handling
        elif field == "funding_rounds":
            parts = []
            if data.get("round"):
                parts.append(str(data["round"]))
            amt = str(data.get("amount", "")).strip()
            curr = str(data.get("currency", "")).strip()
            if amt and curr:
                parts.append(f"{curr}{amt}" if curr in "€$£" else f"{amt} {curr}")
            elif amt:
                parts.append(amt)
            if data.get("valuation"):
                parts.append(f"@ {data['valuation']} valuation")
            return " ".join(parts) if parts else None

        # Metrics with percentages
        elif field in ["gross_margin", "cohorts_retention", "growth_rate"]:
            value = str(data.get("value", data.get("quote", ""))).strip()
            if value and "%" not in value and value.replace(".", "").replace(",", "").isdigit():
                value += "%"
            return value if value else None

        # Time-based fields
        elif field in ["payback_months", "sales_cycle_days", "runway_months"]:
            value = str(data.get("value", data.get("months", data.get("days", "")))).strip()
            if not value:
                return None
            unit = "months" if "months" in field else "days"
            if value.isdigit():
                return f"{value} {unit}"
            return value

        # Default: use quote field
        else:
            quote = str(data.get("quote", "")).strip()
            return quote if quote else None

    def _collect_by_section(self, facts: dict) -> dict:
        """Collect facts organized by canonical sections"""
        sections = {s: [] for s in SECTIONS_ORDER}

        # Process financials (special structure)
        if "financials" in facts and isinstance(facts["financials"], dict):
            for metric, entries in facts["financials"].items():
                if not isinstance(entries, list):
                    continue
                for entry in entries:
                    if not isinstance(entry, dict):
                        continue
                    formatted = self._format_field_value(metric, entry)
                    if formatted:
                        # Map to correct section
                        if metric in ["revenue", "gmv", "vat", "burn", "runway_months", "funding_rounds"]:
                            sections["base_financials"].append(formatted)

        # Process unit_economics (special structure)
        if "unit_economics" in facts and isinstance(facts["unit_economics"], dict):
            for metric, entries in facts["unit_economics"].items():
                if not isinstance(entries, list):
                    continue
                for entry in entries:
                    if not isinstance(entry, dict):
                        continue

                    # Special formatting for unit economics
                    if metric == "cac":
                        value = entry.get("value", "")
                        currency = entry.get("currency", "")
                        channel = entry.get("channel", "")
                        formatted = f"CAC: {currency}{value}" if currency else f"CAC: {value}"
                        if channel:
                            formatted += f" ({channel})"
                    elif metric == "ltv":
                        value = entry.get("value", "")
                        currency = entry.get("currency", "")
                        formatted = f"LTV: {currency}{value}" if currency else f"LTV: {value}"
                    elif metric == "payback_months":
                        value = entry.get("value", "")
                        formatted = f"Payback: {value} months" if value else None
                    elif metric in ["gross_margin", "contribution_margin"]:
                        value = entry.get("value", "")
                        if value and "%" not in str(value):
                            value = f"{value}%"
                        formatted = f"{metric.replace('_', ' ').title()}: {value}" if value else None
                    else:
                        formatted = self._format_field_value(metric, entry)

                    if formatted:
                        sections["unit_economics"].append(formatted)

        # Process traction (special structure)
        if "traction" in facts and isinstance(facts["traction"], dict):
            for metric, entries in facts["traction"].items():
                if not isinstance(entries, list):
                    continue
                for entry in entries:
                    if not isinstance(entry, dict):
                        continue

                    # Special formatting for traction metrics
                    if metric in ["merchants", "users", "transactions"]:
                        value = entry.get("value", "")
                        period = entry.get("period", "")
                        growth = entry.get("growth", "")
                        formatted = f"{metric.title()}: {value}"
                        if period:
                            formatted += f" ({period})"
                        if growth:
                            formatted += f" - {growth} growth"
                    elif metric == "retention":
                        value = entry.get("value", "")
                        cohort = entry.get("cohort", "")
                        formatted = f"Retention: {value}"
                        if cohort:
                            formatted += f" ({cohort} cohort)"
                    elif metric == "nps":
                        value = entry.get("value", "")
                        formatted = f"NPS: {value}" if value else None
                    else:
                        formatted = self._format_field_value(metric, entry)

                    if formatted:
                        sections["qualified_traction"].append(formatted)

        # Process other fields using aliases
        for fact_key, fact_value in facts.items():
            if fact_key in ["financials", "unit_economics", "traction"]:
                continue  # Already processed

            # Find which section this fact belongs to
            for section, fields in FIELDS.items():
                for field in fields:
                    # Check if fact_key matches field or its aliases
                    aliases = FIELD_ALIASES.get(field, [field])
                    if fact_key in aliases or fact_key == field:
                        # Process the fact value
                        if isinstance(fact_value, list):
                            for item in fact_value:
                                if isinstance(item, dict):
                                    formatted = self._format_field_value(field, item)
                                else:
                                    formatted = str(item).strip() if item else None

                                if formatted and formatted not in sections[section]:
                                    sections[section].append(formatted)
                        elif isinstance(fact_value, dict):
                            formatted = self._format_field_value(field, fact_value)
                            if formatted and formatted not in sections[section]:
                                sections[section].append(formatted)
                        elif fact_value:
                            formatted = str(fact_value).strip()
                            if formatted and formatted not in sections[section]:
                                sections[section].append(formatted)

        # Handle common mapping patterns
        mapping = {
            "value_proposition": "value_prop_diff",
            "product": "value_prop_diff",
            "market": "value_prop_diff",
            "competition": "competition",
            "team": "team",
            "risks": "risks_regulation",
            "why_now": "value_prop_diff",
            "gtm": "gtm_sales",
            "go_to_market": "gtm_sales",
            "traction": "qualified_traction",
            "traction_data": "qualified_traction",
            "business_model": "business_model_pricing",
            "roadmap": "roadmap"
        }

        for source_key, target_section in mapping.items():
            if source_key in facts:
                entries = facts[source_key] if isinstance(facts[source_key], list) else [facts[source_key]]
                for entry in entries:
                    if isinstance(entry, dict):
                        quote = entry.get("quote", "")
                    else:
                        quote = str(entry) if entry else ""

                    quote = quote.strip()
                    if quote and quote not in sections[target_section]:
                        sections[target_section].append(quote)

        return sections

    def _compute_hybrid_gaps(self, facts: dict, sections: dict) -> dict:
        """
        GAPs híbrido:
        - Si una sección está vacía -> gap de SECCIÓN
        - Si tiene algo pero faltan subcampos críticos -> lista subcampos faltantes
        """
        # 1) Campos presentes (aprox): si la sección tiene contenido, marcamos sus campos como presentes
        present_fields = set()
        for sec, vals in sections.items():
            if vals:
                # Aproximación: si hay contenido en la sección, asumimos algunos campos presentes
                for field in FIELDS.get(sec, []):
                    # Solo marcar como presente si realmente vemos evidencia
                    for val in vals:
                        if field in val.lower().replace(" ", "_"):
                            present_fields.add(field)

        # 2) Construir faltantes por sección
        section_gaps_critical = []
        section_gaps_nice = []
        subfield_gaps_critical = {}
        subfield_gaps_nice = {}

        # Definir qué campos son críticos (subset de todos los campos)
        CRITICAL_FIELDS_SET = set(
            FIELDS.get("unit_economics", []) +
            FIELDS.get("gtm_sales", []) +
            FIELDS.get("business_model_pricing", []) +
            ["revenue", "gmv", "burn", "runway_months", "funding_rounds"]
        )

        for sec in SECTIONS_ORDER:
            section_fields = FIELDS.get(sec, [])
            section_has_content = bool(sections.get(sec))

            if not section_has_content:
                # Gap de sección completa
                section_name = SECTION_TITLE[sec].rstrip(":")
                if sec in CRITICAL_SECTIONS:
                    section_gaps_critical.append(section_name)
                else:
                    section_gaps_nice.append(section_name)
            else:
                # Sección parcial: verificar campos faltantes
                missing_fields = [f for f in section_fields if f not in present_fields]
                missing_critical = [f for f in missing_fields if f in CRITICAL_FIELDS_SET]
                missing_nice = [f for f in missing_fields if f not in CRITICAL_FIELDS_SET]

                if missing_critical and sec in CRITICAL_SECTIONS:
                    subfield_gaps_critical[sec] = missing_critical[:3]  # Max 3 campos
                elif missing_nice:
                    subfield_gaps_nice[sec] = missing_nice[:3]  # Max 3 campos

        return {
            "section_critical": section_gaps_critical,
            "section_nice": section_gaps_nice,
            "subfield_critical": subfield_gaps_critical,
            "subfield_nice": subfield_gaps_nice,
        }

    def _format_hybrid_gaps(self, gaps: dict) -> tuple:
        """Format gaps in hybrid mode (smart)"""
        critical_lines = []
        nice_lines = []

        # 1) Secciones completamente ausentes
        for name in gaps["section_critical"]:
            critical_lines.append(f"• {name}")

        # 2) Secciones parciales con campos faltantes
        for sec, fields in gaps["subfield_critical"].items():
            if fields:
                section_name = SECTION_TITLE[sec].rstrip(":")
                fields_str = ", ".join([f.replace("_", " ") for f in fields])
                critical_lines.append(f"• {section_name} — faltan: {fields_str}")

        # 3) Nice-to-have sections
        for name in gaps["section_nice"]:
            nice_lines.append(f"• {name}")

        # 4) Nice-to-have fields
        for sec, fields in gaps["subfield_nice"].items():
            if fields:
                section_name = SECTION_TITLE[sec].rstrip(":")
                fields_str = ", ".join([f.replace("_", " ") for f in fields])
                nice_lines.append(f"• {section_name} — faltan: {fields_str}")

        return critical_lines, nice_lines

    def _build_analyst_output(self, sections: dict, facts: dict = None) -> str:
        """Build fixed format analyst output with configurable gaps mode"""
        lines = ["📊 **ANÁLISIS DEL DECK**\n"]

        # Render each section in fixed order
        for section_key in SECTIONS_ORDER:
            title = SECTION_TITLE[section_key]
            bullet_limit = BULLETS_LIMITS.get(section_key, DEFAULT_BULLET_LIMIT)
            bullets = sections.get(section_key, [])[:bullet_limit]

            if bullets:  # Has data - show it
                lines.append(f"**{title}**")
                for bullet in bullets:
                    lines.append(f"• {bullet}")
                lines.append("")  # Blank line

        # Use configurable gap mode
        gap_mode = getattr(self, "GAP_MODE", "smart")
        max_subfields = getattr(self, "MAX_GAP_SUBFIELDS", 3)

        # Compute gaps with hybrid approach
        gaps = self._compute_hybrid_gaps(facts or {}, sections)

        # Format gaps based on configured mode
        if gap_mode == "section":
            # Only show section-level gaps
            critical_lines = [f"• {name}" for name in gaps["section_critical"]]
            nice_lines = [f"• {name}" for name in gaps["section_nice"]]
        elif gap_mode == "field":
            # Only show field-level gaps
            critical_lines = []
            nice_lines = []
            for sec, fields in gaps["subfield_critical"].items():
                if fields:
                    section_name = SECTION_TITLE[sec].rstrip(":")
                    fields_str = ", ".join([f.replace("_", " ") for f in fields[:max_subfields]])
                    critical_lines.append(f"• {section_name} — faltan: {fields_str}")
            for sec, fields in gaps["subfield_nice"].items():
                if fields:
                    section_name = SECTION_TITLE[sec].rstrip(":")
                    fields_str = ", ".join([f.replace("_", " ") for f in fields[:max_subfields]])
                    nice_lines.append(f"• {section_name} — faltan: {fields_str}")
        else:  # "smart" mode (default)
            critical_lines, nice_lines = self._format_hybrid_gaps(gaps)

        # Add gaps section
        lines.append("\n⚠️ **GAPS DETECTADOS**\n")

        lines.append("**Críticos:**")
        if critical_lines:
            lines.extend(critical_lines)
        else:
            lines.append("• Ninguno - información crítica completa")

        lines.append("\n**Nice-to-have:**")
        if nice_lines:
            lines.extend(nice_lines)
        else:
            lines.append("• Ninguno")

        return "\n".join(lines)

    def analyze_dataroom(self, processed_documents: List[Dict[str, Any]],
                         document_summary: Dict[str, Any],
                         market_profile=None) -> Dict[str, Any]:
        """Generate Deck Summary (facts-only) + Gaps (Critical/Nice-to-have), sin inferencias."""
        try:
            logger.info("🧠 Starting AI analysis with deck summary approach...")

            # Store documents for Q&A
            self.processed_documents = processed_documents

            # Store full text for Q&A if available
            self.full_text = ""
            for doc in processed_documents:
                if doc.get('full_text'):
                    self.full_text += f"\n\n--- {doc.get('name', 'Document')} ---\n\n"
                    self.full_text += doc['full_text']

            if self.full_text:
                logger.info(f"📖 Stored {len(self.full_text)} chars of full text for Q&A")

            context = self._prepare_analysis_context(processed_documents, document_summary)

            # 1) Hechos: JSON del extractor (autoridad)
            facts = context.get("facts_json_obj") or {}

            # Add market profile to facts if available
            if market_profile:
                facts['market_detection'] = {
                    'vertical': market_profile.vertical,
                    'sub_vertical': market_profile.sub_vertical,
                    'solution': getattr(market_profile, 'solution', ''),
                    'target_market': getattr(market_profile, 'target_market', ''),
                    'geo_focus': getattr(market_profile, 'geo_focus', '')
                }

            docs_meta = json.loads(context['documents_summary'])

            # Sanity checks and logging
            assert isinstance(facts, dict), f"facts must be dict, got {type(facts)}"
            logger.info(f"📊 Facts loaded: {len([k for k,v in facts.items() if v])} non-empty sections")
            if facts.get('financials'):
                fin = facts['financials']
                logger.info(f"  💰 Financial data: GMV={len(fin.get('gmv', []))}, Revenue={len(fin.get('revenue', []))}, Funding={len(fin.get('funding_rounds', []))}")
            if facts.get('team'):
                logger.info(f"  👥 Team entries: {len(facts['team'])}")
            if facts.get('competition'):
                logger.info(f"  🎯 Competition entries: {len(facts['competition'])}")

            # 2) NEW SIMPLIFIED APPROACH: Use full text for analysis
            if self.full_text:
                logger.info("🔄 Using SIMPLIFIED analysis with full text...")
                final = self._generate_simple_analyst_summary(self.full_text, facts)
            else:
                # Fallback to canonical formatting if no full text
                logger.info("⚠️ No full text available, using canonical formatting...")
                sections = self._collect_by_section(facts)

                # Log what we collected per section
                logger.info(f"📝 Data collected by section:")
                for section_key in SECTIONS_ORDER:
                    bullets = sections.get(section_key, [])
                    if bullets:
                        logger.info(f"  - {SECTION_TITLE[section_key]} {len(bullets)} items")

                # 3) Build analyst output with gaps (passing facts for field-level detection)
                final = self._build_analyst_output(sections, facts)

            # Apply emoji mapping if needed
            final = self._map_emojis(final)

            # Final guard against raw dicts
            if self._contains_raw_dicts(final):
                logger.error("❌ Raw dicts detected in final output!")
                final = self._sanitize_raw_dicts(final)

            # Store for future Q&A
            self.current_analysis = final
            self.analysis_context = context

            logger.info("✅ AI analysis completed successfully")
            logger.info(f"🔍 RETURNING RESULT (type: dict, length: {len(final)})")
            return {"ok": True, "slack_ready_content": final}

        except Exception as e:
            logger.error(f"❌ AI analysis failed: {e}")
            import traceback
            logger.error(f"🔍 FULL TRACEBACK: {traceback.format_exc()}")
            return {
                'error': str(e),
                'executive_summary': ['Analysis failed due to technical error'],
                'scoring': {},
                'red_flags': ['Could not complete analysis'],
                'missing_info': ['Analysis incomplete'],
                'recommendation': 'TECHNICAL_ERROR'
            }

    def _prepare_analysis_context(self, processed_documents: List[Dict[str, Any]],
                                 document_summary: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare structured context for AI analysis"""

        # Document metadata summary
        docs_summary = []
        full_content = ""
        merged_facts: Dict[str, Any] = {}  # JSON de extractor (autoritativo cuando existe)

        for doc in processed_documents:
            if doc['type'] != 'error' and doc.get('content'):
                docs_summary.append({
                    'name': doc['name'],
                    'type': doc['type'],
                    'content_length': len(doc['content']),
                    'metadata': doc.get('metadata', {})
                })

                # Add content with document separator
                full_content += f"\n\n=== DOCUMENT: {doc['name']} ===\n"
                full_content += doc['content']  # ✅ sin truncamiento: preserva fidelidad para el análisis

                # Si el extractor dejó JSON estricto (nuestro GPT-4o), acumúlalo
                if doc['type'] == 'pdf':
                    try:
                        parsed = json.loads(doc['content'])
                        # normalización mínima y merge
                        parsed = self._normalize_financials(parsed)
                        for k, v in parsed.items():
                            if isinstance(v, list):
                                merged_facts[k] = (merged_facts.get(k, []) or []) + v
                            elif isinstance(v, dict):
                                merged_facts[k] = {**merged_facts.get(k, {}), **v}
                            else:
                                merged_facts[k] = v
                    except Exception:
                        pass

                # También procesar facts_json directamente si está disponible
                if doc.get('facts_json'):
                    try:
                        facts_data = doc['facts_json']
                        if isinstance(facts_data, str):
                            facts_data = json.loads(facts_data)

                        # normalización mínima y merge
                        facts_data = self._normalize_financials(facts_data)
                        for k, v in facts_data.items():
                            if isinstance(v, list):
                                merged_facts[k] = (merged_facts.get(k, []) or []) + v
                            elif isinstance(v, dict):
                                merged_facts[k] = {**merged_facts.get(k, {}), **v}
                            else:
                                merged_facts[k] = v
                    except Exception:
                        pass

                # CRITICAL: Process structured_data when available (from GPT4o processor)
                if doc.get('structured_data'):
                    try:
                        structured = doc['structured_data']
                        if isinstance(structured, str):
                            structured = json.loads(structured)

                        # Merge structured data into facts
                        structured = self._normalize_financials(structured)
                        for k, v in structured.items():
                            if isinstance(v, list):
                                merged_facts[k] = (merged_facts.get(k, []) or []) + v
                            elif isinstance(v, dict):
                                merged_facts[k] = {**merged_facts.get(k, {}), **v}
                            else:
                                merged_facts[k] = v
                    except Exception as e:
                        logger.warning(f"Failed to process structured_data: {e}")

        facts_str = json.dumps(merged_facts, ensure_ascii=False) if merged_facts else ""
        return {
            'documents_summary': json.dumps(docs_summary, indent=2),
            'full_content': full_content,
            'facts_json_str': facts_str,
            'facts_json_obj': merged_facts if merged_facts else None,
            'document_count': len(docs_summary),
            'total_content_length': len(full_content)
        }


    def answer_question(self, question: str) -> str:
        """Answer specific questions about the analyzed data room"""
        try:
            # Check if we have data to work with
            if not self.full_text and (not self.current_analysis or not self.analysis_context):
                return "❌ No data room has been analyzed yet. Please run /analyze first."

            logger.info(f"🤔 Answering question: {question[:100]}...")

            # Prioritize full_text if available (most complete content)
            if self.full_text:
                logger.info("📖 Using full text for Q&A (best quality)")
                content_for_qa = self.full_text
            elif self.analysis_context and 'full_content' in self.analysis_context:
                logger.info("📄 Using analysis context for Q&A")
                content_for_qa = self.analysis_context['full_content']
            else:
                return "❌ No content available for Q&A. Please run /analyze first."

            # Extract financial data for Q&A context
            from utils.financial_extractor import extract_financial_data, format_financial_data_for_prompt
            financial_data = extract_financial_data(content_for_qa)
            formatted_financials = format_financial_data_for_prompt(financial_data)

            # Create Q&A prompt with FULL CONTENT and EXTRACTED FINANCIAL DATA
            qa_prompt = QA_PROMPT.format(
                analyzed_documents_summary=content_for_qa,  # ← CONTENIDO REAL sin truncamiento
                extracted_financials=formatted_financials,
                user_question=question
            )

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert VC analyst who has just completed a comprehensive data room analysis."},
                    {"role": "user", "content": qa_prompt}
                ],
                max_tokens=500,
                temperature=0.2
            )

            answer = response.choices[0].message.content
            logger.info("✅ Question answered successfully")
            return answer

        except Exception as e:
            logger.error(f"❌ Failed to answer question: {e}")
            return f"❌ Sorry, I couldn't answer that question due to a technical error: {str(e)}"


    def analyze_gaps(self) -> str:
        """Analyze information gaps using Slack-Ready approach with Critical Gaps"""
        try:
            if not self.current_analysis or not self.analysis_context:
                return "❌ No data room has been analyzed yet. Please run `/analyze` first."

            logger.info("🔍 Using new Slack-Ready gaps analysis with Critical Gaps...")

            # Extract financial data deterministically
            from utils.financial_extractor import extract_financial_data, format_financial_data_for_prompt
            financial_data = extract_financial_data(self.analysis_context['full_content'])
            formatted_financials = format_financial_data_for_prompt(financial_data)

            # Prepare analysis summary (simplified for Slack-Ready)
            analysis_summary = json.dumps({
                'content_type': 'slack_ready_analysis',
                'content_length': self.current_analysis.get('content_length', 0),
                'analysis_sections': 'All sections successfully extracted'
            }, indent=2)

            # Use new Slack-Ready gaps prompt with Critical Gaps
            gaps_prompt = SLACK_READY_GAPS_PROMPT.format(
                analysis_summary=analysis_summary,
                extracted_financials=formatted_financials,
                documents_summary=self.analysis_context['full_content']  # Pass ACTUAL CONTENT like /ask does sin truncamiento
            )

            logger.info("🚨 TESTING: Using Slack-Ready gaps prompt with Critical Gaps distinction")

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a senior VC analyst providing professional gaps analysis ready for Slack display."},
                    {"role": "user", "content": gaps_prompt}
                ],
                max_tokens=800,  # Smaller for Slack format
                temperature=0.2
            )

            # Return the Slack-ready gaps analysis directly
            gaps_analysis = response.choices[0].message.content

            logger.info(f"🔍 SLACK-READY GAPS (length: {len(gaps_analysis)} chars)")
            logger.info("✨ Direct gaps output with Critical Gaps - no parsing needed!")

            return gaps_analysis

        except Exception as e:
            logger.error(f"❌ Failed to analyze gaps: {e}")
            return f"❌ Sorry, I couldn't analyze gaps due to a technical error: {str(e)}"


    def reset_analysis(self):
        """Reset current analysis context"""
        self.current_analysis = None
        self.analysis_context = None
        logger.info("🔄 Analysis context reset")

    # ---------- Formatting Helpers ----------
    def _fmt_currency(self, value: Optional[str], currency: Optional[str]) -> str:
        """Format currency values properly."""
        v = (value or "").strip()
        c = (currency or "").strip()
        if not v:
            return ""
        # Handle EUR/USD/etc formatting
        if c:
            if c.upper() in ['EUR', 'USD', 'GBP']:
                return f"{c.upper()} {v}"
            elif c == '€':
                return f"€{v}"
            elif c == '$':
                return f"${v}"
            else:
                return f"{c}{v}"
        return v

    def _fmt_financial_entry(self, metric: str, entry: Dict[str, Any]) -> Optional[str]:
        """Format financial entries into readable text."""
        m = metric.lower()

        # GMV, Revenue, VAT, Burn
        if m in ("gmv", "revenue", "vat", "burn"):
            num = self._fmt_currency(entry.get("value"), entry.get("currency"))
            if not num:
                return None
            txt = f"{m.upper()}: {num}"
            period = entry.get("period")
            if period:
                txt += f" ({period})"
            return txt

        # Runway
        if m in ("runway", "runway_months"):
            months = entry.get("months") or entry.get("value")
            if months:
                return f"Runway: {months} months"
            return None

        # Funding rounds
        if m == "funding_rounds":
            parts = []
            if entry.get("round"):
                parts.append(f"{entry['round']} round")
            amt = self._fmt_currency(entry.get("amount"), entry.get("currency"))
            if amt:
                parts.append(amt)
            if entry.get("valuation"):
                val = self._fmt_currency(entry.get("valuation"), entry.get("currency", "€"))
                parts.append(f"@ {val} valuation")
            return " ".join(parts) if parts else None

        # Fallback to quote if available
        return entry.get("quote")

    # ---------- Helpers: Summary ----------
    def _collect_relevant_insights(self, facts: Dict[str, Any], docs_meta: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert facts JSON into formatted insights with citation info."""
        insights = []

        def add_insight(section: str, item: Any):
            if not item:
                return

            text = ""
            slide = None
            doc_name = None

            # Handle dict items
            if isinstance(item, dict):
                # Extract citation info
                slide = item.get("slide")
                doc_name = item.get("doc")

                # Format based on section type
                if section in ["gmv", "revenue", "vat", "burn", "runway", "runway_months", "funding_rounds"]:
                    # Financial metric - use specialized formatter
                    text = self._fmt_financial_entry(section, item)
                elif "quote" in item:
                    # Non-financial with quote field
                    text = item.get("quote", "")
                else:
                    # Try to format as financial if it has value/currency
                    if "value" in item or "amount" in item:
                        text = self._fmt_financial_entry(section, item)
                    else:
                        # Last resort - skip raw dicts
                        return
            elif isinstance(item, str):
                text = item
            else:
                return

            # Clean and validate text
            if text:
                text = str(text).strip()
            if not text or len(text) < 5:  # Reduced minimum length
                return

            # Anti-noise filter (minimal - let most content through)
            if self._NOISE_PATTERNS.search(text):
                logger.debug(f"Filtered out noise: {text[:50]}...")
                return
                
            # Extraer información de cita
            slide = None
            doc_name = None
            if isinstance(item, dict):
                slide = item.get("slide")
                doc_name = item.get("doc")
                
            insights.append({
                "text": text,
                "section": section,
                "slide": slide,
                "doc": doc_name
            })
        
        # Helper para financials
        def add_financial(metric: str, entry: Any):
            if isinstance(entry, list):
                for e in entry:
                    add_insight(metric, e)
            elif entry:
                add_insight(metric, entry)

        # Process all facts
        logger.debug(f"Processing facts with keys: {list(facts.keys())}")
        for key, val in facts.items():
            if isinstance(val, list):
                logger.debug(f"Processing list section '{key}' with {len(val)} items")
                for item in val:
                    add_insight(key, item)
            elif isinstance(val, dict):
                # Financials come as nested dict
                if key == "financials":
                    logger.debug(f"Processing financials dict with keys: {list(val.keys())}")
                    for metric, entries in val.items():
                        if isinstance(entries, list):
                            logger.debug(f"  - {metric}: {len(entries)} entries")
                            for e in entries:
                                add_insight(metric, e)
                        elif entries:
                            add_insight(metric, entries)
                else:
                    # Other dict sections - try to extract meaningful content
                    for sub_key, sub_val in val.items():
                        if isinstance(sub_val, list):
                            for item in sub_val:
                                add_insight(sub_key, item)
                        elif sub_val:
                            add_insight(sub_key, sub_val)
            elif val:
                add_insight(key, val)
        
        # Expand team insights if they're comma-separated
        insights = self._expand_team_insights(insights, max_items=3)

        # Remove financial duplicates (same value different metrics)
        insights = self._squash_financial_duplicates(insights)

        # De-duplicate by text (case-insensitive)
        seen = set()
        unique_insights = []
        for ins in insights:
            t = ins.get("text", "").strip().casefold()
            if not t or t in seen:
                continue
            seen.add(t)
            unique_insights.append(ins)

        return unique_insights
    
    def _is_relevant_for_vc(self, text: str) -> bool:
        """Criterios simples de relevancia para VCs basados en patrones."""
        # Métricas específicas (números + unidades)
        if self.NUMERIC_PATTERNS.search(text):
            return True
            
        # Información de equipo con credenciales
        if self.TEAM_PATTERNS.search(text):
            return True
            
        # Competidores nombrados
        if self.COMPETITOR_PATTERNS.search(text):
            return True
            
        # Información de funding
        if self.FUNDING_PATTERNS.search(text):
            return True
            
        # Si es suficientemente descriptivo (no frases vagas)
        if len(text.strip()) > 30 and any(keyword in text.lower() for keyword in 
            ['customers', 'revenue', 'users', 'growth', 'market', 'product', 'technology']):
            return True
            
        return False
    
    def _build_deck_summary(self, insights: List[Dict[str, Any]], max_bullets: int = 12) -> str:
        """Build diversified summary (max 2 bullets per section) without raw dicts."""
        # Diversify insights to avoid one section dominating
        insights = self._rank_diversify(insights, max_bullets=max_bullets, per_section_cap=2)
        lines = []

        for insight in insights:
            # Ensure text is a string
            text = insight.get('text')
            if not isinstance(text, str):
                # Last resort - convert to string
                logger.warning(f"Non-string text found in insight: {type(text)}")
                text = json.dumps(text, ensure_ascii=False) if text else "[formatting error]"

            if self.SHOW_CITATIONS:
                cite_parts = []
                if insight.get("slide"):
                    cite_parts.append(f"S{insight['slide']}")

                cite_str = f" ({' · '.join(cite_parts)})" if cite_parts else ""
                lines.append(f"• {text}{cite_str}")
            else:
                lines.append(f"• {text}")

        return "\n".join(lines)
    
    # ---------- Helpers: Gaps ----------
    def _compute_gaps(self, facts: Dict[str, Any]) -> Dict[str, List[str]]:
        """Evalúa qué secciones faltan según nuestro rubric."""
        present_sections = {k for k, v in facts.items() if v}
        
        critical_missing = []
        nice_missing = []
        
        for section in self.CRITICAL_SECTIONS:
            if section not in present_sections:
                critical_missing.append(section)
                
        for section in self.NICE_TO_HAVE_SECTIONS:
            if section not in present_sections:
                nice_missing.append(section)
                
        # Validación especial: si financials está presente pero sin métricas clave
        if "financials" in present_sections:
            text_blob = json.dumps(facts.get("financials"), ensure_ascii=False)
            if not self.NUMERIC_PATTERNS.search(text_blob):
                critical_missing.append("financials (no key metrics)")
                
        return {
            "critical": sorted(set(critical_missing)),
            "nice": sorted(set(nice_missing))
        }
    
    # ---------- Post-processing helpers ----------
    def _expand_team_insights(self, insights: List[Dict[str, Any]], max_items: int = 3) -> List[Dict[str, Any]]:
        """Expand comma-separated team entries into individual bullets."""
        out = []
        for ins in insights:
            if ins.get("section") == "team" and isinstance(ins.get("text"), str) and "," in ins["text"]:
                # Split by comma and keep parts with roles
                parts = [p.strip() for p in ins["text"].split(",") if p.strip()]
                picks = []
                for p in parts:
                    if re.search(r"\b(CEO|CTO|CMO|CFO|co-?founder|founder)\b", p, re.I):
                        picks.append(p)
                    if len(picks) >= max_items:
                        break
                if picks:
                    out.extend([{"text": f"{t}", "section": "team", "slide": ins.get("slide")} for t in picks])
                    continue
            out.append(ins)
        return out

    def _squash_financial_duplicates(self, insights: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate financial metrics with same value, keeping most specific."""
        sig = {}
        out = []
        pat = re.compile(r"^(GMV|REVENUE|VAT|BURN):\s*([€$]?\s?[A-Za-z0-9\.\,]+)(?:\s*\(([^)]+)\))?", re.I)

        for ins in insights:
            t = ins.get("text", "")
            m = pat.match(t)
            if not m:
                out.append(ins)
                continue

            metric = m.group(1).upper()
            value = m.group(2).strip()
            period = (m.group(3) or "").strip()
            key = (metric, value)
            prev = sig.get(key)

            # Prefer entries with specific period over generic/future
            is_better = prev is None or (period and period.lower() != "future" and
                                        (prev.get("period", "").lower() in ("", "future")))
            if is_better:
                sig[key] = {"ins": ins, "period": period}

        # Reconstruct: chosen financials + non-financials
        chosen = {id(v["ins"]) for v in sig.values()}
        seen = set()

        # Add chosen financial metrics
        for ins in insights:
            if id(ins) in chosen and id(ins) not in seen:
                out.append(ins)
                seen.add(id(ins))

        # Add non-financial insights
        for ins in insights:
            if id(ins) not in seen and not pat.match(ins.get("text", "")):
                out.append(ins)
                seen.add(id(ins))

        return out

    def _rank_diversify(self, insights: List[Dict[str, Any]], max_bullets: int, per_section_cap: int = 2) -> List[Dict[str, Any]]:
        """Diversify insights with max 2 per section, prioritizing important sections."""
        # Priority order for VCs
        order = ["gmv", "revenue", "vat", "funding_rounds", "traction", "team", "product",
                "market", "competition", "gtm", "roadmap", "business_model", "risks", "why_now"]

        by_sec = {s: [] for s in order}
        others = []

        # Group insights by section
        for ins in insights:
            sec = (ins.get("section") or "").lower()
            if sec in by_sec:
                by_sec[sec].append(ins)
            else:
                others.append(ins)

        result = []
        # Add insights in priority order
        for sec in order:
            src = by_sec.get(sec, [])
            for ins in src[:per_section_cap]:
                result.append(ins)
                if len(result) >= max_bullets:
                    return result

        # Add other insights if space remains
        for ins in others[:per_section_cap]:
            result.append(ins)
            if len(result) >= max_bullets:
                return result

        return result[:max_bullets]

    def _format_gaps(self, gaps: Dict[str, List[str]]) -> str:
        """Formatea la sección de gaps para output final."""
        lines = []
        
        critical = gaps.get("critical", [])
        nice = gaps.get("nice", [])
        
        if critical:
            lines.append("**Critical**:")
            for gap in critical:
                lines.append(f"• {gap}")
        else:
            lines.append("**Critical**: none detected")
            
        if nice:
            lines.append("\n**Nice-to-have**:")
            for gap in nice:
                lines.append(f"• {gap}")
                
        return "\n".join(lines)
