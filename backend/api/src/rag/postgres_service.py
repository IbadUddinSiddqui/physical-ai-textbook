import asyncpg
import os
from typing import List, Dict, Optional
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class PostgresConfig:
    """Configuration for Postgres connection"""
    def __init__(self,
                 host: str = os.getenv("NEON_HOST", "localhost"),
                 port: int = int(os.getenv("NEON_PORT", "5432")),
                 database: str = os.getenv("NEON_DATABASE", "textbook_rag"),
                 username: str = os.getenv("NEON_USER", "postgres"),
                 password: str = os.getenv("NEON_PASSWORD", ""),
                 ssl_mode: str = os.getenv("NEON_SSL_MODE", "require")):
        self.host = host
        self.port = port
        self.database = database
        self.username = username
        self.password = password
        self.ssl_mode = ssl_mode
        self.dsn = f"postgresql://{username}:{password}@{host}:{port}/{database}?sslmode={ssl_mode}"

class PostgresService:
    """Service class for interacting with Neon Postgres database"""

    def __init__(self, config: PostgresConfig):
        self.config = config
        self.pool = None

    async def initialize(self):
        """Initialize the connection pool"""
        try:
            self.pool = await asyncpg.create_pool(
                dsn=self.config.dsn,
                min_size=1,
                max_size=10,
                command_timeout=60
            )
            await self._ensure_tables_exist()
            logger.info("Postgres connection pool initialized")
        except Exception as e:
            logger.error(f"Error initializing Postgres connection: {e}")
            raise

    async def _ensure_tables_exist(self):
        """Ensure required tables exist"""
        if not self.pool:
            raise Exception("Postgres connection not initialized")

        async with self.pool.acquire() as conn:
            # Create content_chunks table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS content_chunks (
                    id SERIAL PRIMARY KEY,
                    chunk_id TEXT UNIQUE NOT NULL,
                    chapter_id TEXT NOT NULL,
                    content TEXT NOT NULL,
                    metadata JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Create embeddings_metadata table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS embeddings_metadata (
                    id SERIAL PRIMARY KEY,
                    chunk_id TEXT REFERENCES content_chunks(chunk_id),
                    embedding_id TEXT UNIQUE NOT NULL,
                    content_hash TEXT NOT NULL,
                    chapter_title TEXT,
                    section_title TEXT,
                    page_number INTEGER,
                    source_file TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Create indexes for better performance
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_chunk_id ON content_chunks(chunk_id)")
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_chapter_id ON content_chunks(chapter_id)")
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_embedding_id ON embeddings_metadata(embedding_id)")
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_content_hash ON embeddings_metadata(content_hash)")

            logger.info("Postgres tables created/verified")

    async def store_content_chunk(self, chunk_id: str, chapter_id: str, content: str, metadata: Dict):
        """Store a content chunk in the database"""
        if not self.pool:
            raise Exception("Postgres connection not initialized")

        async with self.pool.acquire() as conn:
            try:
                import json
                # Convert metadata dict to JSON string for proper storage
                metadata_json = json.dumps(metadata) if metadata else '{}'
                
                await conn.execute("""
                    INSERT INTO content_chunks (chunk_id, chapter_id, content, metadata)
                    VALUES ($1, $2, $3, $4::jsonb)
                    ON CONFLICT (chunk_id)
                    DO UPDATE SET content = $3, metadata = $4::jsonb, updated_at = CURRENT_TIMESTAMP
                """, chunk_id, chapter_id, content, metadata_json)

                logger.info(f"Stored content chunk: {chunk_id}")
            except Exception as e:
                logger.error(f"Error storing content chunk: {e}")
                raise

    async def store_embedding_metadata(self, chunk_id: str, embedding_id: str, content_hash: str,
                                     chapter_title: str = None, section_title: str = None,
                                     page_number: int = None, source_file: str = None):
        """Store embedding metadata in the database"""
        if not self.pool:
            raise Exception("Postgres connection not initialized")

        async with self.pool.acquire() as conn:
            try:
                await conn.execute("""
                    INSERT INTO embeddings_metadata
                    (chunk_id, embedding_id, content_hash, chapter_title, section_title, page_number, source_file)
                    VALUES ($1, $2, $3, $4, $5, $6, $7)
                    ON CONFLICT (embedding_id)
                    DO UPDATE SET
                        chunk_id = $1,
                        content_hash = $3,
                        chapter_title = $4,
                        section_title = $5,
                        page_number = $6,
                        source_file = $7
                """, chunk_id, embedding_id, content_hash, chapter_title, section_title, page_number, source_file)

                logger.info(f"Stored embedding metadata: {embedding_id}")
            except Exception as e:
                logger.error(f"Error storing embedding metadata: {e}")
                raise

    async def get_content_chunk(self, chunk_id: str) -> Optional[Dict]:
        """Retrieve a content chunk by ID"""
        if not self.pool:
            raise Exception("Postgres connection not initialized")

        async with self.pool.acquire() as conn:
            try:
                row = await conn.fetchrow("""
                    SELECT chunk_id, chapter_id, content, metadata, created_at, updated_at
                    FROM content_chunks WHERE chunk_id = $1
                """, chunk_id)

                if row:
                    return dict(row)
                return None
            except Exception as e:
                logger.error(f"Error retrieving content chunk: {e}")
                raise

    async def get_embedding_metadata(self, embedding_id: str) -> Optional[Dict]:
        """Retrieve embedding metadata by ID"""
        if not self.pool:
            raise Exception("Postgres connection not initialized")

        async with self.pool.acquire() as conn:
            try:
                row = await conn.fetchrow("""
                    SELECT * FROM embeddings_metadata WHERE embedding_id = $1
                """, embedding_id)

                if row:
                    return dict(row)
                return None
            except Exception as e:
                logger.error(f"Error retrieving embedding metadata: {e}")
                raise

    async def get_chunks_by_chapter(self, chapter_id: str) -> List[Dict]:
        """Retrieve all content chunks for a specific chapter"""
        if not self.pool:
            raise Exception("Postgres connection not initialized")

        async with self.pool.acquire() as conn:
            try:
                rows = await conn.fetch("""
                    SELECT chunk_id, chapter_id, content, metadata, created_at, updated_at
                    FROM content_chunks WHERE chapter_id = $1
                """, chapter_id)

                return [dict(row) for row in rows]
            except Exception as e:
                logger.error(f"Error retrieving chunks by chapter: {e}")
                raise

    async def close(self):
        """Close the connection pool"""
        if self.pool:
            await self.pool.close()
            logger.info("Postgres connection pool closed")