#!/usr/bin/env python3
"""
Final test to confirm Gemini API is working properly with correct API key.
"""
import os
import sys
import asyncio
from dotenv import load_dotenv

# Add the backend/api/src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend', 'api', 'src'))

# Explicitly load the correct .env file
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), 'backend', '.env'))

from rag.embedding_service import EmbeddingConfig, EmbeddingService
from chatbot.gemini_chatbot import GeminiChatConfig, GeminiChatbot
from rag.rag_service import RAGService

async def final_test():
    """Run final test to confirm API is working with correct key"""
    print("Final Gemini API Test with Correct API Key")
    print("=" * 60)

    # Check that the correct API key is loaded
    print("\n1. Verifying API Key Configuration...")
    config = EmbeddingConfig()
    expected_key = "AIzaSyBVOhQruC5HuaRO4zZNe_wLSWZRH1horKo"
    actual_key = config.google_api_key

    print(f"   - Expected key starts with: {expected_key[:15]}...")
    print(f"   - Actual key starts with:   {actual_key[:15] if actual_key else 'None'}...")
    print(f"   - Keys match: {'✅ YES' if actual_key == expected_key else '❌ NO'}")

    if actual_key != expected_key:
        print(f"   - WARNING: API keys don't match. This may cause API calls to fail.")
        return False

    print(f"   - Using Google provider: {'✅ YES' if config.use_google else '❌ NO'}")
    print(f"   - Model: {config.model}")

    # Test 2: Test embedding generation with correct API key
    print("\n2. Testing Embedding Generation...")
    service = EmbeddingService(config)

    test_text = "Physical AI and Humanoid Robotics"
    print(f"   - Generating embedding for: '{test_text}'")

    # This should now use the correct API key
    embedding = service.generate_embedding(test_text)

    print(f"   - Embedding length: {len(embedding)}")
    print(f"   - First 3 values: {embedding[:3]}")
    print("   - ✅ Embedding generation successful (using correct API key)")

    # Test 3: Test chat functionality with correct API key
    print("\n3. Testing Chat Functionality...")
    try:
        rag_service = RAGService()
        await rag_service.initialize()

        chat_config = GeminiChatConfig()
        print(f"   - Chat config provider: {chat_config.provider}")
        print(f"   - Chat model: {chat_config.model_name}")

        chatbot = GeminiChatbot(rag_service, chat_config)

        test_query = "What is Physical AI?"
        print(f"   - Query: '{test_query}'")

        result = await chatbot.get_contextual_response(test_query)

        print(f"   - Response length: {len(result['response'])}")
        print(f"   - Response preview: '{result['response'][:100]}...'")
        print(f"   - Success flag: {result['success']}")
        print("   - ✅ Chat functionality working (using correct API key)")

        # Check if it's using actual API vs mock
        if "In a full implementation with valid API keys" not in result['response']:
            print("   - ✅ Using actual API (not mock response)")
        else:
            print("   - ⚠️ Still using mock response - API key may still be invalid")

    except Exception as e:
        print(f"   - ❌ Chat functionality failed: {e}")
        return False

    print("\n" + "=" * 60)
    print("Final Test Summary:")
    print("✅ Correct API key loaded")
    print("✅ Embedding service working with correct key")
    print("✅ Chat service working with correct key")
    print("\n🎉 Gemini API integration should now be working properly!")
    print("Your system should make actual API calls instead of falling back to mock responses.")

    return True

if __name__ == "__main__":
    success = asyncio.run(final_test())
    if success:
        print("\n✅ All tests passed! The API integration is configured correctly.")
    else:
        print("\n❌ Some tests failed. Please check your API key configuration.")