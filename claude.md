# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 🚨 CRITICAL INSTRUCTION

**NO haré NADA** sin que el usuario diga explícitamente el verbo de acción. NO asumiré permisos implícitos.

Ejemplos:
- ✅ "Actualiza el archivo X" → Procedo
- ✅ "Haz commit de los cambios" → Procedo
- ❌ Usuario dice "sí" → NO asumo que puedo hacer commit
- ❌ "Esto se ve bien" → NO asumo que puedo proceder

**Esperaré instrucciones específicas para CUALQUIER acción.**

## Application Architecture

**DataRoom Intelligence Bot** - Single-tenant RAG system for venture capital firms with professional document analysis.

### Current Project Status
- **Phase**: ✅ **GREENFIELD READY** - Clean slate for single-tenant RAG implementation
- **Branch**: `rag-dataroom-v1` - Greenfield development branch
- **System Status**: 🚧 **READY FOR DEVELOPMENT** - PROJECT_BRIEF.md complete, codebase cleaned
- **Architecture Status**: 📋 **DOCUMENTED** - Single-tenant RAG architecture fully specified
- **Recent Change**: Complete greenfield reset, old system backed up in git history

### Core Architecture Patterns

**Single-Tenant RAG Architecture**:
- **PDF Processing**: LlamaParse → Structured Markdown → Smart Chunking → Vector Embeddings
- **Vector Storage**: ChromaDB with channel-based collections (simple isolation)
- **Document Analysis**: RAG retrieval + GPT-4o synthesis with source attribution
- **Channel Management**: Simple channel = dataroom mapping (no multi-tenancy complexity)

**RAG Processing Pipeline**:
```
PDF Documents (Drive) → LlamaParse (PDF→Markdown) → Smart Chunking (Structure-aware)
→ Embeddings (OpenAI) → Vector Storage (ChromaDB) → RAG Retrieval → GPT-4o Analysis
```

**Single-Tenant Benefits**:
- ✅ **Complete Data Isolation**: Each VC firm has dedicated instance
- ✅ **Simplified Architecture**: No client segregation logic needed
- ✅ **Channel-Based Storage**: channel_id directly maps to dataroom
- ✅ **Customization**: Client-specific configurations and prompts

**No Legacy Components**: All agents, handlers, and complex fallback systems removed for greenfield.

**Development Status**: Ready for RAG core implementation following PROJECT_BRIEF.md specification.

## Core Components

**Entry Point**: `app.py` - Flask + Slack Bolt application with Railway deployment support

**Greenfield Directory Structure**: Ready for RAG implementation
- `core/` - RAG functionality (empty, ready for development)
- `models/` - Data models (empty, ready for development)
- `handlers/` - Slack command handlers (empty, ready for development)
- `utils/` - Utility functions (empty, ready for development)
- `tests/` - Test suite (empty, ready for development)

**Configuration**: `config/settings.py` - Environment-based configuration management

**Preserved Infrastructure**:
- Flask + Slack Bolt foundation
- Railway deployment configuration
- Environment management
- Basic project structure

## Planned Slack Commands (From PROJECT_BRIEF.md)

RAG commands to be implemented:
- `/load [google-drive-url] [optional: dataroom-name]` - Load documents into channel's dataroom
- `/current` - Show current channel's dataroom info
- `/list-datarooms` - List all datarooms across channels in workspace
- `/summary` - Generate comprehensive VC analysis of current dataroom
- `/ask [question]` - Interactive Q&A on current dataroom
- `/health` - System health check (preserved)

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
# Required environment variables for RAG system:
export OPENAI_API_KEY=sk-...          # For embeddings and GPT-4o
export LLAMA_CLOUD_API_KEY=llx-...    # For LlamaParse (NEW)
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

### RAG Processing Pattern
```python
# Single-tenant RAG processing
def load_dataroom(channel_id: str, drive_url: str, custom_name: str = None):
    # 1. Parse documents with LlamaParse
    markdown_docs = llamaparse.parse_documents(drive_url)

    # 2. Smart chunking with structure preservation
    chunks = markdown_chunker.chunk(markdown_docs)

    # 3. Generate embeddings
    embeddings = openai_embeddings.embed(chunks)

    # 4. Store in channel-specific collection
    vector_db = ChromaDB(collection=f"channel_{channel_id}")
    vector_db.store(chunks, embeddings)

    return f"📊 Dataroom loaded and ready"
```

