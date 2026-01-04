from qdrant_client import QdrantClient
from qdrant_client.http import models
from typing import List, Dict, Optional
import logging
import os
from dotenv import load_dotenv

# Load environment variables from backend directory
load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'backend', '.env'))

logger = logging.getLogger(__name__)

class QdrantConfig:
    """Configuration for Qdrant client"""
    def __init__(self, host: str = "localhost", port: int = 6333, collection_name: str = "textbook_content"):
        self.host = host
        self.port = port
        self.collection_name = collection_name
        # Google's text-embedding-004 produces 768-dimensional vectors
        # OpenAI's text-embedding-ada-002 produces 1536-dimensional vectors
        import os
        embedding_model = os.getenv("EMBEDDING_MODEL", "text-embedding-004")
        if "text-embedding-004" in embedding_model:
            self.vector_size = 768  # Google's embedding model
        else:
            self.vector_size = 1536  # OpenAI's embedding model

class QdrantService:
    """Service class for interacting with Qdrant vector database"""

    def __init__(self, config: QdrantConfig):
        self.config = config
        self._collection_ensured = False  # Flag to track if collection has been created
        # Use remote Qdrant if URL is specified
        import os
        qdrant_url = os.getenv("QDRANT_URL", "")
        qdrant_key = os.getenv("QDRANT_KEY", "")
        
        if qdrant_url.startswith("http"):
            # Use remote Qdrant if URL is specified
            print(f"Using remote Qdrant at: {qdrant_url}")
            self.client = QdrantClient(url=qdrant_url, api_key=qdrant_key)
        elif config.host == "localhost" and config.port == 6333:
            # Use in-memory Qdrant for local testing when server not available
            try:
                # First try to connect to the actual server
                self.client = QdrantClient(host=config.host, port=config.port)
                # Test the connection
                self.client.get_collections()
                print("Connected to local Qdrant server")
            except:
                # If connection fails, use in-memory
                print("Qdrant server not available, using in-memory mode for local testing")
                self.client = QdrantClient(":memory:")
        else:
            self.client = QdrantClient(host=config.host, port=config.port)

    def _ensure_collection_exists(self):
        """Ensure the collection exists with proper configuration"""
        try:
            collections = self.client.get_collections()
            collection_names = [c.name for c in collections.collections]

            if self.config.collection_name not in collection_names:
                self.client.create_collection(
                    collection_name=self.config.collection_name,
                    vectors_config=models.VectorParams(
                        size=self.config.vector_size,
                        distance=models.Distance.COSINE
                    )
                )
                logger.info(f"Created Qdrant collection: {self.config.collection_name}")
            else:
                logger.info(f"Qdrant collection already exists: {self.config.collection_name}")
        except Exception as e:
            logger.error(f"Error ensuring collection exists: {e}")
            raise

    def _ensure_collection_exists(self):
        """Ensure the collection exists with proper configuration"""
        if self._collection_ensured:
            return  # Collection already ensured

        try:
            collections = self.client.get_collections()
            collection_names = [c.name for c in collections.collections]

            if self.config.collection_name not in collection_names:
                self.client.create_collection(
                    collection_name=self.config.collection_name,
                    vectors_config=models.VectorParams(
                        size=self.config.vector_size,
                        distance=models.Distance.COSINE
                    )
                )
                logger.info(f"Created Qdrant collection: {self.config.collection_name}")
            else:
                logger.info(f"Qdrant collection already exists: {self.config.collection_name}")
            self._collection_ensured = True
        except Exception as e:
            logger.error(f"Error ensuring collection exists: {e}")
            raise

    def store_embeddings(self, ids: List[str], vectors: List[List[float]], payloads: List[Dict]):
        """Store embeddings in Qdrant"""
        try:
            # Ensure collection exists before storing
            self._ensure_collection_exists()
            # Use string IDs directly (Qdrant supports string IDs)
            self.client.upsert(
                collection_name=self.config.collection_name,
                points=models.Batch(
                    ids=ids,
                    vectors=vectors,
                    payloads=payloads
                )
            )
            logger.info(f"Stored {len(ids)} embeddings in Qdrant")
        except Exception as e:
            logger.error(f"Error storing embeddings: {e}")
            raise

    def search_similar(self, query_vector: List[float], limit: int = 5) -> List[Dict]:
        """Search for similar content based on query vector"""
        try:
            # Ensure collection exists before searching
            self._ensure_collection_exists()
            results = self.client.search(
                collection_name=self.config.collection_name,
                query_vector=query_vector,
                limit=limit
            )

            return [
                {
                    "id": result.id,
                    "payload": result.payload,
                    "score": result.score
                }
                for result in results
            ]
        except Exception as e:
            logger.error(f"Error searching for similar content: {e}")
            raise

    def delete_collection(self):
        """Delete the collection (useful for testing/reinitialization)"""
        try:
            self.client.delete_collection(collection_name=self.config.collection_name)
            logger.info(f"Deleted Qdrant collection: {self.config.collection_name}")
        except Exception as e:
            logger.error(f"Error deleting collection: {e}")
            raise