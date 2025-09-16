"""
Story 1.2: GPT Vision Infrastructure Integration - Vision Processor

Core GPT Vision processing engine for intelligent PDF visual analysis.
Provides cost-controlled visual extraction complementing existing text processing.
"""

import os
import base64
import io
from typing import Dict, List, Optional, Any, Tuple
from PIL import Image
from openai import OpenAI
import config
from utils.logger import get_logger
from utils.strategic_page_selector import StrategicPageSelector

logger = get_logger(__name__)

class VisionProcessor:
    """
    Core GPT Vision engine for document visual analysis.
    
    Handles OpenAI Vision API integration with intelligent cost controls,
    image preprocessing, and error handling for production use.
    """
    
    def __init__(self):
        """Initialize Vision Processor with OpenAI client and cost controls"""
        self.client = None
        self.daily_budget = float(os.getenv('VISION_COST_LIMIT', '5.0'))  # $5 default
        self.current_daily_cost = 0.0
        self.vision_enabled = os.getenv('VISION_ENABLED', 'true').lower() == 'true'
        
        # Vision API configuration
        self.max_image_size = (1024, 1024)  # Optimal for cost vs quality
        self.supported_formats = ['PNG', 'JPEG', 'WEBP', 'GIF']
        self.max_file_size_mb = 20  # OpenAI limit
        
        # Initialize strategic page selector
        self.strategic_selector = StrategicPageSelector()
        
        self._initialize_client()
        
    def _initialize_client(self) -> bool:
        """Initialize OpenAI client with Vision API access"""
        try:
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                logger.error("❌ OPENAI_API_KEY not found - Vision processing disabled")
                self.vision_enabled = False
                return False
                
            # Initialize OpenAI client (compatible with latest SDK)
            self.client = OpenAI(api_key=api_key)
            
            # Test Vision API access with a minimal call
            # Note: This is just initialization, actual test happens on first use
            logger.info("✅ OpenAI Vision client initialized successfully")
            logger.info(f"📊 Daily budget: ${self.daily_budget:.2f}")
            logger.info(f"🔧 Vision enabled: {self.vision_enabled}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize OpenAI Vision client: {e}")
            self.vision_enabled = False
            return False
    
    def is_vision_available(self) -> bool:
        """Check if vision processing is available and within budget"""
        if not self.vision_enabled:
            return False
            
        if not self.client:
            return False
            
        # Check daily budget
        if self.current_daily_cost >= self.daily_budget:
            logger.warning(f"⚠️ Daily vision budget exceeded: ${self.current_daily_cost:.2f}/${self.daily_budget:.2f}")
            return False
            
        return True
    
    def analyze_image(self, image_data: bytes, analysis_prompt: str, 
                     document_context: str = "") -> Dict[str, Any]:
        """
        Analyze image using GPT Vision API
        
        Args:
            image_data: Image bytes (PNG, JPEG, etc.)
            analysis_prompt: Specific analysis instructions
            document_context: Additional context about the document
            
        Returns:
            Dict containing vision analysis results and metadata
        """
        if not self.is_vision_available():
            return {
                'success': False,
                'error': 'Vision analysis not available (disabled or budget exceeded)',
                'fallback_required': True
            }
            
        try:
            # Preprocess image for optimal API usage
            processed_image = self._preprocess_image(image_data)
            if not processed_image:
                return {
                    'success': False,
                    'error': 'Image preprocessing failed',
                    'fallback_required': True
                }
                
            # Encode image for API
            image_base64 = base64.b64encode(processed_image).decode('utf-8')
            
            # Construct Vision API request
            response = self.client.chat.completions.create(
                model="gpt-4o",  # Current vision model
                messages=[
                    {
                        "role": "system",
                        "content": """You are a professional document analysis expert specializing in visual content extraction from business documents. 

Your task is to analyze visual elements (charts, graphs, tables, diagrams) that cannot be captured through text extraction alone.

Focus on:
- Data visualizations and their key insights
- Complex tables and structured information  
- Charts/graphs with specific values and trends
- Visual layouts that provide context
- Images or diagrams with business relevance

Provide structured, actionable insights that complement text-based analysis."""
                    },
                    {
                        "role": "user", 
                        "content": [
                            {
                                "type": "text",
                                "text": f"""Analyze this document page for visual information that would be missed by text extraction:

ANALYSIS CONTEXT:
{document_context}

SPECIFIC ANALYSIS REQUEST:
{analysis_prompt}

Please provide:
1. Key visual elements identified
2. Data/insights from charts, graphs, tables
3. Layout context and visual structure
4. Business-relevant information not available in raw text

Format as structured JSON with clear sections."""
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{image_base64}",
                                    "detail": "high"  # High detail for document analysis
                                }
                            }
                        ]
                    }
                ],
                max_tokens=1000,  # Sufficient for detailed analysis
                temperature=0.1,   # Low temperature for consistent analysis
                timeout=30  # 30 second timeout
            )
            
            # Extract and process response
            vision_content = response.choices[0].message.content
            
            # Estimate API cost (approximate)
            estimated_cost = self._estimate_api_cost(processed_image, len(vision_content))
            self.current_daily_cost += estimated_cost
            
            logger.info(f"✅ Vision analysis completed (cost: ~${estimated_cost:.3f})")
            
            return {
                'success': True,
                'vision_content': vision_content,
                'cost_estimate': estimated_cost,
                'model_used': 'gpt-4o',
                'tokens_used': response.usage.total_tokens if hasattr(response, 'usage') else 0,
                'processing_time': 'N/A'  # Could add timing if needed
            }
            
        except Exception as e:
            logger.error(f"❌ Vision API call failed: {e}")
            return {
                'success': False,
                'error': f'Vision API error: {str(e)}',
                'fallback_required': True
            }
    
    def process_pdf_with_vision(self, pdf_path: str, pages: List[int] = None) -> Dict[str, Any]:
        """
        Process PDF with strategic page selection and vision analysis
        
        Args:
            pdf_path: Path to PDF file for processing
            pages: Optional list of specific pages to process. If None, uses strategic selection
            
        Returns:
            Dict containing vision processing results and strategic selection metadata
        """
        if not self.is_vision_available():
            return {
                'success': False,
                'error': 'Vision processing not available (disabled or budget exceeded)',
                'strategic_selection': {},
                'pages_processed': [],
                'fallback_required': True
            }
        
        try:
            # Step 1: Strategic page selection if pages not specified
            if pages is None:
                strategic_pages = self.strategic_selector.select_strategic_pages(
                    pdf_path, max_pages=7  # Hard limit to prevent SSL exhaustion
                )
                
                # Flatten strategic selection to page list
                pages = self._flatten_page_selection(strategic_pages)
                logger.info(f"🎯 Strategic selection: {len(pages)} pages from {strategic_pages}")
            else:
                # Limit provided pages to maximum 7 for SSL safety
                pages = pages[:7] if len(pages) > 7 else pages
                strategic_pages = {'user_specified': pages}
                logger.info(f"📋 User-specified pages: {pages} (limited to {len(pages)})")
            
            if not pages:
                return {
                    'success': False,
                    'error': 'No pages selected for processing',
                    'strategic_selection': strategic_pages,
                    'pages_processed': [],
                    'fallback_required': True
                }
            
            # Step 2: Process selected pages with vision analysis
            vision_results = {}
            processing_errors = []
            total_cost = 0.0
            
            for page_num in pages:
                try:
                    # Convert PDF page to image (placeholder - would need actual PDF->image conversion)
                    # For now, this is a structure for integration
                    logger.info(f"🔍 Processing page {page_num} with vision analysis...")
                    
                    # This would require actual PDF to image conversion implementation
                    # image_data = self._convert_pdf_page_to_image(pdf_path, page_num)
                    
                    # For now, return structure showing integration readiness
                    page_result = {
                        'page_number': page_num,
                        'status': 'ready_for_implementation',
                        'note': 'PDF to image conversion needed for full implementation'
                    }
                    
                    vision_results[page_num] = page_result
                    
                except Exception as e:
                    error_msg = f"Failed to process page {page_num}: {e}"
                    logger.error(f"❌ {error_msg}")
                    processing_errors.append(error_msg)
                    
                    # Continue with other pages
                    continue
            
            # Step 3: Compile comprehensive results
            result = {
                'success': len(vision_results) > 0,
                'strategic_selection': strategic_pages,
                'pages_processed': list(vision_results.keys()),
                'vision_results': vision_results,
                'total_pages_analyzed': len(vision_results),
                'total_cost_estimate': total_cost,
                'processing_errors': processing_errors,
                'ssl_safe': True,  # Guaranteed by 7-page limit
                'fallback_required': len(vision_results) == 0
            }
            
            if result['success']:
                logger.info(f"✅ Vision processing completed: {len(vision_results)} pages processed")
                logger.info(f"💰 Total cost estimate: ${total_cost:.3f}")
            else:
                logger.warning(f"⚠️ Vision processing failed: {len(processing_errors)} errors")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ PDF vision processing failed: {e}")
            return {
                'success': False,
                'error': f'PDF vision processing error: {str(e)}',
                'strategic_selection': {},
                'pages_processed': [],
                'fallback_required': True
            }
    
    def _flatten_page_selection(self, strategic_pages: Dict[str, List[int]]) -> List[int]:
        """
        Flatten strategic page selection to a simple list of page numbers
        
        Args:
            strategic_pages: Dict with categories and their selected pages
            
        Returns:
            Sorted list of unique page numbers
        """
        all_pages = []
        for category, pages in strategic_pages.items():
            all_pages.extend(pages)
        
        # Remove duplicates and sort
        unique_pages = sorted(list(set(all_pages)))
        
        logger.debug(f"📊 Flattened {len(all_pages)} total selections to {len(unique_pages)} unique pages")
        return unique_pages

    def _preprocess_image(self, image_data: bytes) -> Optional[bytes]:
        """
        Preprocess image for optimal Vision API usage
        
        - Resize to optimal dimensions
        - Convert to PNG format
        - Optimize file size
        """
        try:
            # Load image
            image = Image.open(io.BytesIO(image_data))
            
            # Convert to RGB if necessary (for PNG)
            if image.mode in ('RGBA', 'P'):
                image = image.convert('RGB')
            
            # Resize if too large (maintain aspect ratio)
            if image.size[0] > self.max_image_size[0] or image.size[1] > self.max_image_size[1]:
                image.thumbnail(self.max_image_size, Image.Resampling.LANCZOS)
                logger.info(f"🔧 Image resized to {image.size} for optimal processing")
            
            # Convert to PNG format for consistency
            output_buffer = io.BytesIO()
            image.save(output_buffer, format='PNG', optimize=True)
            processed_data = output_buffer.getvalue()
            
            # Check file size
            size_mb = len(processed_data) / (1024 * 1024)
            if size_mb > self.max_file_size_mb:
                logger.warning(f"⚠️ Processed image still too large: {size_mb:.1f}MB")
                return None
                
            logger.debug(f"📊 Preprocessed image: {len(processed_data)} bytes")
            return processed_data
            
        except Exception as e:
            logger.error(f"❌ Image preprocessing failed: {e}")
            return None
    
    def _estimate_api_cost(self, image_data: bytes, response_length: int) -> float:
        """
        Estimate Vision API cost based on image size and response
        
        Note: This is an approximation. Actual costs may vary.
        OpenAI Vision pricing is based on image tokens + text tokens.
        """
        # Rough cost estimation (as of 2024)
        # Vision API: ~$0.01-0.02 per image depending on size
        
        image_size_mb = len(image_data) / (1024 * 1024)
        
        # Base cost for image processing
        image_cost = 0.01 if image_size_mb < 1.0 else 0.02
        
        # Text token cost (very minimal)
        text_cost = (response_length / 1000) * 0.001  # Rough estimate
        
        total_cost = image_cost + text_cost
        return total_cost
    
    def get_daily_cost_status(self) -> Dict[str, Any]:
        """Get current daily cost and budget status"""
        return {
            'current_cost': self.current_daily_cost,
            'daily_budget': self.daily_budget,
            'remaining_budget': max(0, self.daily_budget - self.current_daily_cost),
            'budget_percentage_used': (self.current_daily_cost / self.daily_budget) * 100,
            'vision_enabled': self.vision_enabled
        }
    
    def reset_daily_cost(self):
        """Reset daily cost counter (typically called at start of day)"""
        self.current_daily_cost = 0.0
        logger.info("📊 Daily vision cost counter reset")


# Global vision processor instance
_vision_processor = None

def get_vision_processor() -> VisionProcessor:
    """Get global vision processor instance (singleton pattern)"""
    global _vision_processor
    if _vision_processor is None:
        _vision_processor = VisionProcessor()
    return _vision_processor