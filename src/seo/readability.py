"""
Readability scoring module.
Computes Flesch Reading Ease, Flesch-Kincaid Grade, and snippet readiness.
"""

import re
from typing import Dict
from utils.helpers import count_words, split_into_sentences


class ReadabilityAnalyzer:
    def __init__(self):
        self.flesch_ease_scale = {
            (90, 100): 'Very Easy',
            (80, 90): 'Easy',
            (70, 80): 'Fairly Easy',
            (60, 70): 'Standard',
            (50, 60): 'Fairly Difficult',
            (30, 50): 'Difficult',
            (0, 30): 'Very Difficult'
        }

    def count_syllables(self, word: str) -> int:
        """Estimate syllable count in a word."""
        word = word.lower()
        vowels = 'aeiouy'
        syllables = 0
        prev_was_vowel = False

        for char in word:
            if char in vowels:
                if not prev_was_vowel:
                    syllables += 1
                prev_was_vowel = True
            else:
                prev_was_vowel = False

        if word.endswith('e'):
            syllables -= 1

        return max(1, syllables)

    def analyze(self, text: str) -> Dict[str, any]:
        """Calculate readability metrics."""
        sentences = split_into_sentences(text)
        words = re.findall(r'\b[a-zA-Z]+\b', text)
        syllables = sum(self.count_syllables(w) for w in words)

        word_count = len(words)
        sentence_count = len(sentences)

        if sentence_count == 0 or word_count == 0:
            return {
                'flesch_reading_ease': 0,
                'flesch_kincaid_grade': 0,
                'avg_words_per_sentence': 0,
                'avg_syllables_per_word': 0,
                'difficulty': 'Unknown'
            }

        avg_words_per_sentence = word_count / sentence_count
        avg_syllables_per_word = syllables / word_count

        # Flesch Reading Ease
        flesch_ease = 206.835 - (1.015 * avg_words_per_sentence) - (84.6 * avg_syllables_per_word)
        flesch_ease = max(0, min(100, flesch_ease))

        # Flesch-Kincaid Grade Level
        fk_grade = (0.39 * avg_words_per_sentence) + (11.8 * avg_syllables_per_word) - 15.59

        # Determine difficulty level
        difficulty = 'Unknown'
        for (low, high), label in self.flesch_ease_scale.items():
            if low <= flesch_ease <= high:
                difficulty = label
                break

        return {
            'flesch_reading_ease': round(flesch_ease, 2),
            'flesch_kincaid_grade': round(fk_grade, 2),
            'avg_words_per_sentence': round(avg_words_per_sentence, 2),
            'avg_syllables_per_word': round(avg_syllables_per_word, 2),
            'difficulty': difficulty,
            'word_count': word_count,
            'sentence_count': sentence_count
        }

    def snippet_readiness_score(self, text: str) -> Dict[str, any]:
        """Calculate how ready content is for featured snippets."""
        sentences = split_into_sentences(text)
        words = re.findall(r'\b[a-zA-Z]+\b', text)

        if not sentences:
            return {'score': 0, 'factors': {}}

        word_count = len(words)
        sentence_count = len(sentences)

        # Ideal snippet: 40-60 words, 2-3 sentences
        factors = {
            'word_count_ideal': 40 <= word_count <= 60,
            'sentence_count_ideal': 2 <= sentence_count <= 4,
            'starts_with_definition': bool(re.match(r'^[A-Z][a-zA-Z\s]+ is ', text)),
            'has_list_format': bool(re.search(r'^[\*\-\d]', text, re.MULTILINE)),
            'has_question_format': text.strip().endswith('?')
        }

        score = 0
        if factors['word_count_ideal']:
            score += 30
        if factors['sentence_count_ideal']:
            score += 25
        if factors['starts_with_definition']:
            score += 25
        if factors['has_list_format']:
            score += 10
        if factors['has_question_format']:
            score += 10

        return {
            'score': score,
            'factors': factors,
            'is_snippet_ready': score >= 70
        }

    def heading_structure_score(self, h1: list, h2: list, h3: list) -> Dict[str, any]:
        """Evaluate heading structure for SEO."""
        score = 0
        issues = []

        if len(h1) == 1:
            score += 30
        else:
            issues.append(f"Found {len(h1)} H1 tags (should be 1)")

        if len(h2) >= 2:
            score += 30
        else:
            issues.append("Need at least 2 H2 tags")

        if len(h3) >= 1:
            score += 20

        # Check heading hierarchy
        if h1 and not h2:
            issues.append("Missing H2 tags after H1")

        score += min(len(h2) * 5, 20)  # Bonus for more H2s

        return {
            'score': min(score, 100),
            'issues': issues,
            'h1_count': len(h1),
            'h2_count': len(h2),
            'h3_count': len(h3)
        }
