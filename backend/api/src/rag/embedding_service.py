import openai
import hashlib
from typing import List, Dict
import os
from dotenv import load_dotenv
import logging
import litellm

# Load environment variables from backend directory
load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'backend', '.env'))

logger = logging.getLogger(__name__)

class EmbeddingConfig:
    """Configuration for embedding generation using LiteLLM with Google models"""
    def __init__(self):
        self.model = os.getenv("EMBEDDING_MODEL", "text-embedding-004")  # Using OpenAI model as default
        self.api_key = os.getenv("OPENAI_API_KEY")
        # Hardcode your actual API key directly
        self.google_api_key = "AIzaSyBVOhQruC5HuaRO4zZNe_wLSWZRH1horKo"  # Your actual API key

        # Debug logging for embedding API key loading
        logger.info(f"Debug: EMBEDDING_MODEL environment variable: {os.getenv('EMBEDDING_MODEL')}")
        logger.info(f"Debug: OPENAI_API_KEY environment variable exists: {bool(self.api_key)}")
        logger.info(f"Debug: GEMINI_API_KEY environment variable exists: {bool(self.google_api_key)}")
        logger.info(f"Debug: Loaded embedding model: {self.model}")
        logger.info(f"Debug: Google API key length (if exists): {len(self.google_api_key) if self.google_api_key else 'None'}")
        logger.info(f"Debug: OpenAI API key length (if exists): {len(self.api_key) if self.api_key else 'None'}")

        # Configure LiteLLM for Google models - using hardcoded key
        if self.google_api_key and self.google_api_key != "YOUR_GEMINI_API_KEY_HERE" and len(self.google_api_key) > 10:
            # Using the hardcoded Google API key
            litellm.set_verbose = False  # Set to True for debugging
            self.use_google = True
            self.model = "text-embedding-004"  # Using OpenAI compatible model name for Google
            logger.info(f"Debug: Using Google embeddings with model: {self.model}")
        elif self.api_key:
            # Using OpenAI API key
            self.use_google = False
            logger.info(f"Debug: Using OpenAI embeddings with model: {self.model}")
        else:
            self.use_google = False
            logger.info(f"Debug: Using OpenAI embeddings with model: {self.model}")
            if not (self.api_key or (self.google_api_key and self.google_api_key != "YOUR_GEMINI_API_KEY_HERE")):
                logger.error("Error: Neither OPENAI_API_KEY nor GEMINI_API_KEY is set for embeddings")
                raise ValueError("Either OPENAI_API_KEY or GEMINI_API_KEY must be set")

