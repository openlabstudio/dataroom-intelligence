# 4. Technical Assumptions

## 4.1. Repository Structure: Monorepo

*   **Rationale:** For a greenfield project of this scope, a single repository (monorepo) is the simplest and most efficient approach. It simplifies dependency management, atomic commits, and initial CI/CD setup.

## 4.2. Service Architecture: Monolith

*   **Rationale:** The application will be built as a single, cohesive service (a monolith). This is the most pragmatic choice for an MVP, prioritizing development speed and ease of deployment over the complexity of a microservices or serverless architecture.

## 4.3. Testing Requirements: Unit + Integration

*   **Rationale:** The project requires a balance of speed and reliability. We will mandate comprehensive unit tests for individual functions and components, supplemented by integration tests to ensure the core RAG pipeline (Parse -> Chunk -> Retrieve -> Generate) works correctly end-to-end.

## 4.4. Additional Technical Assumptions and Requests

*   **PDF Parsing:** The system will use the **LlamaParse API** as its primary document parsing service.
*   **RAG Framework:** The core RAG pipeline will be orchestrated using the **LlamaIndex** framework.
*   **Vector Database:** **ChromaDB** will be used for local development and initial deployment due to its simplicity. The architecture should allow for a future migration to a managed service like Pinecone.
*   **LLM & Embeddings:** The system will use **OpenAI** models, specifically `gpt-4o` for synthesis and `text-embedding-3-small` for embeddings.
*   **Backend:** The existing **Flask + Slack Bolt** backend will be maintained and built upon.

---
