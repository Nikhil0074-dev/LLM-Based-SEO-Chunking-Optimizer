"""
Utility helpers for text processing, HTML cleanup, and data export.
"""

import re
import os
import json
import csv
from datetime import datetime
from typing import List, Dict, Any


def strip_html_tags(text: str) -> str:
    """Remove HTML tags from a string."""
    clean = re.sub(r'<[^>]+>', '', text)
    return clean


def normalize_whitespace(text: str) -> str:
    """Collapse multiple whitespaces into a single space."""
    return re.sub(r'\s+', ' ', text).strip()


def split_into_sentences(text: str) -> List[str]:
    """Split text into sentences using simple regex."""
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in sentences if s.strip()]


def split_into_paragraphs(text: str) -> List[str]:
    """Split text into paragraphs by double newlines."""
    paragraphs = text.split('\n\n')
    return [normalize_whitespace(p) for p in paragraphs if p.strip()]


def count_words(text: str) -> int:
    """Return word count of a text string."""
    return len(text.split())


def truncate_text(text: str, max_words: int) -> str:
    """Truncate text to a maximum number of words."""
    words = text.split()
    if len(words) <= max_words:
        return text
    return ' '.join(words[:max_words]) + '...'


def sanitize_filename(name: str) -> str:
    """Sanitize a string to be used as a filename."""
    name = re.sub(r'[^\w\s-]', '', name).strip()
    return re.sub(r'[-\s]+', '_', name)


def export_to_csv(data: List[Dict[str, Any]], filepath: str):
    """Export a list of dictionaries to a CSV file."""
    if not data:
        return
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    keys = data[0].keys()
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(data)


def export_to_json(data: Any, filepath: str):
    """Export data to a JSON file."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_settings(config_path: str = 'configs/settings.json') -> Dict[str, Any]:
    """Load settings from JSON config file."""
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def current_timestamp() -> str:
    """Return current timestamp as a string."""
    return datetime.now().strftime('%Y-%m-%d_%H-%M-%S')


def ensure_dirs(path: str):
    """Ensure directory exists for a given path."""
    os.makedirs(path, exist_ok=True)


def chunk_list(lst: List[Any], chunk_size: int) -> List[List[Any]]:
    """Split a list into chunks of a specified size."""
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


def is_question(text: str) -> bool:
    """Check if a text looks like a question."""
    question_starters = ('what', 'how', 'why', 'when', 'where', 'who', 'which', 'is', 'are', 'can', 'do', 'does', 'will', 'would')
    text_lower = text.lower().strip()
    return text_lower.endswith('?') or text_lower.startswith(question_starters)

