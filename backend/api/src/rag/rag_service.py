from typing import List, Dict, Optional
from .qdrant_service import QdrantService, QdrantConfig
from .embedding_service import EmbeddingService, EmbeddingConfig
from .chunker import ContentChunker
from .sqlite_service import SQLiteService
import logging
import asyncio
import os

logger = logging.getLogger(__name__)

class RAGService:
    """Main service to coordinate RAG system components"""

    def __init__(self):
        self.qdrant_config = QdrantConfig()
        self.qdrant_service = QdrantService(self.qdrant_config)

        # Check if we should use Postgres or SQLite
        self.use_postgres = self._check_postgres_availability()
        if self.use_postgres:
            from .postgres_service import PostgresService, PostgresConfig
            self.postgres_config = PostgresConfig()
            self.postgres_service = PostgresService(self.postgres_config)
        else:
            print("PostgreSQL not available, using SQLite for local testing")
            self.postgres_service = SQLiteService()
            self.postgres_service.initialize()

        self.embedding_config = EmbeddingConfig()
        self.embedding_service = EmbeddingService(self.embedding_config)

        self.chunker = ContentChunker()

    def _check_postgres_availability(self):
        """Check if Postgres is available, otherwise use SQLite"""
        try:
            # Try to import and check if we can connect to Postgres
            import asyncpg
            # Check if environment variables for Postgres are properly set
            import os
            host = os.getenv("NEON_HOST", "localhost")
            port = int(os.getenv("NEON_PORT", "5432"))

            # For local testing, if it's the default localhost, assume it's not available
            if host == "localhost" and port == 5432:
                # Check if this is just the default, meaning user might not have Postgres running
                return False
            else:
                # If user has specified a different host/port, assume they have it configured
                return True
        except ImportError:
            # If asyncpg is not available, use SQLite
            return False
        except Exception:
            # If there's any error checking, default to SQLite
            return False

    async def initialize(self):
        """Initialize all services"""
        if self.use_postgres:
            await self.postgres_service.initialize()
        logger.info("RAG Service initialized")

    async def process_and_store_content(self, chapter_id: str, content: str) -> Dict:
        """
        Process content by chunking, embedding, and storing in both Qdrant and Postgres
        """
        try:
            # 1. Chunk the content
            chunks = self.chunker.chunk_markdown(content, chapter_id)
            logger.info(f"Chunked content into {len(chunks)} chunks")

            # 2. Generate embeddings for chunks
            processed_chunks = self.embedding_service.process_content_chunks(chunks)
            logger.info(f"Generated embeddings for {len(processed_chunks)} chunks")

            # 3. Prepare data for storage
            chunk_ids = []
            vectors = []
            qdrant_payloads = []
            postgres_chunks = []

            for chunk in processed_chunks:
                chunk_ids.append(chunk['embedding_id'])
                vectors.append(chunk['embedding'])

                # Prepare payload for Qdrant
                qdrant_payload = {
                    'chunk_id': chunk['chunk_id'],
                    'content': chunk['content'],
                    'chapter_id': chapter_id,
                    'content_hash': chunk['content_hash'],
                    **chunk['metadata']
                }
                qdrant_payloads.append(qdrant_payload)

                # Prepare data for Postgres
                postgres_chunk = {
                    'chunk_id': chunk['chunk_id'],
                    'chapter_id': chapter_id,
                    'content': chunk['content'],
                    'metadata': chunk['metadata']
                }
                postgres_chunks.append(postgres_chunk)

            # 4. Store embeddings in Qdrant
            self.qdrant_service.store_embeddings(chunk_ids, vectors, qdrant_payloads)
            logger.info(f"Stored {len(chunk_ids)} embeddings in Qdrant")

            # 5. Store content chunks in Postgres
            for i, chunk_data in enumerate(postgres_chunks):
                # Get the corresponding processed chunk to access the embedding_id
                processed_chunk = processed_chunks[i]

                await self.postgres_service.store_content_chunk(
                    chunk_data['chunk_id'],
                    chunk_data['chapter_id'],
                    chunk_data['content'],
                    chunk_data['metadata']
                )

                # Store embedding metadata in Postgres
                await self.postgres_service.store_embedding_metadata(
                    chunk_data['chunk_id'],
                    processed_chunk['embedding_id'],  # Use the proper embedding_id from processed chunk
                    self.embedding_service.calculate_content_hash(chunk_data['content']),
                    chapter_title=chunk_data['metadata'].get('section_title'),
                    section_title=chunk_data['metadata'].get('section_title')
                )

            logger.info(f"Successfully processed and stored content for chapter {chapter_id}")

            return {
                "success": True,
                "chapter_id": chapter_id,
                "chunks_processed": len(processed_chunks),
                "message": f"Successfully processed and stored {len(processed_chunks)} content chunks"
            }

        except Exception as e:
            logger.error(f"Error processing and storing content: {e}")
            return {
                "success": False,
                "chapter_id": chapter_id,
                "error": str(e),
                "message": f"Error processing content: {str(e)}"
            }

    async def search_content(self, query: str, limit: int = 5) -> List[Dict]:
        """
        Search for content using the RAG system
        """
        try:
            # 1. Generate embedding for query
            query_embedding = self.embedding_service.generate_embedding(query)

            # 2. Search in Qdrant for similar content
            search_results = self.qdrant_service.search_similar(query_embedding, limit)

            # 3. Enhance results with metadata from Postgres
            enhanced_results = []
            for result in search_results:
                chunk_id = result['payload'].get('chunk_id')
                if chunk_id:
                    chunk_detail = await self.postgres_service.get_content_chunk(chunk_id)
                    if chunk_detail:
                        enhanced_result = {
                            **result,
                            'content_detail': chunk_detail
                        }
                        enhanced_results.append(enhanced_result)
                    else:
                        enhanced_results.append(result)
                else:
                    enhanced_results.append(result)

            logger.info(f"Search completed with {len(enhanced_results)} results")
            return enhanced_results

        except Exception as e:
            logger.error(f"Error searching content: {e}")
            # Return empty results instead of raising an exception
            return []

    async def close(self):
        """Close all services"""
        if self.use_postgres:
            await self.postgres_service.close()
        else:
            # For SQLite, call the close method directly (it's synchronous)
            self.postgres_service.close()
        logger.info("RAG Service closed")