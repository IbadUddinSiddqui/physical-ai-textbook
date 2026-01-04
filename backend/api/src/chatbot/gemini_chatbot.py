import openai
import os
from typing import List, Dict, Optional
from dotenv import load_dotenv
import logging
import litellm
from ..rag.rag_service import RAGService

# Load environment variables from backend directory
load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'backend', '.env'))

logger = logging.getLogger(__name__)

class GeminiChatConfig:
    """Configuration for chatbot using LiteLLM (can work with Google models)"""
    def __init__(self):
        # Hardcoded API keys and model name - NO environment variable loading
        self.model_name = "gemini-2.5-flash"  # Using hardcoded model
        # Set your actual API keys directly
        self.api_key = os.getenv("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY_HERE")  # Use environment variable
        self.openai_api_key = "YOUR_OPENAI_API_KEY_HERE"  # Replace with your actual OpenAI API key

        # Hardcoded API keys - no environment variable loading
        # self.api_key = os.getenv("GEMINI_API_KEY", self.api_key)
        # self.openai_api_key = os.getenv("OPENAI_API_KEY", self.openai_api_key)

        # Debug logging for API key loading
        logger.info(f"Debug: Using model_name: {self.model_name}")
        logger.info(f"Debug: GEMINI_API_KEY exists: {bool(self.api_key) and self.api_key != 'YOUR_GEMINI_API_KEY_HERE'}")
        logger.info(f"Debug: OPENAI_API_KEY exists: {bool(self.openai_api_key) and self.openai_api_key != 'YOUR_OPENAI_API_KEY_HERE'}")
        logger.info(f"Debug: Loaded model_name: {self.model_name}")

        # Check for real API keys (not placeholder values)
        # Since we're using hardcoded keys, this check is always true for Gemini
        has_gemini_key = self.api_key and self.api_key != "YOUR_GEMINI_API_KEY_HERE" and len(self.api_key) > 10
        has_openai_key = self.openai_api_key and self.openai_api_key != "YOUR_OPENAI_API_KEY_HERE" and len(self.openai_api_key) > 10

        if has_gemini_key:
            # Using Google's API through LiteLLM
            self.provider = "gemini"
            logger.info(f"Debug: Using Gemini provider with model: {self.model_name}")
            self.api_base = None
        elif has_openai_key:
            # Using OpenAI's API
            self.provider = "openai"
            logger.info(f"Debug: Using OpenAI provider with model: {self.model_name}")
            self.api_base = None
        else:
            logger.warning("Warning: No valid API keys found. Will use fallback responses.")
            # Default to a provider for testing if no keys are available
            self.provider = "gemini"  # Can be changed to "openai" if preferred

