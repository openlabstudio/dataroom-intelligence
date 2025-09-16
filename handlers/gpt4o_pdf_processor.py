"""
GPT-4o Direct PDF Processor for DataRoom Intelligence Bot
Replaces OCR pipeline with OpenAI's native PDF processing capabilities
Story: G4O-001 - GPT-4o PDF Processor Implementation
"""

import os
import time
from typing import Dict, Any, Optional
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
        logger.info(f"🔵 Starting GPT-4o Direct processing for: {file_name}")
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
            
            # Step 2: Process with GPT-4o
            logger.info("🧠 Processing with GPT-4o...")
            extraction_result = self._extract_structured_data(uploaded_file.id, file_name)
            
            # Step 3: Cleanup uploaded file
            try:
                self.client.files.delete(uploaded_file.id)
                logger.info("🧹 Temporary file cleaned up")
            except Exception as cleanup_error:
                logger.warning(f"⚠️ Cleanup warning: {cleanup_error}")
            
            # Step 4: Format results
            processing_time = time.time() - start_time
            logger.info(f"✅ GPT-4o processing completed in {processing_time:.2f}s")
            
            return {
                'name': file_name,
                'type': 'pdf',
                'content': extraction_result['raw_content'],
                'structured_data': extraction_result['structured_data'],
                'metadata': {
                    'extraction_method': 'gpt4o_direct',
                    'processing_time': processing_time,
                    'file_size_bytes': os.path.getsize(pdf_path),
                    'data_quality_score': extraction_result.get('quality_score', 0.95),
                    'slide_references': extraction_result.get('slide_references', []),
                    'has_content': True,
                    'content_length': len(extraction_result['raw_content'])
                }
            }
            
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"❌ GPT-4o processing failed for {file_name}: {e}")
            logger.info(f"⏱️ Failed after {processing_time:.2f}s")
            
            # Return error result for fallback handling
            return {
                'name': file_name,
                'type': 'pdf',
                'content': '',
                'structured_data': None,
                'metadata': {
                    'extraction_method': 'gpt4o_failed',
                    'processing_time': processing_time,
                    'error': str(e),
                    'has_content': False,
                    'fallback_required': True
                }
            }
    
    def _extract_structured_data(self, file_id: str, file_name: str) -> Dict[str, Any]:
        """Extract structured data using GPT-4o with optimized prompt"""
        
        # Optimized prompt for startup pitch deck analysis
        extraction_prompt = """
        Analyze this startup pitch deck and extract key business information with precise slide references.

        **EXTRACT THE FOLLOWING DATA:**

        **FINANCIAL METRICS:**
        - Funding rounds, amounts, and valuations (with slide numbers)
        - Revenue figures and projections
        - Market size (TAM/SAM/SOM)
        - Key financial KPIs
        - Burn rate, runway, or cash flow data

        **TRACTION DATA:**
        - User/customer numbers and growth
        - Transaction volumes and revenue metrics
        - Growth rates and retention data
        - Key partnerships and customers

        **TEAM INFORMATION:**
        - Founders and their backgrounds
        - Key team members and their experience
        - Advisory board if mentioned

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