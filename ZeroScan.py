import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, urlunparse
import time
import logging
from typing import Dict, List, Set
import threading
from collections import deque
import re

class ZeroSkan:
    """
    ZeroSkan - Domain Link Manager for ZeroNet
    Takes lists of links by domains and stores them for ZeroScraper to use
    Crawls domains to discover pages and maintains organized link lists
    """

    def __init__(self, domains_file="domains.json", links_file="discovered_links.json", max_depth=3):
        self.domains_file = domains_file
        self.links_file = links_file
        self.max_depth = max_depth

        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

        self.domains = self._load_domains()
        self.discovered_links = self._load_discovered_links()

        self.visited_urls = set()
        self.url_queue = deque()
        self.lock = threading.Lock()

        self.logger = self._setup_logger()

    def _setup_logger(self):
        logger = logging.getLogger('ZeroSkan')
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('[ZeroSkan] %(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

    def _load_domains(self) -> List[str]:
        try:
            with open(self.domains_file, 'r') as f:
                domains = json.load(f)
            self.logger.info(f"Loaded {len(domains)} domains")
            return domains
        except FileNotFoundError:
            default_domains = ["wikipedia.org", "stackoverflow.com", "github.com", "reddit.com"]
            self._save_domains(default_domains)
            return default_domains

    def _save_domains(self, domains: List[str]):
        try:
            with open(self.domains_file, 'w') as f:
                json.dump(domains, f, indent=2)
            self.logger.info(f"Saved {len(domains)} domains")
        except Exception as e:
            self.logger.error(f"Failed to save domains: {e}")

    def _load_discovered_links(self) -> Dict[str, List[str]]:
        try:
            with open(self.links_file, 'r') as f:
                links = json.load(f)
            total_links = sum(len(urls) for urls in links.values())
            self.logger.info(f"Loaded {total_links} discovered links across {len(links)} domains")
            return links
        except FileNotFoundError:
            return {}

    def _save_discovered_links(self):
        try:
            with open(self.links_file, 'w') as f:
                json.dump(self.discovered_links, f, indent=2)
            total_links = sum(len(urls) for urls in self.discovered_links.values())
            self.logger.info(f"Saved {total_links} discovered links")
        except Exception as e:
            self.logger.error(f"Failed to save discovered links: {e}")

    def add_domain(self, domain: str):
        domain = domain.replace('http://', '').replace('https://', '').replace('www.', '')
        domain = domain.split('/')[0]
        if domain not in self.domains:
            self.domains.append(domain)
            self._save_domains(self.domains)
            self.logger.info(f"Added domain: {domain}")
            return True
        else:
            self.logger.info(f"Domain already exists: {domain}")
            return False

    def remove_domain(self, domain: str):
        if domain in self.domains:
            self.domains.remove(domain)
            if domain in self.discovered_links:
                del self.discovered_links[domain]
            self._save_domains(self.domains)
            self._save_discovered_links()
            self.logger.info(f"Removed domain: {domain}")
            return True
        return False

    def get_domains(self) -> List[str]:
        return self.domains.copy()

    def _is_valid_url(self, url: str, domain: str) -> bool:
        try:
            parsed = urlparse(url)
            if parsed.scheme not in ['http', 'https']:
                return False
            if domain not in parsed.netloc:
                return False
            skip_extensions = {'.pdf', '.jpg', '.jpeg', '.png', '.gif', '.css', '.js', 
                               '.ico', '.zip', '.tar', '.gz', '.mp4', '.mp3', '.avi'}
            if any(url.lower().endswith(ext) for ext in skip_extensions):
                return False
            skip_patterns = ['/api/', '/admin/', '/login', '/logout', '/register', 
                             '/search?', '/tag/', '/category/', '/archive/']
            if any(pattern in url.lower() for pattern in skip_patterns):
                return False
            return True
        except Exception:
            return False

    def _extract_links(self, html_content: str, base_url: str, domain: str) -> Set[str]:
        links = set()
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            for tag in soup.find_all(['a', 'link']):
                href = tag.get('href')
                if not href:
                    continue
                absolute_url = urljoin(base_url, href)
                parsed = urlparse(absolute_url)
                clean_url = urlunparse((parsed.scheme, parsed.netloc, parsed.path, 
                                        parsed.params, parsed.query, ''))
                if self._is_valid_url(clean_url, domain):
                    links.add(clean_url)
        except Exception as e:
            self.logger.error(f"Failed to extract links from {base_url}: {e}")
        return links

    def crawl_domain(self, domain: str) -> List[str]:
        discovered_urls = []
        visited = set()
        queue = deque()

        start_urls = [f"https://{domain}", f"https://www.{domain}"]
        for start_url in start_urls:
            try:
                response = self.session.get(start_url, timeout=10)
                if response.status_code == 200:
                    queue.append((start_url, 0))
                    break
            except:
                continue

        if not queue:
            self.logger.warning(f"Could not access {domain}")
            return []

        self.logger.info(f"Starting full crawl of {domain} (no page limit)")

        while queue:
            try:
                current_url, depth = queue.popleft()
                if current_url in visited or depth > self.max_depth:
                    continue

                visited.add(current_url)

                response = self.session.get(current_url, timeout=10)
                if response.status_code != 200:
                    continue

                discovered_urls.append(current_url)
                self.logger.info(f"Crawled: {current_url}")

                if depth < self.max_depth:
                    links = self._extract_links(response.text, current_url, domain)
                    for link in links:
                        if link not in visited and link not in [u for u, _ in queue]:
                            queue.append((link, depth + 1))

                time.sleep(1)

            except Exception as e:
                self.logger.error(f"Error crawling {current_url}: {e}")
                continue

        self.logger.info(f"Full crawl completed for {domain}: {len(discovered_urls)} pages discovered")
        return discovered_urls

    def scan_all_domains(self):
        self.logger.info("Starting domain scanning...")

        for domain in self.domains:
            self.logger.info(f"Scanning domain: {domain}")
            try:
                discovered_urls = self.crawl_domain(domain)
                if discovered_urls:
                    self.discovered_links[domain] = discovered_urls
                    self.logger.info(f"Found {len(discovered_urls)} URLs for {domain}")
                else:
                    self.logger.warning(f"No URLs discovered for {domain}")
            except Exception as e:
                self.logger.error(f"Failed to scan {domain}: {e}")

        self._save_discovered_links()
        self.logger.info("Domain scanning completed")

    def get_urls_for_scraper(self) -> Dict[str, List[str]]:
        return self.discovered_links.copy()

    def get_all_urls(self) -> List[str]:
        all_urls = []
        for urls in self.discovered_links.values():
            all_urls.extend(urls)
        return all_urls

    def get_stats(self) -> Dict:
        total_urls = sum(len(urls) for urls in self.discovered_links.values())
        domain_stats = {domain: len(urls) for domain, urls in self.discovered_links.items()}
        return {
            'total_domains': len(self.domains),
            'domains_with_links': len(self.discovered_links),
            'total_discovered_urls': total_urls,
            'urls_per_domain': domain_stats,
            'average_urls_per_domain': total_urls / len(self.discovered_links) if self.discovered_links else 0
        }

    def clear_discovered_links(self, domain: str = None):
        if domain:
            if domain in self.discovered_links:
                del self.discovered_links[domain]
                self.logger.info(f"Cleared links for {domain}")
        else:
            self.discovered_links.clear()
            self.logger.info("Cleared all discovered links")

        self._save_discovered_links()

# Integration example
if __name__ == "__main__":
    zero_skan = ZeroSkan()
    print("ZeroSkan - Domain Link Manager")
    print("Current domains:", zero_skan.get_domains())

    zero_skan.add_domain("python.org")

    print("\nScanning domains for links...")
    zero_skan.scan_all_domains()

    stats = zero_skan.get_stats()
    print(f"\nScan Statistics:")
    print(f"Total domains: {stats['total_domains']}")
    print(f"Total discovered URLs: {stats['total_discovered_urls']}")
    print(f"URLs per domain: {stats['urls_per_domain']}")

    urls_for_scraper = zero_skan.get_urls_for_scraper()
    print(f"\nReady to provide {len(zero_skan.get_all_urls())} URLs to ZeroScraper")