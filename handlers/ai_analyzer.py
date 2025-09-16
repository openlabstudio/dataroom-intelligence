"""
AI Analysis handler for DataRoom Intelligence Bot
Integrates with OpenAI GPT-4 to analyze data room documents
"""

import json
from typing import Dict, List, Any, Optional
from openai import OpenAI
from config.settings import config
from prompts.analysis_prompts import DATAROOM_ANALYSIS_PROMPT, SCORING_PROMPT
from prompts.qa_prompts import QA_PROMPT, MEMO_PROMPT, GAPS_PROMPT
from utils.logger import get_logger

logger = get_logger(__name__)

class AIAnalyzer:
    """Handles AI-powered analysis of data room documents using OpenAI GPT-4"""

    def __init__(self):
        self.client = OpenAI(api_key=config.OPENAI_API_KEY)
        self.model = "gpt-4"
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
            
            # Create enhanced analysis prompt with extracted financial data
            analysis_prompt = DATAROOM_ANALYSIS_PROMPT.format(
                documents_with_metadata=context['documents_summary'],
                document_contents=context['full_content'][:25000],  # Increased to ensure financial data is included
                extracted_financials=formatted_financials
            )

            # Call GPT-4 for analysis
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a senior venture capital analyst with 15+ years of experience in due diligence and startup evaluation."},
                    {"role": "user", "content": analysis_prompt}
                ],
                max_tokens=2000,
                temperature=0.3
            )



            # Parse and structure the analysis
            analysis_result = response.choices[0].message.content

            # Debug: Log the raw AI response to understand the format
            logger.info(f"🔍 RAW AI RESPONSE (first 1000 chars):")
            logger.info(f"{analysis_result[:1000]}...")

            structured_analysis = self._parse_analysis_response(analysis_result)
            # Store for future Q&A
            self.current_analysis = structured_analysis
            self.analysis_context = context

            logger.info("✅ AI analysis completed successfully")
            return structured_analysis

        except Exception as e:
            logger.error(f"❌ AI analysis failed: {e}")
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
                full_content += doc['content'][:10000]  # Increased limit to capture financial data

        return {
            'documents_summary': json.dumps(docs_summary, indent=2),
            'full_content': full_content,
            'document_count': len(docs_summary),
            'total_content_length': len(full_content)
        }

    def _parse_analysis_response(self, analysis_text: str) -> Dict[str, Any]:
        """Parse GPT-4 analysis response into structured format with robust scoring extraction"""
        try:
            import re

            # Initialize default structure
            analysis = {
                'executive_summary': [],
                'value_proposition': [],
                'market_analysis': [],
                'competitors': [],
                'product_roadmap': [],
                'go_to_market_strategy': [],
                'financial_highlights': []
            }

            # Improved semantic parsing - look for concepts, not exact format
            def extract_semantic_content(text, keywords, section_name):
                """Extract content semantically using multiple approaches"""
                points = []

                # Approach 1: Look for sections with keywords (with or without numbers)
                for keyword in keywords:
                    patterns = [
                        # With numbers: "1. EXECUTIVE SUMMARY:"
                        rf'\d+\.\s*{keyword}.*?:(.*?)(?=\d+\.|[A-Z]{{3,}}.*?:|$)',
                        # Without numbers: "EXECUTIVE SUMMARY:"
                        rf'^{keyword}.*?:(.*?)(?=^[A-Z]{{3,}}.*?:|$)',
                        # Markdown style: "**EXECUTIVE SUMMARY**"
                        rf'\*\*{keyword}\*\*(.*?)(?=\*\*|$)',
                        # Hash headers: "## EXECUTIVE SUMMARY"
                        rf'## {keyword}(.*?)(?=##|$)',
                        # Simple keyword match: "EXECUTIVE SUMMARY"
                        rf'{keyword}:(.*?)(?=[A-Z]{{3,}}:|$)'
                    ]

                    for pattern in patterns:
                        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE | re.MULTILINE)
                        if match:
                            content = match.group(1).strip()
                            # Extract bullet points
                            for line in content.split('\n'):
                                line = line.strip()
                                if line.startswith(('-', '•', '*')) and len(line) > 5:
                                    points.append(line[1:].strip())
                            if points:
                                logger.info(f"📍 Found {section_name} using pattern: {keyword}")
                                return points

                # Approach 2: If no structured format, extract sentences containing keywords
                sentences = re.split(r'[.!?]+', text)
                for sentence in sentences:
                    sentence = sentence.strip()
                    if len(sentence) > 20 and any(keyword.lower() in sentence.lower() for keyword in keywords):
                        points.append(sentence)
                        if len(points) >= 5:  # Limit to avoid too much content
                            break

                return points[:5]  # Maximum 5 points per section

            # Extract each section using semantic approach
            analysis['executive_summary'] = extract_semantic_content(analysis_text,
                ['EXECUTIVE SUMMARY', 'SUMMARY', 'OVERVIEW'], 'Executive Summary')

            analysis['value_proposition'] = extract_semantic_content(analysis_text,
                ['VALUE PROPOSITION', 'VALUE', 'PROPOSITION', 'UNIQUE SELLING'], 'Value Proposition')

            analysis['market_analysis'] = extract_semantic_content(analysis_text,
                ['MARKET ANALYSIS', 'MARKET', 'TAM', 'SAM', 'OPPORTUNITY'], 'Market Analysis')

            analysis['competitors'] = extract_semantic_content(analysis_text,
                ['COMPETITORS', 'COMPETITIVE', 'COMPETITION', 'BENCHMARK'], 'Competitors')

            analysis['product_roadmap'] = extract_semantic_content(analysis_text,
                ['PRODUCT ROADMAP', 'ROADMAP', 'DEVELOPMENT', 'FEATURES'], 'Product Roadmap')

            analysis['go_to_market_strategy'] = extract_semantic_content(analysis_text,
                ['GO-TO-MARKET', 'GO TO MARKET', 'GTM', 'STRATEGY', 'SALES'], 'Go-to-Market Strategy')

            analysis['financial_highlights'] = extract_semantic_content(analysis_text,
                ['FINANCIAL', 'REVENUE', 'FUNDING', 'GROWTH', 'METRICS'], 'Financial Highlights')


            # Fallback: If parsing failed completely, extract basic information
            total_points = sum(len(v) for v in analysis.values())
            if total_points == 0:
                logger.warning("⚠️ All sections empty - using fallback parsing")
                # Split response into sentences and distribute among sections
                sentences = [s.strip() for s in analysis_text.split('.') if len(s.strip()) > 20]
                if sentences:
                    # Distribute sentences across sections
                    section_count = len(analysis)
                    per_section = max(1, len(sentences) // section_count)

                    sections = list(analysis.keys())
                    for i, section in enumerate(sections):
                        start_idx = i * per_section
                        end_idx = min((i + 1) * per_section, len(sentences))
                        analysis[section] = sentences[start_idx:end_idx]

                    logger.info(f"🔄 Fallback: Distributed {len(sentences)} sentences across sections")

            # Log parsing results
            logger.info(f"📋 Parsing results:")
            logger.info(f"   Executive summary: {len(analysis['executive_summary'])} points")
            logger.info(f"   Value proposition: {len(analysis.get('value_proposition', []))} points")
            logger.info(f"   Market analysis: {len(analysis.get('market_analysis', []))} points")
            logger.info(f"   Competitors: {len(analysis.get('competitors', []))} points")
            logger.info(f"   Product roadmap: {len(analysis.get('product_roadmap', []))} points")
            logger.info(f"   Go-to-market strategy: {len(analysis.get('go_to_market_strategy', []))} points")
            logger.info(f"   Financial highlights: {len(analysis.get('financial_highlights', []))} points")

            return analysis

        except Exception as e:
            logger.error(f"❌ Failed to parse analysis response: {e}")
            logger.debug(f"Raw response: {analysis_text[:500]}...")
            return {
                'error': 'Failed to parse analysis',
                'raw_response': analysis_text,
                'executive_summary': ['Analysis parsing failed'],
                'scoring': {},
                'red_flags': ['Could not parse analysis results'],
                'missing_info': [],
                'recommendation': 'TECHNICAL_ERROR'
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
                analyzed_documents_summary=self.analysis_context['full_content'][:10000],  # ← CONTENIDO REAL
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
        """Analyze information gaps for due diligence using comprehensive analysis data"""
        try:
            if not self.current_analysis or not self.analysis_context:
                return "❌ No data room has been analyzed yet. Please run /analyze first."

            logger.info("🔍 Analyzing information gaps with enhanced context...")

            # Extract financial data deterministically
            from utils.financial_extractor import extract_financial_data, format_financial_data_for_prompt
            financial_data = extract_financial_data(self.analysis_context['full_content'])
            formatted_financials = format_financial_data_for_prompt(financial_data)

            # Prepare comprehensive analysis summary for gaps analysis
            analysis_summary = {
                'executive_summary': self.current_analysis.get('executive_summary', []),
                'value_proposition': self.current_analysis.get('value_proposition', []),
                'market_analysis': self.current_analysis.get('market_analysis', []),
                'competitors': self.current_analysis.get('competitors', []),
                'product_roadmap': self.current_analysis.get('product_roadmap', []),
                'go_to_market_strategy': self.current_analysis.get('go_to_market_strategy', []),
                'financial_highlights': self.current_analysis.get('financial_highlights', [])
            }

            # Enhanced gaps prompt with comprehensive context
            enhanced_gaps_prompt = f"""
You are a senior VC analyst who has just completed a comprehensive analysis of a startup's data room. Your task is to identify REAL information gaps based on what was ACTUALLY analyzed.

DOCUMENTS ANALYZED:
{self.analysis_context['documents_summary']}

EXTRACTED FINANCIAL DATA (CONFIRMED PRESENT):
{formatted_financials}

COMPLETE ANALYSIS RESULTS:
{json.dumps(analysis_summary, indent=2)}

CURRENT ANALYSIS STATUS:
- Executive Summary: {len(analysis_summary['executive_summary'])} items
- Value Proposition: {len(analysis_summary['value_proposition'])} items
- Market Analysis: {len(analysis_summary['market_analysis'])} items
- Competitors: {len(analysis_summary['competitors'])} items
- Product Roadmap: {len(analysis_summary['product_roadmap'])} items
- Go-to-Market Strategy: {len(analysis_summary['go_to_market_strategy'])} items
- Financial Highlights: {len(analysis_summary['financial_highlights'])} items

STAGE ASSESSMENT GUIDANCE:
- €2M funding = SEED stage (not Series B/C)
- €12M pre-money valuation = SEED/early Series A maximum
- Look at actual funding amounts to determine stage accurately

CRITICAL INSTRUCTIONS:
1. DO NOT suggest that financial data is missing if it appears in FINANCIAL HIGHLIGHTS above
2. DO NOT suggest competitive info is missing if it appears in COMPETITORS above
3. DO NOT suggest market data is missing if it appears in MARKET ANALYSIS above
4. Focus on ACTUAL documentation gaps, not data that was successfully extracted
5. Assess stage based on ACTUAL funding data (€2M = Seed, not Series B/C)
6. Be SPECIFIC about what documents are genuinely missing for this stage

Based on the comprehensive analysis above, identify what information is genuinely missing for proper due diligence at this company's actual stage.

RESPONSE FORMAT:

**STAGE ASSESSMENT:**
[Based on funding amounts and metrics, determine actual stage]

**INFORMATION ALREADY AVAILABLE:**
- Financial Data: [List specific data found in Financial Highlights]
- Value Proposition: [List value prop elements found]
- Market Analysis: [List market data found]
- Competitive Intelligence: [List competitor info found]
- Product Development: [List roadmap info found]
- Go-to-Market: [List strategy elements found]

**GENUINE GAPS FOR THIS STAGE:**
[Only list information that is truly missing and needed for this stage]

**PRIORITY RECOMMENDATIONS:**
[Rank gaps by actual importance for investment decision]
"""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert VC analyst who provides accurate gap analysis based on comprehensive startup analysis data. You never suggest that information is missing if it was already found and extracted."},
                    {"role": "user", "content": enhanced_gaps_prompt}
                ],
                max_tokens=1200,
                temperature=0.2
            )

            gaps_analysis = response.choices[0].message.content
            logger.info("✅ Enhanced gaps analysis completed successfully")
            return gaps_analysis

        except Exception as e:
            logger.error(f"❌ Failed to analyze gaps: {e}")
            return f"❌ Sorry, I couldn't analyze gaps due to a technical error: {str(e)}"


    def reset_analysis(self):
        """Reset current analysis context"""
        self.current_analysis = None
        self.analysis_context = None
        logger.info("🔄 Analysis context reset")
