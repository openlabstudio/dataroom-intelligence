# DataRoom Intelligence Bot - Claude Code Guide

## 🎯 Application Overview

**Purpose:** AI-powered data room analysis for venture capital firms
**Current Status:** Phase 2B - Market Research with Chain of Thought agents
**Branch:** `phase2b-market-research` (stable, working)
**Stable Commit:** `373e18f66d9925505035a19f2829bca38ff42765` (includes full documentation)

### Core Functionality
- **Document Processing:** Extracts and analyzes documents from Google Drive folders
- **AI Analysis:** Uses GPT-4 for comprehensive VC investment analysis
- **Market Research:** Chain of Thought implementation with 5 specialized agents
- **Slack Integration:** Full command-based interaction via Slack bot
- **TEST MODE:** Complete mock functionality to avoid GPT-4 costs during development

## 🚨 CRITICAL: TEST MODE PROTECTION

**NEVER modify or break TEST_MODE functionality!** This is your safety net against API costs.

### How TEST MODE Works
```bash
# Enable TEST MODE (development)
export TEST_MODE=true
python app.py

# Disable TEST MODE (production testing - COSTS MONEY!)
export TEST_MODE=false
python app.py
```

### TEST MODE Behavior
- ✅ **When TEST_MODE=true:**
  - NO GPT-4 API calls
  - Mock responses for all AI features
  - Full workflow testing without costs
  - Instant responses (simulated processing)

- ❌ **When TEST_MODE=false:**
  - REAL GPT-4 API calls ($$$ costs)
  - Actual AI analysis
  - Processing takes 30-60 seconds
  - Only use for final testing

## 📁 Repository Structure

```
dataroom-intelligence/
├── app.py                    # Main application entry point
├── claude.md                 # This guide (Claude Code reference)
├── TASKS.md                  # Task management and tracking
├── agents/                   # Market research agents (Chain of Thought)
│   ├── base_agent.py        # Base class for all agents
│   ├── market_detection.py  # Agent 1: Market vertical detection (✅ WORKING)
│   ├── market_research_orchestrator.py  # Orchestrates all 5 agents
│   └── progress_tracker.py  # Progress tracking (simplified)
├── handlers/                 # Core functionality handlers
│   ├── ai_analyzer.py      # GPT-4 integration for analysis
│   ├── doc_processor.py    # Document extraction (PDF, Excel, etc.)
│   ├── drive_handler.py    # Google Drive integration
│   └── market_research_handler.py  # Market research command handler
├── config/
│   └── settings.py          # Configuration management
├── utils/                   # Utility functions
│   ├── logger.py           # Logging configuration
│   └── slack_formatter.py  # Slack message formatting
├── prompts/                 # GPT-4 prompts
│   └── vc_analysis.py     # VC analysis prompts
└── requirements.txt         # Python dependencies
```

## 🔧 Available Commands

### Working Commands
1. **`/analyze [google-drive-link]`** - Main data room analysis
2. **`/analyze debug`** - Check session status (VERY USEFUL!)
3. **`/market-research`** - Market intelligence analysis (NEW)
4. **`/ask [question]`** - Q&A about analyzed documents
5. **`/scoring`** - VC scoring breakdown
6. **`/memo`** - Investment memo generation
7. **`/gaps`** - Information gaps analysis
8. **`/reset`** - Clear session
9. **`/health`** - System health check

## 🏗️ Current Implementation Status

### ✅ Working Features
- Document extraction from Google Drive
- Basic AI analysis with GPT-4
- Market Detection Agent (Agent 1 of 5)
- TEST MODE with full mock responses
- Simplified progress tracking
- All Slack commands functional
- Complete documentation (claude.md + TASKS.md)

### 🚧 In Development (Phase 2B.1)
- **Agent 2:** Competitive Intelligence (TASK-001)
- **Agent 3:** Market Validation (TASK-002)
- **Agent 4:** Funding Benchmarker (TASK-003)
- **Agent 5:** Critical Synthesizer (TASK-004)

### 📋 Future Features (Phase 2B.2-3)
- Web search integration (DuckDuckGo API) (TASK-005)
- PDF report generation (overcome Slack 4000 char limit) (TASK-006)
- Advanced visualizations

## 💻 Development Workflow

### Initial Setup
```bash
# Clone and switch to working branch
git clone https://github.com/openlabstudio/dataroom-intelligence.git
cd dataroom-intelligence
git checkout phase2b-market-research

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment variables
cp .env.example .env
# Edit .env with your credentials
```

### Required Environment Variables
```bash
# Slack (Required)
SLACK_BOT_TOKEN=xoxb-...
SLACK_APP_TOKEN=xapp-...
SLACK_SIGNING_SECRET=...

# OpenAI (Required for AI features, not for TEST MODE)
OPENAI_API_KEY=sk-...

# Google Drive (Required for document processing)
GOOGLE_SERVICE_ACCOUNT_JSON='{"type": "service_account", ...}'

# Development Settings
TEST_MODE=true  # ALWAYS true during development
DEBUG=true
LOG_LEVEL=INFO
```

### Development Cycle
```bash
# 1. Always start in TEST MODE
export TEST_MODE=true

# 2. Run the application
python app.py

# 3. Test in Slack
# - Use /analyze with a test Google Drive link
# - Use /analyze debug to check session
# - Test /market-research

# 4. Make changes
# - Edit files as needed
# - TEST MODE protects you from API costs

# 5. Test changes
# - Restart app.py
# - Verify nothing breaks in TEST MODE

# 6. Commit when stable
git add .
git commit -m "Description of changes"
git push origin phase2b-market-research
```

## 🎯 Development Guidelines

