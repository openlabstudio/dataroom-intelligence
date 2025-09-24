# 7. Epic 2: Core Command Implementation & Analysis

**Expanded Goal:** This epic brings the application to life for the end-user. We will implement the full suite of Slack commands that allow an analyst to load, connect to, manage, and analyze datarooms. By the end of this epic, the user will be able to ask specific questions and receive a full AI-generated summary, realizing the core value proposition of the product.

## Stories

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
