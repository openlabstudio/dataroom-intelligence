# Vision Processing Engine Architecture

**Component**: Core GPT Vision Processing Engine  
**Location**: `handlers/vision_processor.py`  
**Responsibility**: Intelligent visual document analysis with cost optimization  

## Component Overview

The Vision Processing Engine serves as the central component for GPT-4V/5V integration, providing intelligent visual document analysis while maintaining strict cost controls and performance optimization.

### Core Responsibilities

**Primary Functions**
- **Document Complexity Analysis**: Assess PDF pages for visual complexity to determine processing necessity
- **Intelligent Page Selection**: Select 20-40% of pages with highest visual content for vision processing
- **GPT Vision API Integration**: Execute vision analysis with proper error handling and rate limiting
- **Cost Management**: Track and control vision API usage with budget enforcement
- **Result Synthesis**: Combine vision results with text extraction for comprehensive analysis

**Integration Points**
- **Document Processor**: Receives documents from enhanced doc processor for vision analysis
- **AI Analyzer**: Provides vision results to AI analyzer for comprehensive document understanding
- **Session Manager**: Stores vision extraction results in enhanced session structure
- **Cost Monitor**: Integrates with cost tracking and budget enforcement systems

## Architectural Design

### Core Component Structure

```python
# handlers/vision_processor.py
class GPTVisionProcessor:
    """Core GPT Vision processing engine with cost optimization"""
    
    def __init__(self, openai_client):
        self.client = openai_client
        self.model = "gpt-4-vision-preview"
        
        # Sub-components
        self.complexity_analyzer = VisualComplexityAnalyzer()
        self.image_manager = SecureImageManager()
        self.cost_tracker = VisionCostTracker()
        self.rate_limiter = APIRateLimiter(max_requests_per_minute=50)
        
        # Performance monitoring
        self.performance_metrics = {
            'total_requests': 0,
            'successful_extractions': 0,
            'average_processing_time': 0.0,
            'cost_efficiency_ratio': 0.0
        }
```

### Document Processing Pipeline

**Stage 1: Document Analysis and Page Selection**
```python
def process_document_with_vision(self, pdf_path: str, document_context: dict) -> dict:
    """Main entry point for document vision processing"""
    try:
        # Convert PDF to images for analysis
        page_images = self._convert_pdf_to_images(pdf_path)
        
        # Analyze visual complexity for each page
        page_complexity_scores = []
        for page_num, image_path in enumerate(page_images):
            complexity = self.complexity_analyzer.analyze_page_complexity(image_path)
            page_complexity_scores.append({
                'page_number': page_num + 1,
                'image_path': image_path,
                'complexity_score': complexity,
                'estimated_cost': self._estimate_page_cost(complexity)
            })
        
        # Select pages for vision processing (top 20-40% by complexity)
        selected_pages = self._select_pages_for_processing(page_complexity_scores)
        
        # Process selected pages with vision analysis
        vision_results = self._process_pages_with_vision(selected_pages, document_context)
        
        return {
            'vision_extractions': vision_results,
            'processing_summary': {
                'total_pages': len(page_images),
                'pages_analyzed': len(selected_pages),
                'cost_optimization_ratio': 1.0 - (len(selected_pages) / len(page_images)),
                'total_estimated_cost': sum(page['estimated_cost'] for page in selected_pages)
            }
        }
        
    except Exception as e:
        logger.error(f"Vision document processing failed: {e}")
        return self._format_error_result(str(e))
```

**Stage 2: Visual Complexity Analysis**
```python
class VisualComplexityAnalyzer:
    """Analyze visual complexity to determine vision processing necessity"""
    
    def analyze_page_complexity(self, image_path: str) -> float:
        """Calculate complexity score (0.0-1.0) for intelligent processing decisions"""
        
        with Image.open(image_path) as img:
            # Convert to numpy array for analysis
            img_array = np.array(img.convert('RGB'))
            
            # Analyze multiple complexity factors
            metrics = {
                'color_diversity': self._calculate_color_diversity(img_array),
                'edge_density': self._calculate_edge_density(img_array),
                'text_to_visual_ratio': self._calculate_text_visual_ratio(img_array),
                'spatial_complexity': self._calculate_spatial_complexity(img_array)
            }
            
            # Weighted complexity calculation
            complexity_score = (
                metrics['color_diversity'] * 0.25 +      # Charts often have multiple colors
                metrics['edge_density'] * 0.35 +         # Diagrams and tables have many edges
                (1.0 - metrics['text_to_visual_ratio']) * 0.25 +  # Less text = more visual
                metrics['spatial_complexity'] * 0.15     # Complex layouts need vision analysis
            )
            
            return min(1.0, max(0.0, complexity_score))
```

