import asyncio
import os
from pathlib import Path
import sys
import os

# Add the backend/api/src directory to Python path to allow imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from rag.rag_service import RAGService

async def load_and_process_book_content():
    """Load all book content from the Docusaurus docs and process it through the RAG system"""
    rag_service = RAGService()
    await rag_service.initialize()

    try:
        # Path to the Docusaurus docs directory
        docs_path = Path("../../../frontend/docusaurus/docs")

        if not docs_path.exists():
            print(f"Docs directory not found at {docs_path.absolute()}")
            return

        # Process each chapter
        for chapter_dir in docs_path.iterdir():
            if chapter_dir.is_dir() and chapter_dir.name.startswith("chapter-"):
                print(f"Processing {chapter_dir.name}...")

                # Process all MD/MDX files in the chapter
                for file_path in chapter_dir.glob("*.md*"):  # .md or .mdx
                    print(f"  Processing {file_path.name}...")

                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # Use the directory name as chapter ID
                    chapter_id = chapter_dir.name

                    # Process and store the content
                    result = await rag_service.process_and_store_content(
                        chapter_id,
                        content
                    )

                    print(f"    Result: {result['message']}")

        print("All book content has been processed and stored in the RAG system.")

    except Exception as e:
        print(f"Error processing book content: {e}")
    finally:
        await rag_service.close()

if __name__ == "__main__":
    asyncio.run(load_and_process_book_content())