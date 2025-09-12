# Document Processor Enhancement Architecture

**Component**: Enhanced Document Processing Pipeline  
**Location**: `handlers/doc_processor.py`  
**Responsibility**: Intelligent hybrid text + vision document processing  

## Component Overview

The Enhanced Document Processor builds upon the existing robust three-tier text extraction system, adding intelligent visual processing capabilities while maintaining all current reliability and fallback mechanisms.

### Enhancement Philosophy

**Preservation + Enhancement Approach**
- **Maintain**: Existing PyPDF2 → pdfplumber → OCR cascade as foundation
- **Add**: Intelligent vision processing as selective enhancement layer
- **Preserve**: All current error handling, logging, and response formatting
- **Enhance**: Document understanding through hybrid text + visual intelligence

**Integration Strategy**
```python
# Current Workflow: PDF → Text Extraction → Results
# Enhanced Workflow: PDF → Text Extraction + Selective Vision Processing → Merged Results
```

## Architectural Design

### Enhanced Processing Pipeline

**Core Document Processor Structure**
```python
# handlers/doc_processor.py - Enhanced Implementation
class DocumentProcessor:
    """Enhanced document processor with hybrid text+vision extraction"""
    
    def __init__(self):
        # EXISTING: Preserved text extraction processors
        self.pdf_processors = [
            self._extract_with_pypdf2,
            self._extract_with_pdfplumber,
            self._extract_with_ocr
        ]
        
        # NEW: Vision processing integration
        from handlers.vision_processor import GPTVisionProcessor
        from handlers.ai_analyzer import AIAnalyzer
        ai_analyzer = AIAnalyzer()
        self.vision_processor = ai_analyzer.vision_processor
        
        # NEW: Document analysis capabilities
        self.document_classifier = DocumentClassifier()
        self.processing_metrics = ProcessingMetrics()
```

### Multi-Stage Processing Architecture

**Stage 1: Document Classification and Analysis**
```python
def process_pdf(self, file_path: str) -> dict:
    """Enhanced PDF processing with intelligent strategy selection"""
    
    processing_start = time.time()
    
    try:
        # STAGE 1: Document classification and analysis
        document_analysis = self._analyze_document_characteristics(file_path)
        
        # STAGE 2: Text extraction (existing cascade preserved)
        text_extraction_result = self._extract_text_with_cascade(file_path)
        
        # STAGE 3: Vision processing decision
        vision_processing_decision = self._determine_vision_processing_strategy(
            file_path, 
            text_extraction_result, 
            document_analysis
        )
        
        # STAGE 4: Execute processing strategy
        if vision_processing_decision['use_vision']:
            return self._process_with_hybrid_extraction(
                file_path, 
                text_extraction_result, 
                vision_processing_decision
            )
        else:
            return self._format_text_only_result(text_extraction_result)
            
    except Exception as e:
        logger.error(f"Enhanced document processing failed: {e}")
        return self._format_error_result(str(e))
    
    finally:
        processing_time = time.time() - processing_start
        self.processing_metrics.record_processing_time(processing_time)
```

**Stage 2: Document Characteristics Analysis**
```python
def _analyze_document_characteristics(self, file_path: str) -> dict:
    """Analyze document to determine optimal processing strategy"""
    
    try:
        # Basic file analysis
        file_stats = {
            'file_size_mb': os.path.getsize(file_path) / (1024 * 1024),
            'page_count': self._get_page_count(file_path),
            'filename': os.path.basename(file_path).lower()
        }
        
        # Content type indicators from filename
        visual_indicators = {
            'pitch_deck': any(term in file_stats['filename'] for term in ['pitch', 'deck', 'presentation', 'slides']),
            'financial_model': any(term in file_stats['filename'] for term in ['financial', 'model', 'projections', 'forecast']),
            'data_room': any(term in file_stats['filename'] for term in ['dataroom', 'data_room', 'investor']),
            'executive_summary': any(term in file_stats['filename'] for term in ['executive', 'summary', 'overview'])
        }
        
        # Document complexity assessment
        complexity_indicators = {
            'likely_visual_rich': visual_indicators['pitch_deck'] or visual_indicators['financial_model'],
            'large_document': file_stats['page_count'] > 20,
            'appropriate_size': file_stats['file_size_mb'] < 50,  # Manageable for vision processing
        }
        
        return {
            'file_stats': file_stats,
            'visual_indicators': visual_indicators,
            'complexity_assessment': complexity_indicators,
            'recommended_strategy': self._recommend_processing_strategy(visual_indicators, complexity_indicators)
        }
        
    except Exception as e:
        logger.warning(f"Document analysis failed, using default strategy: {e}")
        return self._get_default_analysis()
```

