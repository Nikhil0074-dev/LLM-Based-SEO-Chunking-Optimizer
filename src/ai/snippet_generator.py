"""
Featured Snippet Generator.
Creates 40-60 word answers, bullet lists, and step-by-step guides.
"""

import re
from typing import List, Dict
from utils.helpers import split_into_sentences, count_words, truncate_text


class SnippetGenerator:
    def __init__(self, max_words: int = 60):
        self.max_words = max_words

    def generate_definition_snippet(self, text: str) -> Dict[str, str]:
        """Generate a definition-style snippet (X is ...)."""
        sentences = split_into_sentences(text)
        for sent in sentences:
            match = re.match(r'^([A-Z][a-zA-Z\s]{1,30})\s+is\s+(.+)$', sent)
            if match:
                term, definition = match.groups()
                definition = truncate_text(definition, self.max_words)
                return {
                    'type': 'definition',
                    'term': term.strip(),
                    'answer': definition,
                    'word_count': count_words(definition)
                }
        return {}

    def generate_list_snippet(self, items: List[str]) -> Dict[str, any]:
        """Generate a bullet list snippet."""
        if not items:
            return {}

        # Limit items and words
        selected = items[:7]
        truncated = [truncate_text(item, 12) for item in selected]

        return {
            'type': 'list',
            'format': 'bullet',
            'items': truncated,
            'item_count': len(truncated)
        }

    def generate_step_snippet(self, text: str) -> Dict[str, any]:
        """Generate a step-by-step snippet."""
        sentences = split_into_sentences(text)

        # Look for numbered steps or sequence indicators
        steps = []
        step_markers = ['first', 'second', 'third', 'next', 'then', 'finally', 'lastly']

        for sent in sentences:
            sent_lower = sent.lower()
            if any(marker in sent_lower for marker in step_markers) or re.match(r'^\d+[\.\)]', sent):
                steps.append(sent)

        if not steps:
            # Fallback: split into logical steps
            steps = sentences[:5]

        truncated_steps = [truncate_text(step, 15) for step in steps]

        return {
            'type': 'steps',
            'steps': truncated_steps,
            'step_count': len(truncated_steps)
        }

    def generate_paragraph_snippet(self, text: str) -> Dict[str, str]:
        """Generate a concise paragraph snippet."""
        sentences = split_into_sentences(text)
        selected = []
        word_count = 0

        for sent in sentences:
            sent_words = count_words(sent)
            if word_count + sent_words <= self.max_words:
                selected.append(sent)
                word_count += sent_words
            else:
                break

        answer = ' '.join(selected)
        if not answer:
            answer = truncate_text(text, self.max_words)

        return {
            'type': 'paragraph',
            'answer': answer,
            'word_count': count_words(answer)
        }

    def generate_table_snippet(self, headers: List[str], rows: List[List[str]]) -> Dict[str, any]:
        """Generate a table snippet."""
        if not headers or not rows:
            return {}

        # Limit to 3-4 rows for snippet
        selected_rows = rows[:4]

        return {
            'type': 'table',
            'headers': headers,
            'rows': selected_rows,
            'row_count': len(selected_rows)
        }

    def generate_from_text(self, text: str) -> List[Dict[str, any]]:
        """Generate all possible snippet types from text."""
        snippets = []

        # Try definition
        definition = self.generate_definition_snippet(text)
        if definition:
            snippets.append(definition)

        # Try paragraph
        paragraph = self.generate_paragraph_snippet(text)
        if paragraph:
            snippets.append(paragraph)

        # Try steps
        steps = self.generate_step_snippet(text)
        if steps.get('steps'):
            snippets.append(steps)

        return snippets

    def generate_from_content(self, cleaned_data: Dict[str, any]) -> Dict[str, any]:
        """Generate snippets from all content sections."""
        all_snippets = []

        # From paragraphs
        for para in cleaned_data.get('paragraphs', [])[:3]:
            snippets = self.generate_from_text(para)
            all_snippets.extend(snippets)

        # From lists
        for lst in cleaned_data.get('lists', [])[:2]:
            list_snippet = self.generate_list_snippet(lst)
            if list_snippet:
                all_snippets.append(list_snippet)

        # From tables
        for table in cleaned_data.get('tables', [])[:1]:
            if table:
                headers = table[0] if table else []
                rows = table[1:] if len(table) > 1 else []
                table_snippet = self.generate_table_snippet(headers, rows)
                if table_snippet:
                    all_snippets.append(table_snippet)

        return {
            'snippets': all_snippets,
            'snippet_count': len(all_snippets),
            'best_snippet': all_snippets[0] if all_snippets else None
        }
