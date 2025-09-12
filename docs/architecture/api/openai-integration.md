# OpenAI Integration Architecture

**Component**: Enhanced OpenAI Integration with Vision API  
**Responsibility**: GPT-4 text analysis + GPT Vision integration with cost controls  
**Integration Type**: Extension of existing OpenAI client patterns  

## Integration Overview

The Enhanced OpenAI Integration extends the existing robust GPT-4 text analysis capabilities to include GPT Vision API processing while maintaining all current functionality and adding comprehensive cost management and error handling.

### Integration Philosophy

**Seamless Extension Approach**
- **Preserve**: All existing OpenAI GPT-4 integration patterns and functionality
- **Extend**: Client capabilities to include Vision API with intelligent processing decisions
- **Enhance**: Cost tracking and budget controls for both text and vision processing
- **Maintain**: Existing error handling patterns while adding vision-specific resilience

**API Integration Strategy**
```python
# Current: Single-purpose text analysis
openai_client.chat.completions.create(model="gpt-4", messages=[...])

# Enhanced: Intelligent text + vision analysis  
enhanced_client.analyze_with_hybrid_intelligence(documents, vision_enabled=True)
```

## Enhanced OpenAI Client Architecture

### Core Client Structure

```python
# handlers/enhanced_openai_client.py
class EnhancedOpenAIClient:
    """Extended OpenAI client with Vision API and comprehensive cost management"""
    
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
        
        # Model configuration
        self.text_model = Config.OPENAI_MODEL
        self.vision_model = Config.VISION_MODEL
        self.temperature = Config.OPENAI_TEMPERATURE
        
        # Cost and performance management
        self.cost_tracker = APIUsageTracker()
        self.rate_limiter = APIRateLimiter()
        self.performance_monitor = PerformanceMonitor()
        
        # Request caching for efficiency
        self.response_cache = ResponseCache()
        
        logger.info(f"Enhanced OpenAI client initialized - Text: {self.text_model}, Vision: {self.vision_model}")
    
    def analyze_documents_with_intelligence(self, documents: list, enable_vision: bool = True) -> dict:
        """Main entry point for intelligent document analysis"""
        
        analysis_start_time = time.time()
        
        try:
            # Determine analysis strategy based on document characteristics
            analysis_strategy = self._determine_analysis_strategy(documents, enable_vision)
            
            # Execute appropriate analysis method
            if analysis_strategy['use_vision']:
                result = self._analyze_with_hybrid_intelligence(documents, analysis_strategy)
            else:
                result = self._analyze_with_text_only(documents)
            
            # Record performance metrics
            processing_time = time.time() - analysis_start_time
            self.performance_monitor.record_analysis_session(result, processing_time)
            
            return result
            
        except Exception as e:
            logger.error(f"Document analysis failed: {e}")
            return self._format_analysis_error(str(e))
```

### Vision API Integration

