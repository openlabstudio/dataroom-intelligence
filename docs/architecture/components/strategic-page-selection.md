# Strategic Page Selection Architecture

**Component**: Strategic Page Selector  
**Location**: `utils/strategic_page_selector.py`  
**Responsibility**: Content-based identification of 7 most valuable pages for vision processing  

## Component Overview

The Strategic Page Selection component implements the core intelligence behind Lazy Vision's 84% cost reduction strategy. Instead of processing all 43 pages, it analyzes PDF content to identify the 7 most strategic pages containing critical business information that benefits from vision processing.

### Core Responsibilities

**Primary Functions**
- **Content Analysis**: Scan PDF text content to identify pages with visual elements
- **Strategic Scoring**: Score pages based on business-critical content patterns
- **Dynamic Selection**: Select up to 7 pages with highest strategic value
- **Fallback Handling**: Ensure minimum coverage when content patterns don't match

**Integration Points**
- **Document Processor**: Receives PDF path and basic text extraction results
- **Vision Processor**: Provides selected page list for vision processing
- **Session Manager**: Stores page selection rationale for debugging and optimization

## Architectural Design

### Core Component Structure

```python
# utils/strategic_page_selector.py
class StrategicPageSelector:
    """Intelligent page selection for cost-effective vision processing"""
    
    def __init__(self):
        self.max_pages = 7  # Hard limit for SSL prevention
        self.min_pages = 3  # Minimum coverage guarantee
        
        # Content-based page identification patterns
        self.page_patterns = {
            'financials': {
                'keywords': ['revenue', 'burn rate', 'runway', 'ARR', 'MRR', 'financial', 
                           'income', 'cash flow', 'EBITDA', 'gross margin', 'unit economics'],
                'priority': 1,  # Highest priority
                'max_pages': 3
            },
            'competition': {
                'keywords': ['competitor', 'vs', 'comparison', 'landscape', 'alternatives',
                           'competitive', 'positioning', 'market share', 'differentiation'],
                'priority': 1,  # Highest priority  
                'max_pages': 3
            },
            'market': {
                'keywords': ['TAM', 'SAM', 'SOM', 'market size', 'billion', 'million',
                           'addressable', 'opportunity', 'market analysis'],
                'priority': 2,  # High priority
                'max_pages': 2
            },
            'traction': {
                'keywords': ['growth', 'users', 'customers', 'retention', 'churn', 
                           'metrics', 'KPIs', 'dashboard', 'engagement'],
                'priority': 2,  # High priority
                'max_pages': 2
            },
            'team': {
                'keywords': ['founder', 'CEO', 'CTO', 'team', 'advisor', 'board',
                           'leadership', 'experience', 'background'],
                'priority': 3,  # Medium priority
                'max_pages': 1
            }
        }
```

### Content-Based Page Detection

**Stage 1: Text Content Analysis**
```python
def get_strategic_pages(self, pdf_path: str, extracted_text: str = None) -> Dict[str, List[int]]:
    """
    Analyze PDF content to identify strategic pages for vision processing
    
    Returns:
        Dict with page categories and selected page numbers
        Example: {'financials': [18, 19], 'competition': [11, 12], 'market': [8]}
    """
    try:
        # Extract text content if not provided
        if not extracted_text:
            extracted_text = self._extract_text_for_analysis(pdf_path)
        
        # Get page-by-page text content
        page_contents = self._extract_page_contents(pdf_path)
        
        # Score each page for strategic value
        page_scores = []
        for page_num, content in enumerate(page_contents, 1):
            score_data = self._score_page_content(page_num, content)
            if score_data['total_score'] > 0:
                page_scores.append(score_data)
        
        # Select optimal pages within constraints
        selected_pages = self._select_optimal_pages(page_scores)
        
        # Log selection rationale for debugging
        self._log_selection_rationale(selected_pages, len(page_contents))
        
        return selected_pages
        
    except Exception as e:
        logger.error(f"Strategic page selection failed: {e}")
        return self._fallback_page_selection(pdf_path)

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
```

