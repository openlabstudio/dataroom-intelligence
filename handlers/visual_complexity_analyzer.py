"""
Story 1.2 AC2: Visual Content Detection Algorithm

Intelligent page selection system that identifies PDF pages with high visual content
requiring GPT Vision processing. Optimizes costs by processing only 20-40% of pages
with highest visual complexity (charts, graphs, diagrams, complex layouts).
"""

import io
import os
import fitz  # PyMuPDF
from PIL import Image
import numpy as np
from typing import Dict, List, Tuple, Any
from utils.logger import get_logger

logger = get_logger(__name__)

class VisualComplexityAnalyzer:
    """
    Analyzes PDF pages to determine visual complexity and prioritize
    pages for GPT Vision processing based on cost-optimization strategy.
    """
    
    def __init__(self):
        self.complexity_threshold = float(os.getenv('VISION_COMPLEXITY_THRESHOLD', '0.6'))
        self.max_pages_percentage = float(os.getenv('VISION_MAX_PAGES_PCT', '0.35'))  # 35% max
        
    def analyze_document_visual_complexity(self, pdf_path: str) -> Dict[str, Any]:
        """
        Analyze entire PDF document to identify pages requiring Vision processing.
        
        Returns:
            Dict containing page rankings, complexity scores, and processing recommendations
        """
        try:
            doc = fitz.open(pdf_path)
            total_pages = len(doc)
            
            logger.info(f"📊 Analyzing visual complexity for {total_pages} pages")
            
            page_analyses = []
            
            # Analyze each page for visual complexity
            for page_num in range(total_pages):
                page = doc[page_num]
                complexity_analysis = self._analyze_page_complexity(page, page_num)
                page_analyses.append(complexity_analysis)
                
                logger.debug(f"Page {page_num + 1}: Visual Score {complexity_analysis['visual_score']:.2f}, "
                           f"Text Ratio: {complexity_analysis['text_ratio']:.2f}")
            
            doc.close()
            
            # Rank pages and determine processing strategy
            processing_strategy = self._determine_processing_strategy(page_analyses, total_pages)
            
            logger.info(f"📈 Visual Analysis Complete:")
            logger.info(f"   High Visual Pages: {len(processing_strategy['high_priority_pages'])}")
            logger.info(f"   Vision Processing: {len(processing_strategy['vision_pages'])} pages")
            logger.info(f"   Text-Only Pages: {len(processing_strategy['text_only_pages'])} pages")
            logger.info(f"   Cost Optimization: {processing_strategy['cost_reduction']:.1f}% savings")
            
            return {
                'total_pages': total_pages,
                'page_analyses': page_analyses,
                'processing_strategy': processing_strategy,
                'complexity_distribution': self._get_complexity_distribution(page_analyses)
            }
            
        except Exception as e:
            logger.error(f"❌ Visual complexity analysis failed: {e}")
            return self._get_fallback_analysis(pdf_path)
    
    def _analyze_page_complexity(self, page: fitz.Page, page_num: int) -> Dict[str, Any]:
        """Analyze individual page for visual complexity indicators"""
        
        complexity_indicators = {
            'page_number': page_num + 1,
            'visual_score': 0.0,
            'text_ratio': 0.0,
            'has_images': False,
            'has_drawings': False,
            'has_complex_layout': False,
            'color_complexity': 0.0,
            'requires_vision': False
        }
        
        try:
            # 1. Image Detection
            image_list = page.get_images()
            complexity_indicators['has_images'] = len(image_list) > 0
            image_score = min(len(image_list) * 0.3, 1.0)  # Cap at 1.0
            
            # 2. Drawing/Vector Graphics Detection
            drawings = page.get_drawings()
            complexity_indicators['has_drawings'] = len(drawings) > 3  # Threshold for significance
            drawing_score = min(len(drawings) * 0.1, 1.0)
            
            # 3. Text vs Visual Content Ratio
            text_dict = page.get_text("dict")
            total_chars = sum(len(span["text"]) for block in text_dict["blocks"] 
                            if "lines" in block for line in block["lines"] 
                            for span in line["spans"])
            
            # Estimate visual content by page area coverage
            page_area = page.rect.width * page.rect.height
            text_area = sum(span["bbox"][2] * span["bbox"][3] for block in text_dict["blocks"] 
                          if "lines" in block for line in block["lines"] 
                          for span in line["spans"])
            
            text_ratio = text_area / page_area if page_area > 0 else 0
            complexity_indicators['text_ratio'] = min(text_ratio, 1.0)
            
            # 4. Layout Complexity (multiple columns, complex positioning)
            blocks = text_dict["blocks"]
            layout_score = 0.0
            if len(blocks) > 5:  # Multiple content blocks suggest complex layout
                layout_score = 0.4
                complexity_indicators['has_complex_layout'] = True
            
            # 5. Color Complexity Analysis
            try:
                # Convert page to image for color analysis
                pix = page.get_pixmap(matrix=fitz.Matrix(1.0, 1.0))  # Lower resolution for analysis
                img_data = pix.tobytes("png")
                pil_image = Image.open(io.BytesIO(img_data))
                
                # Simple color diversity check
                colors = pil_image.getcolors(maxcolors=256)
                color_diversity = len(colors) if colors else 0
                color_score = min(color_diversity / 50, 1.0)  # Normalize to 0-1
                complexity_indicators['color_complexity'] = color_score
                
            except Exception:
                color_score = 0.0
            
            # Calculate overall visual complexity score
            visual_score = (
                image_score * 0.35 +      # Images are strong indicators
                drawing_score * 0.25 +    # Vector graphics important
                layout_score * 0.20 +     # Complex layouts need vision
                color_score * 0.15 +      # Color diversity indicates charts/graphics
                (1 - text_ratio) * 0.05   # Non-text content
            )
            
            complexity_indicators['visual_score'] = min(visual_score, 1.0)
            complexity_indicators['requires_vision'] = visual_score >= self.complexity_threshold
            
            # Special case: Financial documents with tables/charts
            text_content = page.get_text().lower()
            financial_keywords = ['revenue', 'profit', 'growth', 'market', 'financial', 
                                'investment', 'funding', 'valuation', 'metrics']
            has_financial_content = any(keyword in text_content for keyword in financial_keywords)
            
            if has_financial_content and (complexity_indicators['has_images'] or 
                                        complexity_indicators['has_drawings']):
                complexity_indicators['visual_score'] = min(visual_score + 0.2, 1.0)
                complexity_indicators['requires_vision'] = True
            
            return complexity_indicators
            
        except Exception as e:
            logger.warning(f"Page {page_num + 1} complexity analysis failed: {e}")
            # Safe fallback
            return {
                **complexity_indicators,
                'visual_score': 0.3,  # Medium complexity fallback
                'requires_vision': False
            }
    
    def _determine_processing_strategy(self, page_analyses: List[Dict], total_pages: int) -> Dict[str, Any]:
        """Determine optimal processing strategy based on complexity analysis"""
        
        # Sort pages by visual complexity score (descending)
        sorted_pages = sorted(page_analyses, key=lambda x: x['visual_score'], reverse=True)
        
        # Calculate max pages for Vision processing (cost optimization)
        max_vision_pages = max(1, int(total_pages * self.max_pages_percentage))
        
        # Identify high priority pages (definitely need Vision)
        high_priority_pages = [
            page for page in sorted_pages 
            if page['visual_score'] >= 0.8 or  # Very high visual complexity
               (page['has_images'] and page['visual_score'] >= 0.6)  # Images with moderate complexity
        ]
        
        # Select pages for Vision processing (within budget)
        vision_pages = []
        text_only_pages = []
        
        # Always include high priority pages
        for page in high_priority_pages[:max_vision_pages]:
            vision_pages.append(page)
        
        # Fill remaining slots with next highest complexity pages
        remaining_slots = max_vision_pages - len(vision_pages)
        for page in sorted_pages:
            if page not in vision_pages and remaining_slots > 0:
                if page['visual_score'] >= self.complexity_threshold:
                    vision_pages.append(page)
                    remaining_slots -= 1
        
        # Remaining pages go to text-only processing
        vision_page_numbers = [p['page_number'] for p in vision_pages]
        text_only_pages = [
            page for page in page_analyses 
            if page['page_number'] not in vision_page_numbers
        ]
        
        # Calculate cost reduction
        cost_reduction = ((total_pages - len(vision_pages)) / total_pages) * 100
        
        return {
            'high_priority_pages': high_priority_pages,
            'vision_pages': sorted(vision_pages, key=lambda x: x['page_number']),
            'text_only_pages': sorted(text_only_pages, key=lambda x: x['page_number']),
            'cost_reduction': cost_reduction,
            'processing_efficiency': len(vision_pages) / total_pages,
            'strategy_summary': {
                'total_pages': total_pages,
                'vision_processed': len(vision_pages),
                'text_only': len(text_only_pages),
                'cost_savings': f"{cost_reduction:.1f}%"
            }
        }
    
    def _get_complexity_distribution(self, page_analyses: List[Dict]) -> Dict[str, int]:
        """Get distribution of complexity levels across document"""
        
        distribution = {
            'high_complexity': 0,    # > 0.7
            'medium_complexity': 0,  # 0.4 - 0.7
            'low_complexity': 0      # < 0.4
        }
        
        for page in page_analyses:
            score = page['visual_score']
            if score > 0.7:
                distribution['high_complexity'] += 1
            elif score >= 0.4:
                distribution['medium_complexity'] += 1
            else:
                distribution['low_complexity'] += 1
        
        return distribution
    
    def _get_fallback_analysis(self, pdf_path: str) -> Dict[str, Any]:
        """Fallback analysis when main analysis fails"""
        
        try:
            doc = fitz.open(pdf_path)
            total_pages = len(doc)
            doc.close()
            
            # Conservative fallback: process first 3 pages and every 5th page
            vision_pages = []
            text_only_pages = []
            
            for i in range(total_pages):
                page_info = {
                    'page_number': i + 1,
                    'visual_score': 0.5,  # Medium complexity assumption
                    'requires_vision': i < 3 or (i + 1) % 5 == 0  # First 3 pages + every 5th
                }
                
                if page_info['requires_vision']:
                    vision_pages.append(page_info)
                else:
                    text_only_pages.append(page_info)
            
            logger.warning(f"⚠️ Using fallback visual analysis for {total_pages} pages")
            
            return {
                'total_pages': total_pages,
                'page_analyses': vision_pages + text_only_pages,
                'processing_strategy': {
                    'vision_pages': vision_pages,
                    'text_only_pages': text_only_pages,
                    'cost_reduction': ((total_pages - len(vision_pages)) / total_pages) * 100,
                    'strategy_summary': {
                        'total_pages': total_pages,
                        'vision_processed': len(vision_pages),
                        'text_only': len(text_only_pages),
                        'fallback_mode': True
                    }
                },
                'complexity_distribution': {
                    'high_complexity': len(vision_pages),
                    'medium_complexity': 0,
                    'low_complexity': len(text_only_pages)
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Fallback analysis also failed: {e}")
            return {
                'total_pages': 0,
                'page_analyses': [],
                'processing_strategy': {'vision_pages': [], 'text_only_pages': []},
                'complexity_distribution': {'high_complexity': 0, 'medium_complexity': 0, 'low_complexity': 0}
            }
    
    def should_use_vision_for_page(self, page_analysis: Dict[str, Any]) -> bool:
        """Quick check if a specific page should use Vision processing"""
        return page_analysis.get('requires_vision', False) or page_analysis.get('visual_score', 0) >= self.complexity_threshold
    
    def get_vision_priority_pages(self, processing_strategy: Dict[str, Any]) -> List[int]:
        """Get list of page numbers that should be processed with Vision (1-indexed)"""
        return [page['page_number'] for page in processing_strategy.get('vision_pages', [])]


# Global instance for easy access
visual_analyzer = VisualComplexityAnalyzer()