**GPT Vision Processing Implementation**
```python
async def analyze_with_vision(self, image_data: str, prompt: str, context: dict = None) -> dict:
    """Execute GPT Vision analysis with comprehensive error handling and cost tracking"""
    
    # Pre-processing validation
    validation_result = self._validate_vision_request(image_data, prompt)
    if not validation_result['valid']:
        raise VisionRequestValidationError(validation_result['error'])
    
    # Cost estimation and budget checking
    estimated_cost = self._estimate_vision_cost(image_data, prompt)
    if not self.cost_tracker.can_afford_vision_request(estimated_cost):
        raise VisionBudgetExceededException(f"Request cost ${estimated_cost:.3f} exceeds remaining budget")
    
    # Rate limiting enforcement
    await self.rate_limiter.acquire_vision_quota()
    
    request_start_time = time.time()
    
    try:
        # Optimize image for API efficiency
        optimized_image_data = self._optimize_image_for_vision_api(image_data)
        
        # Create vision request
        response = await self.client.chat.completions.acreate(
            model=self.vision_model,
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{optimized_image_data}"}
                    }
                ]
            }],
            max_tokens=1500,
            temperature=0.1,
            timeout=Config.VISION_PROCESSING_TIMEOUT
        )
        
        processing_time = time.time() - request_start_time
        actual_cost = self._calculate_actual_vision_cost(response.usage)
        
        # Record successful API usage
        self.cost_tracker.record_vision_usage(actual_cost, processing_time)
        
        # Format and return result
        return {
            'success': True,
            'content': response.choices[0].message.content,
            'usage': {
                'prompt_tokens': response.usage.prompt_tokens,
                'completion_tokens': response.usage.completion_tokens,
                'total_tokens': response.usage.total_tokens
            },
            'cost': actual_cost,
            'processing_time': processing_time,
            'model': self.vision_model
        }
        
    except asyncio.TimeoutError:
        processing_time = time.time() - request_start_time
        logger.warning(f"Vision API request timed out after {processing_time:.1f}s")
        return self._format_vision_timeout_result(processing_time)
        
    except Exception as e:
        processing_time = time.time() - request_start_time
        logger.error(f"Vision API request failed after {processing_time:.1f}s: {e}")
        return self._format_vision_error_result(str(e), processing_time)

def _optimize_image_for_vision_api(self, image_data: str) -> str:
    """Optimize image data for Vision API cost and performance"""
    
    try:
        # Decode base64 image
        image_bytes = base64.b64decode(image_data)
        
        with Image.open(io.BytesIO(image_bytes)) as img:
            # Check if optimization is needed
            original_size = len(image_bytes)
            
            # Resize if image is too large (API limits and cost considerations)
            max_dimension = 2048  # Optimal for Vision API
            if img.width > max_dimension or img.height > max_dimension:
                img.thumbnail((max_dimension, max_dimension), Image.Resampling.LANCZOS)
                logger.debug(f"Resized image from original to {img.size}")
            
            # Optimize compression
            output_buffer = io.BytesIO()
            img.save(output_buffer, format='JPEG', quality=85, optimize=True)
            optimized_bytes = output_buffer.getvalue()
            
            # Log optimization results
            optimized_size = len(optimized_bytes)
            compression_ratio = optimized_size / original_size
            logger.debug(f"Image optimization: {original_size} → {optimized_size} bytes ({compression_ratio:.2f})")
            
            return base64.b64encode(optimized_bytes).decode('utf-8')
            
    except Exception as e:
        logger.warning(f"Image optimization failed, using original: {e}")
        return image_data
```

### Hybrid Analysis Implementation

**Text + Vision Combined Analysis**
```python
def _analyze_with_hybrid_intelligence(self, documents: list, strategy: dict) -> dict:
    """Execute hybrid text + vision analysis for comprehensive document understanding"""
    
    try:
        # Collect all text content
        text_content = self._compile_text_content(documents)
        
        # Collect vision analysis results
        vision_insights = self._compile_vision_insights(documents)
        
        # Create comprehensive analysis prompt
        hybrid_prompt = self._create_hybrid_analysis_prompt(text_content, vision_insights, strategy)
        
        # Execute enhanced GPT-4 analysis
        analysis_response = self.client.chat.completions.create(
            model=self.text_model,
            messages=[
                {
                    "role": "system",
                    "content": """You are an expert business analyst with access to both text-extracted content 
                    and detailed visual analysis from document images. Provide comprehensive analysis that 
                    leverages both text and visual intelligence for superior document understanding."""
                },
                {
                    "role": "user",
                    "content": hybrid_prompt
                }
            ],
            temperature=self.temperature,
            max_tokens=3000
        )
        
        # Calculate costs and track usage
        text_cost = self._calculate_text_analysis_cost(analysis_response.usage)
        vision_cost = sum(doc.get('vision_cost', 0) for doc in documents)
        total_cost = text_cost + vision_cost
        
        self.cost_tracker.record_text_usage(text_cost)
        
        # Format comprehensive result
        return {
            'analysis_type': 'hybrid_text_vision',
            'content': analysis_response.choices[0].message.content,
            'text_analysis': self._extract_text_insights(text_content),
            'vision_analysis': self._extract_vision_insights(vision_insights),
            'combined_insights': self._generate_combined_insights(analysis_response),
            'usage_summary': {
                'text_tokens': analysis_response.usage.total_tokens,
                'vision_pages_processed': len(vision_insights),
                'total_cost': total_cost,
                'cost_breakdown': {
                    'text_analysis': text_cost,
                    'vision_processing': vision_cost
                }
            },
            'confidence_score': self._calculate_hybrid_confidence_score(text_content, vision_insights)
        }
        
    except Exception as e:
        logger.error(f"Hybrid analysis failed: {e}")
        return self._format_hybrid_analysis_error(str(e))

def _create_hybrid_analysis_prompt(self, text_content: str, vision_insights: list, strategy: dict) -> str:
    """Create comprehensive prompt combining text and vision analysis"""
    
    prompt_sections = [
        "# COMPREHENSIVE DOCUMENT ANALYSIS REQUEST",
        "",
        "## TEXT EXTRACTED CONTENT:",
        text_content[:8000],  # Limit text content to stay within token limits
        "",
        "## VISUAL ANALYSIS INSIGHTS:",
    ]
    
    # Add vision insights
    for insight in vision_insights:
        page_num = insight.get('page_number', 'unknown')
        content = insight.get('extracted_content', '')
        confidence = insight.get('confidence_score', 0)
        
        prompt_sections.append(f"### Page {page_num} (Confidence: {confidence:.2f}):")
        prompt_sections.append(content[:1000])  # Limit each insight
        prompt_sections.append("")
    
    # Add analysis instructions
    prompt_sections.extend([
        "## ANALYSIS REQUIREMENTS:",
        "1. Analyze both text-extracted content and visual insights comprehensively",
        "2. Identify information that appears in visual elements but not in text extraction",
        "3. Cross-validate information between text and visual sources",
        "4. Highlight any discrepancies or additional insights from visual analysis",
        "5. Provide investment-focused analysis leveraging all available information",
        "",
        "## EXPECTED OUTPUT:",
        "Provide structured analysis including company overview, solution summary, market analysis, financial insights, and investment recommendation based on comprehensive text and visual document understanding."
    ])
    
    return "\n".join(prompt_sections)
```

