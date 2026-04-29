"""
Content cleaning module to normalize and structure scraped data.
"""

import re
from typing import Dict, List
from utils.helpers import normalize_whitespace, strip_html_tags


class ContentCleaner:
    def __init__(self):
        self.ad_keywords = [
            'advertisement', 'sponsored', 'promoted', 'ad ', 'ads ', 'ad\t',
            'subscribe now', 'sign up today', 'limited time offer',
            'click here to buy', 'affiliate link'
        ]

    def clean_text(self, text: str) -> str:
        """Clean a single text string."""
        text = strip_html_tags(text)
        text = normalize_whitespace(text)
        # Remove URLs
        text = re.sub(r'http\S+', '', text)
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s.,;!?()-]', '', text)
        return text.strip()

    def is_ad_or_noise(self, text: str) -> bool:
        """Check if text is an advertisement or noise."""
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in self.ad_keywords)

    def clean_content(self, raw_data: Dict[str, any]) -> Dict[str, any]:
        """Clean all fields in scraped content."""
        cleaned = {}

        cleaned['title'] = self.clean_text(raw_data.get('title', ''))
        cleaned['meta_description'] = self.clean_text(raw_data.get('meta_description', ''))

        for heading_key in ['h1', 'h2', 'h3']:
            headings = raw_data.get(heading_key, [])
            cleaned[heading_key] = [self.clean_text(h) for h in headings if not self.is_ad_or_noise(h)]

        paragraphs = raw_data.get('paragraphs', [])
        cleaned['paragraphs'] = [
            self.clean_text(p) for p in paragraphs
            if len(p) > 30 and not self.is_ad_or_noise(p)
        ]

        lists = raw_data.get('lists', [])
        cleaned_lists = []
        for lst in lists:
            clean_lst = [self.clean_text(item) for item in lst if not self.is_ad_or_noise(item)]
            if clean_lst:
                cleaned_lists.append(clean_lst)
        cleaned['lists'] = cleaned_lists

        cleaned['links'] = raw_data.get('links', [])
        cleaned['tables'] = raw_data.get('tables', [])
        cleaned['images'] = raw_data.get('images', [])

        return cleaned

    def build_full_text(self, cleaned_data: Dict[str, any]) -> str:
        """Combine all text into a single string for analysis."""
        parts = []
        parts.extend(cleaned_data.get('h1', []))
        parts.extend(cleaned_data.get('h2', []))
        parts.extend(cleaned_data.get('h3', []))
        parts.extend(cleaned_data.get('paragraphs', []))
        for lst in cleaned_data.get('lists', []):
            parts.extend(lst)
        return '\n\n'.join(parts)

