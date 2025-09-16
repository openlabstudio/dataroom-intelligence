# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Application Architecture

**DataRoom Intelligence Bot** - AI-powered data room analysis for venture capital firms with streamlined GPT-4o Direct processing.

### Current Project Status
- **Phase**: Vision Analysis Phase (QA Validated) - GPT-4o Direct PDF Processing
- **Branch**: `phase3-advanced-analyze` - Current active development branch
- **System Status**: ✅ **PRODUCTION READY** - GPT-4o Direct PDF processing with QA validation complete
- **Architecture Status**: ✅ **SIMPLIFIED** - Traditional PDF extraction methods eliminated, GPT-4o Direct only
- **Recent Enhancement**: Vision processing removed, traditional PDF fallback methods removed (PyPDF2/pdfplumber/OCR)

### Core Architecture Patterns

**Streamlined Processing Architecture**:
- **PDF Processing**: GPT-4o Direct only (traditional methods eliminated)
- **Market Research**: Enhanced source collection with BMAD Framework integration
- **Document Analysis**: Structured extraction with slide references
- **Session Management**: In-memory user sessions for state persistence

**PDF Processing Architecture (Recently Updated)**:
```
OLD: PDF → GPT-4o → [FAIL] → PyPDF2 → [FAIL] → pdfplumber → [FAIL] → OCR
NEW: PDF → GPT-4o Direct → Structured Results (or graceful failure)
```

**Benefits of GPT-4o Direct Only**:
- ✅ **Superior Quality**: Contextual financial data extraction vs raw text
- ✅ **Structured Output**: Slide references and organized data
- ✅ **Simplified Maintenance**: Single processing pipeline
- ✅ **Better Performance**: No fallback chain overhead

**Core Agent System**:
- `MarketDetectionAgent` - Market vertical classification
- `MarketResearchOrchestrator` - Enhanced with BMAD Framework integration
- `enhanced_source_collection.py` - 50+ source collection with quality scoring

**Session Management**: User sessions stored in-memory (`user_sessions` dict) containing document analysis state.

**Production-Only Architecture**: All development uses production APIs directly with cost monitoring.

## Core Components

**Entry Point**: `app.py` - Flask + Slack Bolt application with Railway deployment support

**Handlers Directory**: `/handlers/`
- `ai_analyzer.py` - GPT-4 integration wrapper
- `drive_handler.py` - Google Drive document extraction
- `doc_processor.py` - **UPDATED**: GPT-4o Direct PDF processing only (traditional methods removed)
- `gpt4o_pdf_processor.py` - GPT-4o Direct processor implementation
- `market_research_handler.py` - Slack command orchestration

**Agents Directory**: `/agents/`
- `base_agent.py` - Abstract base class for all agents
- `market_detection.py` - Market vertical classification
- `market_research_orchestrator.py` - Enhanced with BMAD Framework integration
- `progress_tracker.py` - Progress tracking for Slack UX
- `enhanced_source_collection.py` - Progressive 4-phase source collection
- `bmad_framework/` - BMAD Framework Professional Market Intelligence Enhancement

**Utils Directory**: `/utils/`
- `expert_formatter.py` - GPT-4 content synthesis system
- `financial_extractor.py` - Financial data extraction utilities
- `logger.py` - Logging configuration
- `slack_formatter.py` - Slack message formatting
- `web_search.py` - Web search utilities

**Configuration**: `config/settings.py` - Environment-based configuration management

## Available Slack Commands

Core commands for testing and operation:
- `/analyze [google-drive-link]` - Main document analysis using GPT-4o Direct processing
- `/analyze debug` - Session status (very useful for development)
- `/market-research` - Independent market analysis with enhanced source collection
- `/ask [question]` - Q&A on analyzed documents
- `/reset` - Clear user session
- `/health` - System health check

## Common Development Commands

### Setup and Running
```bash
# Initial setup
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Run application (production APIs only)
python app.py
```

### Environment Management
```bash
# Required environment variables:
export OPENAI_API_KEY=sk-...
export TAVILY_API_KEY=tvly-...
export SLACK_BOT_TOKEN=xoxb-...
export SLACK_APP_TOKEN=xapp-...
export SLACK_SIGNING_SECRET=...
export GOOGLE_SERVICE_ACCOUNT_JSON='{"type": "service_account", ...}'

python app.py
```

## Key Development Patterns

