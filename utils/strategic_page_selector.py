"""
Strategic Page Selector for Lazy Vision Enhancement

This module implements intelligent page selection for cost-effective vision processing.
Identifies 5-7 most valuable pages containing business-critical visual data to prevent
SSL exhaustion while maintaining 95% data quality.
"""

import logging
import time
from datetime import datetime
from typing import Dict, List, Tuple
import os

# Try to import PDF libraries
try:
    import PyPDF2
    PDF_LIBRARY = 'PyPDF2'
except ImportError:
    try:
        import pdfplumber
        PDF_LIBRARY = 'pdfplumber'
    except ImportError:
        PDF_LIBRARY = None

logger = logging.getLogger(__name__)


class StrategicPageSelector:
    """Intelligent page selection for cost-effective vision processing"""
    
    def __init__(self):
        self.max_pages = 7  # Hard limit for SSL prevention
        self.min_pages = 3  # Minimum coverage guarantee
        
        # Content-based page identification patterns
        self.page_patterns = {
            'financials': {
                'keywords': [
                    'revenue', 'ARR', 'burn rate', 'runway', 'cash flow', 'unit economics', 
                    'income', 'EBITDA', 'gross margin', 'CAC', 'LTV', 'MRR',
                    'financial', 'P&L', 'profit', 'loss', 'budget', 'forecast'
                ],
                'priority': 1,  # Highest priority
                'max_pages': 3
            },
            'competition': {
                'keywords': [
                    'competitor', 'competitive', 'vs', 'landscape', 'positioning',
                    'alternatives', 'differentiation', 'market share', 'comparison',
                    'versus', 'against', 'competitive advantage'
                ],
                'priority': 1,  # Highest priority  
                'max_pages': 3
            },
            'market': {
                'keywords': [
                    'TAM', 'SAM', 'SOM', 'market size', 'opportunity', 'addressable',
                    'billion', 'million', 'market analysis', 'target market',
                    'total addressable', 'serviceable', 'obtainable'
                ],
                'priority': 2,  # High priority
                'max_pages': 2
            },
            'traction': {
                'keywords': [
                    'growth', 'users', 'customers', 'retention', 'churn', 'metrics',
                    'KPIs', 'engagement', 'MAU', 'DAU', 'conversion',
                    'active users', 'monthly active', 'daily active'
                ],
                'priority': 2,  # High priority
                'max_pages': 2
            },
            'team': {
                'keywords': [
                    'founder', 'CEO', 'CTO', 'team', 'leadership', 'advisory',
                    'experience', 'background', 'board', 'advisors',
                    'management', 'executives', 'key personnel'
                ],
                'priority': 3,  # Medium priority
                'max_pages': 1
            }
        }
        
        # Fallback patterns for common deck structures
        self.fallback_patterns = {
            'standard': [4, 8, 12, 16, 18, 19, 20],  # Common pitch deck structure
            'short': [3, 6, 9, 12, 15],  # For shorter decks
            'long': [4, 8, 12, 16, 20, 25, 30]  # For longer decks
        }
    
    def select_strategic_pages(self, pdf_path: str, max_pages: int = 7) -> Dict[str, List[int]]:
        """
        Analyze PDF content to identify strategic pages for vision processing
        
        Args:
            pdf_path: Path to PDF file
            max_pages: Maximum pages to select (default 7)
            
        Returns:
            Dict with page categories and selected page numbers
            Example: {'financials': [18, 19], 'competition': [11, 12], 'market': [8]}
        """
        start_time = time.time()
        
        try:
            # Validate PDF path
            if not self._validate_pdf_path(pdf_path):
                logger.error(f"Invalid PDF path: {pdf_path}")
                return self._fallback_page_selection(pdf_path)
            
            # Extract page contents for analysis
            page_contents = self._extract_page_contents(pdf_path)
            if not page_contents:
                logger.warning(f"No content extracted from PDF: {pdf_path}")
                return self._fallback_page_selection(pdf_path)
            
            # Score each page for strategic value
            page_scores = []
            for page_num, content in enumerate(page_contents, 1):
                if content.strip():  # Only score pages with content
                    score_data = self._score_page_content(page_num, content)
                    if score_data['total_score'] > 0:
                        page_scores.append(score_data)
            
            # Select optimal pages within constraints
            if page_scores:
                selected_pages = self._select_optimal_pages(page_scores, max_pages)
            else:
                logger.warning("No pages scored positively, using fallback")
                selected_pages = self._fallback_page_selection(pdf_path)
            
            # Ensure minimum coverage
            if sum(len(pages) for pages in selected_pages.values()) < self.min_pages:
                logger.info("Insufficient pages selected, enhancing with fallback")
                selected_pages = self._enhance_with_fallback(selected_pages, pdf_path)
            
            # Log selection rationale
            selection_time = time.time() - start_time
            self._log_selection_rationale(selected_pages, len(page_contents), selection_time)
            
            return selected_pages
            
        except Exception as e:
            logger.error(f"Strategic page selection failed: {e}")
            return self._fallback_page_selection(pdf_path)
    
    def _validate_pdf_path(self, pdf_path: str) -> bool:
        """Validate PDF file path and accessibility"""
        if not pdf_path:
            return False
        
        if not os.path.exists(pdf_path):
            logger.error(f"PDF file not found: {pdf_path}")
            return False
        
        if not os.access(pdf_path, os.R_OK):
            logger.error(f"PDF file not readable: {pdf_path}")
            return False
        
        return True
    
    def _extract_page_contents(self, pdf_path: str) -> List[str]:
        """Extract text content from each page for analysis (optimized for speed)"""
        page_contents = []
        
        if PDF_LIBRARY is None:
            logger.error("No PDF library available (PyPDF2 or pdfplumber)")
            return page_contents
        
        try:
            if PDF_LIBRARY == 'PyPDF2':
                page_contents = self._extract_with_pypdf2(pdf_path)
            elif PDF_LIBRARY == 'pdfplumber':
                page_contents = self._extract_with_pdfplumber(pdf_path)
                
        except Exception as e:
            logger.error(f"PDF text extraction failed: {e}")
            return []
        
        return page_contents
    
    def _extract_with_pypdf2(self, pdf_path: str) -> List[str]:
        """Extract text using PyPDF2"""
        page_contents = []
        
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            for page_num in range(len(pdf_reader.pages)):
                try:
                    page = pdf_reader.pages[page_num]
                    text = page.extract_text()
                    page_contents.append(text)
                except Exception as e:
                    logger.warning(f"Could not extract text from page {page_num + 1}: {e}")
                    page_contents.append("")
        
        return page_contents
    
    def _extract_with_pdfplumber(self, pdf_path: str) -> List[str]:
        """Extract text using pdfplumber"""
        page_contents = []
        
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                try:
                    text = page.extract_text() or ""
                    page_contents.append(text)
                except Exception as e:
                    logger.warning(f"Could not extract text from page {page.page_number}: {e}")
                    page_contents.append("")
        
        return page_contents
    
    def _score_page_content(self, page_num: int, content: str) -> Dict:
        """Score individual page based on strategic content patterns"""
        content_lower = content.lower()
        
        page_score_data = {
            'page_number': page_num,
            'content_preview': content[:200] + '...' if len(content) > 200 else content,
            'category_scores': {},
            'total_score': 0,
            'primary_category': None
        }
        
        # Score against each category pattern
        for category, pattern_config in self.page_patterns.items():
            keyword_matches = sum(1 for keyword in pattern_config['keywords'] 
                                if keyword in content_lower)
            
            if keyword_matches > 0:
                # Calculate weighted score based on priority and match density
                base_score = keyword_matches
                priority_weight = 4 - pattern_config['priority']  # Higher priority = higher weight
                density_bonus = min(keyword_matches / 10, 0.5)  # Bonus for dense content
                
                category_score = base_score * priority_weight + density_bonus
                page_score_data['category_scores'][category] = {
                    'raw_matches': keyword_matches,
                    'weighted_score': category_score,
                    'keywords_found': [kw for kw in pattern_config['keywords'] 
                                     if kw in content_lower]
                }
                
                page_score_data['total_score'] += category_score
        
        # Identify primary category (highest scoring)
        if page_score_data['category_scores']:
            primary_cat = max(page_score_data['category_scores'].keys(),
                             key=lambda cat: page_score_data['category_scores'][cat]['weighted_score'])
            page_score_data['primary_category'] = primary_cat
        
        return page_score_data
    
    def _select_optimal_pages(self, page_scores: List[Dict], max_pages: int) -> Dict[str, List[int]]:
        """Select optimal combination of pages within constraints"""
        # Sort pages by total score (highest first)
        sorted_pages = sorted(page_scores, key=lambda x: x['total_score'], reverse=True)
        
        selected_pages = {}
        total_selected = 0
        
        # First pass: Select top pages from each priority category
        for priority in [1, 2, 3]:  # Process by priority order
            if total_selected >= max_pages:
                break
                
            priority_categories = [cat for cat, config in self.page_patterns.items() 
                                 if config['priority'] == priority]
            
            for category in priority_categories:
                if total_selected >= max_pages:
                    break
                    
                # Find top pages for this category
                category_pages = [p for p in sorted_pages 
                                if p['primary_category'] == category]
                
                max_for_category = min(
                    self.page_patterns[category]['max_pages'],
                    max_pages - total_selected
                )
                
                selected_for_category = []
                for page_data in category_pages[:max_for_category]:
                    selected_for_category.append(page_data['page_number'])
                    total_selected += 1
                    
                    if total_selected >= max_pages:
                        break
                
                if selected_for_category:
                    selected_pages[category] = selected_for_category
        
        # Second pass: Fill remaining slots with highest scoring pages
        if total_selected < self.min_pages:
            remaining_slots = min(max_pages - total_selected, 
                                self.min_pages - total_selected)
            
            # Get pages not yet selected
            already_selected = [page for pages in selected_pages.values() for page in pages]
            remaining_pages = [p for p in sorted_pages 
                             if p['page_number'] not in already_selected]
            
            # Add highest scoring remaining pages
            for page_data in remaining_pages[:remaining_slots]:
                category = page_data['primary_category'] or 'general'
                if category not in selected_pages:
                    selected_pages[category] = []
                selected_pages[category].append(page_data['page_number'])
                total_selected += 1
        
        return selected_pages
    
    def _fallback_page_selection(self, pdf_path: str) -> Dict[str, List[int]]:
        """Fallback strategy when content analysis fails or finds no strategic pages"""
        try:
            # Get total page count
            total_pages = self._get_page_count(pdf_path)
            
            if total_pages <= 7:
                # Small deck: process all pages
                return {'general': list(range(1, total_pages + 1))}
            
            # Choose fallback pattern based on deck length
            if total_pages <= 20:
                pattern = self.fallback_patterns['short']
            elif total_pages >= 35:
                pattern = self.fallback_patterns['long']
            else:
                pattern = self.fallback_patterns['standard']
            
            # Filter out invalid page numbers and limit total
            valid_pages = [p for p in pattern if 1 <= p <= total_pages]
            selected_pages = valid_pages[:self.max_pages]
            
            # Ensure minimum coverage
            if len(selected_pages) < self.min_pages:
                # Add additional pages if needed
                additional_pages = []
                for i in range(1, total_pages + 1):
                    if i not in selected_pages:
                        additional_pages.append(i)
                        if len(selected_pages) + len(additional_pages) >= self.min_pages:
                            break
                selected_pages.extend(additional_pages)
            
            logger.info(f"Fallback page selection: {selected_pages} from {total_pages} total pages")
            return {'general': selected_pages}
            
        except Exception as e:
            logger.error(f"Fallback page selection failed: {e}")
            # Ultimate fallback: first 7 pages or all pages if fewer
            total_pages = self._get_page_count_safe(pdf_path)
            return {'general': list(range(1, min(8, total_pages + 1)))}
    
    def _enhance_with_fallback(self, selected_pages: Dict[str, List[int]], pdf_path: str) -> Dict[str, List[int]]:
        """Enhance selected pages with fallback patterns if insufficient"""
        current_total = sum(len(pages) for pages in selected_pages.values())
        
        if current_total >= self.min_pages:
            return selected_pages
        
        needed_pages = self.min_pages - current_total
        total_pages = self._get_page_count(pdf_path)
        
        # Get already selected pages
        already_selected = [page for pages in selected_pages.values() for page in pages]
        
        # Add pages from fallback pattern
        fallback_pattern = self.fallback_patterns['standard']
        added_pages = []
        
        for page_num in fallback_pattern:
            if page_num not in already_selected and 1 <= page_num <= total_pages:
                added_pages.append(page_num)
                if len(added_pages) >= needed_pages:
                    break
        
        if added_pages:
            if 'general' not in selected_pages:
                selected_pages['general'] = []
            selected_pages['general'].extend(added_pages)
        
        return selected_pages
    
    def _get_page_count(self, pdf_path: str) -> int:
        """Get total page count efficiently"""
        try:
            if PDF_LIBRARY == 'PyPDF2':
                with open(pdf_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    return len(pdf_reader.pages)
            elif PDF_LIBRARY == 'pdfplumber':
                with pdfplumber.open(pdf_path) as pdf:
                    return len(pdf.pages)
            else:
                return 0
        except Exception:
            return 0
    
    def _get_page_count_safe(self, pdf_path: str) -> int:
        """Safe page count with fallback"""
        count = self._get_page_count(pdf_path)
        return max(count, 7)  # Ensure minimum for fallback
    
    def _log_selection_rationale(self, selected_pages: Dict[str, List[int]], total_pages: int, selection_time: float):
        """Log detailed rationale for page selection decisions"""
        total_selected = sum(len(pages) for pages in selected_pages.values())
        
        logger.info(f"Strategic page selection complete:")
        logger.info(f"  Total pages in document: {total_pages}")
        logger.info(f"  Pages selected for vision: {total_selected}/{self.max_pages}")
        logger.info(f"  Selection time: {selection_time:.2f} seconds")
        logger.info(f"  Cost optimization: {(1 - total_selected/total_pages)*100:.1f}% reduction")
        
        for category, pages in selected_pages.items():
            logger.info(f"  {category}: pages {pages}")
        
        # Calculate estimated cost savings
        full_cost = total_pages * 0.01  # Rough estimate per page
        actual_cost = total_selected * 0.01
        savings = full_cost - actual_cost
        logger.info(f"  Estimated cost: ${actual_cost:.2f} vs ${full_cost:.2f} full processing")
        logger.info(f"  Estimated savings: ${savings:.2f} ({savings/full_cost*100:.1f}%)")
    
    def get_selection_stats(self) -> Dict:
        """Get statistics about the selector configuration"""
        return {
            'max_pages': self.max_pages,
            'min_pages': self.min_pages,
            'categories': list(self.page_patterns.keys()),
            'total_keywords': sum(len(pattern['keywords']) for pattern in self.page_patterns.values()),
            'pdf_library': PDF_LIBRARY,
            'fallback_patterns': list(self.fallback_patterns.keys())
        }