**Stage 3: Intelligent Page Selection**
```python
def _select_pages_for_processing(self, page_scores: list) -> list:
    """Select optimal pages for vision processing based on complexity and cost"""
    
    # Sort pages by complexity score (highest first)
    sorted_pages = sorted(page_scores, key=lambda x: x['complexity_score'], reverse=True)
    
    # Determine selection criteria
    min_pages = max(1, len(sorted_pages) // 10)      # At least 10% of pages
    max_pages = min(len(sorted_pages), len(sorted_pages) // 2.5)  # At most 40% of pages
    
    # Select pages above complexity threshold
    complexity_threshold = 0.6
    high_complexity_pages = [
        page for page in sorted_pages 
        if page['complexity_score'] >= complexity_threshold
    ]
    
    # Ensure selection within min/max bounds
    if len(high_complexity_pages) < min_pages:
        selected_pages = sorted_pages[:min_pages]
    elif len(high_complexity_pages) > max_pages:
        selected_pages = high_complexity_pages[:max_pages]
    else:
        selected_pages = high_complexity_pages
    
    # Cost validation
    total_estimated_cost = sum(page['estimated_cost'] for page in selected_pages)
    if not self.cost_tracker.can_afford(total_estimated_cost):
        # Reduce selection to fit budget
        budget_remaining = self.cost_tracker.get_remaining_budget()
        selected_pages = self._fit_selection_to_budget(selected_pages, budget_remaining)
    
    return selected_pages
```

### Vision API Integration

**GPT Vision Processing Implementation**
```python
async def _process_single_page(self, page_info: dict, context: dict) -> dict:
    """Process individual page with GPT Vision API"""
    
    # Rate limiting enforcement
    await self.rate_limiter.acquire()
    
    # Cost validation
    estimated_cost = page_info['estimated_cost']
    if not self.cost_tracker.can_afford(estimated_cost):
        raise VisionBudgetExceededException(f"Cannot afford ${estimated_cost} processing cost")
    
    start_time = time.time()
    
    try:
        # Prepare image for API
        image_data = self.image_manager.prepare_image_for_api(page_info['image_path'])
        
        # Create context-aware vision prompt
        vision_prompt = self._create_vision_prompt(context, page_info['page_number'])
        
        # Execute GPT Vision API call
        response = await self.client.chat.completions.acreate(
            model=self.model,
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": vision_prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{image_data}"}
                    }
                ]
            }],
            max_tokens=1500,
            temperature=0.1
        )
        
        processing_time = time.time() - start_time
        actual_cost = self._calculate_actual_cost(response.usage)
        
        # Record successful processing
        self.cost_tracker.record_usage(actual_cost)
        self._update_performance_metrics(processing_time, actual_cost)
        
        return {
            'page_number': page_info['page_number'],
            'complexity_score': page_info['complexity_score'],
            'extracted_content': response.choices[0].message.content,
            'visual_elements': self._extract_visual_elements(response.choices[0].message.content),
            'confidence_score': self._calculate_confidence_score(response),
            'processing_time': processing_time,
            'actual_cost': actual_cost,
            'tokens_used': response.usage.total_tokens
        }
        
    except Exception as e:
        logger.error(f"Vision processing failed for page {page_info['page_number']}: {e}")
        return {
            'page_number': page_info['page_number'],
            'error': str(e),
            'extracted_content': '',
            'processing_time': time.time() - start_time
        }
```

### Cost Management Integration

