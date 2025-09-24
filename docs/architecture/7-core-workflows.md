# 7. Core Workflows

## 7.1. Workflow 1: Data Ingestion via `/load` Command

This diagram illustrates the asynchronous process of loading and processing a new dataroom.

```mermaid
sequenceDiagram
    actor User
    participant Slack API
    participant Slack Handlers
    participant DataroomManager
    participant RAGEngine
    participant GDrive API
    participant LlamaParse API
    participant OpenAI API
    participant VectorStore

    User->>+Slack API: /load [url] [name]
    Slack API->>+Slack Handlers: Command Received
    Slack Handlers-->>-User: "✅ Request received. Processing will begin shortly..."
    
    par Background Processing
        Slack Handlers->>+DataroomManager: create_dataroom(name, url)
        DataroomManager->>+RAGEngine: process_and_store_documents(files)
        RAGEngine->>+GDrive API: download_files(url)
        GDrive API-->>-RAGEngine: Return file paths
        
        loop For each file
            RAGEngine->>+LlamaParse API: parse(file)
            LlamaParse API-->>-RAGEngine: Return Markdown
        end
        
        RAGEngine->>RAGEngine: Chunk Markdown
        
        loop For each chunk
            RAGEngine->>+OpenAI API: create_embedding(chunk)
            OpenAI API-->>-RAGEngine: Return vector
        end
        
        RAGEngine->>+VectorStore: add_vectors(collection_name, vectors)
        VectorStore-->>-RAGEngine: Success
        RAGEngine-->>-DataroomManager: Processing Complete
        DataroomManager-->>-Slack Handlers: Dataroom Ready
        
        Slack Handlers->>+Slack API: Post "✅ Dataroom '[name]' is loaded and ready" message
        Slack API-->>-User: Display success message
    end
```

## 7.2. Workflow 2: Q&A via `/ask` Command

This diagram illustrates the synchronous process of answering a user's question.

```mermaid
sequenceDiagram
    actor User
    participant Slack API
    participant Slack Handlers
    participant DataroomManager
    participant RAGEngine
    participant VectorStore
    participant OpenAI API

    User->>+Slack API: /ask [question]
    Slack API->>+Slack Handlers: Command Received
    
    Slack Handlers->>+DataroomManager: get_active_dataroom_for_channel(channel_id)
    DataroomManager-->>-Slack Handlers: Return dataroom_id
    
    Slack Handlers->>+RAGEngine: query(question, dataroom_id)
    RAGEngine->>+OpenAI API: create_embedding(question)
    OpenAI API-->>-RAGEngine: Return query_vector
    
    RAGEngine->>+VectorStore: semantic_search(collection_name, query_vector)
    VectorStore-->>-RAGEngine: Return relevant chunks
    
    RAGEngine->>RAGEngine: Re-rank chunks (Story 3.1)
    RAGEngine->>RAGEngine: Construct Prompt
    
    RAGEngine->>+OpenAI API: get_completion(prompt)
    OpenAI API-->>-RAGEngine: Return synthesized answer
    
    RAGEngine-->>-Slack Handlers: Return final answer
    Slack Handlers->>Slack Handlers: Format answer
    
    Slack Handlers->>+Slack API: Post formatted answer
    Slack API-->>-User: Display answer
```

---