**Stage 3: Vision Processing Decision Logic**
```python
def _determine_vision_processing_strategy(self, file_path: str, text_result: dict, analysis: dict) -> dict:
    """Intelligent decision-making for vision processing necessity"""
    
    # Check if vision processing is enabled globally
    if not os.getenv('VISION_ENABLED', 'true').lower() == 'true':
        return {
            'use_vision': False,
            'reason': 'vision_processing_disabled',
            'processing_strategy': 'text_only'
        }
    
    # Evaluate text extraction quality
    text_quality_score = self._assess_text_extraction_quality(text_result)
    
    # Decision factors
    decision_factors = {
        'text_quality_insufficient': text_quality_score < 0.7,
        'visual_indicators_present': analysis['complexity_assessment']['likely_visual_rich'],
        'document_size_appropriate': analysis['complexity_assessment']['appropriate_size'],
        'cost_budget_available': self.vision_processor.cost_tracker.can_afford(self._estimate_processing_cost(analysis)),
        'filename_suggests_visual': analysis['visual_indicators']['pitch_deck'] or analysis['visual_indicators']['financial_model']
    }
    
    # Decision algorithm
    vision_recommended = (
        decision_factors['text_quality_insufficient'] or
        (decision_factors['visual_indicators_present'] and decision_factors['document_size_appropriate'])
    ) and decision_factors['cost_budget_available']
    
    # Determine processing intensity
    if vision_recommended:
        if decision_factors['filename_suggests_visual'] and decision_factors['text_quality_insufficient']:
            processing_intensity = 'comprehensive'  # Process 30-40% of pages
        elif decision_factors['visual_indicators_present']:
            processing_intensity = 'selective'      # Process 20-30% of pages
        else:
            processing_intensity = 'minimal'        # Process 10-20% of pages
    else:
        processing_intensity = 'none'
    
    return {
        'use_vision': vision_recommended,
        'processing_intensity': processing_intensity,
        'decision_factors': decision_factors,
        'estimated_cost': self._estimate_processing_cost(analysis) if vision_recommended else 0.0,
        'reason': self._explain_decision(decision_factors, vision_recommended)
    }
```

### Hybrid Processing Implementation

**Text + Vision Integration**
```python
def _process_with_hybrid_extraction(self, file_path: str, text_result: dict, vision_decision: dict) -> dict:
    """Execute hybrid text + vision processing"""
    
    try:
        # Create document context for vision processing
        document_context = self._create_document_context(text_result, vision_decision)
        
        # Execute vision processing with intelligent page selection
        vision_result = self.vision_processor.process_document_with_vision(
            file_path, 
            document_context
        )
        
        # Merge text and vision extractions
        merged_result = self._merge_text_and_vision_extractions(
            text_result, 
            vision_result, 
            vision_decision
        )
        
        # Validate and optimize merged result
        validated_result = self._validate_merged_extraction(merged_result)
        
        return validated_result
        
    except VisionProcessingError as e:
        logger.warning(f"Vision processing failed, using text-only result: {e}")
        return self._format_text_fallback_result(text_result, str(e))
    
    except Exception as e:
        logger.error(f"Hybrid processing failed: {e}")
        return self._format_error_result(str(e))
```

