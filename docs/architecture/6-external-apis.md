# 6. External APIs

This project relies on three primary external services for its core functionality, plus the Google Drive API for document retrieval.

## 6.1. LlamaParse API

*   **Purpose:** To parse source documents (especially PDFs) into high-quality, structured Markdown, preserving layout elements like tables. This is the cornerstone of our data ingestion pipeline.
*   **Documentation:** [LlamaParse API Reference](https://cloud.llamaindex.ai/parse)
*   **Authentication:** API Key provided via the `LLAMA_CLOUD_API_KEY` environment variable.
*   **Rate Limits:** Subject to the user's LlamaCloud plan. The implementation must handle potential rate limit errors gracefully.
*   **Key Endpoints Used:** The `llama-parse` library abstracts the direct endpoint, which is effectively `POST /api/v1/parse`.

## 6.2. OpenAI API

This API is used for two distinct purposes: generating embeddings and synthesizing text.

*   **Purpose:**
    1.  **Embeddings:** To convert the structured text chunks into vector representations for semantic search.
    2.  **Chat Completions:** To generate narrative summaries and answers based on the user's query and the retrieved context.
*   **Documentation:** [OpenAI API Reference](https://platform.openai.com/docs/api-reference)
*   **Authentication:** API Key provided via the `OPENAI_API_KEY` environment variable.
*   **Rate Limits:** Depends on the user's OpenAI account tier. The application must implement retry logic (as per NFR5).
*   **Key Endpoints Used:**
    *   `POST /v1/embeddings` (using model `text-embedding-3-small`)
    *   `POST /v1/chat/completions` (using model `gpt-4o`)

## 6.3. Google Drive API

*   **Purpose:** To list and download source documents from the Google Drive folder URL provided by the user in the `/load` command.
*   **Documentation:** [Google Drive API Reference](https://developers.google.com/drive/api/v3/reference)
*   **Authentication:** Service Account JSON credentials provided via the `GOOGLE_SERVICE_ACCOUNT_JSON` environment variable.
*   **Rate Limits:** Standard Google API usage limits apply.
*   **Key Endpoints Used:**
    *   `files.list`
    *   `files.get` (with `alt=media` for download)

---
