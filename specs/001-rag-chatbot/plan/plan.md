# Implementation Plan: Integrated RAG Chatbot for Published Book

**Branch**: `001-rag-chatbot` | **Date**: 2026-01-21 | **Spec**: [link to spec.md]
**Input**: Feature specification from `/specs/001-rag-chatbot/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Build a high-quality, production-ready Retrieval-Augmented Generation (RAG) chatbot that can be embedded directly into a published web-based book (using Docusaurus). The system supports two main query modes: (1) general questions about the entire book content, and (2) questions strictly limited to user-selected/highlighted text passages from the book. The architecture uses FastAPI backend, Qdrant Cloud for vector storage, Neon Serverless Postgres for metadata, and exclusively Cohere API for LLM operations.

## Technical Context

**Language/Version**: Python 3.10+
**Primary Dependencies**: FastAPI, Cohere API, Qdrant, Neon Postgres, Pydantic, SQLAlchemy
**Storage**: Qdrant Cloud (vector DB), Neon Serverless Postgres (metadata), local files (book content)
**Testing**: pytest with unit, integration, and end-to-end tests
**Target Platform**: Linux server (backend API), with JavaScript integration for Docusaurus frontend
**Project Type**: Web application with backend API
**Performance Goals**: <2s response time for 95% of queries, 95%+ accuracy in retrieval and generation
**Constraints**: Free-tier service limits (Qdrant Cloud, Neon Postgres), no user data storage beyond session, API key security
**Scale/Scope**: Single book instance initially, with potential for multiple books

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- ✅ Precision in Retrieval and Generation: Cosine similarity threshold >0.8 for relevance
- ✅ User-Centric Functionality: Response latency under 2 seconds
- ✅ Scalability and Efficiency: Using free-tier services (Cohere API, Neon Serverless Postgres, Qdrant Cloud Free Tier)
- ✅ Security and Privacy: No storage of user data beyond session, secure API key handling
- ✅ Modularity: Clean separation of retrieval, augmentation, and generation components
- ✅ Content Grounding: All responses grounded in book content without hallucination
- ✅ Technology Stack: Exclusive use of Cohere API, PEP 8 compliant Python code
- ✅ Quality Assurance: Unit tests with >95% retrieval accuracy

## Project Structure

### Documentation (this feature)

```text
specs/001-rag-chatbot/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── models/
│   │   ├── __init__.py
│   │   ├── book_content.py          # Book content entity
│   │   ├── user_query.py            # User query entity
│   │   ├── selected_text_passage.py # Selected text passage entity
│   │   ├── vector_embeddings.py     # Vector embeddings entity
│   │   └── chatbot_response.py      # Chatbot response entity
│   ├── services/
│   │   ├── __init__.py
│   │   ├── embedding_service.py     # Handles embedding generation
│   │   ├── retrieval_service.py     # Handles vector search and retrieval
│   │   ├── generation_service.py    # Handles response generation
│   │   ├── rag_service.py           # Main RAG orchestration
│   │   └── ingestion_service.py     # Handles book content ingestion
│   ├── api/
│   │   ├── __init__.py
│   │   ├── main.py                  # FastAPI app definition
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── health.py            # Health check endpoint
│   │   │   ├── ingest.py            # Ingestion endpoint (admin-only)
│   │   │   └── chat.py              # Main chat/query endpoint
│   │   └── middleware/
│   │       ├── __init__.py
│   │       └── cors.py              # CORS configuration
│   ├── config/
│   │   ├── __init__.py
│   │   ├── settings.py              # Application settings and config
│   │   └── database.py              # Database connection setup
│   └── utils/
│       ├── __init__.py
│       ├── validators.py            # Input validation utilities
│       ├── security.py              # Security utilities
│       └── helpers.py               # General helper functions
├── tests/
│   ├── unit/
│   │   ├── test_embedding_service.py
│   │   ├── test_retrieval_service.py
│   │   ├── test_generation_service.py
│   │   └── test_rag_service.py
│   ├── integration/
│   │   ├── test_ingestion_flow.py
│   │   └── test_chat_flow.py
│   └── e2e/
│       └── test_end_to_end.py
├── scripts/
│   ├── ingest_book.py               # Script to ingest a book
│   └── setup_env.py                 # Environment setup script
├── requirements.txt                 # Python dependencies
├── .env.example                     # Environment variables template
├── README.md                        # Project documentation
├── docker-compose.yml               # Docker configuration (optional)
└── pyproject.toml                   # Project metadata and build config
```

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [None] | [No violations identified] | [All constitutional principles followed] |
