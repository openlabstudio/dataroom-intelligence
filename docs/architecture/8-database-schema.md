# 8. Database Schema

## 8.1. Metadata Storage: JSON Files

For the MVP, all non-vector metadata will be stored in simple JSON files on the local filesystem. This approach is simple, human-readable, and sufficient for our single-tenant architecture, avoiding the need for a traditional relational database.

**`datarooms.json`**
*   **Purpose:** Acts as the primary index for all persistent Datarooms.
*   **Structure:** A dictionary where the key is the `dataroom_id` and the value is an object containing its metadata.

    ```json
    {
      "dr_20250922_startup_x": {
        "name": "Startup X Series A",
        "created_at": "2025-09-22T18:00:00Z",
        "source_url": "https://drive.google.com/...",
        "vector_collection_name": "collection_startup_x_123",
        "document_manifest": [
          { "name": "pitch_deck.pdf", "chunks": 192 },
          { "name": "financials.xlsx", "chunks": 45 }
        ]
      }
    }
    ```

**`connections.json`**
*   **Purpose:** Maps an active Slack channel to a Dataroom.
*   **Structure:** A simple dictionary where the key is the `channel_id` and the value is the `dataroom_id`.

    ```json
    {
      "C09E2JQ6YET": "dr_20250922_startup_x"
    }
    ```

## 8.2. Vector Store Schema (ChromaDB)

ChromaDB is a document-oriented vector database. We will not define a rigid schema, but rather a consistent structure for the **metadata** associated with each vector/chunk. This metadata is critical for source attribution and advanced retrieval strategies.

*   **Collection Name:** Each Dataroom will have its own collection in ChromaDB, named using its `vector_collection_name` (e.g., `collection_startup_x_123`).
*   **Document Content:** The text content of each chunk.
*   **Document Metadata Schema:** Each vector will have the following metadata attached:

    ```json
    {
      "source_document_name": "pitch_deck.pdf",
      "chunk_type": "table", // or "paragraph", "list_item", etc.
      "page_number": 5, // If applicable
      "parent_chunk_id": "parent_chunk_abc" // For Parent Document Retrieval
    }
    ```
*   **Rationale:** This metadata structure allows us to filter queries (e.g., "search only in tables") and to reliably trace any piece of retrieved context back to its exact source document and location, fulfilling requirement **NFR2**.

---
