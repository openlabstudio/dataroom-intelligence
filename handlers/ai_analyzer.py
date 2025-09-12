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

    def generate_investment_memo(self, enhanced_session_data: Optional[Dict[str, Any]] = None) -> str:
        """Generate a structured investment memo with enhanced visual insights"""
        try:
            if not self.current_analysis or not self.analysis_context:
                return "❌ No data room has been analyzed yet. Please run /analyze first."

            logger.info("📄 Generating enhanced investment memo with visual insights...")

            # NEW: Include visual insights from enhanced sessions (AC1 requirement)
            visual_insights = ""
            chart_references = []
            
            if enhanced_session_data and enhanced_session_data.get('extraction_metadata', {}).get('vision_extraction_complete'):
                logger.info("📊 Including visual analysis in investment memo")
                
                # Extract vision data for memo generation
                vision_analysis = enhanced_session_data.get('vision_analysis', {})
                command_data = enhanced_session_data.get('command_data', {}).get('memo', {})
                
                if vision_analysis and command_data:
                    # Chart and visual evidence references
                    chart_references = command_data.get('chart_references', [])
                    visual_evidence = command_data.get('visual_evidence', {})
                    financial_charts = command_data.get('financial_chart_analysis', {})
                    
                    visual_insights = f"\n\nVISUAL ANALYSIS INSIGHTS:\n"
                    
                    # Financial chart insights
                    if financial_charts:
                        visual_insights += "Financial Charts Analysis:\n"
                        for chart_type, data in financial_charts.items():
                            if isinstance(data, dict) and data.get('insights'):
                                visual_insights += f"- {chart_type}: {data['insights']}\n"
                    
                    # Visual evidence supporting key claims
                    if visual_evidence:
                        visual_insights += "\nVisual Evidence Supporting Analysis:\n"
                        for evidence_type, details in visual_evidence.items():
                            if isinstance(details, str) and details.strip():
                                visual_insights += f"- {evidence_type}: {details}\n"
                            elif isinstance(details, list) and details:
                                visual_insights += f"- {evidence_type}: {'; '.join(details[:3])}\n"
                    
                    # Chart references for supporting documentation
                    if chart_references:
                        visual_insights += f"\nVisual Supporting Materials:\n"
                        for ref in chart_references[:5]:  # Limit to top 5 references
                            visual_insights += f"- {ref}\n"
                    
                    # Processing summary for transparency
                    processing_summary = vision_analysis.get('processing_summary', {})
                    if processing_summary.get('total_pages_analyzed'):
                        visual_insights += f"\nVisual Analysis Coverage:\n"
                        visual_insights += f"- Pages with visual content analyzed: {processing_summary.get('successful_analyses', 0)}/{processing_summary.get('total_pages_analyzed', 0)}\n"
                    
                    logger.info(f"✅ Visual insights integrated: {len(chart_references)} chart references, {len(financial_charts)} financial charts")
                else:
                    visual_insights = "\n\nNote: Visual analysis data was processed but specific insights not available for memo integration."
            else:
                logger.info("📄 Vision data not available - generating text-only memo")

            # Enhanced memo prompt with visual insights
            enhanced_memo_prompt = MEMO_PROMPT.format(
                analysis_summary=json.dumps(self.current_analysis, indent=2),
                document_context=self.analysis_context['documents_summary']
            ) + visual_insights

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a senior partner at a VC firm writing a comprehensive investment memo that incorporates both textual analysis and visual insights from charts and diagrams."},
                    {"role": "user", "content": enhanced_memo_prompt}
                ],
                max_tokens=1700,  # Increased for enhanced content
                temperature=0.3
            )

            memo = response.choices[0].message.content
            logger.info("✅ Enhanced investment memo generated successfully")
            return memo

        except Exception as e:
            logger.error(f"❌ Failed to generate enhanced memo: {e}")
            return f"❌ Sorry, I couldn't generate the memo due to a technical error: {str(e)}"

    def analyze_gaps(self, enhanced_session_data: Optional[Dict[str, Any]] = None) -> str:
            """Analyze information gaps with enhanced visual and textual extraction results"""
            try:
                if not self.current_analysis or not self.analysis_context:
                    return "❌ No data room has been analyzed yet. Please run /analyze first."

                logger.info("🔍 Analyzing information gaps with enhanced extraction data...")

                # PHASE 1: Extract financial data deterministically
                from utils.financial_extractor import extract_financial_data, format_financial_data_for_prompt
                financial_data = extract_financial_data(self.analysis_context['full_content'])
                formatted_financials = format_financial_data_for_prompt(financial_data)

                # NEW: Integrate vision data from enhanced sessions (AC1 requirement)
                vision_context = ""
                visual_gaps_identified = []
                
                if enhanced_session_data and enhanced_session_data.get('extraction_metadata', {}).get('vision_extraction_complete'):
                    logger.info("📊 Incorporating vision analysis data for gap identification")
                    
                    # Extract vision data for gap analysis
                    vision_analysis = enhanced_session_data.get('vision_analysis', {})
                    command_data = enhanced_session_data.get('command_data', {}).get('gaps', {})
                    
                    if vision_analysis and command_data:
                        visual_gaps_identified = command_data.get('visual_gaps', [])
                        chart_analysis = command_data.get('chart_analysis', {})
                        
                        vision_context = f"\n\nVISION-BASED GAP ANALYSIS:\n"
                        vision_context += f"- Charts and Visual Elements Analyzed: {len(chart_analysis.get('identified_charts', []))}\n"
                        vision_context += f"- Visual Content Gaps Identified: {len(visual_gaps_identified)}\n"
                        
                        if visual_gaps_identified:
                            vision_context += "- Specific Visual Gaps Found:\n"
                            for gap in visual_gaps_identified[:5]:  # Limit to top 5 for prompt efficiency
                                vision_context += f"  • {gap}\n"
                        
                        # Include chart-text consistency analysis
                        consistency_issues = command_data.get('consistency_analysis', {}).get('issues', [])
                        if consistency_issues:
                            vision_context += f"- Chart-Text Inconsistencies Detected: {len(consistency_issues)}\n"
                            for issue in consistency_issues[:3]:
                                vision_context += f"  • {issue}\n"
                    
                    logger.info(f"✅ Vision data integrated: {len(visual_gaps_identified)} visual gaps identified")
                else:
                    logger.info("📄 Vision data not available - using text-only gap analysis")

                # Enhanced gaps prompt with vision context
                gaps_prompt = GAPS_PROMPT.format(
                    available_documents=self.analysis_context['documents_summary'],
                    content_summary=json.dumps(self.current_analysis.get('missing_info', []), indent=2),
                    extracted_financials=formatted_financials
                ) + vision_context

                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are a VC expert identifying critical missing information for due diligence using both textual and visual document analysis."},
                        {"role": "user", "content": gaps_prompt}
                    ],
                    max_tokens=1200,  # Increased for enhanced analysis
                    temperature=0.2
                )

                gaps_analysis = response.choices[0].message.content
                logger.info("✅ Enhanced gaps analysis completed successfully")
                return gaps_analysis

            except Exception as e:
                logger.error(f"❌ Failed to analyze gaps: {e}")
                return f"❌ Sorry, I couldn't analyze gaps due to a technical error: {str(e)}"

    def get_detailed_scoring(self, enhanced_session_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get detailed scoring breakdown with enhanced visual content quality assessment"""
        if not self.current_analysis:
            return {"error": "No analysis available. Please run /analyze first."}

        logger.info("📊 Generating enhanced scoring with visual content assessment...")

        # Base scoring from existing analysis
        base_scoring = {
            'overall_score': self.current_analysis.get('overall_score', 0),
            'category_scores': self.current_analysis.get('scoring', {}),
            'recommendation': self.current_analysis.get('recommendation', 'UNKNOWN'),
            'summary': self.current_analysis.get('executive_summary', [])
        }

        # NEW: Enhance scoring with visual content quality assessment (AC1 requirement)
        if enhanced_session_data and enhanced_session_data.get('extraction_metadata', {}).get('vision_extraction_complete'):
            logger.info("📊 Including visual content quality in scoring assessment")
            
            # Extract vision scoring data
            vision_analysis = enhanced_session_data.get('vision_analysis', {})
            command_data = enhanced_session_data.get('command_data', {}).get('scoring', {})
            
            if vision_analysis and command_data:
                # Visual content quality metrics
                visual_metrics = command_data.get('visual_scoring_metrics', {})
                presentation_quality = command_data.get('presentation_quality_score', 0)
                visual_completeness = command_data.get('visual_completeness_score', 0)
                
                # Enhanced scoring structure
                base_scoring.update({
                    'enhanced_scoring': {
                        'content_analysis': base_scoring['category_scores'],
                        'visual_presentation_quality': {
                            'score': presentation_quality,
                            'metrics': visual_metrics.get('presentation_metrics', {}),
                            'justification': f"Visual presentation quality based on chart quality, design consistency, and information clarity"
                        },
                        'visual_content_completeness': {
                            'score': visual_completeness,
                            'metrics': visual_metrics.get('completeness_metrics', {}),
                            'justification': f"Assessment of visual content completeness including required charts, financial projections, and supporting diagrams"
                        }
                    },
                    'visual_text_alignment': command_data.get('visual_text_alignment_score', 0),
                    'comprehensive_score_breakdown': {
                        'text_based_analysis': base_scoring['overall_score'],
                        'visual_presentation': presentation_quality,
                        'content_completeness': visual_completeness,
                        'alignment_consistency': command_data.get('visual_text_alignment_score', 0)
                    }
                })
                
                # Calculate enhanced overall score incorporating visual assessment
                if presentation_quality > 0 or visual_completeness > 0:
                    text_weight = 0.7
                    visual_weight = 0.3
                    
                    visual_component = (presentation_quality + visual_completeness) / 2
                    enhanced_overall = (base_scoring['overall_score'] * text_weight) + (visual_component * visual_weight)
                    
                    base_scoring['enhanced_overall_score'] = round(enhanced_overall, 1)
                    base_scoring['scoring_methodology'] = {
                        'text_analysis_weight': text_weight,
                        'visual_analysis_weight': visual_weight,
                        'includes_visual_assessment': True
                    }
                    
                    logger.info(f"✅ Enhanced scoring calculated: {enhanced_overall:.1f}/10 (Text: {base_scoring['overall_score']}, Visual: {visual_component:.1f})")
                else:
                    base_scoring['enhanced_overall_score'] = base_scoring['overall_score']
                    base_scoring['scoring_methodology'] = {
                        'text_analysis_weight': 1.0,
                        'visual_analysis_weight': 0.0,
                        'includes_visual_assessment': False,
                        'note': 'Visual scoring data processed but metrics not available'
                    }
            else:
                base_scoring['enhanced_overall_score'] = base_scoring['overall_score']
                base_scoring['scoring_methodology'] = {
                    'text_analysis_weight': 1.0,
                    'visual_analysis_weight': 0.0,
                    'includes_visual_assessment': False,
                    'note': 'Vision processing completed but scoring data not available'
                }
        else:
            logger.info("📄 Vision data not available - using text-only scoring")
            base_scoring['enhanced_overall_score'] = base_scoring['overall_score']
            base_scoring['scoring_methodology'] = {
                'text_analysis_weight': 1.0,
                'visual_analysis_weight': 0.0,
                'includes_visual_assessment': False,
                'note': 'Text-only analysis - vision processing not performed'
            }

        return base_scoring

    def reset_analysis(self):
        """Reset current analysis context"""
        self.current_analysis = None
        self.analysis_context = None
        logger.info("🔄 Analysis context reset")
