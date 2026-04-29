"""
Question-based chunking module for 'People Also Ask' and FAQ generation.
"""

import re
from typing import List, Dict
from utils.helpers import split_into_sentences, count_words, is_question


class QuestionChunker:
    def __init__(self, max_answer_words: int = 60):
        self.max_answer_words = max_answer_words
        self.question_starters = [
            'what is', 'how to', 'why does', 'when should', 'where is',
            'who is', 'which', 'can i', 'do i', 'does', 'will', 'would',
            'what are', 'how do', 'why is', 'when do', 'where can',
            'who are', 'can you', 'do you', 'is it', 'are there'
        ]

    def extract_existing_questions(self, text: str) -> List[str]:
        """Extract questions already present in the text."""
        sentences = split_into_sentences(text)
        questions = [s for s in sentences if is_question(s)]
        return questions

    def generate_questions_from_headings(self, headings: List[str]) -> List[Dict[str, str]]:
        """Convert headings into question format."""
        questions = []
        for h in headings:
            h_clean = h.strip().rstrip('?:.')
            # Simple transformation rules
            if h_clean.lower().startswith(('the ', 'a ', 'an ')):
                q = f"What is {h_clean}?"
            elif 'how' in h_clean.lower():
                q = f"{h_clean}?"
            elif 'why' in h_clean.lower():
                q = f"{h_clean}?"
            elif 'best' in h_clean.lower():
                q = f"What are the {h_clean}?"
            elif 'tips' in h_clean.lower() or 'ways' in h_clean.lower():
                q = f"What are some {h_clean}?"
            else:
                q = f"What is {h_clean}?"

            questions.append({
                'question': q,
                'source_heading': h
            })
        return questions

    def find_answer(self, question: str, paragraphs: List[str]) -> str:
        """Find the best matching paragraph as an answer."""
        q_words = set(re.findall(r'\w+', question.lower()))
        best_para = ''
        best_score = 0

        for para in paragraphs:
            p_words = set(re.findall(r'\w+', para.lower()))
            common = q_words & p_words
            score = len(common) / max(len(q_words), 1)

            if score > best_score and len(para) > 20:
                best_score = score
                best_para = para

        words = best_para.split()
        if len(words) > self.max_answer_words:
            return ' '.join(words[:self.max_answer_words]) + '...'
        return best_para

    def generate_faq(self, cleaned_data: Dict[str, any]) -> List[Dict[str, str]]:
        """Generate FAQ section from content."""
        headings = cleaned_data.get('h2', []) + cleaned_data.get('h3', [])
        paragraphs = cleaned_data.get('paragraphs', [])
        full_text = ' '.join(paragraphs)

        faq = []

        # Extract existing questions
        existing = self.extract_existing_questions(full_text)
        for q in existing:
            answer = self.find_answer(q, paragraphs)
            faq.append({
                'question': q,
                'answer': answer,
                'type': 'existing'
            })

        # Generate from headings
        generated = self.generate_questions_from_headings(headings)
        for item in generated:
            answer = self.find_answer(item['question'], paragraphs)
            faq.append({
                'question': item['question'],
                'answer': answer,
                'type': 'generated'
            })

        # Deduplicate
        seen = set()
        unique_faq = []
        for item in faq:
            q = item['question'].lower().strip()
            if q not in seen and item['answer']:
                seen.add(q)
                unique_faq.append(item)

        return unique_faq

    def generate_paa(self, cleaned_data: Dict[str, any]) -> List[Dict[str, str]]:
        """Generate 'People Also Ask' style questions."""
        faq = self.generate_faq(cleaned_data)
        paa = []
        for item in faq[:8]:  # Limit to top 8 PAA
            paa.append({
                'question': item['question'],
                'short_answer': item['answer'],
                'expanded': False
            })
        return paa