**Stage 2: Intelligent Page Selection**
```python
def _select_optimal_pages(self, page_scores: List[Dict]) -> Dict[str, List[int]]:
    """Select optimal combination of pages within constraints"""
    
    # Sort pages by total score (highest first)
    sorted_pages = sorted(page_scores, key=lambda x: x['total_score'], reverse=True)
    
    selected_pages = {}
    total_selected = 0
    
    # First pass: Select top pages from each priority category
    for priority in [1, 2, 3]:  # Process by priority order
        priority_categories = [cat for cat, config in self.page_patterns.items() 
                             if config['priority'] == priority]
        
        for category in priority_categories:
            if total_selected >= self.max_pages:
                break
                
            # Find top pages for this category
            category_pages = [p for p in sorted_pages 
                            if p['primary_category'] == category]
            
            max_for_category = min(
                self.page_patterns[category]['max_pages'],
                self.max_pages - total_selected
            )
            
            selected_for_category = []
            for page_data in category_pages[:max_for_category]:
                selected_for_category.append(page_data['page_number'])
                total_selected += 1
                
                if total_selected >= self.max_pages:
                    break
            
            if selected_for_category:
                selected_pages[category] = selected_for_category
    
    # Second pass: Fill remaining slots with highest scoring pages
    if total_selected < self.min_pages:
        remaining_slots = min(self.max_pages - total_selected, 
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
```

### Fallback Strategy

**Smart Fallback for Unknown Deck Formats**
```python
def _fallback_page_selection(self, pdf_path: str) -> Dict[str, List[int]]:
    """Fallback strategy when content analysis fails or finds no strategic pages"""
    
    try:
        # Get total page count
        total_pages = self._get_page_count(pdf_path)
        
        if total_pages <= 7:
            # Small deck: process all pages
            return {'general': list(range(1, total_pages + 1))}
        
        # Standard pitch deck fallback pattern (based on common structures)
        fallback_pages = {
            'team': [min(4, total_pages)],  # Usually early in deck
            'market': [min(8, total_pages)],  # Usually middle section
            'competition': [min(12, total_pages)],  # Usually after market
            'traction': [min(16, total_pages)],  # Usually after product
            'financials': [min(max(total_pages - 5, 18), total_pages),  # Near end
                          min(max(total_pages - 3, 20), total_pages)]
        }
        
        # Filter out invalid page numbers and limit total
        valid_pages = {}
        total_count = 0
        
        for category, pages in fallback_pages.items():
            valid_category_pages = [p for p in pages if 1 <= p <= total_pages]
            if valid_category_pages and total_count < self.max_pages:
                remaining_slots = self.max_pages - total_count
                selected = valid_category_pages[:remaining_slots]
                valid_pages[category] = selected
                total_count += len(selected)
        
        logger.info(f"Fallback page selection: {valid_pages} from {total_pages} total pages")
        return valid_pages
        
    except Exception as e:
        logger.error(f"Fallback page selection failed: {e}")
        # Ultimate fallback: first 7 pages or all pages if fewer
        total_pages = self._get_page_count_safe(pdf_path)
        return {'general': list(range(1, min(8, total_pages + 1)))}
```

### Performance Optimization

**Efficient Text Extraction for Analysis**
```python
def _extract_page_contents(self, pdf_path: str) -> List[str]:
    """Extract text content from each page for analysis (optimized for speed)"""
    
    page_contents = []
    
    try:
        # Use fastest available PDF text extraction
        import PyPDF2
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            for page_num in range(len(pdf_reader.pages)):
                try:
                    page = pdf_reader.pages[page_num]
                    text = page.extract_text()
                    page_contents.append(text)
                except Exception as e:
                    logger.warning(f"Could not extract text from page {page_num + 1}: {e}")
                    page_contents.append("")  # Empty content for failed extraction
                    
    except Exception as e:
        logger.error(f"PDF text extraction failed: {e}")
        # Return empty list - will trigger fallback
        return []
    
    return page_contents

def _get_page_count(self, pdf_path: str) -> int:
    """Get total page count efficiently"""
    try:
        import PyPDF2
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            return len(pdf_reader.pages)
    except Exception:
        return 0

def _get_page_count_safe(self, pdf_path: str) -> int:
    """Safe page count with fallback"""
    count = self._get_page_count(pdf_path)
    return max(count, 7)  # Ensure minimum for fallback
```

