"""
AI Analysis handler for DataRoom Intelligence Bot
Integrates with OpenAI GPT-5 to analyze data room documents
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
    """Handles AI-powered analysis of data room documents using OpenAI GPT-5"""

    def __init__(self):
        self.client = OpenAI(api_key=config.OPENAI_API_KEY)
        self.model = "gpt-4"
        self.current_analysis = None
        self.analysis_context = None

    def analyze_dataroom(self, processed_documents: List[Dict[str, Any]],
                        document_summary: Dict[str, Any]) -> Dict[str, Any]:
        """Perform comprehensive data room analysis using GPT-5"""
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

            # Call GPT-5 for analysis
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
        """Parse GPT-5 analysis response into structured format with robust scoring extraction"""
        try:
            import re

            # Initialize default structure
            analysis = {
                'executive_summary': [],
                'scoring': {
                    'team_management': {'score': 0, 'justification': 'Not analyzed'},
                    'business_model': {'score': 0, 'justification': 'Not analyzed'},
                    'financials_traction': {'score': 0, 'justification': 'Not analyzed'},
                    'market_competition': {'score': 0, 'justification': 'Not analyzed'},
                    'technology_product': {'score': 0, 'justification': 'Not analyzed'},
                    'legal_compliance': {'score': 0, 'justification': 'Not analyzed'}
                },
                'overall_score': 0,
                'red_flags': [],
                'missing_info': [],
                'key_questions': [],
                'recommendation': 'INVESTIGATE_FURTHER'
            }

            # Extract executive summary
            exec_match = re.search(r'1\.\s*EXECUTIVE SUMMARY.*?:(.*?)(?=2\.|$)', analysis_text, re.DOTALL | re.IGNORECASE)
            if exec_match:
                exec_content = exec_match.group(1)
                for line in exec_content.split('\n'):
                    line = line.strip()
                    if line.startswith(('-', '•', '*')) and len(line) > 5:
                        analysis['executive_summary'].append(line[1:].strip())

            # Extract scoring with improved regex
            scoring_patterns = {
                'team_management': [r'Team\s*&?\s*Management:?\s*(\d+)/10\s*--?\s*(.*?)(?=\n|Business Model|$)'],
                'business_model': [r'Business Model:?\s*(\d+)/10\s*--?\s*(.*?)(?=\n|Financials|$)'],
                'financials_traction': [r'Financials?\s*&?\s*Traction:?\s*(\d+)/10\s*--?\s*(.*?)(?=\n|Market|$)'],
                'market_competition': [r'Market\s*&?\s*Competition:?\s*(\d+)/10\s*--?\s*(.*?)(?=\n|Technology|$)'],
                'technology_product': [r'Technology/?Product:?\s*(\d+)/10\s*--?\s*(.*?)(?=\n|Legal|$)'],
                'legal_compliance': [r'Legal\s*&?\s*Compliance:?\s*(\d+)/10\s*--?\s*(.*?)(?=\n|3\.|$)']
            }

            for category, patterns in scoring_patterns.items():
                for pattern in patterns:
                    match = re.search(pattern, analysis_text, re.DOTALL | re.IGNORECASE)
                    if match:
                        try:
                            score = int(match.group(1))
                            justification = match.group(2).strip()
                            analysis['scoring'][category] = {
                                'score': max(0, min(10, score)),  # Ensure score is 0-10
                                'justification': justification if justification else f"Score: {score}/10"
                            }
                            logger.debug(f"✅ Extracted {category}: {score}/10")
                        except (ValueError, IndexError) as e:
                            logger.debug(f"⚠️ Failed to parse {category}: {e}")
                        break

            # Calculate overall score
            scores = [data.get('score', 0) for data in analysis['scoring'].values()]
            if scores and any(s > 0 for s in scores):
                analysis['overall_score'] = round(sum(scores) / len(scores), 1)
                logger.info(f"📊 Calculated overall score: {analysis['overall_score']}/10")

            # Extract red flags
            red_flags_match = re.search(r'3\.\s*RED FLAGS.*?:(.*?)(?=4\.|$)', analysis_text, re.DOTALL | re.IGNORECASE)
            if red_flags_match:
                for line in red_flags_match.group(1).split('\n'):
                    line = line.strip()
                    if line.startswith(('-', '•', '*')) and len(line) > 5:
                        analysis['red_flags'].append(line[1:].strip())

            # Extract missing information
            missing_match = re.search(r'4\.\s*CRITICAL MISSING.*?:(.*?)(?=5\.|$)', analysis_text, re.DOTALL | re.IGNORECASE)
            if missing_match:
                for line in missing_match.group(1).split('\n'):
                    line = line.strip()
                    if line.startswith(('-', '•', '*')) and len(line) > 5:
                        analysis['missing_info'].append(line[1:].strip())

            # Extract key questions
            questions_match = re.search(r'5\.\s*KEY QUESTIONS.*?:(.*?)(?=6\.|$)', analysis_text, re.DOTALL | re.IGNORECASE)
            if questions_match:
                for line in questions_match.group(1).split('\n'):
                    line = line.strip()
                    if line.startswith(('-', '•', '*')) and len(line) > 5:
                        analysis['key_questions'].append(line[1:].strip())

            # Extract recommendation
            rec_match = re.search(r'6\.\s*PRELIMINARY RECOMMENDATION.*?:\s*-?\s*(PASS|INVESTIGATE[^/]*|NO GO)', analysis_text, re.IGNORECASE)
            if rec_match:
                analysis['recommendation'] = rec_match.group(1).strip().upper()

            # Log parsing results
            logger.info(f"📋 Parsing results:")
            logger.info(f"   Executive summary: {len(analysis['executive_summary'])} points")
            logger.info(f"   Scoring: {sum(1 for v in analysis['scoring'].values() if v['score'] > 0)}/6 categories")
            logger.info(f"   Red flags: {len(analysis['red_flags'])}")
            logger.info(f"   Missing info: {len(analysis['missing_info'])}")
            logger.info(f"   Overall score: {analysis['overall_score']}/10")

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

    def generate_investment_memo(self) -> str:
        """Generate a structured investment memo"""
        try:
            if not self.current_analysis or not self.analysis_context:
                return "❌ No data room has been analyzed yet. Please run /analyze first."

            logger.info("📄 Generating investment memo...")

            # Create memo prompt
            memo_prompt = MEMO_PROMPT.format(
                analysis_summary=json.dumps(self.current_analysis, indent=2),
                document_context=self.analysis_context['documents_summary']
            )

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a senior partner at a VC firm writing a comprehensive investment memo."},
                    {"role": "user", "content": memo_prompt}
                ],
                max_tokens=1500,
                temperature=0.3
            )

            memo = response.choices[0].message.content
            logger.info("✅ Investment memo generated successfully")
            return memo

        except Exception as e:
            logger.error(f"❌ Failed to generate memo: {e}")
            return f"❌ Sorry, I couldn't generate the memo due to a technical error: {str(e)}"

    def analyze_gaps(self) -> str:
        """Analyze information gaps for due diligence"""
        try:
            if not self.current_analysis or not self.analysis_context:
                return "❌ No data room has been analyzed yet. Please run /analyze first."

            logger.info("🔍 Analyzing information gaps...")

            # Extract financial data deterministically
            from utils.financial_extractor import extract_financial_data, format_financial_data_for_prompt
            financial_data = extract_financial_data(self.analysis_context['full_content'])
            formatted_financials = format_financial_data_for_prompt(financial_data)

            # Create gaps prompt
            gaps_prompt = GAPS_PROMPT.format(
                available_documents=self.analysis_context['documents_summary'],
                content_summary=json.dumps(self.current_analysis.get('missing_info', []), indent=2),
                extracted_financials=formatted_financials
            )

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a VC expert identifying critical missing information for due diligence."},
                    {"role": "user", "content": gaps_prompt}
                ],
                max_tokens=1000,
                temperature=0.2
            )

            gaps_analysis = response.choices[0].message.content
            logger.info("✅ Gaps analysis completed successfully")
            return gaps_analysis

        except Exception as e:
            logger.error(f"❌ Failed to analyze gaps: {e}")
            return f"❌ Sorry, I couldn't analyze gaps due to a technical error: {str(e)}"

    def get_detailed_scoring(self) -> Dict[str, Any]:
        """Get detailed scoring breakdown"""
        if not self.current_analysis:
            return {"error": "No analysis available. Please run /analyze first."}

        logger.info("📊 Generating detailed scoring breakdown...")

        # Base scoring from existing analysis
        base_scoring = {
            'overall_score': self.current_analysis.get('overall_score', 0),
            'category_scores': self.current_analysis.get('scoring', {}),
            'recommendation': self.current_analysis.get('recommendation', 'UNKNOWN'),
            'summary': self.current_analysis.get('executive_summary', [])
        }


        return base_scoring

    def reset_analysis(self):
        """Reset current analysis context"""
        self.current_analysis = None
        self.analysis_context = None
        logger.info("🔄 Analysis context reset")