### Cost Management and Tracking

**Comprehensive API Usage Tracking**
```python
class APIUsageTracker:
    """Comprehensive tracking and management of OpenAI API costs"""
    
    def __init__(self):
        self.daily_limits = {
            'text': float(os.getenv('TEXT_API_DAILY_LIMIT', '20.0')),
            'vision': float(os.getenv('VISION_API_DAILY_LIMIT', '5.0')),
            'total': float(os.getenv('TOTAL_API_DAILY_LIMIT', '25.0'))
        }
        
        self.current_usage = {
            'text': 0.0,
            'vision': 0.0,
            'total': 0.0
        }
        
        self.usage_history = []
        self.budget_alerts_sent = set()
        
        # Reset usage daily
        self.last_reset_date = datetime.utcnow().date()
        
    def can_afford_vision_request(self, estimated_cost: float) -> bool:
        """Check if vision request can proceed within budget limits"""
        
        self._reset_usage_if_new_day()
        
        # Check individual vision budget
        if (self.current_usage['vision'] + estimated_cost) > self.daily_limits['vision']:
            logger.warning(f"Vision request would exceed daily vision limit: ${estimated_cost:.3f}")
            return False
        
        # Check total API budget
        if (self.current_usage['total'] + estimated_cost) > self.daily_limits['total']:
            logger.warning(f"Vision request would exceed total daily API limit: ${estimated_cost:.3f}")
            return False
        
        return True
    
    def record_vision_usage(self, actual_cost: float, processing_time: float):
        """Record actual vision API usage"""
        
        self.current_usage['vision'] += actual_cost
        self.current_usage['total'] += actual_cost
        
        # Record detailed usage
        usage_record = {
            'timestamp': datetime.utcnow(),
            'api_type': 'vision',
            'cost': actual_cost,
            'processing_time': processing_time,
            'cumulative_daily_cost': self.current_usage['total']
        }
        
        self.usage_history.append(usage_record)
        
        # Budget monitoring and alerts
        self._check_budget_alerts()
        
        logger.info(f"Vision API usage: ${actual_cost:.3f}, Daily total: ${self.current_usage['total']:.2f}")
    
    def record_text_usage(self, actual_cost: float):
        """Record text API usage"""
        
        self.current_usage['text'] += actual_cost
        self.current_usage['total'] += actual_cost
        
        usage_record = {
            'timestamp': datetime.utcnow(),
            'api_type': 'text',
            'cost': actual_cost,
            'cumulative_daily_cost': self.current_usage['total']
        }
        
        self.usage_history.append(usage_record)
        self._check_budget_alerts()
    
    def _check_budget_alerts(self):
        """Monitor budget usage and send appropriate alerts"""
        
        total_usage = self.current_usage['total']
        total_limit = self.daily_limits['total']
        usage_percentage = (total_usage / total_limit) * 100
        
        # 50% budget alert
        if usage_percentage >= 50 and 'budget_50' not in self.budget_alerts_sent:
            logger.warning(f"API budget at 50%: ${total_usage:.2f}/${total_limit:.2f}")
            self.budget_alerts_sent.add('budget_50')
        
        # 80% budget alert
        if usage_percentage >= 80 and 'budget_80' not in self.budget_alerts_sent:
            logger.warning(f"API budget at 80%: ${total_usage:.2f}/${total_limit:.2f}")
            self.budget_alerts_sent.add('budget_80')
        
        # 95% budget alert
        if usage_percentage >= 95 and 'budget_95' not in self.budget_alerts_sent:
            logger.error(f"API budget at 95%: ${total_usage:.2f}/${total_limit:.2f}")
            self.budget_alerts_sent.add('budget_95')
    
    def get_usage_summary(self) -> dict:
        """Get comprehensive usage summary for monitoring"""
        
        return {
            'current_usage': self.current_usage.copy(),
            'daily_limits': self.daily_limits.copy(),
            'usage_percentages': {
                'text': (self.current_usage['text'] / self.daily_limits['text']) * 100,
                'vision': (self.current_usage['vision'] / self.daily_limits['vision']) * 100,
                'total': (self.current_usage['total'] / self.daily_limits['total']) * 100
            },
            'remaining_budget': {
                'text': self.daily_limits['text'] - self.current_usage['text'],
                'vision': self.daily_limits['vision'] - self.current_usage['vision'],
                'total': self.daily_limits['total'] - self.current_usage['total']
            },
            'requests_today': len(self.usage_history),
            'last_reset': self.last_reset_date.isoformat()
        }
```

