#!/usr/bin/env python3
"""
Simple test to verify backend service configurations
"""

import sys
import os
sys.path.insert(0, 'src')

# Load settings
from src.config.settings import get_settings

print("Testing configuration loading...")
try:
    settings = get_settings()
    print(f"[SUCCESS] Successfully loaded settings")
    print(f"  - Cohere API key loaded: {'Yes' if settings.cohere_api_key else 'No'}")
    print(f"  - Qdrant URL loaded: {settings.qdrant_cluster_url}")
    print(f"  - Neon DB URL loaded: {'Yes' if settings.neon_db_url else 'No'}")
except Exception as e:
    print(f"[ERROR] Failed to load settings: {e}")
    sys.exit(1)

print("\nTesting service initializations...")

# Test embedding service
try:
    from src.services.embedding_service import EmbeddingService
    embedding_service = EmbeddingService(settings.cohere_api_key)
    print("[SUCCESS] Embedding service initialized successfully")
except Exception as e:
    print(f"[ERROR] Failed to initialize embedding service: {e}")

# Test retrieval service
try:
    from src.services.retrieval_service import RetrievalService
    retrieval_service = RetrievalService(settings.qdrant_cluster_url, settings.qdrant_api_key)
    print("[SUCCESS] Retrieval service initialized successfully")
except Exception as e:
    print(f"[ERROR] Failed to initialize retrieval service: {e}")

# Test generation service
try:
    from src.services.generation_service import GenerationService
    generation_service = GenerationService(settings.cohere_api_key)
    print("[SUCCESS] Generation service initialized successfully")
except Exception as e:
    print(f"[ERROR] Failed to initialize generation service: {e}")

print("\nConfiguration test completed.")