### Slack Command Pattern
```python
def handle_command(ack, body, client):
    ack()  # MUST acknowledge immediately
    # Process in background thread
    threading.Thread(target=process_command, args=(body, client)).start()
```

### Error Handling Pattern
```python
try:
    result = risky_operation()
except Exception as e:
    logger.error(f"Operation failed: {e}")
    return format_error_response("operation", str(e))
```

### GPT-4o PDF Processing Pattern
```python
# GPT-4o Direct processing (no fallback)
if self.gpt4o_processor:
    result = self.gpt4o_processor.process_pdf_document(file_path, file_name)
    if result and result.get('content'):
        return result
    else:
        # Graceful failure - no fallback to traditional methods
        return structured_empty_result
```

## Architecture Principles

**Production-First Development**: All development uses production APIs directly with cost monitoring

**Session Persistence**: Commands depend on session state - always check `user_id in user_sessions`

**Transparent Error Handling**: Clear error messages when services fail, no mock data fallbacks

**GPT-4o Direct Processing**: Single processing method for PDFs, traditional methods eliminated

**Quality Over Complexity**: Simplified architecture with superior results

## Environment Variables Required

```bash
# Slack Integration
SLACK_BOT_TOKEN=xoxb-...
SLACK_APP_TOKEN=xapp-...
SLACK_SIGNING_SECRET=...

# AI Services
OPENAI_API_KEY=sk-...
TAVILY_API_KEY=tvly-...

# Google Drive
GOOGLE_SERVICE_ACCOUNT_JSON='{"type": "service_account", ...}'
```

## Development Workflow

1. **Direct production API development** - All development uses real APIs with cost monitoring
2. **Incremental development and testing** - Build features incrementally with real API feedback
3. **Test session persistence** - Use `/analyze debug` frequently
4. **Quality validation** - Test GPT-4o processing with real documents
5. **Commit working increments** - Stability over features

## Recent Changes and Removals

### ❌ **REMOVED COMPONENTS**:
- **Vision Processing Pipeline**: Complete removal of vision integration (handlers/vision_*.py files removed)
- **Vision Dependencies**: handlers/enhanced_session_manager.py removed, stories/ directory with Vision stories deleted
- **Vision Logic**: All Vision processing code removed from handlers/ai_analyzer.py methods
- **Traditional PDF Methods**: PyPDF2, pdfplumber, OCR extraction methods eliminated
- **Fallback Architecture**: Complex fallback chain replaced with GPT-4o Direct only
- **Test Mode Complexity**: Simplified to production-only development
- **Unused Dependencies**: PyPDF2, pdfplumber, pytesseract, pdf2image, Pillow removed from requirements

### ✅ **ENHANCED COMPONENTS**:
- **GPT-4o Direct Processing**: Streamlined PDF processing with superior structured extraction
- **Enhanced Source Collection**: 50+ source collection with quality scoring
- **BMAD Framework Integration**: Professional market intelligence methodologies
- **Simplified Architecture**: Reduced complexity while maintaining functionality
- **QA Validated**: Complete QA validation of GPT-4o processing implementation

## Testing and Validation

**Current Status**: All core functionality QA validated and production-ready

**Testing Commands**:
```bash
# Test document processing
python -c "from handlers.doc_processor import DocumentProcessor; dp = DocumentProcessor(); print('✅ Ready')"

# Test GPT-4o processor
python -c "from handlers.gpt4o_pdf_processor import GPT4oDirectProcessor; print('✅ GPT-4o Available')"

# Run application
python app.py
```

## Common Gotchas

**Session Dependencies**: Many commands require prior `/analyze` execution - always check session state

**Slack Acknowledgment**: All Slack handlers must call `ack()` immediately to prevent timeouts

**GPT-4o Only Processing**: No fallback methods available - ensure GPT-4o processor is properly initialized

**Production APIs**: All development uses real APIs - monitor costs during development

## Railway Deployment

Application auto-deploys from main branch with environment-based configuration. Health check endpoint at `/health` for Railway monitoring.

## Current Development Focus

**System Status**: ✅ **STABLE AND PRODUCTION-READY**

**Key Achievements**:
- GPT-4o Direct PDF processing implementation complete and QA validated
- Traditional extraction methods successfully eliminated
- Architecture simplified without capability loss
- Dependencies cleaned up and optimized
- Vision processing removed (no longer needed)

**Next Evolution**: Focus on market research quality improvements and professional report generation using existing BMAD Framework foundation.