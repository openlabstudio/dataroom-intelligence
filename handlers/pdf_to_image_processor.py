"""
Story 1.2 AC3: PDF to Image Processing Pipeline

Converts PDF pages to high-quality images optimized for GPT Vision analysis.
Handles image preprocessing, format optimization, and quality control
for maximum extraction accuracy while minimizing API costs.
"""

import io
import os
import fitz  # PyMuPDF
from PIL import Image, ImageEnhance, ImageOps
import base64
from typing import Dict, List, Tuple, Optional, Any
from utils.logger import get_logger

logger = get_logger(__name__)

class PDFToImageProcessor:
    """
    Converts PDF pages to optimized images for GPT Vision processing.
    Handles quality optimization, format conversion, and size management.
    """
    
    def __init__(self):
        # Vision API optimization settings
        self.target_dpi = int(os.getenv('VISION_IMAGE_DPI', '150'))  # Balance quality/cost
        self.max_image_size = int(os.getenv('VISION_MAX_IMAGE_SIZE', '2048'))  # 2048px max dimension
        self.image_quality = int(os.getenv('VISION_IMAGE_QUALITY', '85'))  # JPEG quality
        self.enable_enhancement = os.getenv('VISION_ENHANCE_IMAGES', 'true').lower() == 'true'
        
        # Supported output formats
        self.output_format = os.getenv('VISION_OUTPUT_FORMAT', 'PNG')  # PNG or JPEG
        
        logger.info(f"🖼️ PDF to Image Processor initialized:")
        logger.info(f"   Target DPI: {self.target_dpi}")
        logger.info(f"   Max Dimension: {self.max_image_size}px")
        logger.info(f"   Output Format: {self.output_format}")
        logger.info(f"   Enhancement: {'Enabled' if self.enable_enhancement else 'Disabled'}")
    
    def process_pdf_pages(self, pdf_path: str, page_numbers: List[int]) -> Dict[int, Dict[str, Any]]:
        """
        Convert specified PDF pages to optimized images for Vision analysis.
        
        Args:
            pdf_path: Path to PDF file
            page_numbers: List of page numbers to process (1-indexed)
            
        Returns:
            Dict mapping page numbers to image data and metadata
        """
        
        try:
            doc = fitz.open(pdf_path)
            processed_pages = {}
            
            logger.info(f"🔄 Processing {len(page_numbers)} pages from PDF: {os.path.basename(pdf_path)}")
            
            for page_num in page_numbers:
                try:
                    # Convert to 0-indexed for PyMuPDF
                    page_index = page_num - 1
                    
                    if page_index < 0 or page_index >= len(doc):
                        logger.warning(f"⚠️ Page {page_num} out of range, skipping")
                        continue
                    
                    page = doc[page_index]
                    image_data = self._convert_page_to_image(page, page_num)
                    
                    if image_data:
                        processed_pages[page_num] = image_data
                        logger.debug(f"✅ Page {page_num}: {image_data['size_kb']:.1f}KB, "
                                   f"{image_data['dimensions'][0]}x{image_data['dimensions'][1]}px")
                    
                except Exception as e:
                    logger.error(f"❌ Failed to process page {page_num}: {e}")
                    continue
            
            doc.close()
            
            # Calculate processing statistics
            total_size_kb = sum(page['size_kb'] for page in processed_pages.values())
            avg_size_kb = total_size_kb / len(processed_pages) if processed_pages else 0
            
            logger.info(f"📊 PDF Processing Complete:")
            logger.info(f"   Processed Pages: {len(processed_pages)}/{len(page_numbers)}")
            logger.info(f"   Total Size: {total_size_kb:.1f}KB")
            logger.info(f"   Average Size: {avg_size_kb:.1f}KB per page")
            
            return processed_pages
            
        except Exception as e:
            logger.error(f"❌ PDF processing failed: {e}")
            return {}
    
    def _convert_page_to_image(self, page: fitz.Page, page_num: int) -> Optional[Dict[str, Any]]:
        """Convert single PDF page to optimized image"""
        
        try:
            # Calculate optimal resolution matrix
            zoom_factor = self.target_dpi / 72  # PDF default is 72 DPI
            matrix = fitz.Matrix(zoom_factor, zoom_factor)
            
            # Render page to pixmap
            pix = page.get_pixmap(matrix=matrix, alpha=False)  # No alpha for smaller files
            
            # Convert to PIL Image
            img_data = pix.tobytes("png")
            pil_image = Image.open(io.BytesIO(img_data))
            
            # Apply enhancements if enabled
            if self.enable_enhancement:
                pil_image = self._enhance_image_for_vision(pil_image)
            
            # Resize if needed (maintain aspect ratio)
            pil_image = self._resize_to_max_dimension(pil_image, self.max_image_size)
            
            # Convert to target format
            optimized_image = self._optimize_for_vision_api(pil_image)
            
            # Generate base64 encoding for API
            buffered = io.BytesIO()
            format_name = self.output_format.upper()
            
            if format_name == 'JPEG':
                optimized_image.save(buffered, format=format_name, quality=self.image_quality, optimize=True)
            else:
                optimized_image.save(buffered, format=format_name, optimize=True)
            
            image_bytes = buffered.getvalue()
            base64_image = base64.b64encode(image_bytes).decode('utf-8')
            
            # Calculate size and metadata
            size_kb = len(image_bytes) / 1024
            width, height = optimized_image.size
            
            return {
                'page_number': page_num,
                'image_data': base64_image,
                'format': self.output_format.lower(),
                'dimensions': (width, height),
                'size_kb': size_kb,
                'dpi': self.target_dpi,
                'processing_timestamp': page_num,  # Simple tracking
                'mime_type': f'image/{self.output_format.lower()}' if self.output_format.lower() != 'jpg' else 'image/jpeg'
            }
            
        except Exception as e:
            logger.error(f"❌ Page {page_num} image conversion failed: {e}")
            return None
    
    def _enhance_image_for_vision(self, image: Image.Image) -> Image.Image:
        """Apply image enhancements to improve Vision API accuracy"""
        
        try:
            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Apply contrast enhancement for better text/chart readability
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(1.2)  # Slightly increase contrast
            
            # Apply sharpness enhancement for clearer details
            sharpener = ImageEnhance.Sharpness(image)
            image = sharpener.enhance(1.1)  # Subtle sharpening
            
            # Auto-level for better visibility
            image = ImageOps.autocontrast(image, cutoff=1)
            
            return image
            
        except Exception as e:
            logger.warning(f"⚠️ Image enhancement failed: {e}")
            return image  # Return original if enhancement fails
    
    def _resize_to_max_dimension(self, image: Image.Image, max_dimension: int) -> Image.Image:
        """Resize image while maintaining aspect ratio"""
        
        width, height = image.size
        max_current = max(width, height)
        
        if max_current <= max_dimension:
            return image  # No resize needed
        
        # Calculate new dimensions
        scale_factor = max_dimension / max_current
        new_width = int(width * scale_factor)
        new_height = int(height * scale_factor)
        
        # High-quality resize
        resized_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        logger.debug(f"📏 Resized: {width}x{height} → {new_width}x{new_height}")
        return resized_image
    
    def _optimize_for_vision_api(self, image: Image.Image) -> Image.Image:
        """Apply Vision API specific optimizations"""
        
        # Ensure RGB mode for consistency
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # For financial documents, ensure high contrast for better chart reading
        # Check if image seems to contain charts/graphs (high color diversity)
        colors = image.getcolors(maxcolors=256)
        if colors and len(colors) > 50:  # Likely contains charts/graphics
            # Apply slight contrast boost for better chart visibility
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(1.15)
        
        return image
    
    def create_vision_api_payload(self, page_data: Dict[str, Any], analysis_prompt: str) -> Dict[str, Any]:
        """
        Create properly formatted payload for OpenAI Vision API
        
        Args:
            page_data: Image data from process_pdf_pages()
            analysis_prompt: Prompt for Vision analysis
            
        Returns:
            Formatted Vision API payload
        """
        
        return {
            "model": "gpt-4-vision-preview",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": analysis_prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{page_data['mime_type']};base64,{page_data['image_data']}",
                                "detail": "high"  # High detail for financial documents
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 1500  # Reasonable limit for detailed analysis
        }
    
    def estimate_processing_cost(self, page_count: int, avg_size_kb: float = 150) -> Dict[str, float]:
        """
        Estimate Vision API costs for processing pages
        
        Args:
            page_count: Number of pages to process
            avg_size_kb: Average image size in KB
            
        Returns:
            Cost estimates
        """
        
        # OpenAI Vision API pricing (as of latest update)
        # High detail images: $0.00765 per image
        cost_per_high_detail_image = 0.00765
        
        total_cost = page_count * cost_per_high_detail_image
        
        return {
            'pages': page_count,
            'cost_per_page': cost_per_high_detail_image,
            'total_cost_usd': total_cost,
            'avg_image_size_kb': avg_size_kb,
            'processing_mode': 'high_detail'
        }
    
    def batch_process_with_progress(self, pdf_path: str, page_numbers: List[int]) -> Dict[str, Any]:
        """
        Process pages in batches with progress tracking for large documents
        
        Returns:
            Complete processing results with progress information
        """
        
        batch_size = int(os.getenv('VISION_BATCH_SIZE', '5'))  # Process 5 pages at a time
        processed_pages = {}
        total_pages = len(page_numbers)
        
        logger.info(f"📦 Batch processing {total_pages} pages (batch size: {batch_size})")
        
        for i in range(0, total_pages, batch_size):
            batch_pages = page_numbers[i:i + batch_size]
            batch_num = (i // batch_size) + 1
            total_batches = (total_pages + batch_size - 1) // batch_size
            
            logger.info(f"🔄 Processing batch {batch_num}/{total_batches}: pages {batch_pages}")
            
            batch_results = self.process_pdf_pages(pdf_path, batch_pages)
            processed_pages.update(batch_results)
            
            progress = (len(processed_pages) / total_pages) * 100
            logger.info(f"📊 Progress: {progress:.1f}% ({len(processed_pages)}/{total_pages} pages)")
        
        return {
            'processed_pages': processed_pages,
            'total_processed': len(processed_pages),
            'total_requested': total_pages,
            'success_rate': (len(processed_pages) / total_pages) * 100 if total_pages > 0 else 0,
            'batch_info': {
                'batch_size': batch_size,
                'total_batches': total_batches
            }
        }


# Global instance for easy access
pdf_image_processor = PDFToImageProcessor()