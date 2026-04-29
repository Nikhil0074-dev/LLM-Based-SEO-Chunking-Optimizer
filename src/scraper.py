"""
Web scraping module to fetch and extract webpage content.
"""

import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Optional
from urllib.parse import urljoin, urlparse
import time


class WebScraper:
    def __init__(self, timeout: int = 30, user_agent: str = None):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': user_agent or (
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/120.0.0.0 Safari/537.36'
            )
        })

    def fetch(self, url: str, retries: int = 3) -> Optional[str]:
        """Fetch raw HTML content from a URL."""
        for attempt in range(retries):
            try:
                response = self.session.get(url, timeout=self.timeout)
                response.raise_for_status()
                return response.text
            except requests.RequestException as e:
                if attempt == retries - 1:
                    print(f"Failed to fetch {url}: {e}")
                    return None
                time.sleep(1)
        return None

    def extract_content(self, html: str, base_url: str = '') -> Dict[str, any]:
        """Extract structured content from HTML."""
        soup = BeautifulSoup(html, 'lxml')

        # Remove unwanted elements
        for tag in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 'form', 'iframe', 'advertisement', 'ad']):
            tag.decompose()

        data = {
            'title': self._get_title(soup),
            'meta_description': self._get_meta_description(soup),
            'h1': self._get_headings(soup, 'h1'),
            'h2': self._get_headings(soup, 'h2'),
            'h3': self._get_headings(soup, 'h3'),
            'paragraphs': self._get_paragraphs(soup),
            'lists': self._get_lists(soup),
            'links': self._get_links(soup, base_url),
            'tables': self._get_tables(soup),
            'images': self._get_images(soup, base_url),
        }
        return data

    def _get_title(self, soup: BeautifulSoup) -> str:
        title_tag = soup.find('title')
        return title_tag.get_text(strip=True) if title_tag else ''

    def _get_meta_description(self, soup: BeautifulSoup) -> str:
        meta = soup.find('meta', attrs={'name': 'description'})
        if meta:
            return meta.get('content', '')
        og_desc = soup.find('meta', attrs={'property': 'og:description'})
        if og_desc:
            return og_desc.get('content', '')
        return ''

    def _get_headings(self, soup: BeautifulSoup, tag: str) -> List[str]:
        return [h.get_text(strip=True) for h in soup.find_all(tag)]

    def _get_paragraphs(self, soup: BeautifulSoup) -> List[str]:
        paragraphs = []
        for p in soup.find_all('p'):
            text = p.get_text(strip=True)
            if len(text) > 20:
                paragraphs.append(text)
        return paragraphs

    def _get_lists(self, soup: BeautifulSoup) -> List[List[str]]:
        lists = []
        for ul in soup.find_all(['ul', 'ol']):
            items = [li.get_text(strip=True) for li in ul.find_all('li') if li.get_text(strip=True)]
            if items:
                lists.append(items)
        return lists

    def _get_links(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, str]]:
        links = []
        for a in soup.find_all('a', href=True):
            href = urljoin(base_url, a['href'])
            text = a.get_text(strip=True)
            if text and href.startswith('http'):
                links.append({'text': text, 'url': href})
        return links

    def _get_tables(self, soup: BeautifulSoup) -> List[List[List[str]]]:
        tables = []
        for table in soup.find_all('table'):
            rows = []
            for tr in table.find_all('tr'):
                cells = [td.get_text(strip=True) for td in tr.find_all(['td', 'th'])]
                if cells:
                    rows.append(cells)
            if rows:
                tables.append(rows)
        return tables

    def _get_images(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, str]]:
        images = []
        for img in soup.find_all('img', src=True):
            src = urljoin(base_url, img['src'])
            alt = img.get('alt', '')
            images.append({'src': src, 'alt': alt})
        return images

    def scrape(self, url: str) -> Optional[Dict[str, any]]:
        """Full scrape pipeline: fetch + extract."""
        html = self.fetch(url)
        if html is None:
            return None
        return self.extract_content(html, base_url=url)

