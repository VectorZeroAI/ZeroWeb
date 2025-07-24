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
        
        # Initialize session for requests
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Domain management
        self.domains = self._load_domains()
        self.discovered_links = self._load_discovered_links()
        
        # Crawling state
        self.visited_urls = set()
        self.url_queue = deque()
        self.lock = threading.Lock()
        
        self.logger = self._setup_logger()
    
    def _setup_logger(self):
        """Setup logging for ZeroSkan"""
        logger = logging.getLogger('ZeroSkan')
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('[ZeroSkan] %(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger
    
    def _load_domains(self) -> List[str]:
        """Load domain list from file"""
        try:
            with open(self.domains_file, 'r') as f:
                domains = json.load(f)
            self.logger.info(f"Loaded {len(domains)} domains")
            return domains
        except FileNotFoundError:
            # Default domains
            default_domains = [
                "wikipedia.org",
                "stackoverflow.com",
                "github.com",
                "reddit.com"
            ]
            self._save_domains(default_domains)
            return default_domains
    
    def _save_domains(self, domains: List[str]):
        """Save domain list to file"""
        try:
            with open(self.domains_file, 'w') as f:
                json.dump(domains, f, indent=2)
            self.logger.info(f"Saved {len(domains)} domains")
        except Exception as e:
            self.logger.error(f"Failed to save domains: {e}")
    
    def _load_discovered_links(self) -> Dict[str, List[str]]:
        """Load discovered links from file"""
        try:
            with open(self.links_file, 'r') as f:
                links = json.load(f)
            total_links = sum(len(urls) for urls in links.values())
            self.logger.info(f"Loaded {total_links} discovered links across {len(links)} domains")
            return links
        except FileNotFoundError:
            return {}
    
    def _save_discovered_links(self):
        """Save discovered links to file"""
        try:
            with open(self.links_file, 'w') as f:
                json.dump(self.discovered_links, f, indent=2)
            total_links = sum(len(urls) for urls in self.discovered_links.values())
            self.logger.info(f"Saved {total_links} discovered links")
        except Exception as e:
            self.logger.error(f"Failed to save discovered links: {e}")
    
    def add_domain(self, domain: str):
        """
        Add a new domain to the list
        
        Args:
            domain (str): Domain to add (e.g., 'example.com')
        """
        # Clean domain name
        domain = domain.replace('http://', '').replace('https://', '').replace('www.', '')
        domain = domain.split('/')[0]  # Remove any path
        
        if domain not in self.domains:
            self.domains.append(domain)
            self._save_domains(self.domains)
            self.logger.info(f"Added domain: {domain}")
            return True
        else:
            self.logger.info(f"Domain already exists: {domain}")
            return False
    
    def remove_domain(self, domain: str):
        """
        Remove a domain from the list
        
        Args:
            domain (str): Domain to remove
        """
        if domain in self.domains:
            self.domains.remove(domain)
            # Also remove discovered links for this domain
            if domain in self.discovered_links:
                del self.discovered_links[domain]
            self._save_domains(self.domains)
            self._save_discovered_links()
            self.logger.info(f"Removed domain: {domain}")
            return True
        return False
    
    def get_domains(self) -> List[str]:
        """Get list of managed domains"""
        return self.domains.copy()
    
    def _is_valid_url(self, url: str, domain: str) -> bool:
        """
        Check if URL is valid for crawling
        
        Args:
            url (str): URL to check
            domain (str): Expected domain
            
        Returns:
            bool: True if valid for crawling
        """
        try:
            parsed = urlparse(url)
            
            # Must be HTTP/HTTPS
            if parsed.scheme not in ['http', 'https']:
                return False
            
            # Must belong to the expected domain
            if domain not in parsed.netloc:
                return False
            
            # Skip common non-content files
            skip_extensions = {'.pdf', '.jpg', '.jpeg', '.png', '.gif', '.css', '.js', 
                             '.ico', '.zip', '.tar', '.gz', '.mp4', '.mp3', '.avi'}
            if any(url.lower().endswith(ext) for ext in skip_extensions):
                return False
            
            # Skip common non-content paths
            skip_patterns = ['/api/', '/admin/', '/login', '/logout', '/register', 
                           '/search?', '/tag/', '/category/', '/archive/']
            if any(pattern in url.lower() for pattern in skip_patterns):
                return False
            
            return True
            
        except Exception:
            return False
    
    def _extract_links(self, html_content: str, base_url: str, domain: str) -> Set[str]:
        """
        Extract valid links from HTML content
        
        Args:
            html_content (str): HTML content
            base_url (str): Base URL for relative links
            domain (str): Target domain
            
        Returns:
            Set[str]: Set of discovered URLs
        """
        links = set()
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Find all links
            for tag in soup.find_all(['a', 'link']):
                href = tag.get('href')
                if not href:
                    continue
                
                # Convert relative URLs to absolute
                absolute_url = urljoin(base_url, href)
                
                # Clean URL (remove fragments, normalize)
                parsed = urlparse(absolute_url)
                clean_url = urlunparse((parsed.scheme, parsed.netloc, parsed.path, 
                                      parsed.params, parsed.query, ''))
                
                # Validate URL
                if self._is_valid_url(clean_url, domain):
                    links.add(clean_url)
            
        except Exception as e:
            self.logger.error(f"Failed to extract links from {base_url}: {e}")
        
        return links
    
    def crawl_domain(self, domain: str, max_pages: int = 100) -> List[str]:
        """
        Crawl a domain to discover pages
        
        Args:
            domain (str): Domain to crawl
            max_pages (int): Maximum pages to crawl
            
        Returns:
            List[str]: List of discovered URLs
        """
        discovered_urls = []
        visited = set()
        queue = deque()
        
        # Start with domain homepage
        start_urls = [f"https://{domain}", f"https://www.{domain}"]
        
        for start_url in start_urls:
            try:
                response = self.session.get(start_url, timeout=10)
                if response.status_code == 200:
                    queue.append((start_url, 0))  # (url, depth)
                    break
            except:
                continue
        
        if not queue:
            self.logger.warning(f"Could not access {domain}")
            return []
        
        self.logger.info(f"Starting crawl of {domain} (max {max_pages} pages)")
        
        while queue and len(discovered_urls) < max_pages:
            try:
                current_url, depth = queue.popleft()
                
                if current_url in visited or depth > self.max_depth:
                    continue
                
                visited.add(current_url)
                
                # Fetch page
                response = self.session.get(current_url, timeout=10)
                if response.status_code != 200:
                    continue
                
                discovered_urls.append(current_url)
                self.logger.info(f"Crawled: {current_url}")
                
                # Extract links for next level
                if depth < self.max_depth:
                    links = self._extract_links(response.text, current_url, domain)
                    for link in links:
                        if link not in visited:
                            queue.append((link, depth + 1))
                
                # Respectful crawling delay
                time.sleep(1)
                
            except Exception as e:
                self.logger.error(f"Error crawling {current_url}: {e}")
                continue
        
        self.logger.info(f"Crawl completed for {domain}: {len(discovered_urls)} pages discovered")
        return discovered_urls
    
    def scan_all_domains(self, max_pages_per_domain: int = 100):
        """
        Scan all managed domains for links
        
        Args:
            max_pages_per_domain (int): Maximum pages to crawl per domain
        """
        self.logger.info("Starting domain scanning...")
        
        for domain in self.domains:
            self.logger.info(f"Scanning domain: {domain}")
            
            try:
                discovered_urls = self.crawl_domain(domain, max_pages_per_domain)
                
                if discovered_urls:
                    self.discovered_links[domain] = discovered_urls
                    self.logger.info(f"Found {len(discovered_urls)} URLs for {domain}")
                else:
                    self.logger.warning(f"No URLs discovered for {domain}")
                
            except Exception as e:
                self.logger.error(f"Failed to scan {domain}: {e}")
        
        # Save discovered links
        self._save_discovered_links()
        self.logger.info("Domain scanning completed")
    
    def get_urls_for_scraper(self) -> Dict[str, List[str]]:
        """
        Get discovered URLs formatted for ZeroScraper
        
        Returns:
            Dict[str, List[str]]: Domain -> URLs mapping
        """
        return self.discovered_links.copy()
    
    def get_all_urls(self) -> List[str]:
        """
        Get all discovered URLs as a flat list
        
        Returns:
            List[str]: All discovered URLs
        """
        all_urls = []
        for urls in self.discovered_links.values():
            all_urls.extend(urls)
        return all_urls
    
    def get_stats(self) -> Dict:
        """
        Get statistics about discovered links
        
        Returns:
            Dict: Statistics about managed domains and links
        """
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
        """
        Clear discovered links for a domain or all domains
        
        Args:
            domain (str, optional): Specific domain to clear, or None for all
        """
        if domain:
            if domain in self.discovered_links:
                del self.discovered_links[domain]
                self.logger.info(f"Cleared links for {domain}")
        else:
            self.discovered_links.clear()
            self.logger.info("Cleared all discovered links")
        
        self._save_discovered_links()

# Integration example for ZeroNet
if __name__ == "__main__":
    # Initialize ZeroSkan
    zero_skan = ZeroSkan()
    
    print("ZeroSkan - Domain Link Manager")
    print("Current domains:", zero_skan.get_domains())
    
    # Example: Add a new domain
    zero_skan.add_domain("python.org")
    
    # Scan domains for links
    print("\nScanning domains for links...")
    zero_skan.scan_all_domains(max_pages_per_domain=20)  # Small number for demo
    
    # Display statistics
    stats = zero_skan.get_stats()
    print(f"\nScan Statistics:")
    print(f"Total domains: {stats['total_domains']}")
    print(f"Total discovered URLs: {stats['total_discovered_urls']}")
    print(f"URLs per domain: {stats['urls_per_domain']}")
    
    # Get URLs for ZeroScraper
    urls_for_scraper = zero_skan.get_urls_for_scraper()
    print(f"\nReady to provide {len(zero_skan.get_all_urls())} URLs to ZeroScraper")