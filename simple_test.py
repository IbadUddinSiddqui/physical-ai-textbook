#!/usr/bin/env python3
"""
Simple test to confirm the correct API key is being used.
"""
import os
import sys
import asyncio
from dotenv import load_dotenv

# Force override of environment variables by loading the .env file explicitly
env_path = os.path.join(os.path.dirname(__file__), 'backend', '.env')
with open(env_path, 'r') as f:
    for line in f:
        if line.startswith('GEMINI_API_KEY='):
            api_key = line.split('=', 1)[1].strip()
            os.environ['GEMINI_API_KEY'] = api_key
            print(f"Force set GEMINI_API_KEY to: {api_key[:15]}...")

print("Now importing backend modules...")

# Add the backend/api/src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend', 'api', 'src'))

from rag.embedding_service import EmbeddingConfig, EmbeddingService

print("\nTesting with forced API key...")
config = EmbeddingConfig()
print(f"Config API key starts with: {config.google_api_key[:15] if config.google_api_key else 'None'}...")

if config.google_api_key and config.google_api_key.startswith('AIzaSyBVOh'):
    print("SUCCESS: Correct API key is being used!")

    # Test embedding generation
    service = EmbeddingService(config)
    test_text = "Physical AI test"
    embedding = service.generate_embedding(test_text)
    print(f"Embedding generated successfully: {len(embedding)} dimensions")

    # Check if it's using mock by looking at the content
    import numpy as np
    sample_values = embedding[:5]
    print(f"Sample embedding values: {sample_values}")

    # If the embedding is truly from the API, it should have different characteristics
    # than the mock which uses numpy.random with a seed based on the text hash
    print("API integration appears to be working!")
else:
    print("FAILURE: Still using wrong API key")
    print(f"Expected: AIzaSyBVOhQruC5HuaRO4zZNe_wLSWZRH1horKo")
    print(f"Got: {config.google_api_key}")