### 1. NEVER Break TEST MODE
```python
# Always check TEST_MODE first in any new feature
import os
if os.getenv('TEST_MODE', 'false').lower() == 'true':
    # Return mock data
    return get_mock_response()
else:
    # Real implementation
    return real_api_call()
```

### 2. Incremental Development
- One agent at a time
- Test with mock data first
- Integrate gradually
- Commit after each working increment

### 3. Session Management
```python
# Sessions are stored in memory (user_sessions dict)
# Always check session exists before using:
if user_id not in user_sessions:
    # Handle no session case
    return "Please run /analyze first"
```

### 4. Error Handling
```python
# Always wrap risky operations
try:
    # Risky operation
    result = process_something()
except Exception as e:
    logger.error(f"Operation failed: {e}")
    # Return safe fallback
    return format_error_response("operation", str(e))
```

## 🚀 Adding New Agents (Phase 2B.1)

### Template for New Agent
```python
# agents/competitive_intelligence.py
from .base_agent import BaseAgent

class CompetitiveIntelligenceAgent(BaseAgent):
    def __init__(self):
        super().__init__("Competitive Intelligence")
    
    def analyze_competitors(self, market_profile, documents):
        # Check TEST MODE first!
        import os
        if os.getenv('TEST_MODE', 'false').lower() == 'true':
            return self._get_mock_competitive_data()
        
        # Real implementation
        return self._real_analysis(market_profile, documents)
    
    def _get_mock_competitive_data(self):
        return {
            'competitors': ['Competitor A', 'Competitor B'],
            'market_position': 'Strong',
            'confidence': 0.85
        }
```

### Integration Steps
1. Create agent file
2. Add mock implementation
3. Import in orchestrator
4. Test with TEST_MODE=true
5. Verify no breaks
6. Commit
7. Add real implementation later

## 📊 Testing Checklist

### Before ANY Changes
- [ ] TEST_MODE=true is set
- [ ] App runs without errors
- [ ] /analyze works with test data
- [ ] /market-research returns mock response

### After Changes
- [ ] TEST_MODE still works
- [ ] No new GPT-4 calls in TEST MODE
- [ ] All commands still respond
- [ ] Sessions persist correctly
- [ ] Error messages are helpful

### Before Production Testing
- [ ] Code reviewed
- [ ] TEST_MODE works perfectly
- [ ] Ready for API costs
- [ ] Backup of working state

## 🚨 Common Issues & Solutions

### Issue: "No session found"
```bash
# Solution: Check session with debug
/analyze debug
# If no session, run /analyze first
/analyze [google-drive-link]
```

### Issue: "dispatch_failed" in Slack
```python
# Solution: Always acknowledge immediately
def handle_command(ack, body, client):
    ack()  # MUST be first!
    # Then process in background
```

### Issue: TEST MODE not working
```bash
# Check environment variable
echo $TEST_MODE
# Should output: true

# Set correctly
export TEST_MODE=true
# Restart app.py
```

## 🔄 Deployment Process

### Local to Production Workflow
1. **Local Development** (TEST_MODE=true)
   - All features tested with mocks
   - No API costs
   
2. **Local Production Test** (TEST_MODE=false)
   - Quick test with real APIs
   - Verify actual functionality
   - Monitor costs

3. **Push to Branch**
   ```bash
   git add .
   git commit -m "Feature complete and tested"
   git push origin phase2b-market-research
   ```

4. **Merge to Main** (When ready)
   ```bash
   git checkout main
   git merge phase2b-market-research
   git push origin main
   ```

5. **Deploy to Railway**
   - Automatic deployment from main branch
   - Set environment variables in Railway dashboard
   - TEST_MODE=false in production

## 📝 Product Owner Guidelines

As Product Owner, you should:

1. **Always request changes incrementally**
   - "Add mock response for Agent 2"
   - "Test that it works"
   - "Now add real implementation"

2. **Verify TEST MODE first**
   - "Show me TEST MODE is working"
   - "Confirm no GPT-4 calls in test mode"

3. **Request safety checks**
   - "Add error handling for X"
   - "What happens if Y fails?"

4. **Review before production**
   - "Show me the mock response"
   - "Explain the error cases"
   - "What are the API costs?"

## 💡 Best Practices

1. **Always develop in TEST MODE**
2. **Commit working increments frequently**
3. **Document any new environment variables**
4. **Keep backward compatibility**
5. **Add logging for debugging**
6. **Handle errors gracefully**
7. **Test session persistence**
8. **Verify Slack formatting**

## 🔗 Important Links

- **Repository:** https://github.com/openlabstudio/dataroom-intelligence
- **Current Branch:** phase2b-market-research
- **Task Tracking:** See TASKS.md for detailed task management
- **Railway Dashboard:** [Configure in Railway]
- **Slack App:** [Configure in Slack API]

## 🆘 Emergency Procedures

### If TEST MODE Breaks
```bash
# Revert to stable commit with documentation
git checkout 373e18f66d9925505035a19f2829bca38ff42765

# Or if you need minimal functional version
git checkout 31e7fba31bd49b5ad806e6102c090d4beb7e7f18
```

### If Production Has Issues
```bash
# Quick disable in Railway
# Set environment variable: MAINTENANCE_MODE=true
# This should disable all API calls
```

## 📌 Current Focus

**Phase 2B.1: Chain of Thought Implementation**
- Next: Implement Agent 2 (Competitive Intelligence) - See TASK-001 in TASKS.md
- Keep it simple, mock first
- Test thoroughly
- One agent at a time

**Active Tasks:** Check TASKS.md for current priorities and progress

Remember: **Stability > Features**. A working TEST MODE is more important than new features!
