"""
AI Content Rewriter using OpenAI GPT-4o or Google Gemini.
Includes a mock fallback for demo mode without API keys.
"""

import os
import json
from typing import Dict, Optional
from utils.helpers import count_words, split_into_sentences


class AIRewriter:
    def __init__(self, model: str = None, api_key: str = None):
        self.settings = self._load_settings()
        self.model = model or self.settings.get('ai', {}).get('default_model', 'gpt-4o')
        self.api_key = api_key or os.getenv('OPENAI_API_KEY') or os.getenv('GEMINI_API_KEY')
        self.client = None
        self._init_client()

    def _load_settings(self):
        try:
            with open('configs/settings.json', 'r') as f:
                return json.load(f)
        except:
            return {}

    def _init_client(self):
        """Initialize the appropriate AI client."""
        if not self.api_key:
            return

        if self.model.startswith('gpt'):
            try:
                import openai
                self.client = openai.OpenAI(api_key=self.api_key)
            except (ImportError, TypeError) as e:
                print(f"OpenAI client init failed: {e}. Using mock fallback.")
                self.client = None
        elif self.model.startswith('gemini'):
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self.client = genai
            except (ImportError, TypeError) as e:
                print(f"Gemini client init failed: {e}. Using mock fallback.")
                self.client = None

    def _mock_rewrite(self, text: str, instruction: str = "Rewrite for SEO") -> str:
        """Mock rewriter for demo mode without API keys."""
        sentences = split_into_sentences(text)
        rewritten = []

        for sent in sentences:
            # Simple transformations
            sent = sent.strip()
            if len(sent) > 100:
                # Break long sentences
                parts = sent.split(', ')
                if len(parts) > 1:
                    rewritten.append(parts[0] + '.')
                    rewritten.append(' '.join(parts[1:]).capitalize() + '.')
                else:
                    rewritten.append(sent)
            else:
                rewritten.append(sent)

        result = ' '.join(rewritten)
        # Add SEO-friendly prefix if it's a definition
        if ' is ' in result[:50]:
            result = result[0].upper() + result[1:]

        return result

    def rewrite(self, text: str, style: str = "seo") -> str:
        """Rewrite content using AI or mock fallback."""
        if not self.client:
            return self._mock_rewrite(text)

        prompt = self._build_prompt(text, style)

        try:
            if self.model.startswith('gpt'):
                return self._call_openai(prompt)
            elif self.model.startswith('gemini'):
                return self._call_gemini(prompt)
        except Exception as e:
            print(f"AI call failed: {e}. Using mock fallback.")
            return self._mock_rewrite(text)

        return self._mock_rewrite(text)

    def _build_prompt(self, text: str, style: str) -> str:
        """Build the prompt for the AI model."""
        prompts = {
            "seo": (
                "Rewrite the following content to be SEO-optimized. "
                "Use short paragraphs, clear headings, and bullet points where appropriate. "
                "Make it snippet-ready and easy to read:\n\n"
                f"{text}"
            ),
            "snippet": (
                "Rewrite the following into a concise, 40-60 word answer "
                "suitable for a Google Featured Snippet:\n\n"
                f"{text}"
            ),
            "faq": (
                "Rewrite the following into a clear question-and-answer format "
                "suitable for an FAQ section:\n\n"
                f"{text}"
            ),
            "simple": (
                "Simplify the following text to improve readability. "
                "Use shorter sentences and simpler words:\n\n"
                f"{text}"
            )
        }
        return prompts.get(style, prompts["seo"])

    def _call_openai(self, prompt: str) -> str:
        """Call OpenAI API."""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are an expert SEO content optimizer."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=self.settings.get('ai', {}).get('max_tokens', 2048),
            temperature=self.settings.get('ai', {}).get('temperature', 0.3)
        )
        return response.choices[0].message.content

    def _call_gemini(self, prompt: str) -> str:
        """Call Google Gemini API."""
        model = self.client.GenerativeModel(self.model)
        response = model.generate_content(prompt)
        return response.text

    def optimize_full_content(self, cleaned_data: Dict[str, any]) -> Dict[str, any]:
        """Optimize all content sections."""
        optimized = {}

        # Optimize title
        title = cleaned_data.get('title', '')
        optimized['title'] = self.rewrite(title, style='seo') if title else ''

        # Optimize meta description
        meta = cleaned_data.get('meta_description', '')
        optimized['meta_description'] = self.rewrite(meta, style='snippet') if meta else ''

        # Optimize paragraphs
        paragraphs = cleaned_data.get('paragraphs', [])
        optimized['paragraphs'] = [self.rewrite(p, style='seo') for p in paragraphs]

        # Optimize headings
        for h in ['h1', 'h2', 'h3']:
            headings = cleaned_data.get(h, [])
            optimized[h] = [self.rewrite(hd, style='seo') for hd in headings]

        # Keep lists and links as-is (structure is good)
        optimized['lists'] = cleaned_data.get('lists', [])
        optimized['links'] = cleaned_data.get('links', [])

        return optimized
