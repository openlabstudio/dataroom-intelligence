# 3. Tech Stack

## 3.1. Cloud Infrastructure

*   **Provider:** Railway.app (or similar PaaS)
    *   *Rationale:* For the MVP, a simple Platform-as-a-Service is ideal. It minimizes infrastructure overhead, allowing us to focus on application development. The presence of `railway.toml` in the repository suggests a pre-existing preference.
*   **Key Services:** App Hosting, Persistent Volumes (for ChromaDB).

## 3.2. Technology Stack Table

| Category | Technology | Version | Purpose | Rationale |
| :--- | :--- | :--- | :--- | :--- |
| **Language** | Python | ~3.11 | Primary development language | Mature, extensive data science ecosystem, required by core frameworks. |
| **Backend Framework** | Flask | ~2.3 | Web server for health checks | Lightweight, simple, and already integrated into the project. |
| **Slack Integration** | Slack Bolt for Python | ~1.18 | Core Slack app framework | The official and robust library for building Slack apps. |
| **PDF Parsing** | LlamaParse API | N/A (API) | PDF to Markdown conversion | Chosen for its optimal balance of quality, speed, and native Markdown output. |
| **RAG Framework** | LlamaIndex | ~0.9.0 | RAG orchestration | Purpose-built for RAG, with excellent support for our chosen components. |
| **Vector Database** | ChromaDB | ~0.4.0 | Vector storage for embeddings | Simple, local-first, and sufficient for MVP needs. Allows for future migration. |
| **Embeddings Model**| OpenAI API | `text-embedding-3-small` | Text-to-vector conversion | Best balance of performance and cost in the OpenAI model family. |
| **LLM** | OpenAI API | `gpt-4o` | Core model for synthesis/analysis | State-of-the-art reasoning, speed, and large context window. |
| **Data Validation** | Pydantic | ~2.0 | Data validation & settings | Modern, robust data validation to ensure type safety and reliability. |

---
