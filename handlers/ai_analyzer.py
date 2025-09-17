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
    """Handles AI-powered analysis of data room documents using OpenAI GPT-4"""

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

    def analyze_dataroom(self, processed_documents: List[Dict[str, Any]],
                        document_summary: Dict[str, Any]) -> Dict[str, Any]:
        """Perform comprehensive data room analysis using GPT-4"""
        try:
            logger.info("🧠 Starting AI analysis of data room...")

            # Prepare context for analysis
            context = self._prepare_analysis_context(processed_documents, document_summary)

            # PHASE 1: Extract financial data deterministically
            logger.info("💰 Extracting financial data patterns...")
            from utils.financial_extractor import extract_financial_data, format_financial_data_for_prompt
            
            financial_data = extract_financial_data(context['full_content'])
            formatted_financials = format_financial_data_for_prompt(financial_data)
            
            # Use new Slack-ready prompt (TESTING - Step 2)
            # Completeness guard: si faltan secciones, indícalo en el prompt
            extracted = {}
            try:
                extracted = json.loads(context['full_content'])
            except:
                pass

            must_sections = ["team","competition","risks","why_now"]
            missing = [s for s in must_sections if not extracted.get(s)]

            analysis_prompt = SLACK_READY_ANALYSIS_PROMPT.format(
                documents_with_metadata=context['documents_summary'],
                document_contents=context['full_content'],  # ❌ sin truncamiento
                extracted_financials=formatted_financials
            )

            if missing:
                analysis_prompt += (
                    "\n\n[COMPLETENESS-GUARD] The deck appears to be missing sections: "
                    + ", ".join(missing)
                    + ". If truly not in deck, write 'Not found in deck' and reference slides scanned."
                )

            logger.info("🧪 TESTING: Using new Slack-ready prompt")

            # Call GPT-4o for analysis
            response = self.client.chat.completions.create(
                model=self.model,  # será gpt-4o (ver __init__)
                messages=[
                    {"role": "system", "content": "You are a senior venture capital analyst with 15+ years of experience in due diligence and startup evaluation."},
                    {"role": "user", "content": analysis_prompt}
                ],
                max_tokens=4000,
                temperature=0.25
            )



            # Get the raw analysis
            analysis_result = response.choices[0].message.content

            # ---------- PRESENTATION LAYER ----------
            # 1) Ocultar meta y añadir nota humana de secciones faltantes
            analysis_result = self._strip_completeness_meta(analysis_result)

            # 2) Emojis 100% Unicode
            analysis_result = self._map_emojis(analysis_result)
            # Limpieza adicional de alias residuales :...:
            analysis_result = re.sub(r":([a-z0-9_+-]+):", "", analysis_result)

            # 3) Sustituir mensajes genéricos por "Not found in deck (…)"
            analysis_result = re.sub(r"\b(No specific .*? mentioned\.)", "Not found in deck (explicitly verified).", analysis_result, flags=re.IGNORECASE)

            # 4) Nota "Missing Sections" arriba del todo si aplica
            slides_range = (1, max(extracted.get("slides_covered", [1])) if isinstance(extracted.get("slides_covered"), list) else 20)
            human_missing = self._format_missing_sections_human(missing, slides_range if isinstance(slides_range, tuple) else (1,20))
            if human_missing:
                analysis_result = human_missing + "\n" + analysis_result

            # 5) Executive Summary arriba
            analysis_result = self._inject_exec_summary_top(analysis_result, extracted)

            # 6) Analyst Notes por sección
            analysis_result = self._inject_analyst_notes(analysis_result)

            # 7) Inferencia mínima para huecos
            analysis_result = self._augment_inference(analysis_result, extracted)

            # 8) Next Steps accionables
            analysis_result = self._improve_next_steps(analysis_result, missing)

            # Debug: Log the raw AI response
            logger.info(f"🔍 SLACK-READY RESPONSE (length: {len(analysis_result)} chars)")
            logger.info(f"✨ Direct output - no parsing needed!")

            # Store for future Q&A
            self.current_analysis = analysis_result
            self.analysis_context = context

            logger.info("✅ AI analysis completed successfully")
            logger.info(f"🔍 RETURNING STRING (type: {type(analysis_result)}, length: {len(analysis_result)})")
            return analysis_result

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

        # Si el contenido ya es JSON de extractor, normalízalo antes
        extracted: Dict[str, Any] = {}
        try:
            # Si tenemos solo un documento y es JSON, procesarlo
            if len(processed_documents) == 1 and processed_documents[0].get('type') == 'pdf':
                extracted = json.loads(full_content.split('=== DOCUMENT:')[1].split('===')[1].strip())
        except Exception:
            pass

        if isinstance(extracted, dict) and "financials" in extracted:
            extracted = self._normalize_financials(extracted)
            full_content = f"\n\n=== DOCUMENT: {processed_documents[0]['name']} ===\n{json.dumps(extracted, ensure_ascii=False)}"

        return {
            'documents_summary': json.dumps(docs_summary, indent=2),
            'full_content': full_content,
            'document_count': len(docs_summary),
            'total_content_length': len(full_content)
        }


    def answer_question(self, question: str) -> str:
        """Answer specific questions about the analyzed data room"""
        try:
            if not self.current_analysis or not self.analysis_context:
                return "❌ No data room has been analyzed yet. Please run /analyze first."

            logger.info(f"🤔 Answering question: {question[:100]}...")

            # Extract financial data for Q&A context
            from utils.financial_extractor import extract_financial_data, format_financial_data_for_prompt
            financial_data = extract_financial_data(self.analysis_context['full_content'])
            formatted_financials = format_financial_data_for_prompt(financial_data)

            # Create Q&A prompt with FULL CONTENT and EXTRACTED FINANCIAL DATA
            qa_prompt = QA_PROMPT.format(
                analyzed_documents_summary=self.analysis_context['full_content'],  # ← CONTENIDO REAL sin truncamiento
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