**Extraction Result Synthesis**
```python
def _merge_text_and_vision_extractions(self, text_result: dict, vision_result: dict, decision_context: dict) -> dict:
    """Intelligently combine text and vision extraction results"""
    
    # Base result structure from text extraction
    merged_result = {
        'extraction_method': 'hybrid_text_vision',
        'primary_content': text_result.get('content', ''),
        'text_extraction_metadata': text_result.get('metadata', {}),
        
        # Vision enhancement data
        'vision_extractions': vision_result.get('vision_extractions', []),
        'vision_processing_summary': vision_result.get('processing_summary', {}),
        
        # Synthesis results
        'enhanced_content': self._synthesize_content(text_result, vision_result),
        'extracted_insights': self._extract_comprehensive_insights(text_result, vision_result),
        'confidence_scores': self._calculate_extraction_confidence(text_result, vision_result),
        
        # Processing metadata
        'processing_strategy': decision_context['processing_intensity'],
        'decision_factors': decision_context['decision_factors'],
        'cost_summary': vision_result.get('processing_summary', {}).get('total_estimated_cost', 0.0)
    }
    
    # Enhanced content synthesis
    merged_result['comprehensive_analysis'] = self._create_comprehensive_analysis(
        text_result, 
        vision_result
    )
    
    return merged_result

def _synthesize_content(self, text_result: dict, vision_result: dict) -> str:
    """Create enhanced content combining text and visual insights"""
    
    base_content = text_result.get('content', '')
    vision_extractions = vision_result.get('vision_extractions', [])
    
    # Extract visual insights
    visual_insights = []
    for extraction in vision_extractions:
        if extraction.get('extracted_content'):
            page_num = extraction.get('page_number', 'unknown')
            content = extraction.get('extracted_content', '')
            visual_insights.append(f"[Page {page_num} Visual Analysis]: {content}")
    
    # Combine content intelligently
    if visual_insights:
        enhanced_content = base_content + "\n\n--- VISUAL ANALYSIS INSIGHTS ---\n" + "\n".join(visual_insights)
    else:
        enhanced_content = base_content
    
    return enhanced_content
```

### Text Extraction Quality Assessment

**Quality Scoring for Processing Decisions**
```python
def _assess_text_extraction_quality(self, text_result: dict) -> float:
    """Assess text extraction quality to inform vision processing decisions"""
    
    content = text_result.get('content', '')
    
    if not content or len(content.strip()) < 100:
        return 0.1  # Very poor extraction
    
    # Quality indicators
    quality_metrics = {
        'content_length': min(1.0, len(content) / 5000),  # Normalized content length
        'word_density': self._calculate_word_density(content),
        'sentence_structure': self._assess_sentence_structure(content),
        'extraction_completeness': self._estimate_extraction_completeness(content),
        'readable_formatting': self._assess_formatting_quality(content)
    }
    
    # Weighted quality score
    quality_score = (
        quality_metrics['content_length'] * 0.2 +
        quality_metrics['word_density'] * 0.2 +
        quality_metrics['sentence_structure'] * 0.25 +
        quality_metrics['extraction_completeness'] * 0.2 +
        quality_metrics['readable_formatting'] * 0.15
    )
    
    return min(1.0, max(0.0, quality_score))

def _calculate_word_density(self, content: str) -> float:
    """Calculate word density as quality indicator"""
    if not content:
        return 0.0
    
    words = len(content.split())
    characters = len(content)
    
    # Reasonable word density suggests good extraction
    word_density = words / characters if characters > 0 else 0.0
    
    # Normalize to 0-1 range (typical range 0.15-0.25 for good extraction)
    normalized_density = min(1.0, max(0.0, (word_density - 0.1) / 0.15))
    
    return normalized_density
```

### Error Handling and Fallback Strategy

