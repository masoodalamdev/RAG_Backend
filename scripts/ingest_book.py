#!/usr/bin/env python3
"""
Script to ingest a book into the RAG system.
"""

import argparse
import asyncio
import sys
import os
from pathlib import Path

# Add the src directory to the path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.services.rag_service import RAGService
from src.config.settings import get_settings


async def main():
    parser = argparse.ArgumentParser(description="Ingest a book into the RAG system")
    parser.add_argument("--title", required=True, help="Title of the book")
    parser.add_argument("--author", required=True, help="Author of the book")
    parser.add_argument("--file", required=True, help="Path to the book file")
    parser.add_argument("--isbn", help="ISBN of the book (optional)")
    
    args = parser.parse_args()
    
    # Validate that the file exists
    if not os.path.isfile(args.file):
        print(f"Error: File '{args.file}' does not exist.")
        sys.exit(1)
    
    # Read the content from the file
    try:
        with open(args.file, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)
    
    # Get settings
    settings = get_settings()
    
    # Create RAG service
    rag_service = RAGService(
        cohere_api_key=settings.cohere_api_key,
        qdrant_url=settings.qdrant_cluster_url,
        qdrant_api_key=settings.qdrant_api_key,
        neon_db_url=settings.neon_db_url
    )
    
    # Ingest the book
    try:
        book_id = await rag_service.ingest_book(
            title=args.title,
            author=args.author,
            content=content,
            isbn=args.isbn
        )
        
        print(f"Book successfully ingested with ID: {book_id}")
    except Exception as e:
        print(f"Error ingesting book: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())