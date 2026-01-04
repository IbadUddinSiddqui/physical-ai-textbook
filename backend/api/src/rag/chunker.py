import re
from typing import List, Dict
# Remove the relative import since ContentChunk is not used in this file

class ContentChunker:
    """Algorithm for chunking book content into manageable pieces for embedding"""

    def __init__(self, chunk_size: int = 1000, overlap: int = 100):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk_text(self, text: str, chapter_id: str) -> List[Dict]:
        """
        Chunk the text into smaller pieces with overlap.

        Args:
            text: The text to be chunked
            chapter_id: The identifier for the chapter

        Returns:
            List of dictionaries containing chunk information
        """
        # Split text by paragraphs first
        paragraphs = text.split('\n\n')

        # If paragraphs are too large, split by sentences
        sentences = []
        for para in paragraphs:
            if len(para) <= self.chunk_size:
                sentences.append(para)
            else:
                # Split by sentences if paragraph is too large
                para_sentences = re.split(r'[.!?]+\s+', para)
                current_chunk = ""

                for sentence in para_sentences:
                    if len(current_chunk + " " + sentence) <= self.chunk_size:
                        current_chunk += " " + sentence if current_chunk else sentence
                    else:
                        if current_chunk:
                            sentences.append(current_chunk.strip())
                        current_chunk = sentence

                if current_chunk:
                    sentences.append(current_chunk.strip())

        chunks = []
        current_pos = 0

        while current_pos < len(sentences):
            chunk_text = ""
            start_pos = current_pos

            # Add sentences until we reach the chunk size
            while current_pos < len(sentences):
                sentence = sentences[current_pos]
                if len(chunk_text + " " + sentence) <= self.chunk_size or current_pos == start_pos:
                    chunk_text += " " + sentence if chunk_text else sentence
                    current_pos += 1
                else:
                    break

            # Create chunk with overlap if possible
            if start_pos > 0 and self.overlap > 0:
                # Add overlap from previous chunk
                overlap_start = max(0, start_pos - self.overlap)
                overlap_text = " ".join(sentences[overlap_start:start_pos])
                chunk_text = overlap_text + " " + chunk_text

            import uuid
            chunk_id = str(uuid.uuid4())

            chunk_data = {
                "chunk_id": chunk_id,
                "chapter_id": chapter_id,
                "content": chunk_text.strip(),
                "metadata": {
                    "position": len(chunks),
                    "original_length": len(text),
                    "chunk_size": len(chunk_text),
                    "type": "text"
                }
            }

            chunks.append(chunk_data)

        return chunks

    def chunk_markdown(self, markdown_text: str, chapter_id: str) -> List[Dict]:
        """
        Specialized chunking for markdown content, preserving structure.

        Args:
            markdown_text: The markdown text to be chunked
            chapter_id: The identifier for the chapter

        Returns:
            List of dictionaries containing chunk information
        """
        # Split by markdown headers to maintain content structure
        header_pattern = r'^(#{1,6})\s+(.+)$'
        lines = markdown_text.split('\n')

        sections = []
        current_section = {'header': '', 'content': [], 'level': 0}

        for line in lines:
            match = re.match(header_pattern, line.strip())
            if match:
                # Save previous section if it has content
                if current_section['content']:
                    sections.append(current_section.copy())

                # Start new section
                header_level = len(match.group(1))
                header_text = match.group(2)
                current_section = {
                    'header': header_text,
                    'content': [line],
                    'level': header_level
                }
            else:
                current_section['content'].append(line)

        # Add the last section
        if current_section['content']:
            sections.append(current_section)

        # Convert sections to chunks
        chunks = []
        for i, section in enumerate(sections):
            section_text = '\n'.join(section['content']).strip()

            # If section is too large, further chunk it
            if len(section_text) > self.chunk_size:
                # Use regular text chunking for large sections
                import uuid
                temp_chunks = self.chunk_text(section_text, str(uuid.uuid4()))
                for chunk in temp_chunks:
                    chunk['metadata']['section_title'] = section['header']
                    chunks.append(chunk)
            else:
                import uuid
                chunk_id = str(uuid.uuid4())
                chunk_data = {
                    "chunk_id": chunk_id,
                    "chapter_id": chapter_id,
                    "content": section_text,
                    "metadata": {
                        "section_title": section['header'],
                        "section_level": section['level'],
                        "position": i,
                        "type": "markdown_section"
                    }
                }
                chunks.append(chunk_data)

        return chunks