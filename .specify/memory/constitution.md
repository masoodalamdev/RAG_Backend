<!-- SYNC IMPACT REPORT
Version change: N/A → 1.0.0
Modified principles: N/A (new constitution)
Added sections: All sections (new constitution)
Removed sections: N/A
Templates requiring updates: ⚠ pending - .specify/templates/plan-template.md, .specify/templates/spec-template.md, .specify/templates/tasks-template.md
Follow-up TODOs: None
-->
# Integrated RAG Chatbot for Published Book Constitution

## Core Principles

### Precision in Retrieval and Generation
Ensure accurate retrieval and generation through vector embeddings and semantic search with cosine similarity threshold >0.8 for relevance

### User-Centric Functionality
Provide seamless integration into the book with handling of general and selected-text queries, ensuring response latency under 2 seconds

### Scalability and Efficiency
Utilize free-tier services (Cohere API, Neon Serverless Postgres, Qdrant Cloud Free Tier) without compromising performance

### Security and Privacy
Implement no storage of user data beyond session and follow API key handling best practices

### Modularity
Maintain clean separation of retrieval, augmentation, and generation components

### Content Grounding
All responses must be grounded in the book's content or user-selected text without hallucination

## Technology Stack and Standards
Exclusive use of Cohere API keys for LLM operations, PEP 8 compliant Python code, efficient schema design in Neon Postgres for metadata storage, comprehensive error handling and logging, Qdrant for storing and querying embeddings

## Quality Assurance and Documentation
Unit tests for each component (retrieval accuracy >95%, generation coherence), end-to-end integration tests, inline comments, README with setup instructions, and deployment guide

## Governance
All responses must be grounded in the book's content or user-selected text, exclusive use of Cohere API keys for LLM operations, code quality follows PEP 8 standards, database usage with efficient schema design in Neon Postgres, vector database operations using Qdrant with cosine similarity threshold >0.8, comprehensive testing of each component, proper documentation with inline comments and setup guides

**Version**: 1.0.0 | **Ratified**: 2026-01-21 | **Last Amended**: 2026-01-21
