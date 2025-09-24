# 4. Data Models

For our MVP, the data model is simple and focuses on two core entities: the `Dataroom` and the `ChannelConnection`.

## 4.1. Dataroom

This is the central entity in our system. It represents a single, processed collection of documents that has been loaded into the system via the `/load` command.

*   **Purpose:** To act as a persistent, reusable container for a complete set of analyzed documents and their corresponding vector embeddings.
*   **Key Attributes:**
    *   `dataroom_id` (string): A unique identifier for the dataroom (e.g., `dr_20250922_startup_x`).
    *   `name` (string): The user-friendly display name (e.g., "Startup X Series A").
    *   `created_at` (datetime): Timestamp of when the dataroom was created.
    *   `source_url` (string): The original Google Drive URL from which the documents were loaded.
    *   `vector_collection_name` (string): The name of the corresponding collection within ChromaDB where the document chunks are stored.
    *   `document_manifest` (list): A list of metadata objects for each document processed, including filename, page count, and chunk count.
*   **Relationships:** A `Dataroom` can be connected to one or more `ChannelConnection`s.

## 4.2. ChannelConnection

This is not a database model, but a simple mapping to track which Dataroom is active in which Slack channel. For the MVP, this will be managed by the `DataroomManager` and can be persisted in a simple JSON file.

*   **Purpose:** To link a specific Slack channel to a specific `Dataroom`, providing the context for commands like `/ask` and `/summary`.
*   **Key Attributes:**
    *   `channel_id` (string): The unique ID of the Slack channel (e.g., `C09E2JQ6YET`).
    *   `dataroom_id` (string): The ID of the `Dataroom` currently connected to this channel.

---
