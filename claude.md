# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Application Architecture

**DataRoom Intelligence Bot** - AI-powered data room analysis for venture capital firms using a chain-of-thought agent architecture.

### Current Project Status
- **Phase**: 3 - **DEEP MARKET ANALYSIS RECONSTRUCTION** (🚧 CRITICAL SYSTEM OVERHAUL)
- **Branch**: `phase3-deep-market-analysis` - Complete architecture redesign in progress
- **System Status**: ⚠️ **CRITICAL FAILURE** - Current `/market-research` produces toy-level output unsuitable for professional use
- **Quality Reality**: Current system generates "deplorable quality" analysis described as unpresentable to VC analysts
- **Architecture Problem**: Previous "optimization" eliminated essential intelligence processing, resulting in superficial analysis
- **Development Priority**: 🚨 **URGENT RECONSTRUCTION** - Building professional-grade market intelligence system from new foundation

### Core Architecture Patterns

**Streamlined Agent System**: Optimized architecture with only essential components:
- `MarketDetectionAgent` - Market vertical classification (✅ Essential - kept)
- `MarketResearchOrchestrator` - Direct web search coordination (✅ Optimized)
- **GPT-4 Synthesis** - Single intelligent analysis replacing multiple agents (✅ Revolutionary)

**ELIMINATED LEGACY AGENTS** (194KB code garbage removed):
- ❌ `CompetitiveIntelligenceAgent` - Replaced by direct web search + GPT-4 synthesis
- ❌ `MarketValidationAgent` - Replaced by direct web search + GPT-4 synthesis
- ❌ `FundingBenchmarkerAgent` - Replaced by direct web search + GPT-4 synthesis
- ❌ `CriticalSynthesizerAgent` - Replaced by unified GPT-4 synthesis

**Direct Web Search Integration**: **Tavily API** with zero intermediate processing:
- Direct search execution: Solution → Sub-vertical → Vertical (no complex agents)
- 24 high-quality sources collected efficiently
- Zero redundant GPT-4 processing during search phase
- Professional sources maintained (MordorIntelligence, StartUs-Insights, etc.)

**GPT-4 Synthesis Current Reality**: The simplified approach has critical flaws:
- **Quality Failure**: Current output is "toy-like" and unpresentable for professional VC use
- **Source Utilization**: Only 2-4 meaningful sources vs required 30+ for professional analysis
- **Analysis Depth**: Produces 3-4 superficial insights vs required 8-10 actionable insights
- **Professional Gap**: Output quality fails McKinsey/BCG consultant standards required by users
- **Strategic Impact**: System considered a "critical failure" requiring complete reconstruction

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
# Note: Previous test files have been removed during Phase 3 preparation
# Current development uses direct system testing with TEST_MODE=false

# Test market research in development mode
export TEST_MODE=true
python app.py

# Production testing (Phase 3 development - COSTS MONEY!)
export TEST_MODE=false
python app.py
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

### Gemini CLI for Large Codebase Analysis

When analyzing large codebases or multiple files that might exceed context limits, use the Gemini CLI with its massive context window:

**Basic Usage:**
```bash
# Single file analysis
gemini -p "@src/main.py Explain this file's purpose and structure"

# Multiple files
gemini -p "@package.json @src/index.js Analyze the dependencies used in the code"

# Entire directory
gemini -p "@src/ Summarize the architecture of this codebase"

# Multiple directories
gemini -p "@src/ @tests/ Analyze test coverage for the source code"

# Current directory and subdirectories
gemini -p "@./ Give me an overview of this entire project"

# Or use --all_files flag
gemini --all_files -p "Analyze the project structure and dependencies"
```

**Implementation Verification Examples:**
```bash
# Check if a feature is implemented
gemini -p "@src/ @lib/ Has dark mode been implemented in this codebase? Show me the relevant files and functions"

# Verify authentication implementation
gemini -p "@src/ @middleware/ Is JWT authentication implemented? List all auth-related endpoints and middleware"

# Check for specific patterns
gemini -p "@src/ Are there any React hooks that handle WebSocket connections? List them with file paths"

# Verify error handling
gemini -p "@src/ @api/ Is proper error handling implemented for all API endpoints? Show examples of try-catch blocks"

# Check for rate limiting
gemini -p "@backend/ @middleware/ Is rate limiting implemented for the API? Show the implementation details"

# Verify caching strategy
gemini -p "@src/ @lib/ @services/ Is Redis caching implemented? List all cache-related functions and their usage"

# Check for specific security measures
gemini -p "@src/ @api/ Are SQL injection protections implemented? Show how user inputs are sanitized"

# Verify test coverage for features
gemini -p "@src/payment/ @tests/ Is the payment processing module fully tested? List all test cases"
```

**When to Use Gemini CLI:**
- Analyzing entire codebases or large directories
- Comparing multiple large files
- Need to understand project-wide patterns or architecture
- Current context window is insufficient for the task
- Working with files totaling more than 100KB
- Verifying if specific features, patterns, or security measures are implemented
- Checking for the presence of certain coding patterns across the entire codebase

