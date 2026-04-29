"""
SEO Analysis Report Generator.
Aggregates all metrics into a comprehensive SEO report.
"""

import json
from typing import Dict, Any
from utils.helpers import current_timestamp, count_words


class SEOAnalyzer:
    def __init__(self):
        pass

    def calculate_overall_score(self, readability: Dict, keywords: Dict, headings: Dict, snippet: Dict, links: Dict) -> int:
        """Calculate an overall SEO score out of 100."""
        score = 0

        # Readability (max 25)
        ease = readability.get('flesch_reading_ease', 0)
        if ease >= 60:
            score += 25
        elif ease >= 50:
            score += 20
        elif ease >= 40:
            score += 15
        else:
            score += 10

        # Keyword optimization (max 20)
        if keywords.get('title_optimized'):
            score += 10
        if len(keywords.get('placement', {}).get('in_first_paragraph', [])) > 0:
            score += 10

        # Heading structure (max 20)
        score += min(headings.get('score', 0) * 0.2, 20)

        # Snippet readiness (max 20)
        score += min(snippet.get('score', 0) * 0.2, 20)

        # Link distribution (max 15)
        link_dist = links.get('distribution', 'None')
        if link_dist == 'Balanced':
            score += 15
        elif link_dist == 'Sparse':
            score += 10
        elif link_dist == 'Dense':
            score += 5

        return min(int(score), 100)

    def generate_report(self, url: str, cleaned_data: Dict[str, Any], optimized_data: Dict[str, Any],
                        readability: Dict, keywords: Dict, headings: Dict,
                        snippet: Dict, links: Dict, paa: list, faq: list) -> Dict[str, Any]:
        """Generate a comprehensive SEO analysis report."""

        original_word_count = count_words(' '.join(cleaned_data.get('paragraphs', [])))
        optimized_word_count = count_words(' '.join(optimized_data.get('paragraphs', [])))

        overall_score = self.calculate_overall_score(readability, keywords, headings, snippet, links)

        report = {
            'url': url,
            'timestamp': current_timestamp(),
            'overall_seo_score': overall_score,
            'grade': self._get_grade(overall_score),
            'content_metrics': {
                'original_word_count': original_word_count,
                'optimized_word_count': optimized_word_count,
                'heading_counts': {
                    'h1': len(cleaned_data.get('h1', [])),
                    'h2': len(cleaned_data.get('h2', [])),
                    'h3': len(cleaned_data.get('h3', []))
                }
            },
            'readability': readability,
            'keyword_analysis': keywords,
            'heading_structure': headings,
            'snippet_readiness': snippet,
            'link_analysis': links,
            'people_also_ask': paa,
            'faq': faq,
            'recommendations': self._generate_recommendations(readability, keywords, headings, snippet, links)
        }

        return report

    def _get_grade(self, score: int) -> str:
        """Convert numeric score to letter grade."""
        if score >= 90:
            return 'A+'
        elif score >= 80:
            return 'A'
        elif score >= 70:
            return 'B'
        elif score >= 60:
            return 'C'
        elif score >= 50:
            return 'D'
        else:
            return 'F'

    def _generate_recommendations(self, readability: Dict, keywords: Dict, headings: Dict, snippet: Dict, links: Dict) -> list:
        """Generate actionable SEO recommendations."""
        recommendations = []

        # Readability
        ease = readability.get('flesch_reading_ease', 0)
        if ease < 50:
            recommendations.append("Content is too difficult to read. Simplify sentences and use shorter words.")
        elif ease < 60:
            recommendations.append("Readability can be improved. Break down complex sentences.")

        # Keywords
        if not keywords.get('title_optimized'):
            recommendations.append("Add primary keywords to the title tag.")
        if keywords.get('placement', {}).get('missing'):
            recommendations.append(f"Keywords missing from body text: {', '.join(keywords['placement']['missing'][:3])}")

        # Headings
        for issue in headings.get('issues', []):
            recommendations.append(f"Heading issue: {issue}")

        # Snippet
        if not snippet.get('is_snippet_ready'):
            recommendations.append("Add a concise definition or step-by-step list to improve snippet readiness.")

        # Links
        link_rec = links.get('recommendation', '')
        if 'Add more' in link_rec:
            recommendations.append(link_rec)

        return recommendations

    def compare_before_after(self, original: Dict[str, Any], optimized: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a before/after comparison report."""
        return {
            'title': {
                'before': original.get('title', ''),
                'after': optimized.get('title', '')
            },
            'meta_description': {
                'before': original.get('meta_description', ''),
                'after': optimized.get('meta_description', '')
            },
            'headings': {
                'before': {
                    'h1': original.get('h1', []),
                    'h2': original.get('h2', [])
                },
                'after': {
                    'h1': optimized.get('h1', []),
                    'h2': optimized.get('h2', [])
                }
            },
            'paragraph_count': {
                'before': len(original.get('paragraphs', [])),
                'after': len(optimized.get('paragraphs', []))
            }
        }