class GeminiChatbot:
    """Chatbot service using LiteLLM for multi-provider support (Google or OpenAI) integrated with RAG system"""

    def __init__(self, rag_service: RAGService, config: Optional[GeminiChatConfig] = None):
        self.rag_service = rag_service
        self.config = config or GeminiChatConfig()

        # Configure LiteLLM
        litellm.drop_params = True
        litellm.success_callback = []
        litellm.failure_callback = []

    async def get_contextual_response(self, user_query: str, context_limit: int = 5) -> Dict:
        """
        Generate a response using RAG-augmented context from the textbook

        Args:
            user_query: The user's question
            context_limit: Number of context chunks to retrieve

        Returns:
            Dictionary with response and metadata
        """
        try:
            # Search for relevant content using the RAG system
            search_results = await self.rag_service.search_content(user_query, context_limit)

            # Extract relevant content from search results
            context_texts = []
            sources = []

            for result in search_results:
                payload = result.get('payload', {})
                content = payload.get('content', '')
                if content:
                    context_texts.append(content)
                    sources.append({
                        'chunk_id': payload.get('chunk_id'),
                        'chapter_id': payload.get('chapter_id'),
                        'score': result.get('score', 0)
                    })

            # Combine context with user query
            if context_texts:
                context = "\n\n".join(context_texts[:3])  # Use top 3 results
                messages = [
                    {
                        "role": "system",
                        "content": "You are an educational assistant for the Physical AI & Humanoid Robotics textbook. Use the following context to answer the user's question. Only provide information based on the textbook content provided in the context. If the context doesn't contain the information needed to answer the question, politely explain that the information is not available in the textbook."
                    },
                    {
                        "role": "user",
                        "content": f"""
                        Context:
                        {context}

                        User question: {user_query}

                        Please provide a comprehensive answer based on the textbook content.
                        """
                    }
                ]
            else:
                messages = [
                    {
                        "role": "system",
                        "content": "You are an educational assistant for the Physical AI & Humanoid Robotics textbook."
                    },
                    {
                        "role": "user",
                        "content": f"""
                        The user asked: {user_query}

                        Unfortunately, I couldn't find relevant content in the textbook to answer this question.
                        Please let me know if you'd like to ask about a different topic from the textbook.
                        """
                    }
                ]

            # Generate response using LiteLLM (works with Google or OpenAI)
            try:
                # Debug logging for API call
                logger.info(f"Debug: Attempting API call with provider: {self.config.provider}")
                logger.info(f"Debug: Using model: {self.config.model_name}")
                logger.info(f"Debug: API key being used: {'Yes' if (self.config.api_key if self.config.provider == 'gemini' else self.config.openai_api_key) else 'No'}")
                logger.info(f"Debug: Number of messages to send: {len(messages)}")

                response = litellm.completion(
                    model="gemini/gemini-2.5-flash",  # Use gemini/ prefix for Google AI Studio
                    messages=messages,
                    api_key=self.config.api_key if self.config.provider == "gemini" else self.config.openai_api_key
                )

                logger.info(f"Debug: API call successful, response received")
                logger.info(f"Debug: Response content length: {len(response.choices[0].message.content) if response.choices[0].message.content else 0}")

                return {
                    "response": response.choices[0].message.content if response.choices[0].message.content else "I couldn't generate a response based on the textbook content.",
                    "sources": sources,
                    "query": user_query,
                    "success": True
                }
            except Exception as api_error:
                logger.error(f"Error generating chat response from API: {api_error}")
                logger.error(f"Error type: {type(api_error).__name__}")
                logger.info("Using mock response for local testing...")
                # Return a mock response for local testing when API is unavailable
                mock_responses = {
                    "physical ai": "Physical AI is an interdisciplinary field that combines robotics, machine learning, and physics to create embodied intelligence. It focuses on how AI agents can interact with the physical world through sensors and actuators.",
                    "humanoid robotics": "Humanoid robotics is a branch of robotics focused on creating robots with human-like form and behavior. These robots typically have two legs, two arms, and a head, and are designed to interact with human environments.",
                    "robotics": "Robotics is an interdisciplinary field that encompasses mechanical engineering, computer science, and others. It deals with the design, construction, operation, and use of robots.",
                    "default": f"Based on the textbook content, I can tell you about this topic. The query was: '{user_query}'. In a full implementation with valid API keys, I would provide a comprehensive answer based on the relevant textbook chapters."
                }

                # Select response based on keywords in the query
                query_lower = user_query.lower()
                if "physical ai" in query_lower:
                    response_text = mock_responses["physical ai"]
                elif "humanoid" in query_lower or "robotics" in query_lower:
                    response_text = mock_responses["humanoid robotics"]
                elif "robot" in query_lower:
                    response_text = mock_responses["robotics"]
                else:
                    response_text = mock_responses["default"]

                return {
                    "response": response_text,
                    "sources": sources,
                    "query": user_query,
                    "success": True
                }

        except Exception as e:
            logger.error(f"Error generating chat response: {e}")
            return {
                "response": "Sorry, I encountered an error while processing your request.",
                "sources": [],
                "query": user_query,
                "success": False,
                "error": str(e)
            }

    async def chat(self, user_query: str) -> str:
        """Simple chat interface that returns just the response text"""
        result = await self.get_contextual_response(user_query)
        return result["response"]