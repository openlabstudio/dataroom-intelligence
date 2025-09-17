# System Architecture Document

## Overview
We are evolving the `/analyze` command from handling a **single deck PDF** to supporting **full DataRooms** containing multiple documents (decks, excels, PDFs legales, etc.).
The system must generate a **holistic analysis summary** and enable `/ask` queries across all ingested documentation.

## Components

### 1. Ingestion Layer
- Handles upload of multiple file types (PDF, DOCX, XLSX, etc.).
- Normalizes metadata (filename, type, origin).
- Passes raw content to chunking pipeline.

### 2. Chunking & Preprocessing
- Splits documents into semantically meaningful chunks.
- Preserves source references (doc ID, page/slide number).
- Prepares embeddings for storage.

### 3. Vector Database (RAG Store)
- Stores embeddings + metadata for all chunks.
- Recommended tech: **Pinecone** or **Astra DB (with Vec extension)**.
- Enables semantic search across entire DataRoom.

### 4. Analysis Engine
- Runs **initial holistic summary**:
  - Synthesizes across all docs (not isolated per file).
  - Identifies gaps, inconsistencies, diligence flags.
- Powered by GPT-4o or Claude Sonnet.
- Uses retrieved context from RAG when generating structured analysis.

### 5. Query Engine (`/ask`)
- Accepts natural language questions from analysts.
- Uses **RAG retrieval + reasoning** to answer complex queries.
  - Example: "Compare financial plan with technology roadmap".
- Returns answers with references to original docs.

### 6. Slack Integration Layer
- Keeps compatibility with existing Slack output format.
- Routes:
  - `/analyze` → Holistic summary (Slack-ready string).
  - `/ask` → Contextual Q&A results.

## APIs

1. **Ingestion API**
   - `POST /dataroom/upload` → Accepts docs, returns IDs.
2. **Chunking API**
   - Internal: `process_document(doc_id)`.
3. **Vector Store API**
   - `PUT /chunks` → Store embeddings.
   - `GET /search?query=...` → Retrieve relevant chunks.
4. **Analysis API**
   - `POST /analyze` → Generates Slack-ready summary.
5. **Ask API**
   - `POST /ask` → Accepts query, retrieves + reasons, outputs Slack-ready response.

## Technology Recommendations

- **LLM**: GPT-4o for structured analysis, Claude Sonnet for deep reasoning fallback.
- **Vector DB**: Pinecone (managed, scalable) or Astra DB (already integrated).
- **Embeddings**: OpenAI `text-embedding-3-large`.
- **Chunking**: LangChain or LlamaIndex for doc parsing + splitting.
- **Backend**: Python FastAPI (extend current app).
- **Slack Integration**: Reuse existing Bolt SDK setup.

## Risks & Trade-offs

- **Embedding Costs**: Large DataRooms = high token + storage cost. Mitigation: dynamic chunking thresholds.
- **Context Fragility**: LLM might hallucinate if retrieval misses key chunks. Mitigation: hybrid retrieval (semantic + keyword).
- **Performance**: Query latency may grow with large DataRooms. Mitigation: async ingestion + caching.
- **Backward Compatibility**: Slack layer expects formatted output. Ensure legacy `/analyze` contract preserved.

## Evolution Roadmap

1. **Phase 1**: Multi-doc ingestion + chunking + RAG store.
2. **Phase 2**: Holistic `/analyze` using RAG synthesis.
3. **Phase 3**: `/ask` natural language Q&A with multi-doc reasoning.
4. **Phase 4**: Advanced features (cross-doc comparison, risk scoring).
