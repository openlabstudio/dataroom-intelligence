# DataRoom Intelligence Bot v2.0 Product Requirements Document (PRD)

## 1. Goals and Background Context

### 1.1. Goals

*   **G1:** Achieve commercial-grade analysis quality suitable for professional venture capital firms.
*   **G2:** Re-architect the system to implement a professional, state-of-the-art RAG (Retrieval-Augmented Generation) pipeline.
*   **G3:** Solve the root cause of poor quality by preserving document structure (layout, tables, hierarchy) during data ingestion.
*   **G4:** Improve key data extraction accuracy to over 90%.
*   **G5:** Enable a reliable, context-aware Q&A capability.
*   **G6:** Implement a persistent, channel-based data store to manage different datarooms securely and independently.

### 1.2. Background Context

The current system fails because it treats complex, visual PDFs as simple text files. This "flattens" the document, destroying the structural context (tables, columns, headers) that is essential for accurate analysis. The result is low-quality data extraction and unreliable answers, rendering the tool unusable for professional analysis.

This project will correct this by building a proper data engineering pipeline. We will parse the document structure, convert it to a rich format (Markdown), chunk it intelligently, and build a RAG system on top of this high-fidelity data. This moves us from a flawed `PDF → GPT-4o` model to a professional `PDF → Parse → Chunk → RAG → GPT-4o` architecture.

### 1.3. Change Log

| Date | Version | Description | Author |
| :--- | :--- | :--- | :--- |
| 2025-09-22 | 1.1 | Integrated detailed requirements and concrete defaults from Problem Statement v2. | John (PM) |
| 2025-09-22 | 1.0 | Initial PRD draft based on Project Brief v2.0. | John (PM) |

---

## 2. Requirements

### 2.1. Functional