## Architecture Principles

**Single-Tenant Design**: One instance per VC firm with complete data isolation

**Channel-Based Storage**: Simple channel_id → dataroom mapping (no multi-tenancy complexity)

**RAG-First Processing**: LlamaParse → Chunking → Embeddings → Vector Storage → Retrieval

**Production APIs Only**: All development uses real APIs with cost monitoring

**Quality Over Complexity**: Simplified architecture following PROJECT_BRIEF.md specification

## Environment Variables Required

```bash
# Slack Integration
SLACK_BOT_TOKEN=xoxb-...
SLACK_APP_TOKEN=xapp-...
SLACK_SIGNING_SECRET=...

# RAG Stack APIs
OPENAI_API_KEY=sk-...              # Embeddings + GPT-4o
LLAMA_CLOUD_API_KEY=llx-...        # LlamaParse

# Google Drive
GOOGLE_SERVICE_ACCOUNT_JSON='{"type": "service_account", ...}'
```

## Development Workflow

1. **RAG-First Development** - Implement core RAG pipeline following PROJECT_BRIEF.md
2. **Single-Tenant Focus** - Simple channel → dataroom mapping, no multi-tenancy
3. **Production APIs Only** - Real LlamaParse + OpenAI + ChromaDB from day one
4. **Explicit Permissions** - NEVER take actions without explicit user verb commands
5. **Test with Real Documents** - Validate RAG quality with actual VC datarooms

## Greenfield Transformation

### 🧹 **REMOVED (Greenfield Reset)**:
- **Entire Legacy System**: All handlers, agents, utils, tests from previous system
- **Complex Multi-Tenancy**: Removed session management, user segregation logic
- **Market Research**: BMAD framework, enhanced source collection, orchestrators
- **Traditional Processing**: GPT-4o direct, fallback chains, vision processing
- **Development Artifacts**: QA gates, test cases, documentation, decision logs

### 🚀 **NEW GREENFIELD FOUNDATION**:
- **Single-Tenant RAG**: Simple, clean architecture per PROJECT_BRIEF.md
- **Channel-Based Storage**: Direct channel → dataroom mapping
- **Professional Pipeline**: LlamaParse → Chunking → Embeddings → ChromaDB → GPT-4o
- **Empty Structure**: Ready for RAG implementation with clear directories
- **Git History**: Previous system preserved as backup in commit history

## Testing and Validation

**Current Status**: 🚧 **GREENFIELD READY** - No tests yet, RAG system to be implemented

**Future Testing Strategy** (from PROJECT_BRIEF.md):
- **Quality Metrics**: >90% data extraction accuracy, <15s response time
- **Test Datarooms**: Simple pitch deck, complex financial model, multi-document cases
- **Evaluation Framework**: Automated quality testing for standard VC queries

**Basic Health Check**:
```bash
# Run application (basic Flask + Slack)
python app.py
```

## Common Gotchas

**Channel Context**: Commands operate on current channel's dataroom - ensure proper channel mapping

**Slack Acknowledgment**: All Slack handlers must call `ack()` immediately to prevent timeouts

**RAG Dependencies**: Ensure LlamaParse + OpenAI + ChromaDB are properly configured

**Production APIs**: All development uses real APIs - monitor costs during development

**Explicit Permissions**: NEVER take actions without explicit user command verbs

## Railway Deployment

Application auto-deploys from main branch with environment-based configuration. Health check endpoint at `/health` for Railway monitoring.

## Current Development Focus

**System Status**: 🚧 **GREENFIELD READY FOR RAG IMPLEMENTATION**

**Completed Preparation**:
- Complete greenfield reset with legacy system backup
- PROJECT_BRIEF.md with detailed single-tenant RAG architecture
- Clean directory structure ready for development
- Infrastructure preserved (Flask, Slack, Railway deployment)
- Critical instruction: explicit permission requirement implemented

**Next Steps**:
1. Wait for user instruction to begin RAG core implementation
2. Follow PROJECT_BRIEF.md specification exactly
3. Implement single-tenant channel-based dataroom system
4. Build professional RAG pipeline: LlamaParse → ChromaDB → GPT-4o