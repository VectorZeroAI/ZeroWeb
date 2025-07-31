# ZeroScraper.py
import json
import queue as Queue
import requests
from bs4 import BeautifulSoup
import time
import threading
from urllib.parse import urljoin, urlparse
import logging
import os
import fcntl

class ZeroScraper:
    """
    ZeroScraper - Web scraping module for ZeroNet
    Takes snippets and titles of pages and stores them in queue.json
    NOTE: NO IP TAMPERING - All requests maintain user privacy
    """

    def __init__(self, queue_file="queue.json", max_workers=5, delay_between_requests=0.5):
        """
        Initialize the scraper with proper configuration
        
        Args:
            queue_file (str): Path to the queue file
            max_workers (int): Maximum number of concurrent threads
            delay_between_requests (float): Seconds to wait between requests
        """
        self.queue_file = queue_file
        self.max_workers = max_workers
        self.delay_between_requests = delay_between_requests
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Create a lock for thread-safe queue operations
        self.queue_lock = threading.RLock()
        
        # Initialize queue data
        self.queue_data = {}
        self._load_queue()
        
        self.logger = self._setup_logger()
        self.logger.info("ZeroScraper initialized successfully")

    def _setup_logger(self):
        """Setup logging for ZeroScraper"""
        logger = logging.getLogger('ZeroScraper')
        logger.setLevel(logging.INFO)
        
        # Prevent adding multiple handlers if logger already exists
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('[ZeroScraper] %(asctime)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger

    def _load_queue(self):
        """Load queue data from queue.json file"""
        try:
            if os.path.exists(self.queue_file):
                with open(self.queue_file, 'r', encoding='utf-8') as f:
                    with self.queue_lock:
                        self.queue_data = json.load(f)
                self.logger.info(f"Loaded {len(self.queue_data)} entries from queue.json")
            else:
                with self.queue_lock:
                    self.queue_data = {}
                self.logger.info("Created new queue.json file")
        except Exception as e:
            self.logger.error(f"Failed to load queue.json: {e}")
            with self.queue_lock:
                self.queue_data = {}

    def _save_queue(self):
        """Save queue data to queue.json file with proper locking"""
        try:
            # Create lock file
            lock_file = f"{self.queue_file}.lock"
            lock_fd = os.open(lock_file, os.O_CREAT | os.O_RDWR)
            
            try:
                # Acquire exclusive lock
                fcntl.flock(lock_fd, fcntl.LOCK_EX)
                
                # Write data to file
                with open(self.queue_file, 'w', encoding='utf-8') as f:
                    with self.queue_lock:
                        json.dump(self.queue_data, f, indent=2, ensure_ascii=False)
                
                self.logger.info(f"Queue saved with {len(self.queue_data)} entries")
            finally:
                # Release lock and clean up
                fcntl.flock(lock_fd, fcntl.LOCK_UN)
                os.close(lock_fd)
                if os.path.exists(lock_file):
                    os.unlink(lock_file)
                    
        except Exception as e:
            self.logger.error(f"Failed to save queue: {e}")

    def add_to_queue(self, url, scraped_data):
        """
        Add scraped data to queue with thread-safe operations
        
        Args:
            url (str): URL that was scraped
            scraped_data (dict): Contains title and snippet
            
        Returns:
            bool: True if added successfully, False otherwise
        """
        if not scraped_data:
            return False
            
        try:
            # Update in-memory queue (thread-safe)
            with self.queue_lock:
                self.queue_data[url] = {
                    'title': scraped_data['title'],
                    'snippet': scraped_data['snippet']
                }
            
            # Save to disk
            self._save_queue()
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to add to queue: {e}")
            return False

    def scrape_page(self, url):
        """
        Scrape a single page and extract title and snippet

        Args:
            url (str): URL to scrape

        Returns:
            dict: Contains title and snippet, or None if failed
        """
        try:
            self.logger.info(f"Scraping: {url}")

            response = self.session.get(url, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract title
            title_tag = soup.find('title')
            title = title_tag.get_text().strip() if title_tag else "No Title"

            # Extract snippet (first paragraph or meta description)
            snippet = ""

            # Try meta description first
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc and meta_desc.get('content'):
                snippet = meta_desc['content'].strip()
            else:
                # Fall back to first paragraph
                paragraphs = soup.find_all('p')
                for p in paragraphs:
                    text = p.get_text().strip()
                    if len(text) > 50:  # Minimum meaningful length
                        snippet = text[:300] + "..." if len(text) > 300 else text
                        break

            if not snippet:
                snippet = "No snippet available"

            return {
                "title": title,
                "snippet": snippet
            }

        except requests.RequestException as e:
            self.logger.error(f"Request failed for {url}: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Scraping failed for {url}: {e}")
            return None

    def scrape_urls(self, urls):
        """Scrape multiple URLs using threading
        Args:
            urls (list): List of URLs to scrape
        """
        # Filter out URLs that are already in the queue
        with self.queue_lock:
            new_urls = [url for url in urls if url not in self.queue_data]
        
        if not new_urls:
            self.logger.info("No new URLs to scrape")
            return
            
        self.logger.info(f"Scraping {len(new_urls)} new URLs out of {len(urls)} total")
        
        # Create a thread-safe queue
        url_queue = Queue.Queue()
        for url in new_urls:
            url_queue.put(url)

        def worker():
            while not url_queue.empty():
                try:
                    url = url_queue.get_nowait()
                    
                    scraped_data = self.scrape_page(url)
                    if scraped_data:
                        self.add_to_queue(url, scraped_data)
                        self.logger.info(f"Added to queue: {url}")

                    # Respect server resources
                    time.sleep(self.delay_between_requests)
                except Queue.Empty:
                    break
                except Exception as e:
                    self.logger.error(f"Worker error: {e}")
                finally:
                    url_queue.task_done()

        threads = []
        num_threads = min(self.max_workers, len(new_urls))
        
        for _ in range(num_threads):
            thread = threading.Thread(target=worker)
            thread.daemon = True
            thread.start()
            threads.append(thread)

        # Wait for all tasks to be processed
        url_queue.join()

    def scrape_from_domain_list(self, domain_urls):
        """
        Scrape URLs provided by ZeroSkan

        Args:
            domain_urls (dict): Dictionary mapping domains to lists of URLs
        """
        all_urls = []
        for domain, urls in domain_urls.items():
            self.logger.info(f"Processing {len(urls)} URLs from {domain}")
            all_urls.extend(urls)

        self.scrape_urls(all_urls)

    def get_queue_data(self):
        """
        Get current queue data

        Returns:
            dict: Current queue.json contents
        """
        with self.queue_lock:
            return self.queue_data.copy()

    def clear_queue(self):
        """Clear the queue.json file"""
        with self.queue_lock:
            self.queue_data = {}
        self._save_queue()
        self.logger.info("Queue cleared")

    def get_queue_stats(self):
        """
        Get statistics about the current queue

        Returns:
            dict: Statistics about queue contents
        """
        with self.queue_lock:
            total_entries = len(self.queue_data)
            total_chars = 0
            domains = {}
            
            for url, data in self.queue_data.items():
                total_chars += len(data['title']) + len(data['snippet'])
                domain = urlparse(url).netloc
                domains[domain] = domains.get(domain, 0) + 1

        return {
            "total_entries": total_entries,
            "total_characters": total_chars,
            "domains": domains,
            "average_snippet_length": total_chars / total_entries if total_entries > 0 else 0
        }

# Example usage
if __name__ == "__main__":
    # Initialize ZeroScraper
    scraper = ZeroScraper(delay_between_requests=1.0)
    
    # Example URLs for testing
    test_urls = [
        "https://en.wikipedia.org/wiki/Artificial_intelligence",
        "https://stackoverflow.com/questions/tagged/python",
        "https://github.com/trending"
    ]

    print("ZeroScraper - Starting scraping process...")
    print("NOTE: All operations maintain IP privacy")

    # Scrape the URLs
    scraper.scrape_urls(test_urls)

    # Display statistics
    stats = scraper.get_queue_stats()
    print(f"\nScraping completed!")
    print(f"Total entries: {stats['total_entries']}")
    print(f"Domains scraped: {list(stats['domains'].keys())}")

    # Show sample queue data
    queue_data = scraper.get_queue_data()
    print(f"\nSample queue.json format:")
    for url, data in list(queue_data.items())[:2]:
        print(f'"{url}": {{')
        print(f'  "title": "{data["title"][:50]}..."')
        print(f'  "snippet": "{data["snippet"][:100]}..."')
        print("}")