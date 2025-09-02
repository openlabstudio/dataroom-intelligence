# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Application Architecture

**DataRoom Intelligence Bot** - AI-powered data room analysis for venture capital firms using a chain-of-thought agent architecture.

### Current Project Status  
- **Phase**: 2B - Market Research + **GPT-4 Synthesis** (✅ BREAKTHROUGH COMPLETED)
- **Stable Commit**: `d9e1442` + **New GPT-4 Enhancement** - Revolutionary content synthesis system
- **System Status**: ✅ All 5 agents + **GPT-4 Content Synthesizer** - Professional VC analyst output
- **Investment Framework**: ✅ PROCEED/PASS recommendations with risk assessment
- **Output Quality**: 🚀 **REVOLUTIONARY** - Real content analysis from scraped references
- **Demo Status**: ✅ **READY** - Professional investment analysis that exceeds competitor capabilities

### Core Architecture Patterns

**Agent-Based System**: The application uses 5 specialized agents in a chain-of-thought pattern:
- `MarketDetectionAgent` - Market vertical classification (✅ Complete)
- `CompetitiveIntelligenceAgent` - Competitive landscape analysis (✅ Complete)
- `MarketValidationAgent` - TAM/SAM/SOM validation (✅ Complete)  
- `FundingBenchmarkerAgent` - Market funding benchmarks (✅ Complete)
- `CriticalSynthesizerAgent` - Final synthesis and recommendations (✅ Complete)

**Web Search Integration**: Migrated from DuckDuckGo → **Tavily API** (professional web search for AI research)
- Hierarchical search: Solution → Sub-vertical → Vertical  
- Market Taxonomy: 4-level hierarchy implemented
- Sources attribution pipeline with professional sources (MordorIntelligence, StartUs-Insights, etc.)

**GPT-4 Content Synthesis**: Revolutionary breakthrough in output quality
- **Real Content Analysis**: Automatically scrapes 8-10 collected references  
- **Professional VC Analysis**: GPT-4 as senior analyst (Sequoia/a16z level)
- **Investment Decisions**: Clear PROCEED/PASS recommendations with risk levels
- **Natural References**: [1][2][3] integrated seamlessly in professional paragraphs
- **Quality Control**: "Better to say nothing than speculate without data"

**Session Management**: User sessions stored in-memory (`user_sessions` dict) containing document analysis state and market research data.

**TEST MODE Architecture**: Critical dual-mode system for development:
- `TEST_MODE=true` - Mock responses, no API costs
- `TEST_MODE=false` - Real GPT-4/Tavily API calls (costly)

## Common Development Commands

### Setup and Running
```bash
# Initial setup
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Run application (TEST MODE enabled by default)
python app.py
```

### Testing Commands
```bash
# Run individual test files
python test_fase2c.py
python test_market_research_tavily.py

# Test specific functionality
python debug_web_search.py
```

### Environment Management
```bash
# Development (default - no API costs)
export TEST_MODE=true
python app.py

# Production testing (COSTS MONEY!)  
export TEST_MODE=false
export PRODUCTION_MODE=true
python app.py
```

## Critical Development Patterns

### Agent Implementation Template
```python
from .base_agent import BaseAgent

class NewAgent(BaseAgent):
    def __init__(self):
        super().__init__("Agent Name")
    
    def analyze(self, processed_documents, document_summary):
        # ALWAYS check TEST_MODE first
        import os
        if os.getenv('TEST_MODE', 'false').lower() == 'true':
            return self._get_mock_response()
        
        # Real implementation
        return self._real_analysis(processed_documents)
```

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

## Core Components

**Entry Point**: `app.py` - Flask + Slack Bolt application with Railway deployment support

**Agents Directory**: `/agents/`
- `base_agent.py` - Abstract base class for all agents
- `market_research_orchestrator.py` - Coordinates the 5-agent pipeline
- Individual agent implementations

**Handlers Directory**: `/handlers/`
- `ai_analyzer.py` - GPT-4 integration wrapper
- `drive_handler.py` - Google Drive document extraction
- `doc_processor.py` - PDF/Excel/Word processing
- `market_research_handler.py` - Slack command orchestration

**Utils Directory**: `/utils/`
- `expert_formatter.py` - **NEW**: GPT-4 content synthesis system
  - `synthesize_market_intelligence_with_gpt4()` - Core synthesis function
  - `MARKET_SYNTHESIZER_PROMPT` - 50-line expert VC analyst prompt
  - Professional reference collection and web scraping integration

**Configuration**: `config/settings.py` - Environment-based configuration management

## Available Slack Commands

Core commands for testing and operation:
- `/analyze [google-drive-link]` - Main document analysis
- `/analyze debug` - Session status (very useful for development)
- `/market-research` - Independent market analysis
- `/ask [question]` - Q&A on analyzed documents
- `/reset` - Clear user session
- `/health` - System health check

## Key Architectural Principles

**TEST MODE First**: All new features must work in TEST_MODE before real API integration

**Session Persistence**: Commands depend on session state - always check `user_id in user_sessions`

**Transparent Error Handling**: Never return mock data in production - show clear error messages when services fail

**Dual Command Purpose**:
- `/analyze` - What does the startup claim in their documents?
- `/market-research` - What does independent market analysis show?

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

# Deployment Mode
TEST_MODE=true           # Development default
PRODUCTION_MODE=false    # Railway sets to true
```

## Development Workflow

1. **Always start with TEST_MODE=true** - Protects against API costs
2. **Implement mock responses first** - Validates UX before real integration  
3. **Test session persistence** - Use `/analyze debug` frequently
4. **One agent at a time** - Incremental development and testing
5. **Commit working increments** - Stability over features

## Testing Strategy

The project uses individual test files rather than a unified test framework:
- `test_fase2c.py` - Latest phase testing
- `test_market_research_tavily.py` - Web search integration
- `debug_web_search.py` - Search functionality debugging

Run tests manually with `python [test_file.py]` during development.

## Common Gotchas

**Session Dependencies**: Many commands require prior `/analyze` execution - always check session state

**TEST_MODE Bypass**: Never skip TEST_MODE development - production testing is expensive and time-limited

**Slack Acknowledgment**: All Slack handlers must call `ack()` immediately to prevent timeouts

**Agent Chain Dependencies**: Agents depend on previous agent outputs - respect the orchestration order

## Railway Deployment

Application auto-deploys from main branch with environment-based configuration. Health check endpoint at `/health` for Railway monitoring.

## Current Development Priorities

### System Status: ✅ PRODUCTION READY
**All 5 agents complete and functioning with professional VC-analyst level output**

### Available Next Development Paths

**Option A: Enhanced Intelligence System** (3-4 days)
- 12-query expansion for specialized markets  
- Advanced synthesis capabilities
- Deeper analysis for niche sectors

**Option B: PDF Report Generation** (1-2 weeks)  
- Comprehensive reports beyond 4000 char Slack limit
- Professional client-ready documents
- Complete sources and citations

**Option C: GPT-4 Competitive Intelligence Enhancement**
- Replace regex extraction with GPT-4 for 95% accuracy
- Enhanced company name extraction
- Improved competitive landscape precision

## Project References

- **Detailed Task Tracking**: See `TASKS.md` for complete roadmap and progress
- **Stable Rollback Points**: Listed in TASKS.md with specific commits
- **Current Branch**: `phase2b-market-research`