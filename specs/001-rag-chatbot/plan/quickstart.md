# Quickstart Guide: Integrated RAG Chatbot for Published Book

## Prerequisites

- Python 3.10+
- pip package manager
- Git
- Access to Cohere API (API key)
- Access to Neon Serverless Postgres (connection string)
- Access to Qdrant Cloud (API key and cluster URL)

## Setup Instructions

### 1. Clone the Repository
```bash
git clone <repository-url>
cd backend
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy the example environment file and fill in your credentials:

```bash
cp .env.example .env
```

Edit `.env` and set:
- `COHERE_API_KEY` - Your Cohere API key
- `NEON_DB_URL` - Your Neon Postgres connection string
- `QDRANT_API_KEY` - Your Qdrant Cloud API key
- `QDRANT_CLUSTER_URL` - Your Qdrant Cloud cluster URL

### 5. Run Database Migrations (if applicable)
```bash
# If using Alembic for migrations
alembic upgrade head
```

### 6. Start the Application
```bash
uvicorn src.api.main:app --reload --port 8000
```

## Ingest a Book

To ingest a book into the RAG system:

1. Prepare your book content as a text file
2. Run the ingestion script:
```bash
python scripts/ingest_book.py --title "Book Title" --author "Author Name" --file path/to/book.txt
```

This will:
- Chunk the book content
- Generate embeddings using Cohere
- Store chunks in Neon Postgres
- Store embeddings in Qdrant

## Test the API

Once the server is running, you can test the endpoints:

### Health Check
```bash
curl http://localhost:8000/health
```

### Query the Chatbot
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

## Troubleshooting

### Common Issues

1. **API Keys Not Working**: Verify your API keys in the `.env` file are correct and have the necessary permissions.

2. **Database Connection Issues**: Check your Neon Postgres connection string and ensure the database is accessible.

3. **Qdrant Connection Issues**: Verify your Qdrant cluster URL and API key are correct.

4. **Slow Response Times**: Check your Cohere API rate limits and Qdrant performance.

### Useful Commands

- Check application logs: `tail -f logs/app.log`
- Run tests: `pytest`
- Format code: `black src/ tests/`
- Check code quality: `flake8 src/`

## Next Steps

1. Integrate the backend API with your Docusaurus book frontend
2. Customize the chatbot UI to match your book's design
3. Add additional books to your RAG system
4. Monitor usage and performance metrics