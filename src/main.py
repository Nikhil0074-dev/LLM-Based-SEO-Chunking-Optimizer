"""
Main orchestrator for the SEO URL Optimizer.
Ties scraping, cleaning, chunking, AI optimization, and reporting together.
"""

import sys
import os
import json

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scraper import WebScraper
from cleaner import ContentCleaner
from chunking.seo_chunk import SEOChunker
from chunking.question_chunk import QuestionChunker
from chunking.topic_chunk import TopicChunker
from ai.rewriter import AIRewriter
from ai.snippet_generator import SnippetGenerator
from seo.keyword import KeywordOptimizer
from seo.readability import ReadabilityAnalyzer
from seo.linking import LinkingOptimizer
from analyzer.seo_score import SEOAnalyzer
from utils.helpers import export_to_json, export_to_csv, ensure_dirs, load_settings


class SEOOptimizerPipeline:
    def __init__(self, config_path: str = '../configs/settings.json'):
        self.settings = load_settings(config_path) if os.path.exists(config_path) else {}
        self.scraper = WebScraper()
        self.cleaner = ContentCleaner()
        self.seo_chunker = SEOChunker()
        self.question_chunker = QuestionChunker()
        self.topic_chunker = TopicChunker()
        self.rewriter = AIRewriter()
        self.snippet_generator = SnippetGenerator()
        self.keyword_optimizer = KeywordOptimizer()
        self.readability_analyzer = ReadabilityAnalyzer()
        self.linking_optimizer = LinkingOptimizer()
        self.seo_analyzer = SEOAnalyzer()

        # Ensure output dirs
        ensure_dirs('../output/optimized_content')
        ensure_dirs('../output/reports')

    def process_url(self, url: str) -> dict:
        """Process a single URL through the full pipeline."""
        print(f"Processing: {url}")

        # Step 1: Scrape
        raw_data = self.scraper.scrape(url)
        if not raw_data:
            return {'error': f'Failed to scrape {url}'}

        # Step 2: Clean
        cleaned = self.cleaner.clean_content(raw_data)
        full_text = self.cleaner.build_full_text(cleaned)

        # Step 3: AI Optimization
        optimized = self.rewriter.optimize_full_content(cleaned)

        # Step 4: Chunking
        seo_chunks = self.seo_chunker.optimize_content(cleaned)
        faq = self.question_chunker.generate_faq(cleaned)
        paa = self.question_chunker.generate_paa(cleaned)
        topics = self.topic_chunker.chunk(full_text)

        # Step 5: Snippet Generation
        featured_snippets = []
        for para in cleaned.get('paragraphs', [])[:3]:
            snippets = self.snippet_generator.generate_from_text(para)
            featured_snippets.extend(snippets)

        # Step 6: SEO Analysis
        readability = self.readability_analyzer.analyze(full_text)
        keywords = self.keyword_optimizer.optimize_keywords(full_text, cleaned.get('title', ''))
        headings = self.readability_analyzer.heading_structure_score(
            cleaned.get('h1', []),
            cleaned.get('h2', []),
            cleaned.get('h3', [])
        )
        snippet_readiness = self.readability_analyzer.snippet_readiness_score(full_text)
        link_analysis = self.linking_optimizer.analyze_link_distribution(
            cleaned.get('paragraphs', []),
            cleaned.get('links', [])
        )

        report = self.seo_analyzer.generate_report(
            url=url,
            cleaned_data=cleaned,
            optimized_data=optimized,
            readability=readability,
            keywords=keywords,
            headings=headings,
            snippet=snippet_readiness,
            links=link_analysis,
            paa=paa,
            faq=faq
        )

        comparison = self.seo_analyzer.compare_before_after(cleaned, optimized)

        result = {
            'url': url,
            'original_content': cleaned,
            'optimized_content': optimized,
            'seo_chunks': seo_chunks,
            'topics': topics,
            'featured_snippets': featured_snippets,
            'faq': faq,
            'paa': paa,
            'report': report,
            'comparison': comparison
        }

        return result

    def save_results(self, result: dict, output_dir: str = '../output'):
        """Save optimization results to files."""
        url_safe = result['url'].replace('https://', '').replace('http://', '').replace('/', '_')

        # Save optimized content as JSON
        content_path = os.path.join(output_dir, 'optimized_content', f'{url_safe}.json')
        export_to_json({
            'url': result['url'],
            'optimized_content': result['optimized_content'],
            'featured_snippets': result['featured_snippets'],
            'faq': result['faq'],
            'paa': result['paa']
        }, content_path)

        # Save report as JSON
        report_path = os.path.join(output_dir, 'reports', f'{url_safe}_report.json')
        export_to_json(result['report'], report_path)

        print(f"Saved results to {output_dir}")

    def process_batch(self, urls: list) -> list:
        """Process multiple URLs."""
        results = []
        for url in urls:
            result = self.process_url(url)
            if 'error' not in result:
                self.save_results(result)
            results.append(result)
        return results


def main():
    import argparse
    parser = argparse.ArgumentParser(description='SEO URL Optimizer')
    parser.add_argument('--url', type=str, help='Single URL to optimize')
    parser.add_argument('--batch', type=str, help='CSV file with URLs')
    parser.add_argument('--output', type=str, default='../output', help='Output directory')
    args = parser.parse_args()

    pipeline = SEOOptimizerPipeline()

    if args.url:
        result = pipeline.process_url(args.url)
        if 'error' in result:
            print(f"Error: {result['error']}")
        else:
            pipeline.save_results(result, args.output)
            print(json.dumps(result['report'], indent=2))
    elif args.batch:
        import csv
        urls = []
        with open(args.batch, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                urls.append(row['url'])
        pipeline.process_batch(urls)
    else:
        print("Usage: python main.py --url <URL> or --batch <CSV_FILE>")


if __name__ == '__main__':
    main()
