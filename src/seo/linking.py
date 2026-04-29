"""
Internal linking suggestions module.
"""

import re
from typing import List, Dict
from collections import Counter


class LinkingOptimizer:
    def __init__(self):
        pass

    def extract_anchor_text_candidates(self, text: str, top_n: int = 10) -> List[str]:
        """Extract potential anchor text phrases from content."""
        candidates = []

        # Capitalized phrases (2-4 words)
        capitalized = re.findall(r'\b[A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+){1,3}\b', text)
        candidates.extend(capitalized)

        # Quoted phrases
        quoted = re.findall(r'"([^"]{5,50})"', text)
        candidates.extend(quoted)

        # Frequent noun phrases (simple heuristic)
        words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())
        freq = Counter(words)
        common = [w for w, c in freq.most_common(top_n) if c >= 2]
        candidates.extend(common)

        # Deduplicate and filter
        seen = set()
        unique = []
        for c in candidates:
            c_lower = c.lower()
            if c_lower not in seen and len(c) > 10:
                seen.add(c_lower)
                unique.append(c)

        return unique[:top_n]

    def suggest_internal_links(self, text: str, existing_links: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Suggest internal linking opportunities."""
        suggestions = []
        anchors = self.extract_anchor_text_candidates(text)

        for anchor in anchors:
            # Check if already linked
            already_linked = any(
                anchor.lower() in link.get('text', '').lower()
                for link in existing_links
            )

            if not already_linked:
                suggestions.append({
                    'anchor_text': anchor,
                    'suggested_url': f'/{anchor.lower().replace(" ", "-")}',
                    'context': text[max(0, text.lower().find(anchor.lower()) - 50):
                                  text.lower().find(anchor.lower()) + len(anchor) + 50]
                })

        return suggestions[:10]

    def analyze_link_distribution(self, paragraphs: List[str], links: List[Dict[str, str]]) -> Dict[str, any]:
        """Analyze how links are distributed across content."""
        link_count = len(links)
        para_count = len(paragraphs)

        if para_count == 0:
            return {
                'total_links': link_count,
                'links_per_paragraph': 0,
                'distribution': 'None',
                'recommendation': 'Add content first'
            }

        ratio = link_count / para_count

        if ratio < 0.1:
            distribution = 'Sparse'
            recommendation = 'Add more internal links'
        elif ratio > 0.5:
            distribution = 'Dense'
            recommendation = 'Consider reducing link density'
        else:
            distribution = 'Balanced'
            recommendation = 'Good link distribution'

        return {
            'total_links': link_count,
            'links_per_paragraph': round(ratio, 2),
            'distribution': distribution,
            'recommendation': recommendation
        }
