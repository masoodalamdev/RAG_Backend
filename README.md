# Integrated RAG Chatbot for Published Books

A high-quality, production-ready Retrieval-Augmented Generation (RAG) chatbot that can be embedded directly into a published web-based book. The system supports two main query modes: (1) general questions about the entire book content, and (2) questions strictly limited to user-selected/highlighted text passages from the book.

## Features

- **Accurate Retrieval**: Uses vector embeddings and semantic search with cosine similarity threshold >0.8 for relevance
- **Dual Query Modes**: Supports both general book queries and selected text queries
- **Fast Response**: Designed to respond to queries with latency under 2 seconds
- **Hallucination-Free**: All responses are grounded in the book's content without hallucinations
- **User Authentication**: Secure email/password authentication with custom profile fields
- **Personalization**: Ability to customize responses based on user profile and background
- **Secure**: No storage of user data beyond session, with secure API key handling
- **Modular Architecture**: Clean separation of retrieval, augmentation, generation, and authentication components

## Architecture

- **Backend**: FastAPI (Python) serving a REST API
- **Vector Database**: Qdrant Cloud (free tier) for storing book chunk embeddings
- **Relational Database**: Neon Serverless Postgres for storing metadata
- **LLM & Embeddings**: Exclusively Cohere API (embed-v3 for embeddings, command-r for generation)
- **Development Workflow**: SpecifyPlus + Qwen CLI for development orchestration

## Prerequisites

- Python 3.10+
- Access to Cohere API (API key)
- Access to Neon Serverless Postgres (connection string)
- Access to Qdrant Cloud (API key and cluster URL)

## Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables:
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and set your credentials.

5. Start the application:
   ```bash
   uvicorn src.api.main:app --reload --port 8000
   ```

## Usage

### User Authentication

#### Register a new user:
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePassword123!",
    "software_background": {
      "languages": ["Python", "JavaScript"],
      "frameworks": ["FastAPI", "React"],
      "experience_years": 5
    },
    "hardware_background": {
      "devices": ["Laptop", "Desktop"],
      "os_preference": "Linux",
      "setup_description": "Dual monitor setup with mechanical keyboard"
    }
  }'
```

#### Login:
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePassword123!"
  }'
```

#### Get user profile:
```bash
curl -X GET http://localhost:8000/api/user/profile \
  -H "Authorization: Bearer <your-jwt-token>"
```

#### Update user profile:
```bash
curl -X PUT http://localhost:8000/api/user/profile \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your-jwt-token>" \
  -d '{
    "software_background": {
      "languages": ["Python", "JavaScript", "Go"],
      "experience_years": 6
    }
  }'
```

### Ingest a Book

To add a book to the RAG system:

```bash
python scripts/ingest_book.py --title "Book Title" --author "Author Name" --file path/to/book.txt
```

### Query the Chatbot

Send a POST request to `/chat` endpoint:

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the main concept discussed in chapter 1?",
    "book_id": "<book-id>",
    "mode": "full"
  }'
```

For selected text queries:
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Explain this concept",
    "book_id": "<book-id>",
    "selected_text": "The concept of artificial intelligence...",
    "mode": "selected"
  }'
```

## API Documentation

View the interactive API documentation at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Project Structure

```
backend/
├── src/
│   ├── models/           # Data models
│   ├── services/         # Business logic
│   ├── api/              # API endpoints
│   ├── config/           # Configuration
│   └── utils/            # Utility functions
├── tests/                # Test suite
├── scripts/              # Utility scripts
├── requirements.txt      # Python dependencies
├── .env.example          # Environment variables template
└── README.md             # This file
```

## Testing

Run the test suite:
```bash
pytest
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## License

This project is licensed under the MIT License.