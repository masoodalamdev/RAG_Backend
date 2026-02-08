#!/usr/bin/env python3
"""
Test to check if external services (Cohere, Qdrant) are accessible
"""

import sys
sys.path.insert(0, 'src')

from src.config.settings import get_settings
from src.services.embedding_service import EmbeddingService
from src.services.retrieval_service import RetrievalService
from src.services.generation_service import GenerationService

def test_external_services():
    print("Testing external service connectivity...")
    
    # Load settings
    settings = get_settings()
    
    # Initialize services
    embedding_service = EmbeddingService(settings.cohere_api_key)
    retrieval_service = RetrievalService(settings.qdrant_cluster_url, settings.qdrant_api_key)
    generation_service = GenerationService(settings.cohere_api_key)
    
    # Test Cohere embedding
    print("\nTesting Cohere embedding service...")
    try:
        result = embedding_service.generate_embedding("test")
        print(f"[SUCCESS] Cohere embedding worked, vector length: {len(result.embedding)}")
    except Exception as e:
        print(f"[ERROR] Cohere embedding failed: {e}")
    
    # Test Cohere generation
    print("\nTesting Cohere generation service...")
    try:
        result = generation_service.generate_response("Say hello", max_tokens=10)
        print(f"[SUCCESS] Cohere generation worked: {result.text[:50]}...")
    except Exception as e:
        print(f"[ERROR] Cohere generation failed: {e}")
    
    # Test Qdrant connection (this might fail if collection doesn't exist)
    print("\nTesting Qdrant connection...")
    try:
        # Try to get collection info (this will test the connection)
        collections = retrieval_service.client.get_collections()
        print(f"[SUCCESS] Qdrant connection successful, collections: {[c.name for c in collections.collections]}")
    except Exception as e:
        print(f"[ERROR] Qdrant connection failed: {e}")
    
    print("\nExternal service connectivity test completed.")

if __name__ == "__main__":
    test_external_services()