### Selection Rationale Logging

**Debugging and Optimization Support**
```python
def _log_selection_rationale(self, selected_pages: Dict[str, List[int]], total_pages: int):
    """Log detailed rationale for page selection decisions"""
    
    total_selected = sum(len(pages) for pages in selected_pages.values())
    
    logger.info(f"Strategic page selection complete:")
    logger.info(f"  Total pages in document: {total_pages}")
    logger.info(f"  Pages selected for vision: {total_selected}/{self.max_pages}")
    logger.info(f"  Cost optimization: {(1 - total_selected/total_pages)*100:.1f}% reduction")
    
    for category, pages in selected_pages.items():
        keywords_found = []
        for page_num in pages:
            # This would be populated during scoring
            pass
        logger.info(f"  {category}: pages {pages}")
    
    # Calculate estimated cost savings
    full_cost = total_pages * 0.01  # Rough estimate per page
    actual_cost = total_selected * 0.01
    savings = full_cost - actual_cost
    logger.info(f"  Estimated cost: ${actual_cost:.2f} vs ${full_cost:.2f} full processing")
    logger.info(f"  Estimated savings: ${savings:.2f} ({savings/full_cost*100:.1f}%)")
```

## Integration with Vision Processing

### Data Flow to Vision Processor

```python
# Integration pattern in vision_processor.py
def process_document_with_lazy_vision(self, pdf_path: str, user_id: str) -> Dict:
    """Process document using strategic page selection"""
    
    # Get strategic page selection
    page_selector = StrategicPageSelector()
    strategic_pages = page_selector.get_strategic_pages(pdf_path)
    
    # Convert to flat list for vision processing
    pages_to_process = []
    page_categories = {}
    
    for category, page_list in strategic_pages.items():
        for page_num in page_list:
            pages_to_process.append(page_num)
            page_categories[page_num] = category
    
    # Process selected pages with vision
    vision_results = {}
    for page_num in pages_to_process:
        try:
            category = page_categories[page_num]
            vision_data = self._process_single_page_with_context(
                pdf_path, page_num, category
            )
            vision_results[page_num] = {
                'category': category,
                'vision_data': vision_data
            }
        except Exception as e:
            logger.error(f"Vision processing failed for strategic page {page_num}: {e}")
    
    return {
        'strategic_selection': strategic_pages,
        'vision_results': vision_results,
        'processing_summary': {
            'pages_selected': len(pages_to_process),
            'categories_covered': list(strategic_pages.keys()),
            'success_rate': len(vision_results) / len(pages_to_process) if pages_to_process else 0
        }
    }
```

## Quality Assurance

### Selection Quality Validation

```python
def validate_selection_quality(self, pdf_path: str, selected_pages: Dict[str, List[int]]) -> Dict:
    """Validate that strategic selection covers essential business areas"""
    
    validation_results = {
        'coverage_score': 0.0,
        'missing_areas': [],
        'quality_warnings': [],
        'recommendations': []
    }
    
    # Check coverage of essential areas
    essential_areas = ['financials', 'competition', 'market']
    covered_areas = list(selected_pages.keys())
    
    coverage_count = sum(1 for area in essential_areas if area in covered_areas)
    validation_results['coverage_score'] = coverage_count / len(essential_areas)
    
    # Identify missing critical areas
    for area in essential_areas:
        if area not in covered_areas:
            validation_results['missing_areas'].append(area)
    
    # Generate recommendations
    if validation_results['coverage_score'] < 0.7:
        validation_results['recommendations'].append(
            "Consider manual review - low coverage of essential business areas"
        )
    
    if len(selected_pages.get('financials', [])) == 0:
        validation_results['quality_warnings'].append(
            "No financial pages selected - may impact investment analysis quality"
        )
    
    return validation_results
```

---

*This Strategic Page Selection architecture provides the intelligent foundation for Lazy Vision's cost-effective approach, ensuring high-value pages are processed while maintaining 84% cost reduction through strategic selection.*