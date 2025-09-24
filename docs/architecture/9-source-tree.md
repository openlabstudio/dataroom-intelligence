# 9. Source Tree

The project will follow a clean, modular structure designed to separate the Slack-facing handlers from the core business logic.

```
dataroom-intelligence/
├── .env.example              # Environment variable template
├── .gitignore
├── app.py                    # Main Flask/Slack application entry point
├── Procfile                  # For deployment (e.g., Railway, Heroku)
├── requirements.txt          # Python dependencies
│
├── core/                     # Core business logic and services (The "Engine")
│   ├── __init__.py
│   ├── dataroom_manager.py   # Manages Dataroom entities and connections
│   ├── parser.py             # Handles LlamaParse API integration
│   ├── rag_engine.py         # Orchestrates the RAG pipeline (chunk, embed, retrieve, synth)
│   └── vector_store.py       # Abstraction for ChromaDB
│
├── data/                     # Local data persistence for MVP
│   ├── datarooms.json        # Metadata index for all Dataroom entities
│   ├── connections.json      # Maps Slack channels to Dataroom IDs
│   └── vector_storage/       # Directory for ChromaDB's on-disk persistence
│
├── handlers/                 # Slack command handlers (The "Presentation Layer")
│   ├── __init__.py
│   ├── admin_handlers.py     # Handles /list, /current, /disconnect, /help
│   ├── ask_handler.py        # Handles the /ask command
│   ├── connect_handler.py    # Handles the /connect command
│   ├── load_handler.py       # Handles the /load command
│   └── summary_handler.py    # Handles the /summary command
│
├── models/                   # Pydantic data models
│   ├── __init__.py
│   └── dataroom.py           # Defines the Dataroom and Document models
│
├── prompts/                  # Centralized storage for all LLM prompts
│   ├── __init__.py
│   ├── analysis_prompts.py   # Prompts for /summary
│   └── qa_prompts.py         # Prompts for /ask
│
├── docs/                     # Project documentation
│   ├── prd.md                # The Product Requirements Document
│   └── architecture.md       # This document
│
└── tests/                    # Unit and Integration tests
    ├── __init__.py
    ├── test_core_logic.py
    └── test_handlers.py
```

---