**Comprehensive Error Management**
```python
def _handle_processing_error(self, error: Exception, file_path: str, stage: str) -> dict:
    """Comprehensive error handling with intelligent fallback"""
    
    error_type = type(error).__name__
    
    if stage == 'vision_processing':
        # Vision processing errors fall back to text extraction
        logger.warning(f"Vision processing failed, falling back to text extraction: {error}")
        try:
            text_result = self._extract_text_with_cascade(file_path)
            return self._format_text_fallback_result(text_result, str(error))
        except Exception as fallback_error:
            logger.error(f"Text extraction fallback also failed: {fallback_error}")
            return self._format_complete_failure_result(str(error), str(fallback_error))
    
    elif stage == 'text_extraction':
        # Text extraction errors are critical
        logger.error(f"Text extraction failed: {error}")
        return self._format_extraction_error_result(str(error))
    
    else:
        # General processing errors
        logger.error(f"Document processing failed at stage {stage}: {error}")
        return self._format_general_error_result(str(error), stage)

def _format_text_fallback_result(self, text_result: dict, vision_error: str) -> dict:
    """Format result when vision processing fails but text extraction succeeds"""
    return {
        'extraction_method': 'text_only_fallback',
        'content': text_result.get('content', ''),
        'metadata': text_result.get('metadata', {}),
        'processing_notes': {
            'vision_processing_attempted': True,
            'vision_error': vision_error,
            'fallback_used': 'text_extraction',
            'extraction_quality': 'reduced_due_to_vision_failure'
        },
        'confidence_score': max(0.5, text_result.get('confidence_score', 0.8) - 0.2)  # Reduced confidence
    }
```

### Performance Monitoring and Optimization

**Processing Metrics and Optimization**
```python
class ProcessingMetrics:
    """Monitor and optimize document processing performance"""
    
    def __init__(self):
        self.processing_history = []
        self.performance_thresholds = {
            'max_processing_time': 300,  # 5 minutes maximum
            'min_text_quality': 0.6,
            'max_vision_cost_per_document': 2.0
        }
    
    def record_processing_session(self, processing_data: dict):
        """Record comprehensive processing session data"""
        session_record = {
            'timestamp': datetime.utcnow(),
            'file_path': processing_data.get('file_path', ''),
            'processing_method': processing_data.get('extraction_method', ''),
            'processing_time': processing_data.get('processing_time', 0),
            'text_quality_score': processing_data.get('text_quality_score', 0),
            'vision_cost': processing_data.get('vision_cost', 0),
            'success': processing_data.get('success', False),
            'error_type': processing_data.get('error_type', None)
        }
        
        self.processing_history.append(session_record)
        
        # Performance analysis and optimization recommendations
        self._analyze_performance_trends()
    
    def get_optimization_recommendations(self) -> list:
        """Generate optimization recommendations based on processing history"""
        recommendations = []
        
        recent_sessions = self.processing_history[-50:]  # Last 50 sessions
        
        if recent_sessions:
            avg_processing_time = sum(s['processing_time'] for s in recent_sessions) / len(recent_sessions)
            avg_vision_cost = sum(s['vision_cost'] for s in recent_sessions) / len(recent_sessions)
            
            if avg_processing_time > self.performance_thresholds['max_processing_time']:
                recommendations.append({
                    'type': 'performance',
                    'issue': 'processing_time_high',
                    'recommendation': 'Consider reducing vision processing intensity or document size limits'
                })
            
            if avg_vision_cost > self.performance_thresholds['max_vision_cost_per_document']:
                recommendations.append({
                    'type': 'cost',
                    'issue': 'vision_cost_high',
                    'recommendation': 'Optimize page selection algorithm to reduce API calls'
                })
        
        return recommendations
```

---

*This Document Processor Enhancement architecture provides intelligent hybrid processing while preserving all existing reliability and fallback mechanisms, ensuring improved extraction quality with controlled costs and comprehensive error handling.*