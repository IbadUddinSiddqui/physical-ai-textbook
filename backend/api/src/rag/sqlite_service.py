import sqlite3
import json
import os
from typing import List, Dict, Optional
import logging
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class SQLiteService:
    """SQLite-based alternative for local testing instead of Postgres"""

    def __init__(self, db_path: str = "textbook_rag.db"):
        self.db_path = db_path
        self.conn = None

    def initialize(self):
        """Initialize the SQLite database and create tables"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row  # This allows accessing columns by name
            self._ensure_tables_exist()
            logger.info("SQLite database initialized")
        except Exception as e:
            logger.error(f"Error initializing SQLite database: {e}")
            raise

    def _ensure_tables_exist(self):
        """Ensure required tables exist in SQLite"""
        if not self.conn:
            raise Exception("SQLite connection not initialized")

        # Create content_chunks table
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS content_chunks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chunk_id TEXT UNIQUE NOT NULL,
                chapter_id TEXT NOT NULL,
                content TEXT NOT NULL,
                metadata TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create embeddings_metadata table
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS embeddings_metadata (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chunk_id TEXT,
                embedding_id TEXT UNIQUE NOT NULL,
                content_hash TEXT NOT NULL,
                chapter_title TEXT,
                section_title TEXT,
                page_number INTEGER,
                source_file TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (chunk_id) REFERENCES content_chunks(chunk_id)
            )
        """)

        # Create indexes
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_chunk_id ON content_chunks(chunk_id)")
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_chapter_id ON content_chunks(chapter_id)")
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_embedding_id ON embeddings_metadata(embedding_id)")
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_content_hash ON embeddings_metadata(content_hash)")

        self.conn.commit()
        logger.info("SQLite tables created/verified")

    def store_content_chunk(self, chunk_id: str, chapter_id: str, content: str, metadata: Dict):
        """Store a content chunk in the database"""
        if not self.conn:
            raise Exception("SQLite connection not initialized")

        try:
            # Convert metadata to JSON string
            metadata_json = json.dumps(metadata)

            self.conn.execute("""
                INSERT OR REPLACE INTO content_chunks
                (chunk_id, chapter_id, content, metadata, updated_at)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (chunk_id, chapter_id, content, metadata_json))

            self.conn.commit()
            logger.info(f"Stored content chunk: {chunk_id}")
        except Exception as e:
            logger.error(f"Error storing content chunk: {e}")
            raise

    def store_embedding_metadata(self, chunk_id: str, embedding_id: str, content_hash: str,
                               chapter_title: str = None, section_title: str = None,
                               page_number: int = None, source_file: str = None):
        """Store embedding metadata in the database"""
        if not self.conn:
            raise Exception("SQLite connection not initialized")

        try:
            self.conn.execute("""
                INSERT OR REPLACE INTO embeddings_metadata
                (chunk_id, embedding_id, content_hash, chapter_title, section_title, page_number, source_file)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (chunk_id, embedding_id, content_hash, chapter_title, section_title, page_number, source_file))

            self.conn.commit()
            logger.info(f"Stored embedding metadata: {embedding_id}")
        except Exception as e:
            logger.error(f"Error storing embedding metadata: {e}")
            raise

    def get_content_chunk(self, chunk_id: str) -> Optional[Dict]:
        """Retrieve a content chunk by ID"""
        if not self.conn:
            raise Exception("SQLite connection not initialized")

        try:
            cursor = self.conn.execute("""
                SELECT chunk_id, chapter_id, content, metadata, created_at, updated_at
                FROM content_chunks WHERE chunk_id = ?
            """, (chunk_id,))

            row = cursor.fetchone()
            if row:
                result = dict(row)
                # Convert metadata JSON string back to dict
                result['metadata'] = json.loads(result['metadata']) if result['metadata'] else {}
                return result
            return None
        except Exception as e:
            logger.error(f"Error retrieving content chunk: {e}")
            raise

    def get_embedding_metadata(self, embedding_id: str) -> Optional[Dict]:
        """Retrieve embedding metadata by ID"""
        if not self.conn:
            raise Exception("SQLite connection not initialized")

        try:
            cursor = self.conn.execute("""
                SELECT * FROM embeddings_metadata WHERE embedding_id = ?
            """, (embedding_id,))

            row = cursor.fetchone()
            if row:
                return dict(row)
            return None
        except Exception as e:
            logger.error(f"Error retrieving embedding metadata: {e}")
            raise

    def get_chunks_by_chapter(self, chapter_id: str) -> List[Dict]:
        """Retrieve all content chunks for a specific chapter"""
        if not self.conn:
            raise Exception("SQLite connection not initialized")

        try:
            cursor = self.conn.execute("""
                SELECT chunk_id, chapter_id, content, metadata, created_at, updated_at
                FROM content_chunks WHERE chapter_id = ?
            """, (chapter_id,))

            rows = cursor.fetchall()
            results = []
            for row in rows:
                result = dict(row)
                # Convert metadata JSON string back to dict
                result['metadata'] = json.loads(result['metadata']) if result['metadata'] else {}
                results.append(result)
            return results
        except Exception as e:
            logger.error(f"Error retrieving chunks by chapter: {e}")
            raise

    def close(self):
        """Close the database connection"""
        if self.conn:
            self.conn.close()
            logger.info("SQLite connection closed")