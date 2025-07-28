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

            # Create analysis prompt
            analysis_prompt = DATAROOM_ANALYSIS_PROMPT.format(
                documents_with_metadata=context['documents_summary'],
                document_contents=context['full_content'][:15000]  # Limit to avoid token limits
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

            analysis_result = response.choices[0].message.content

            # Parse and structure the analysis
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
                full_content += doc['content'][:5000]  # Limit per document

        return {
            'documents_summary': json.dumps(docs_summary, indent=2),
            'full_content': full_content,
            'document_count': len(docs_summary),
            'total_content_length': len(full_content)
        }

    def _parse_analysis_response(self, analysis_text: str) -> Dict[str, Any]:
        """Parse GPT-4 analysis response into structured format"""
        try:
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

            # Simple parsing logic (in real implementation, you'd want more robust parsing)
            lines = analysis_text.split('\n')
            current_section = None

            for line in lines:
                line = line.strip()
                if not line:
                    continue

                # Detect sections
                if 'EXECUTIVE SUMMARY' in line.upper():
                    current_section = 'executive_summary'
                elif 'SCORING' in line.upper() or 'DETAILED SCORE' in line.upper():
                    current_section = 'scoring'
                elif 'RED FLAGS' in line.upper():
                    current_section = 'red_flags'
                elif 'MISSING INFORMATION' in line.upper() or 'INFORMATION GAPS' in line.upper():
                    current_section = 'missing_info'
                elif 'KEY QUESTIONS' in line.upper() or 'QUESTIONS FOR DUE DILIGENCE' in line.upper():
                    current_section = 'key_questions'
                elif 'RECOMMENDATION' in line.upper():
                    current_section = 'recommendation'

                # Parse content based on current section
                elif current_section == 'executive_summary' and (line.startswith('-') or line.startswith('•')):
                    analysis['executive_summary'].append(line[1:].strip())
                elif current_section == 'red_flags' and (line.startswith('-') or line.startswith('•')):
                    analysis['red_flags'].append(line[1:].strip())
                elif current_section == 'missing_info' and (line.startswith('-') or line.startswith('•')):
                    analysis['missing_info'].append(line[1:].strip())
                elif current_section == 'key_questions' and (line.startswith('-') or line.startswith('•')):
                    analysis['key_questions'].append(line[1:].strip())

            # Calculate overall score (average of individual scores)
            scores = [score_data.get('score', 0) for score_data in analysis['scoring'].values()]
            if scores:
                analysis['overall_score'] = round(sum(scores) / len(scores), 1)

            return analysis

        except Exception as e:
            logger.error(f"❌ Failed to parse analysis response: {e}")
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

            # Create Q&A prompt
            qa_prompt = QA_PROMPT.format(
                analyzed_documents_summary=json.dumps(self.analysis_context['documents_summary'], indent=2),
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

            memo_prompt = MEMO_PROMPT.format(
                analysis_summary=json.dumps(self.current_analysis, indent=2),
                document_context=self.analysis_context['documents_summary']
            )

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a senior partner at a VC firm writing an investment memo for the partnership."},
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
        """Analyze information gaps in the data room"""
        try:
            if not self.current_analysis or not self.analysis_context:
                return "❌ No data room has been analyzed yet. Please run /analyze first."

            logger.info("🔍 Analyzing information gaps...")

            gaps_prompt = GAPS_PROMPT.format(
                available_documents=self.analysis_context['documents_summary'],
                content_summary=json.dumps(self.current_analysis.get('missing_info', []), indent=2)
            )

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a VC expert identifying critical missing information for due diligence."},
                    {"role": "user", "content": gaps_prompt}
                ],
                max_tokens=800,
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

        return {
            'overall_score': self.current_analysis.get('overall_score', 0),
            'category_scores': self.current_analysis.get('scoring', {}),
            'recommendation': self.current_analysis.get('recommendation', 'UNKNOWN'),
            'summary': self.current_analysis.get('executive_summary', [])
        }

    def reset_analysis(self):
        """Reset current analysis context"""
        self.current_analysis = None
        self.analysis_context = None
        logger.info("🔄 Analysis context reset")