class EmbeddingService:
    """Service for generating embeddings for content chunks using LiteLLM for multi-provider support"""

    def __init__(self, config: EmbeddingConfig):
        self.config = config

    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text using LiteLLM or mock for local testing"""
        try:
            # Debug logging for embedding generation
            logger.info(f"Debug: Attempting to generate embedding")
            logger.info(f"Debug: Using provider: {'Google' if self.config.use_google else 'OpenAI'}")
            logger.info(f"Debug: Using model: {self.config.model}")
            logger.info(f"Debug: Text length for embedding: {len(text)}")
            logger.info(f"Debug: API key available: {'Yes' if (self.config.google_api_key if self.config.use_google else self.config.api_key) else 'No'}")

            # Using LiteLLM to call Google embedding model through OpenAI-compatible interface
            if self.config.use_google:
                # Configure LiteLLM to use Google's embedding model
                logger.info(f"Debug: Calling Google embedding API with model: text-embedding-004")
                response = litellm.embedding(
                    model="text-embedding-004",  # Google's embedding model via LiteLLM
                    input=[text],  # Input should be a list for embeddings
                    api_key=self.config.google_api_key,
                    custom_llm_provider="gemini"
                )
                logger.info(f"Debug: Google embedding API call successful")
            else:
                # Use OpenAI
                logger.info(f"Debug: Calling OpenAI embedding API with model: {self.config.model}")
                client = openai.OpenAI(api_key=self.config.api_key)
                response = client.embeddings.create(
                    input=text,
                    model=self.config.model
                )
                logger.info(f"Debug: OpenAI embedding API call successful")

            return response.data[0].embedding
        except Exception as e:
            logger.warning(f"Error generating embedding from API: {e}")
            logger.warning(f"Error type: {type(e).__name__}")
            logger.info("Using mock embedding for local testing...")
            # Return a mock embedding for local testing
            import numpy as np
            # Generate a deterministic mock embedding based on the text hash
            text_hash = hash(text) % (2**32)
            np.random.seed(abs(text_hash))
            # Use correct dimensions based on the model
            if "text-embedding-004" in self.config.model:
                return np.random.random(768).tolist()  # Google's embedding model
            else:
                return np.random.random(1536).tolist()  # OpenAI's embedding model

    def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a batch of texts"""
        try:
            # Debug logging for batch embedding generation
            logger.info(f"Debug: Attempting to generate batch embeddings for {len(texts)} texts")
            logger.info(f"Debug: Using provider: {'Google' if self.config.use_google else 'OpenAI'}")
            logger.info(f"Debug: Using model: {self.config.model}")
            logger.info(f"Debug: API key available: {'Yes' if (self.config.google_api_key if self.config.use_google else self.config.api_key) else 'No'}")

            if self.config.use_google:
                # Using LiteLLM for Google models
                logger.info(f"Debug: Calling Google batch embedding API with model: text-embedding-004")
                response = litellm.embedding(
                    model="text-embedding-004",
                    input=texts,
                    api_key=self.config.google_api_key,
                    custom_llm_provider="gemini"
                )
                logger.info(f"Debug: Google batch embedding API call successful")
            else:
                # Use OpenAI
                logger.info(f"Debug: Calling OpenAI batch embedding API with model: {self.config.model}")
                client = openai.OpenAI(api_key=self.config.api_key)
                response = client.embeddings.create(
                    input=texts,
                    model=self.config.model
                )
                logger.info(f"Debug: OpenAI batch embedding API call successful")

            return [item.embedding for item in response.data]
        except Exception as e:
            logger.warning(f"Error generating batch embeddings from API: {e}")
            logger.warning(f"Error type: {type(e).__name__}")
            logger.info("Using mock embeddings for local testing...")
            # Generate mock embeddings for local testing
            import numpy as np
            embeddings = []
            for text in texts:
                text_hash = hash(text) % (2**32)
                np.random.seed(abs(text_hash))
                # Use correct dimensions based on the model
                if "text-embedding-004" in self.config.model:
                    embeddings.append(np.random.random(768).tolist())  # Google's embedding model
                else:
                    embeddings.append(np.random.random(1536).tolist())  # OpenAI's embedding model
            return embeddings

    def calculate_content_hash(self, content: str) -> str:
        """Calculate hash of content for identification"""
        return hashlib.sha256(content.encode()).hexdigest()

    def process_content_chunks(self, chunks: List[Dict]) -> List[Dict]:
        """
        Process content chunks to generate embeddings and metadata

        Args:
            chunks: List of content chunks

        Returns:
            List of processed chunks with embeddings and metadata
        """
        processed_chunks = []

        # Extract all text contents for batch processing if using OpenAI
        if not self.config.use_google:
            texts = [chunk['content'] for chunk in chunks]
            embeddings = self.generate_embeddings_batch(texts)

            for i, chunk in enumerate(chunks):
                content_hash = self.calculate_content_hash(chunk['content'])
                # Generate a UUID for Qdrant compatibility
                import uuid
                embedding_id = str(uuid.uuid4())

                processed_chunk = {
                    'chunk_id': chunk['chunk_id'],
                    'embedding_id': embedding_id,
                    'content': chunk['content'],
                    'embedding': embeddings[i],
                    'content_hash': content_hash,
                    'metadata': {
                        **chunk.get('metadata', {}),
                        'chunk_id': chunk['chunk_id'],
                        'content_hash': content_hash,
                        'embedding_id': embedding_id
                    }
                }

                processed_chunks.append(processed_chunk)
        else:
            # For Google models, process one by one to avoid potential batch issues
            for i, chunk in enumerate(chunks):
                content_hash = self.calculate_content_hash(chunk['content'])
                # Generate a UUID for Qdrant compatibility
                import uuid
                embedding_id = str(uuid.uuid4())

                # Generate embedding for this specific chunk
                embedding = self.generate_embedding(chunk['content'])

                processed_chunk = {
                    'chunk_id': chunk['chunk_id'],
                    'embedding_id': embedding_id,
                    'content': chunk['content'],
                    'embedding': embedding,
                    'content_hash': content_hash,
                    'metadata': {
                        **chunk.get('metadata', {}),
                        'chunk_id': chunk['chunk_id'],
                        'content_hash': content_hash,
                        'embedding_id': embedding_id
                    }
                }

                processed_chunks.append(processed_chunk)

        logger.info(f"Processed {len(processed_chunks)} chunks with embeddings")
        return processed_chunks