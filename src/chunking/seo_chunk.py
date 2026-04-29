"""
SEO-focused chunking module.
Breaks content into short, snippet-ready paragraphs and blocks.
"""

import re
from typing import List, Dict
from utils.helpers import split_into_sentences, count_words, truncate_text


class SEOChunker:
    def __init__(self, max_paragraph_words: int = 60, max_snippet_words: int = 60):
        self.max_paragraph_words = max_paragraph_words
        self.max_snippet_words = max_snippet_words

    def chunk_paragraphs(self, text: str) -> List[str]:
        """Split long paragraphs into shorter SEO-friendly chunks."""
        sentences = split_into_sentences(text)
        chunks = []
        current_chunk = []

        for sentence in sentences:
            current_chunk.append(sentence)
            if count_words(' '.join(current_chunk)) >= self.max_paragraph_words:
                chunks.append(' '.join(current_chunk))
                current_chunk = []

        if current_chunk:
            chunks.append(' '.join(current_chunk))

        return chunks

    def create_snippet_blocks(self, text: str) -> List[Dict[str, str]]:
        """Create snippet-ready blocks (40-60 words)."""
        sentences = split_into_sentences(text)
        blocks = []
        current_block = []

        for sentence in sentences:
            current_block.append(sentence)
            word_count = count_words(' '.join(current_block))
            if word_count >= 40:
                block_text = ' '.join(current_block)
                if word_count <= self.max_snippet_words:
                    blocks.append({
                        'type': 'snippet',
                        'text': block_text,
                        'word_count': word_count
                    })
                else:
                    blocks.append({
                        'type': 'snippet',
                        'text': truncate_text(block_text, self.max_snippet_words),
                        'word_count': self.max_snippet_words
                    })
                current_block = []

        if current_block:
            block_text = ' '.join(current_block)
            word_count = count_words(block_text)
            if word_count <= self.max_snippet_words:
                blocks.append({
                    'type': 'snippet',
                    'text': block_text,
                    'word_count': word_count
                })

        return blocks

    def chunk_by_headings(self, headings: List[str], paragraphs: List[str]) -> List[Dict[str, any]]:
        """Group paragraphs under their nearest heading."""
        chunks = []
        current_heading = 'Introduction'
        current_paragraphs = []

        para_idx = 0
        for para in paragraphs:
            # Simple heuristic: if paragraph starts with a heading text, create new chunk
            assigned = False
            for h in headings:
                if para.lower().startswith(h.lower()):
                    if current_paragraphs:
                        chunks.append({
                            'heading': current_heading,
                            'paragraphs': current_paragraphs
                        })
                    current_heading = h
                    current_paragraphs = []
                    assigned = True
                    break

            if not assigned:
                current_paragraphs.append(para)

        if current_paragraphs:
            chunks.append({
                'heading': current_heading,
                'paragraphs': current_paragraphs
            })

        return chunks

    def create_definition_blocks(self, text: str) -> List[Dict[str, str]]:
        """Extract definition-style blocks (X is ...)."""
        pattern = re.compile(r'([A-Z][A-Za-z\s]{1,30})\s+is\s+([^\.]{10,200}\.)')
        matches = pattern.findall(text)
        blocks = []
        for match in matches:
            term, definition = match
            blocks.append({
                'type': 'definition',
                'term': term.strip(),
                'definition': definition.strip(),
                'word_count': count_words(definition)
            })
        return blocks

    def optimize_content(self, cleaned_data: Dict[str, any]) -> Dict[str, any]:
        """Run full SEO chunking pipeline on cleaned content."""
        full_text = ' '.join(cleaned_data.get('paragraphs', []))

        result = {
            'title': cleaned_data.get('title', ''),
            'meta_description': cleaned_data.get('meta_description', ''),
            'heading_chunks': self.chunk_by_headings(
                cleaned_data.get('h2', []) + cleaned_data.get('h3', []),
                cleaned_data.get('paragraphs', [])
            ),
            'snippet_blocks': self.create_snippet_blocks(full_text),
            'definition_blocks': self.create_definition_blocks(full_text),
            'short_paragraphs': self.chunk_paragraphs(full_text),
            'lists': cleaned_data.get('lists', []),
            'links': cleaned_data.get('links', [])
        }
        return result
