# 2. High Level Architecture

## 2.1. Technical Summary

This architecture implements a professional **Retrieval-Augmented Generation (RAG)** pipeline within a Python-based monolithic application. The core of the system is a data processing engine that uses **LlamaParse** for layout-aware document parsing and **LlamaIndex** for orchestration, with **ChromaDB** serving as the vector store. This design directly addresses the primary goal of the PRD (G3) by creating a high-fidelity, structured data foundation to enable reliable, context-aware analysis by the **GPT-4o** model.

## 2.2. High Level Overview

*   **Architectural Style:** The system is designed as a **Monolith**. This is a pragmatic choice for the MVP, prioritizing development speed, ease of deployment, and simplified debugging over the complexities of a distributed system.
*   **Repository Structure:** A **Monorepo** will be used, containing all application code, handlers, and core logic in a single repository. This simplifies dependency management and ensures atomic commits across the system.
*   **Primary Data Flow:**
    1.  **Ingestion (`/load`):** Documents are downloaded from a source, parsed into structured Markdown by **LlamaParse**, segmented into layout-aware chunks, converted to embeddings, and stored in a persistent **ChromaDB** collection.
    2.  **Retrieval (`/ask`, `/summary`):** A user query is used to retrieve relevant chunks from the vector store. These chunks, along with the original query, are passed to the **GPT-4o** model for synthesis, and the final answer is returned to the user.

## 2.3. High Level Project Diagram

```mermaid
graph TD
    subgraph User Interface
        A[Slack Workspace]
    end

    subgraph Application Layer (Python Monolith)
        B[Slack Bolt Handlers]
        C[Dataroom Manager]
        D[RAG Engine]
        E[Core Services]
    end

    subgraph Data Layer
        F[ChromaDB (Vector Store)]
        G[JSON Index (Dataroom Metadata)]
    end

    subgraph External Services
        H[Google Drive API]
        I[LlamaParse API]
        J[OpenAI API]
    end

    A -- /load, /connect, /ask, etc. --> B;
    B -- Manages --> C;
    B -- Uses --> D;
    C -- Accesses --> G;
    D -- Uses --> E;
    D -- Accesses --> F;
    E -- Calls --> H;
    E -- Calls --> I;
    D -- Calls --> J;
```

## 2.4. Architectural and Design Patterns

*   **Repository Pattern:** This pattern will be used to abstract all data storage operations. Specifically, the `DataroomManager` will handle metadata storage (via a JSON file for the MVP), and a `VectorStore` service will abstract the interactions with ChromaDB.
    *   *Rationale:* This decouples our application logic from the specific database implementation, making it easier to swap out ChromaDB for Pinecone in the future or change how metadata is stored. It also simplifies testing.
*   **Service Layer:** The core logic will be organized into distinct services within the `core/` directory (e.g., `ParsingService`, `RAGEngine`). These services will be instantiated and used by the Slack command handlers.
    *   *Rationale:* This promotes a clean separation of concerns between the presentation layer (Slack handlers) and the business logic, improving modularity and testability.
*   **Asynchronous Task Execution:** The `/load` command, which is a long-running I/O-bound operation, will be executed in a background thread.
    *   *Rationale:* This fulfills requirement **NFR6** by preventing the application from appearing frozen and allowing the bot to provide progress updates to the user in Slack.

---