**Vision Cost Tracking and Control**
```python
class VisionCostTracker:
    """Comprehensive cost management for Vision API usage"""
    
    def __init__(self):
        self.daily_limit = float(os.getenv('VISION_COST_LIMIT', '5.0'))
        self.current_usage = 0.0
        self.usage_history = []
        self.budget_warnings_sent = set()
        
    def can_afford(self, estimated_cost: float) -> bool:
        """Check if processing can proceed within budget"""
        projected_usage = self.current_usage + estimated_cost
        
        if projected_usage > self.daily_limit:
            logger.warning(f"Vision processing would exceed daily budget: ${projected_usage:.2f} > ${self.daily_limit:.2f}")
            return False
        
        # Send warning at 80% budget utilization
        if projected_usage > (self.daily_limit * 0.8) and 'budget_80' not in self.budget_warnings_sent:
            logger.warning(f"Vision budget at 80%: ${projected_usage:.2f}/${self.daily_limit:.2f}")
            self.budget_warnings_sent.add('budget_80')
        
        return True
    
    def record_usage(self, actual_cost: float):
        """Record actual API usage with detailed tracking"""
        self.current_usage += actual_cost
        self.usage_history.append({
            'timestamp': datetime.utcnow(),
            'cost': actual_cost,
            'cumulative_cost': self.current_usage
        })
        
        logger.info(f"Vision API usage: ${actual_cost:.3f}, Daily total: ${self.current_usage:.2f}/${self.daily_limit:.2f}")
    
    def get_cost_summary(self) -> dict:
        """Generate comprehensive cost summary for monitoring"""
        return {
            'daily_budget': self.daily_limit,
            'current_usage': self.current_usage,
            'remaining_budget': self.daily_limit - self.current_usage,
            'utilization_percentage': (self.current_usage / self.daily_limit) * 100,
            'transactions_today': len(self.usage_history),
            'average_cost_per_page': self._calculate_average_cost_per_page()
        }
```

### Performance Optimization

**Image Processing Optimization**
```python
class SecureImageManager:
    """Secure and efficient image processing for Vision API"""
    
    def __init__(self):
        self.temp_dir = tempfile.mkdtemp(prefix='vision_')
        self.max_image_size = (2048, 2048)  # Optimal for Vision API
        self.supported_formats = ['PNG', 'JPEG', 'WebP']
        
    def prepare_image_for_api(self, image_path: str) -> str:
        """Optimize image for Vision API with cost/quality balance"""
        
        with Image.open(image_path) as img:
            # Convert to RGB if necessary
            if img.mode not in ['RGB', 'RGBA']:
                img = img.convert('RGB')
            
            # Resize if too large (API has size limits and costs scale with size)
            if img.width > self.max_image_size[0] or img.height > self.max_image_size[1]:
                img.thumbnail(self.max_image_size, Image.Resampling.LANCZOS)
                logger.debug(f"Resized image from original size to {img.size}")
            
            # Optimize compression for API efficiency
            buffer = io.BytesIO()
            img.save(buffer, format='JPEG', quality=85, optimize=True)
            
            # Convert to base64 for API transmission
            image_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
            
            # Cleanup
            buffer.close()
            
            return image_data
    
    def cleanup_temp_files(self):
        """Secure cleanup of temporary image files"""
        try:
            shutil.rmtree(self.temp_dir)
            self.temp_dir = tempfile.mkdtemp(prefix='vision_')
        except Exception as e:
            logger.warning(f"Temp file cleanup warning: {e}")
```

### Error Handling and Resilience

**Comprehensive Error Management**
```python
def _handle_vision_processing_error(self, error: Exception, page_info: dict) -> dict:
    """Comprehensive error handling for vision processing failures"""
    
    error_type = type(error).__name__
    page_number = page_info.get('page_number', 'unknown')
    
    # Categorize errors for appropriate handling
    if isinstance(error, VisionBudgetExceededException):
        logger.warning(f"Budget limit reached, skipping page {page_number}")
        return self._format_budget_limit_result(page_info)
    
    elif isinstance(error, APIRateLimitError):
        logger.warning(f"Rate limit hit, will retry page {page_number}")
        return self._format_rate_limit_result(page_info)
    
    elif isinstance(error, APITimeoutError):
        logger.error(f"API timeout for page {page_number}")
        return self._format_timeout_result(page_info)
    
    else:
        logger.error(f"Unexpected vision processing error for page {page_number}: {error}")
        return self._format_general_error_result(page_info, str(error))

def _format_error_result(self, error_message: str) -> dict:
    """Format consistent error response for vision processing failures"""
    return {
        'vision_extractions': [],
        'processing_summary': {
            'total_pages': 0,
            'pages_analyzed': 0,
            'error': error_message,
            'fallback_recommended': True
        },
        'error_details': {
            'component': 'vision_processor',
            'timestamp': datetime.utcnow().isoformat(),
            'recovery_action': 'fallback_to_text_extraction'
        }
    }
```

---

*This Vision Processing Engine architecture provides the core intelligence for GPT Vision integration while maintaining strict cost controls, performance optimization, and comprehensive error handling for reliable operation within the DataRoom Intelligence system.*