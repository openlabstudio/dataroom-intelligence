# 5. Components

The application will be organized into the following logical components, primarily separated into a `handlers` layer for Slack interactions and a `core` layer for business logic.

## 5.1. Slack Command Handlers

*   **Responsibility:** This layer is the entry point for all user interactions. Its sole responsibility is to parse incoming Slack commands, validate inputs, call the appropriate core services, and format the results for posting back to Slack. It contains no business logic.
*   **Key Interfaces:** `handle_load()`, `handle_connect()`, `handle_ask()`, `handle_summary()`, etc.
*   **Dependencies:** `DataroomManager`, `RAGEngine`.
*   **Location:** `handlers/`

## 5.2. DataroomManager

*   **Responsibility:** To be the central service for managing the lifecycle of Dataroom entities and their connections to Slack channels. It handles the creation, persistence, and retrieval of all Dataroom metadata.
*   **Key Interfaces:** `create_dataroom()`, `get_dataroom_by_name()`, `list_all_datarooms()`, `connect_channel_to_dataroom()`, `get_active_dataroom_for_channel()`.
*   **Dependencies:** `RAGEngine` (to trigger processing), `VectorStore` (to manage collections).
*   **Location:** `core/dataroom_manager.py`

## 5.3. ParsingService

*   **Responsibility:** To abstract all interactions with the external document parsing API (LlamaParse). This component's job is to take a file path and return structured Markdown.
*   **Key Interfaces:** `parse_document(file_path)`.
*   **Dependencies:** LlamaParse API Client.
*   **Location:** `core/parser.py`

## 5.4. RAGEngine

*   **Responsibility:** To orchestrate the entire RAG pipeline for a given set of documents. This includes chunking the parsed Markdown, generating embeddings, storing them in the vector store, and handling the retrieval/synthesis process for answering questions.
*   **Key Interfaces:** `process_and_store_documents()`, `query()`, `get_summary()`.
*   **Dependencies:** `ParsingService`, `VectorStore`, OpenAI API Client.
*   **Location:** `core/rag_engine.py`

## 5.5. VectorStore

*   **Responsibility:** To provide a simple, abstract interface for interacting with the vector database (ChromaDB). This isolates the rest of the application from the specific implementation details of the DB.
*   **Key Interfaces:** `create_collection()`, `add_nodes()`, `semantic_search()`.
*   **Dependencies:** ChromaDB Client.
*   **Location:** `core/vector_store.py`

---
