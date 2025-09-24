# 6. Epic 1: RAG Foundation & Core Pipeline

**Expanded Goal:** The objective of this epic is to build the core data ingestion and processing engine. By the end of this epic, we will have a system that can take a Google Drive URL, process the documents within it using a professional-grade parsing and chunking strategy, and store the resulting embeddings in a persistent vector database. This creates the non-negotiable foundation upon which all user-facing analysis features will be built.

## Stories

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
