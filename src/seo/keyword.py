"""
Keyword extraction, density analysis, and optimization suggestions.
"""

import re
from collections import Counter
from typing import List, Dict, Tuple
from utils.helpers import count_words


class KeywordOptimizer:
    def __init__(self):
        self.stopwords = {
            'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been',
            'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
            'would', 'could', 'should', 'may', 'might', 'must', 'shall',
            'can', 'need', 'used', 'to', 'of', 'in', 'for', 'on', 'with',
            'at', 'by', 'from', 'as', 'into', 'through', 'during', 'before',
            'after', 'above', 'below', 'between', 'under', 'and', 'but',
            'or', 'yet', 'so', 'if', 'because', 'although', 'though',
            'while', 'where', 'when', 'that', 'which', 'who', 'whom',
            'whose', 'what', 'this', 'these', 'those', 'i', 'you', 'he',
            'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them',
            'my', 'your', 'his', 'its', 'our', 'their', 'mine', 'yours',
            'hers', 'ours', 'theirs', 'all', 'each', 'every', 'both',
            'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor',
            'not', 'only', 'own', 'same', 'than', 'too', 'very', 'just',
            'now', 'then', 'here', 'there', 'how'
        }

    def extract_keywords(self, text: str, top_n: int = 15) -> List[Tuple[str, int]]:
        """Extract top keywords by frequency."""
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        filtered = [w for w in words if w not in self.stopwords]
        freq = Counter(filtered)
        return freq.most_common(top_n)

    def calculate_density(self, text: str, keyword: str) -> float:
        """Calculate keyword density as percentage."""
        total_words = count_words(text)
        if total_words == 0:
            return 0.0
        keyword_count = len(re.findall(rf'\b{re.escape(keyword.lower())}\b', text.lower()))
        return (keyword_count / total_words) * 100

    def analyze_keyword_placement(self, text: str, keywords: List[str]) -> Dict[str, any]:
        """Analyze where keywords appear in the content."""
        paragraphs = text.split('\n\n')
        placement = {
            'in_first_paragraph': [],
            'in_headings': [],
            'in_body': [],
            'missing': []
        }

        first_para = paragraphs[0] if paragraphs else ''

        for kw in keywords:
            kw_lower = kw.lower()
            if kw_lower in first_para.lower():
                placement['in_first_paragraph'].append(kw)

            if any(kw_lower in p.lower() for p in paragraphs[1:]):
                placement['in_body'].append(kw)
            else:
                placement['missing'].append(kw)

        return placement

    def suggest_keywords(self, text: str, existing_keywords: List[str]) -> List[str]:
        """Suggest missing keywords based on common SEO terms."""
        current = set(kw.lower() for kw, _ in self.extract_keywords(text, top_n=30))

        seo_terms = {
            'guide', 'tutorial', 'tips', 'best', 'review', 'comparison',
            'how to', 'what is', 'why', 'benefits', 'features', 'examples',
            'step by step', 'ultimate', 'complete', 'beginner', 'advanced'
        }

        missing = [term for term in seo_terms if term not in current and term not in existing_keywords]
        return missing[:10]

    def optimize_keywords(self, text: str, title: str = '') -> Dict[str, any]:
        """Run full keyword optimization analysis."""
        keywords = self.extract_keywords(text, top_n=20)

        densities = {}
        for kw, _ in keywords:
            densities[kw] = round(self.calculate_density(text, kw), 2)

        placement = self.analyze_keyword_placement(text, [kw for kw, _ in keywords])

        title_keywords = []
        if title:
            for kw, _ in keywords[:5]:
                if kw.lower() in title.lower():
                    title_keywords.append(kw)

        suggestions = self.suggest_keywords(text, [kw for kw, _ in keywords])

        return {
            'top_keywords': keywords,
            'densities': densities,
            'placement': placement,
            'title_optimized': len(title_keywords) > 0,
            'title_keywords': title_keywords,
            'suggested_keywords': suggestions,
            'keyword_count': len(keywords)
        }
