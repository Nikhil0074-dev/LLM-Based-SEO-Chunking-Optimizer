"""
Topic-based chunking using keyword clustering.
"""

import re
from collections import Counter
from typing import List, Dict
from utils.helpers import split_into_paragraphs


class TopicChunker:
    def __init__(self, min_keyword_freq: int = 2):
        self.min_keyword_freq = min_keyword_freq
        self.stopwords = {
            'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been',
            'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
            'would', 'could', 'should', 'may', 'might', 'must', 'shall',
            'can', 'need', 'dare', 'ought', 'used', 'to', 'of', 'in',
            'for', 'on', 'with', 'at', 'by', 'from', 'as', 'into',
            'through', 'during', 'before', 'after', 'above', 'below',
            'between', 'under', 'and', 'but', 'or', 'yet', 'so', 'if',
            'because', 'although', 'though', 'while', 'where', 'when',
            'that', 'which', 'who', 'whom', 'whose', 'what', 'this',
            'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they',
            'me', 'him', 'her', 'us', 'them', 'my', 'your', 'his', 'its',
            'our', 'their', 'mine', 'yours', 'hers', 'ours', 'theirs',
            'myself', 'yourself', 'himself', 'herself', 'itself',
            'ourselves', 'yourselves', 'themselves', 'all', 'each',
            'every', 'both', 'few', 'more', 'most', 'other', 'some',
            'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'than',
            'too', 'very', 'just', 'now', 'then', 'here', 'there'
        }

    def extract_keywords(self, text: str, top_n: int = 10) -> List[str]:
        """Extract frequent keywords from text."""
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        filtered = [w for w in words if w not in self.stopwords]
        freq = Counter(filtered)
        return [word for word, count in freq.most_common(top_n) if count >= self.min_keyword_freq]

    def extract_bigrams(self, text: str, top_n: int = 10) -> List[str]:
        """Extract frequent two-word phrases."""
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        filtered = [w for w in words if w not in self.stopwords]
        bigrams = [f"{filtered[i]} {filtered[i+1]}" for i in range(len(filtered)-1)]
        freq = Counter(bigrams)
        return [b for b, count in freq.most_common(top_n) if count >= self.min_keyword_freq]

    def assign_topics(self, paragraphs: List[str], keywords: List[str]) -> List[Dict[str, any]]:
        """Assign topics to paragraphs based on keyword overlap."""
        topic_chunks = []
        for para in paragraphs:
            para_lower = para.lower()
            matched_keywords = [kw for kw in keywords if kw in para_lower]
            if matched_keywords:
                primary_topic = matched_keywords[0]
            else:
                primary_topic = 'general'

            topic_chunks.append({
                'topic': primary_topic,
                'keywords': matched_keywords,
                'text': para
            })
        return topic_chunks

    def cluster_by_topic(self, topic_chunks: List[Dict[str, any]]) -> Dict[str, List[str]]:
        """Group paragraphs by their primary topic."""
        clusters = {}
        for chunk in topic_chunks:
            topic = chunk['topic']
            if topic not in clusters:
                clusters[topic] = []
            clusters[topic].append(chunk['text'])
        return clusters

    def chunk(self, text: str) -> Dict[str, any]:
        """Run full topic-based chunking pipeline."""
        paragraphs = split_into_paragraphs(text)
        full_text = ' '.join(paragraphs)

        keywords = self.extract_keywords(full_text, top_n=15)
        bigrams = self.extract_bigrams(full_text, top_n=10)

        topic_chunks = self.assign_topics(paragraphs, keywords + bigrams)
        clusters = self.cluster_by_topic(topic_chunks)

        return {
            'keywords': keywords,
            'bigrams': bigrams,
            'topic_chunks': topic_chunks,
            'clusters': clusters
        }