**Important Notes:**
- Paths in @ syntax are relative to your current working directory when invoking gemini
- The CLI will include file contents directly in the context
- No need for --yolo flag for read-only analysis
- Gemini's context window can handle entire codebases that would overflow Claude's context
- When checking implementations, be specific about what you're looking for to get accurate results

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

## Architecture Optimization (September 2025)

### ⚠️ **CRITICAL ARCHITECTURE FAILURE: Phase 2C "Optimization" Analysis**

**Problem Identified**: The Phase 2C "optimization" was a **strategic error**:
- Eliminated essential intelligence processing that was actually providing value
- Resulted in "toy-like" output quality unacceptable for professional VC use
- Cost savings came at the expense of analysis quality - a false economy
- Current system produces superficial analysis described as "deplorable quality"

**Architecture Evolution Required**: **Phase 3 Professional Market Intelligence System**
```
FAILED PHASE 2C ARCHITECTURE:
MarketDetection → Direct WebSearch → Single GPT-4 Synthesis (insufficient processing)

NEW PHASE 3 ARCHITECTURE (in development):
MarketDetection → Multi-Source Intelligence (50+ sources) → BMAD Framework Analysis → Professional Report Generation (10-20 pages) → Intelligent Summarization
```

**Phase 3 Goals**:
- 🎯 **Consultant-Quality Output** (McKinsey/BCG standard)
- 📊 **8-10 actionable insights** (vs current 3-4 superficial ones)
- 📚 **30+ synthesized sources** (vs current 4-6)
- 📝 **10-20 page professional reports** (currently missing entirely)
- ⚖️ **Investment-grade recommendations** with confidence scoring

**Critical Lesson**: Efficiency without quality is worthless for professional applications. Phase 3 prioritizes analysis quality over cost optimization.

## Core Components

**Entry Point**: `app.py` - Flask + Slack Bolt application with Railway deployment support

**Agents Directory**: `/agents/` (STREAMLINED)
- `base_agent.py` - Abstract base class for all agents
- `market_detection.py` - Market vertical classification (Essential)
- `market_research_orchestrator.py` - Direct web search + GPT-4 synthesis coordination (Optimized)
- `progress_tracker.py` - Progress tracking for Slack UX

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

## Phase 3 Testing Strategy

**Production-Only Testing Approach**: Phase 3 development uses real system testing exclusively:
- **No TEST_MODE development** - All testing done with `TEST_MODE=false`
- **Direct system validation** - Test quality improvements on actual market research queries
- **Professional quality benchmarking** - Compare output against McKinsey/BCG report standards
- **User feedback integration** - Validate with real VC analyst requirements

**Testing Commands**:
```bash
# Phase 3 development testing (COSTS API CREDITS)
export TEST_MODE=false
python app.py

# Test specific market research scenarios
# Use Slack commands: /market-research [sector/startup]
```

**Quality Gates**: Every output must pass professional quality thresholds before user delivery.

## Common Gotchas

**Session Dependencies**: Many commands require prior `/analyze` execution - always check session state

**TEST_MODE Bypass**: Never skip TEST_MODE development - production testing is expensive and time-limited

**Slack Acknowledgment**: All Slack handlers must call `ack()` immediately to prevent timeouts

**Agent Chain Dependencies**: Agents depend on previous agent outputs - respect the orchestration order

## Railway Deployment

Application auto-deploys from main branch with environment-based configuration. Health check endpoint at `/health` for Railway monitoring.

## Phase 3 Development Priorities

### System Status: 🚧 **CRITICAL RECONSTRUCTION IN PROGRESS**
**Current `/market-research` is critically flawed and requires complete rebuild**

### Phase 3 Objectives (3 weeks timeline)

**Primary Objective: Professional Market Intelligence System**
- Build new Single Process Architecture with BMAD Framework integration
- Generate 10-20 page professional reports (McKinsey/BCG quality standard)
- Achieve 8-10 actionable insights per analysis vs current 3-4 superficial ones
- Synthesize 30+ sources vs current 4-6 meaningful sources
- Implement investment-grade recommendations with confidence scoring

**Technical Architecture Changes**:
- Replace failed direct synthesis approach with structured intelligence processing
- Integrate BMAD Framework methodologies (8 research types, expert personas)
- Implement professional report generation system
- Add intelligent summarization for Slack delivery
- Build quality assurance gates to prevent low-quality output

**Development Approach**:
- **No TEST_MODE development** - Build and test on real system only
- Parallel development alongside existing system (feature flag approach)
- Focus on quality over cost optimization
- 3-week sprint to functional prototype

## Project References

- **Project Brief**: `docs/Project-Brief-Deep-market-research.md` - Core requirements and strategy
- **Phase 3 Specifications**: `docs/DRI_Phase3_Advanced_Intelligence_high-level-Specs.md` - Technical requirements
- **Current Branch**: `phase3-deep-market-analysis` - Active development branch
- **Baseline Branch**: `phase1-2-MVP-fixes` - Stable codebase with implemented fixes
