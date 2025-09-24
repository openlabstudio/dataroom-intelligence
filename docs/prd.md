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
| 2025-09-22 | 1.0 | Initial PRD draft based on Project Brief v2.0. | John (PM) |

---

## 2. Requirements

### 2.1. Functional

*   **FR1:** The system must provide a `/load` command to ingest documents from a source (e.g., Google Drive URL) and process them into a named, persistent **Dataroom** entity. This process is independent of any specific channel.
*   **FR2:** The system must provide a `/connect` command to link the current Slack channel to an existing, persistent **Dataroom**, making it the active context for analysis in that channel.
*   **FR3:** The system must provide a `/disconnect` command to unlink the current Slack channel from its active **Dataroom**.
*   **FR4:** The parsing pipeline must handle various document formats (PDF, Excel, TXT, etc.).
*   **FR5:** The system must intelligently segment structured content into context-aware chunks.
*   **FR6:** The `/summary` command must generate a comprehensive analysis based on the **Dataroom** currently connected to the channel.
*   **FR7:** The `/ask` command must answer questions based on the **Dataroom** currently connected to the channel, with source attribution.
*   **FR8:** The system must provide management commands: `/list` (to see all persistent Datarooms) and `/current` (to see the current channel's connection).
*   **FR9:** Re-running `/load` with the name of an existing Dataroom will completely replace its contents.
*   **FR10:** The `/load` command must process all supported document types from the source.
*   **FR11:** The system must provide a `/help` command that lists all available commands and a brief description of their function.

### 2.2. Non-Functional

*   **NFR1:** Data extraction accuracy for key financial metrics must exceed 90%.
*   **NFR2:** All facts and metrics presented in the `/summary` output must be attributable to their source document.
*   **NFR3:** The end-to-end response time for `/ask` should be less than 15 seconds. The response time for `/summary` should be less than 30 seconds.
*   **NFR4:** The architecture must enforce strict data isolation between different clients (single-tenant instances).
*   **NFR5:** The system must handle transient API failures (e.g., LlamaParse, OpenAI) and infrastructure connection failures (e.g., Redis) gracefully, using retry logic where appropriate.
*   **NFR6:** The system must provide feedback to the user on the progress of long-running operations (e.g., `/load`, `/summary`), indicating the current status or expected waiting time.

---

## 3. User Interface Design Goals

### 3.1. Overall UX Vision

The user experience should be akin to interacting with a competent, fast, and reliable junior analyst via a command-line interface. The bot must be professional, concise, and predictable. All interactions should inspire confidence in the data and the analysis provided.

### 3.2. Key Interaction Paradigms

*   **Command-Driven:** All primary actions are initiated via clear and simple Slack slash commands (e.g., `/load`, `/connect`, `/summary`, `/ask`).
*   **Conversational Feedback:** The bot must provide clear, human-readable feedback for all operations, including success messages, error messages, and progress updates for long-running tasks as per NFR6.
*   **Data-Dense, Scannable Outputs:** Analytical outputs (`/summary`, `/ask`) must be well-structured, using Markdown formatting (bolding, bullets, etc.) to be easily scannable and digestible within the Slack interface.

### 3.3. Core Screens and Views

*   **Dataroom Load Confirmation:** A message confirming which documents were loaded.
*   **Dataroom List View (`/list`):** A formatted list showing all available Datarooms.
*   **Current Dataroom View (`/current`):** A status message detailing the Dataroom connected to the current channel.
*   **Summary Report View (`/summary`):** The structured, multi-section investment analysis report.
*   **Q&A Response View (`/ask`):** A concise answer to a user's question, with source attribution.
*   **Help View (`/help`):** A formatted message that displays all user-facing commands and their purpose.

### 3.4. Accessibility: Standard Slack Accessibility

As the UI is embedded within Slack, we will adhere to the accessibility standards provided by the Slack platform itself.

### 3.5. Branding

No custom branding is required for the MVP.

### 3.6. Target Device and Platforms: Slack Client

The interface must be fully functional and readable on all official Slack clients (Web Responsive, Desktop, and Mobile).

---

## 4. Technical Assumptions

### 4.1. Repository Structure: Monorepo

*   **Rationale:** For a greenfield project of this scope, a single repository (monorepo) is the simplest and most efficient approach. It simplifies dependency management, atomic commits, and initial CI/CD setup.

### 4.2. Service Architecture: Monolith

*   **Rationale:** The application will be built as a single, cohesive service (a monolith). This is the most pragmatic choice for an MVP, prioritizing development speed and ease of deployment over the complexity of a microservices or serverless architecture.

### 4.3. Testing Requirements: Unit + Integration

*   **Rationale:** The project requires a balance of speed and reliability. We will mandate comprehensive unit tests for individual functions and components, supplemented by integration tests to ensure the core RAG pipeline (Parse -> Chunk -> Retrieve -> Generate) works correctly end-to-end.

### 4.4. Additional Technical Assumptions and Requests

*   **PDF Parsing:** The system will use the **LlamaParse API** as its primary document parsing service.
*   **RAG Framework:** The core RAG pipeline will be orchestrated using the **LlamaIndex** framework.
*   **Vector Database:** **ChromaDB** will be used for local development and initial deployment due to its simplicity. The architecture should allow for a future migration to a managed service like Pinecone.
*   **LLM & Embeddings:** The system will use **OpenAI** models, specifically `gpt-4o` for synthesis and `text-embedding-3-small` for embeddings.
*   **Backend:** The existing **Flask + Slack Bolt** backend will be maintained and built upon.

---

## 5. Epic List

*   **Epic 1: RAG Foundation & Core Pipeline**
    *   **Goal:** Establish the foundational RAG pipeline by integrating LlamaParse, a structure-aware chunker, and ChromaDB to successfully load a dataroom and make it searchable.

*   **Epic 2: Core Command Implementation & Analysis**
    *   **Goal:** Implement the primary user-facing Slack commands (`/load`, `/connect`, `/disconnect`, `/list`, `/current`, `/summary`, `/ask`) to enable a complete, end-to-end analysis workflow.

*   **Epic 3: Advanced RAG & Quality of Service**
    *   **Goal:** Enhance the quality and reliability of the RAG engine by implementing advanced features like re-ranking and improving error handling and performance.

*   **Epic 4: Production Readiness & Polish**
    *   **Goal:** Ensure the application is commercially viable by conducting comprehensive testing with real-world datarooms, adding robust logging, and polishing the overall user experience.

---

## 6. Epic 1: RAG Foundation & Core Pipeline

**Expanded Goal:** The objective of this epic is to build the core data ingestion and processing engine. By the end of this epic, we will have a system that can take a Google Drive URL, process the documents within it using a professional-grade parsing and chunking strategy, and store the resulting embeddings in a persistent vector database. This creates the non-negotiable foundation upon which all user-facing analysis features will be built.

### Stories

**Story 1.1: Project Setup & Core Dependencies**
*   **As a** developer, **I want** a new project structure with all required dependencies and environment variables defined, **so that** I can begin building the RAG pipeline on a clean and correct foundation.
*   **Acceptance Criteria:**
    1.  A `requirements.txt` file is created containing `llama-parse`, `llama-index`, `chromadb`, `openai`, `flask`, `slack-bolt`, and `pydantic`.
    2.  A new, clean file structure is created (e.g., `core/`, `handlers/`, `models/`) as outlined in the Project Brief.
    3.  A basic `app.py` skeleton exists that initializes the Slack and Flask apps without errors.

**Story 1.2: Implement LlamaParse Service**
*   **As a** system, **I want** to process a document file using the LlamaParse API, **so that** its content is converted into a structured Markdown string.
*   **Acceptance Criteria:**
    1.  A function within `core/parser.py` accepts a file path.
    2.  It correctly calls the LlamaParse API and returns the resulting Markdown content as a string.
    3.  It properly handles API key configuration and logs errors on failure.

**Story 1.3: Implement Structure-Aware Chunking**
*   **As a** system, **I want** to segment a Markdown string using a `MarkdownElementNodeParser`, **so that** the document's structure (e.g., tables) is preserved within the resulting chunks.
*   **Acceptance Criteria:**
    1.  A function within `core/chunker.py` accepts a Markdown string.
    2.  It returns a list of structured `Node` objects, ready for embedding.

**Story 1.4: Implement Embedding and Vector Storage**
*   **As a** system, **I want** to generate vector embeddings for text chunks and store them in a persistent ChromaDB collection, **so that** they can be retrieved later for analysis.
*   **Acceptance Criteria:**
    1.  A class or functions within `core/vector_store.py` can initialize a ChromaDB client with a local on-disk directory.
    2.  It can take a list of chunks and a unique collection name (e.g., `dataroom-xyz`), generate embeddings, and save them to the specified collection.
    3.  The data must persist between application restarts.

**Story 1.5: Implement Foundational `/load` Command**
*   **As an** analyst, **I want** a basic `/load` command that accepts a URL and a name, **so that** I can trigger the complete Parse-Chunk-Store pipeline for a new Dataroom.
*   **Acceptance Criteria:**
    1.  A new `/load` command handler is created.
    2.  It successfully orchestrates the calls to the services created in stories 1.2, 1.3, and 1.4.
    3.  It provides a simple "Success" or "Failure" message in Slack upon completion.
    4.  The resulting vector store is saved on disk under a name derived from the command input.

---

## 7. Epic 2: Core Command Implementation & Analysis

**Expanded Goal:** This epic brings the application to life for the end-user. We will implement the full suite of Slack commands that allow an analyst to load, connect to, manage, and analyze datarooms. By the end of this epic, the user will be able to ask specific questions and receive a full AI-generated summary, realizing the core value proposition of the product.

### Stories

**Story 2.1: Dataroom Management Service**
*   **As a** developer, **I want** a central `DataroomManager` service that creates, tracks, and retrieves the persistent Dataroom entities, **so that** we can manage the lifecycle of all processed datarooms in the workspace.
*   **Acceptance Criteria:**
    1.  A `DataroomManager` class is created.
    2.  It can create a new Dataroom entity, storing its metadata (name, creation date, vector collection name) in a persistent format (e.g., a simple JSON index file).
    3.  It can list all managed Datarooms.
    4.  It can associate a Slack `channel_id` with a Dataroom ID, and remove the association.

**Story 2.2: Implement Full `/load` & `/connect` Commands**
*   **As an** analyst, **I want** to use `/load` to create a persistent Dataroom and `/connect` to link it to my current channel, **so that** I can set up my workspace for analysis.
*   **Acceptance Criteria:**
    1.  The `/load` command from Epic 1 is updated to use the `DataroomManager` to create the persistent Dataroom entity.
    2.  A new `/connect [dataroom-name]` command is implemented that uses the `DataroomManager` to link the current channel to the specified Dataroom.
    3.  The `/current` command is implemented to display the name of the Dataroom connected to the current channel.

**Story 2.3: Implement `/disconnect` & `/list` Commands**
*   **As an** analyst, **I want** to `/disconnect` a Dataroom from my channel and `/list` all available Datarooms, **so that** I can easily manage my workspace and discover available data.
*   **Acceptance Criteria:**
    1.  A `/disconnect` command is implemented that removes the channel-to-dataroom association for the current channel.
    2.  A `/list` command is implemented that displays a formatted list of all persistent Datarooms managed by the `DataroomManager`.

**Story 2.4: Implement Core RAG Retrieval Engine**
*   **As a** system, **I want** to retrieve relevant text chunks from a Dataroom's vector store based on a user's query, **so that** I can provide context for AI analysis.
*   **Acceptance Criteria:**
    1.  A function in `core/rag_engine.py` accepts a query string and a `dataroom_id`.
    2.  It correctly identifies the ChromaDB collection associated with the `dataroom_id`.
    3.  It performs a semantic search and returns the top 'k' most relevant text chunks.

**Story 2.5: Implement `/ask` Command**
*   **As an** analyst, **I want** to use the `/ask` command to get a direct answer to a specific question about the connected Dataroom, **so that** I can quickly find key information.
*   **Acceptance Criteria:**
    1.  The `/ask` command handler is created.
    2.  It uses the RAG retrieval engine (Story 2.4) to get context.
    3.  It passes the context and the user's question to the LLM and posts the answer back to Slack.
    4.  The response includes source attribution, referencing the original document.

**Story 2.6: Implement `/summary` Command**
*   **As an** analyst, **I want** to use the `/summary` command to receive a full, narrative-style investment analysis of the connected Dataroom, **so that** I can get a comprehensive overview quickly.
*   **Acceptance Criteria:**
    1.  The `/summary` command handler is created.
    2.  It retrieves a large amount of context from the RAG engine.
    3.  It uses a specialized prompt to instruct the LLM to generate a full, structured analysis.
    4.  The formatted analysis is posted back to the Slack channel.

---

## 8. Epic 3: Advanced RAG & Quality of Service

**Expanded Goal:** With core functionality in place, this epic transforms the application from a functional prototype into a professional tool. We will implement advanced RAG techniques to improve the relevance of retrieved context, leading to more accurate AI responses. We will also add robust error handling and performance optimizations to ensure the system is reliable and feels responsive.

### Stories

**Story 3.1: Implement Re-ranking in RAG Pipeline**
*   **As a** system, **I want** to re-rank the initial list of retrieved document chunks using a more powerful model, **so that** the most relevant context is prioritized and sent to the final LLM, improving answer quality.
*   **Acceptance Criteria:**
    1.  The RAG retrieval process is updated to fetch a larger set of initial candidates (e.g., top 20).
    2.  A second-stage re-ranking model (e.g., a LlamaIndex `CohereRerank` or cross-encoder) is integrated.
    3.  The re-ranker re-orders the candidates based on relevance to the specific query.
    4.  The final, top 'k' re-ranked chunks are passed to the LLM for synthesis.

**Story 3.2: Implement Parent Document Retriever Strategy**
*   **As a** system, **I want** to retrieve larger, context-rich parent chunks after searching on smaller, more precise child chunks, **so that** the LLM has both the precision of a targeted search and the broad context needed for high-quality reasoning.
*   **Acceptance Criteria:**
    1.  The chunking strategy is updated to create parent chunks (e.g., full sections or pages) and smaller child chunks derived from them.
    2.  The retrieval engine is configured to search for the most relevant *child* chunks.
    3.  Upon finding the best child chunks, the engine retrieves their corresponding *parent* chunks to be sent to the LLM.

**Story 3.3: Comprehensive & User-Friendly Error Handling**
*   **As an** analyst, **I want** to receive clear, helpful error messages when an operation fails, **so that** I understand what went wrong and what I can do about it.
*   **Acceptance Criteria:**
    1.  All primary command handlers (`/load`, `/connect`, etc.) have comprehensive error handling.
    2.  Specific, anticipated errors (e.g., "Dataroom not found," "Invalid Google Drive URL," "LlamaParse API key not set") result in user-friendly, actionable error messages posted to Slack.
    3.  Generic or unexpected errors are caught and result in a message asking the user to report the issue, along with a unique error ID for logging.

**Story 3.4: Asynchronous Processing for Long-Running Tasks**
*   **As an** analyst, **I want** long-running commands like `/load` to run in the background and provide status updates, **so that** the app feels responsive and I'm kept informed of the progress.
*   **Acceptance Criteria:**
    1.  The `/load` command handler immediately posts an initial "Processing..." message to Slack.
    2.  The actual data processing (parsing, chunking, embedding) is executed in a background thread.
    3.  The handler posts periodic updates to the initial Slack message (e.g., "Step 1/3: Parsing documents...", "Step 2/3: Storing data...").
    4.  A final "Success" or "Failure" message is posted upon completion.

---

## 9. Epic 4: Production Readiness & Polish

**Expanded Goal:** This final epic is focused on hardening the application for production use. We will move beyond functional correctness and concentrate on reliability, observability, and creating a polished user experience. This includes rigorous testing against a suite of diverse documents, implementing structured logging for easier debugging, and refining all user-facing messages for maximum clarity.

### Stories

**Story 4.1: Create Standardized Test Suite**
*   **As a** developer, **I want** a standardized test suite of diverse and challenging documents, **so that** I can rigorously and consistently test the RAG pipeline's performance and quality.
*   **Acceptance Criteria:**
    1.  A dedicated test folder is created in the repository.
    2.  The folder contains at least 5 distinct test cases as specified in the Project Brief: a simple deck, a document with complex tables, a visual-heavy deck, a multi-document dataroom, and a poor-quality scanned PDF.

**Story 4.2: Implement Structured, Production-Grade Logging**
*   **As a** developer, **I want** structured, context-rich logging throughout the application, **so that** I can easily trace a user request from start to finish and quickly debug issues in production.
*   **Acceptance Criteria:**
    1.  The logging system is configured to output in a structured format (e.g., JSON).
    2.  All log entries related to a specific user request contain a unique `trace_id` and the relevant `channel_id`.
    3.  Sensitive information (e.g., API keys) is properly redacted from all logs.

**Story 4.3: Refine and Polish All User-Facing Messages**
*   **As an** analyst, **I want** all bot messages to be professional, clear, and consistently formatted, **so that** the application feels polished and trustworthy.
*   **Acceptance Criteria:**
    1.  A full review of all bot responses (for success, errors, help, status, etc.) is conducted.
    2.  Text is edited for clarity, professional tone, and consistency.
    3.  The use of Markdown formatting and emojis is standardized across all messages to create a cohesive user experience.

**Story 4.4: Final End-to-End Validation**
*   **As a** product owner, **I want** to perform final acceptance testing on the complete application against the full test suite, **so that** I can formally sign off on the MVP's quality and commercial viability.
*   **Acceptance Criteria:**
    1.  The application is deployed to a staging environment that mirrors production.
    2.  All commands are tested against all documents in the standardized test suite.
    3.  The outputs are validated against the quality metrics defined in the Project Brief (e.g., >90% data extraction accuracy, response times).
    4.  The final `gemini`-level quality bar is met consistently.
