# 2. Requirements

## 2.1. Functional

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

## 2.2. Non-Functional

*   **NFR1:** Data extraction accuracy for key financial metrics must exceed 90%.
*   **NFR2:** All facts and metrics presented in the `/summary` output must be attributable to their source document.
*   **NFR3:** The end-to-end response time for `/ask` should be less than 15 seconds. The response time for `/summary` should be less than 30 seconds.
*   **NFR4:** The architecture must enforce strict data isolation between different clients (single-tenant instances).
*   **NFR5:** The system must handle transient API failures (e.g., LlamaParse, OpenAI) and infrastructure connection failures (e.g., Redis) gracefully, using retry logic where appropriate.
*   **NFR6:** The system must provide feedback to the user on the progress of long-running operations (e.g., `/load`, `/summary`), indicating the current status or expected waiting time.

---