*   **FR1:** The system must provide a `/load` command to ingest documents from a source (e.g., Google Drive URL) and process them into a named, persistent **Dataroom** entity. This process is independent of any specific channel.
*   **FR2:** The system must provide a `/connect` command to link the current Slack channel to an existing, persistent **Dataroom**, making it the active context for analysis in that channel.
*   **FR3:** The system must provide a `/disconnect` command to unlink the current Slack channel from its active **Dataroom**.
*   **FR4:** The parsing pipeline must handle multiple formats with specific normalized outputs: PDF→Markdown; XLSX/CSV→JSON for tables + Markdown summary of text; TXT/DOCX→Markdown. OCR for scanned documents is out of scope for the MVP.
*   **FR5:** The system must intelligently segment structured content into context-aware chunks.
*   **FR6:** The `/summary` command must generate a comprehensive analysis based on the **Dataroom** currently connected to the channel.
*   **FR7:** The `/ask` command must answer questions based on the **Dataroom** currently connected to the channel, with source attribution formatted as `[Document Name, Page X]` and limited to a maximum of 5 citations per response.
*   **FR8:** The system must provide management commands: `/list` (to see all persistent Datarooms) and `/current` (to see the current channel's connection).
*   **FR9:** Re-running `/load` with the name of an existing Dataroom will use a `staging -> swap` mechanism to atomically replace its contents, rolling back on failure.
*   **FR10:** The `/load` command must process all supported document types from the source.
*   **FR11:** The system must provide a `/help` command that lists all available commands and a brief description of their function.
*   **FR12:** The `/load` command must correctly parse Google Drive folder IDs from various URL formats, require the Service Account to have "Reader" permissions, recursively process subfolders up to a depth of **2 levels**, enforce a maximum file size of **25 MB** (configurable), and use retry logic with exponential backoff on downloads.
*   **FR13:** The RAG engine must default to a `parent-child` retrieval strategy (child chunks ~400-800 tokens, parent ~1.5k-2k tokens) and use a re-ranking layer (`CohereRerank`) that retrieves `k=20` candidates and refines them to `k'=5`. `/summary` responses must be streamed. A cache (scope: per-dataroom, TTL: 15 min) for frequent queries must be implemented and invalidated on a successful `/load` swap.
*   **FR14:** The system must enforce cost management quotas, including a per-`/load` limit (50 docs/100MB) and monthly total dataroom load quotas based on the subscription plan (e.g., Free: 3, Team: 100). User warnings must be issued at 80% and 100% usage. These are operational soft guardrails for the MVP.
*   **FR15:** The system must provide a `/delete [dataroom-name]` command that performs a secure wipe of the specified dataroom's data.

### 2.2. Non-Functional

*   **NFR1:** Data extraction accuracy for tabular data must be >90% when measured against the benchmark test suite.
*   **NFR2:** All facts and metrics presented in the `/summary` output must be attributable to their source document.
*   **NFR3:** SLOs for core commands are defined as: `/ask` ≤ 15s (P95); `/summary` ≤ 30s (P95). These are to be measured on a rolling window of N≥200 requests or 14 days, under test conditions of ≤50 documents and ≤100MB per dataroom.
*   **NFR4:** The architecture must enforce strict data isolation between different clients (single-tenant instances).
*   **NFR5:** The system must handle transient failures for all external services (Google Drive downloads, LlamaParse parsing, OpenAI calls, Redis connections) gracefully, using a retry policy with exponential backoff.
*   **NFR6:** Long-running operations (`/load`) must provide idempotent progress updates in Slack (via `thread_ts`) showing specific states: `queued` → `downloading` → `parsing` → `embedding` → `indexing` → `swapping` → `done`|`error`.
*   **NFR7:** **Internationalization:** The system must support multilingual documents and queries (minimum ES/EN), using embedding models and prompts designed for multilingual performance.
*   **NFR8:** **Observability:** The system must collect and expose key performance metrics, including P50/P95 latency, token counts, estimated cost per command, and error/retry ratios. Alerts must be configured for critical thresholds.
*   **NFR9:** **Security & Data Management:** All data must be secured with **encryption in transit (TLS 1.2+)** and **encryption at rest** (for both file and database volumes). The data retention policy is indefinite until a user manually triggers a `/delete` command. A data export procedure must be available.

---

## 3. User Interface Design Goals

*(No significant changes in this section, updated to reflect new commands/states)*

### 3.1. Overall UX Vision

The user experience should be akin to interacting with a competent, fast, and reliable junior analyst via a command-line interface. The bot must be professional, concise, and predictable.

### 3.2. Key Interaction Paradigms

*   **Command-Driven:** All primary actions are initiated via clear and simple Slack slash commands.
*   **Conversational Feedback:** The bot must provide clear, human-readable feedback for all operations, including success, errors, and progress updates.
*   **Data-Dense, Scannable Outputs:** Analytical outputs must be well-structured with Markdown for readability.

### 3.3. Core Screens and Views

*   **Dataroom Load Confirmation:** A message confirming which documents were loaded, including progress updates for each stage.
*   **Dataroom List View (`/list`):** A formatted list showing all available Datarooms.
*   **Current Dataroom View (`/current`):** A status message detailing the Dataroom connected to the current channel, or a message indicating no connection.
*   **Summary Report View (`/summary`):** The structured, multi-section investment analysis report, streamed to the user.
*   **Q&A Response View (`/ask`):** A concise answer to a user's question, with formatted citations (max 5).
*   **Help View (`/help`):** A formatted message that displays all user-facing commands and their purpose.
*   **Delete Confirmation View (`/delete`):** A confirmation prompt before securely wiping a dataroom.
*   **Quota Warning View:** A proactive message when usage approaches 80% or 100% of monthly limits.

---

## 4. Technical Assumptions

*(This section remains as a high-level summary; the Architecture Document is the source of truth for technical details.)*

*   **Architecture:** Monolith, Monorepo.
*   **Testing:** Unit + Integration.
*   **Core Technologies:** LlamaParse, LlamaIndex, ChromaDB, OpenAI, Flask, Slack Bolt, Redis.

---

## 5. Epic List

*   **Epic 1: RAG Foundation & Core Pipeline**
*   **Epic 2: Core Command Implementation & Analysis**
*   **Epic 3: Advanced RAG & Quality of Service**
*   **Epic 4: Production Readiness & Polish**

---

## 6. Epic 1: RAG Foundation & Core Pipeline

**Expanded Goal:** Establish the core data ingestion engine, enabling a document set to be processed from a source URL into a persistent, searchable vector database.

### Stories

**Story 1.1: Project Setup & Core Dependencies**
*   **AC:** `requirements.txt` includes all specified libraries (`llama-parse`, `llama-index`, `chromadb`, `redis`, etc.). New file structure is created. Basic app skeleton runs.

**Story 1.2: Implement LlamaParse Service**
*   **AC:** A parser function in `core/parser.py` handles multiple file types (PDF, XLSX, DOCX, etc.) and returns the specified normalized output (e.g., Markdown, or JSON for tables).

**Story 1.3: Implement Structure-Aware Chunking**
*   **AC:** A chunker function in `core/chunker.py` accepts Markdown and returns a list of structured `Node` objects, preserving tables and lists.

**Story 1.4: Implement Embedding and Vector Storage**
*   **AC:** A `VectorStore` service in `core/vector_store.py` initializes a ChromaDB client, generates embeddings using the specified multilingual model, and saves them to a persistent, named collection.

**Story 1.5: Implement Foundational `/load` Command**
*   **AC:** The `/load` handler orchestrates the full Parse-Chunk-Store pipeline. It handles various Google Drive URL formats, recursively checks subfolders, enforces file size limits, and provides detailed, idempotent progress updates to Slack.

---

## 7. Epic 2: Core Command Implementation & Analysis

**Expanded Goal:** Implement the full suite of user-facing commands to manage, connect to, and analyze datarooms.

### Stories

**Story 2.1: Dataroom Management Service**
*   **AC:** The `DataroomManager` service implements the `staging -> swap` mechanism for atomic replacement and a `/delete` function for secure data wipes.

**Story 2.2: Implement Full `/load` & `/connect` Commands**
*   **AC:** `/load` uses the `DataroomManager` to create persistent entities. `/connect` links a channel to a dataroom. `/current` shows the active connection.

**Story 2.3: Implement `/disconnect` & `/list` Commands**
*   **AC:** `/disconnect` removes a channel-to-dataroom link. `/list` displays all persistent datarooms.

**Story 2.4: Implement Core RAG Retrieval Engine**
*   **AC:** The `RAGEngine` retrieves chunks from the correct ChromaDB collection based on a query.

**Story 2.5: Implement `/ask` Command**
*   **AC:** The `/ask` handler uses the RAG engine and returns an answer with formatted citations (max 5).

**Story 2.6: Implement `/summary` Command**
*   **AC:** The `/summary` handler uses the RAG engine and streams the formatted analysis to Slack.

---

## 8. Epic 3: Advanced RAG & Quality of Service

**Expanded Goal:** Transform the functional prototype into a professional tool by enhancing relevance, reliability, and performance.

### Stories

**Story 3.1: Implement Re-ranking in RAG Pipeline**
*   **AC:** The RAG engine integrates `CohereRerank` to refine search results from `k=20` to `k'=5`.

**Story 3.2: Implement Parent Document Retriever Strategy**
*   **AC:** The chunking process is updated to use a parent-child strategy with the specified chunk sizes (~400-800 child, ~1.5k-2k parent).

**Story 3.3: Comprehensive & User-Friendly Error Handling**
*   **AC:** All command handlers provide specific, actionable error messages for known failure modes (e.g., invalid URL, API key error).

**Story 3.4: Asynchronous Processing for Long-Running Tasks**
*   **AC:** The `/load` command uses a background thread and provides idempotent status updates to Slack for each stage of the pipeline.

---

## 9. Epic 4: Production Readiness & Polish

**Expanded Goal:** Harden the application for production use through rigorous testing, observability, and refinement.

### Stories

**Story 4.1: Create Standardized Test Suite**
*   **AC:** A test suite with at least 5 diverse documents (simple PDF, complex tables, visual-heavy, etc.) is created in `tests/fixtures/`.

**Story 4.2: Implement Structured, Production-Grade Logging**
*   **AC:** All logs are structured (JSON) and include a `trace_id` and `channel_id`.

**Story 4.3: Refine and Polish All User-Facing Messages**
*   **AC:** A full review of all bot responses is conducted to ensure a professional and consistent tone.

**Story 4.4: Final End-to-End Validation**
*   **AC:** The application is deployed to a staging environment and validated against the full test suite and all quality metrics (SLOs, accuracy).