### Error Handling and Resilience

**Comprehensive Error Management**
```python
def _handle_api_error(self, error: Exception, api_type: str, context: dict) -> dict:
    """Comprehensive error handling for OpenAI API failures"""
    
    error_type = type(error).__name__
    
    # Rate limiting errors
    if 'RateLimitError' in error_type:
        retry_delay = self._calculate_retry_delay(error)
        logger.warning(f"{api_type} API rate limited, retry in {retry_delay}s")
        return {
            'success': False,
            'error_type': 'rate_limit',
            'error_message': f"API rate limit reached for {api_type}",
            'retry_after': retry_delay,
            'recovery_action': 'retry_with_delay'
        }
    
    # Authentication errors
    elif 'AuthenticationError' in error_type:
        logger.error(f"{api_type} API authentication failed")
        return {
            'success': False,
            'error_type': 'authentication',
            'error_message': f"API authentication failed for {api_type}",
            'recovery_action': 'check_api_key'
        }
    
    # Timeout errors
    elif 'TimeoutError' in error_type or 'timeout' in str(error).lower():
        logger.warning(f"{api_type} API request timed out")
        return {
            'success': False,
            'error_type': 'timeout',
            'error_message': f"API request timed out for {api_type}",
            'recovery_action': 'retry_with_fallback'
        }
    
    # Budget exceeded errors
    elif isinstance(error, VisionBudgetExceededException):
        logger.warning(f"Vision API budget exceeded: {error}")
        return {
            'success': False,
            'error_type': 'budget_exceeded',
            'error_message': str(error),
            'recovery_action': 'fallback_to_text_only'
        }
    
    # General API errors
    else:
        logger.error(f"{api_type} API error: {error}")
        return {
            'success': False,
            'error_type': 'api_error',
            'error_message': f"API error for {api_type}: {str(error)}",
            'recovery_action': 'fallback_to_alternative'
        }

def _execute_error_recovery(self, error_result: dict, original_request: dict) -> dict:
    """Execute appropriate recovery action based on error type"""
    
    recovery_action = error_result.get('recovery_action')
    
    if recovery_action == 'retry_with_delay':
        # Implement exponential backoff retry
        return self._retry_with_exponential_backoff(original_request)
    
    elif recovery_action == 'fallback_to_text_only':
        # Fall back to text-only analysis when vision processing fails
        return self._analyze_with_text_only(original_request['documents'])
    
    elif recovery_action == 'retry_with_fallback':
        # Retry once, then fall back
        try:
            return self._retry_request_once(original_request)
        except Exception:
            return self._analyze_with_text_only(original_request['documents'])
    
    else:
        # Return error result if no recovery possible
        return error_result
```

---

*This OpenAI Integration architecture provides comprehensive text and vision API capabilities while maintaining cost efficiency, robust error handling, and seamless integration with the existing DataRoom Intelligence system.*