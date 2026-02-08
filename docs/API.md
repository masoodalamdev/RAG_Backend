# RAG Chatbot API Documentation

## Overview
This API provides a Retrieval-Augmented Generation (RAG) chatbot that answers questions about book content. The system supports two main query modes:
1. General questions about the entire book content
2. Questions strictly limited to user-selected/highlighted text passages from the book

## Architecture
- **Backend**: FastAPI (Python) serving a REST API
- **Vector Database**: Qdrant Cloud (free tier) for storing book chunk embeddings
- **Relational Database**: Neon Serverless Postgres for storing metadata
- **LLM & Embeddings**: Exclusively Cohere API (embed-v3 for embeddings, command-r for generation)

## API Endpoints

### GET /health
Health check endpoint to verify the application is running.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2026-01-21T10:00:00Z",
  "uptime": 123.45
}
```

### POST /chat
Submit a query to the RAG chatbot and receive a response.

**Request Body:**
```json
{
  "query": "What is the main concept discussed in the book?",
  "book_id": "123e4567-e89b-12d3-a456-426614174000",
  "selected_text": "Optional selected text for focused queries",
  "mode": "full", // or "selected"
  "session_id": "Optional session identifier"
}
```

**Response:**
```json
{
  "response": "The main concept discussed in the book is...",
  "sources": [
    {
      "chunk_id": "chunk-123",
      "page_number": 15,
      "section_title": "Introduction"
    }
  ],
  "confidence_score": 0.92
}
```

### POST /ingest
Ingest a book into the RAG system (admin-only endpoint).

**Request Parameters:**
- `title`: Title of the book
- `author`: Author of the book
- `isbn`: ISBN of the book (optional)

**Response:**
```json
{
  "message": "Book successfully ingested",
  "book_id": "123e4567-e89b-12d3-a456-426614174000"
}
```

## Performance Metrics
The system tracks response times and other performance metrics. The target is to respond to queries with latency under 2 seconds.

## Security
- API keys are securely handled via environment variables
- No user data is stored beyond the session
- Input validation is performed on all endpoints