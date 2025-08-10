# ZeroScraper.py

import requests
from validators import url as validate_url
from urllib.robotparser import RobotFileParser
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
import time
import re
import trafilatura
from requests.exceptions import RequestException
import json
import logging
from config import COMMON_CRAWL_INDEX_NAME, MAX_URLS_PER_DOMAIN

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)

USER_AGENT = "ZeroWeb/1.0 (Compatible; ZeroScraper; +https://github.com/your-repo)"
CDX_SERVER = "http://index.commoncrawl.org"

def get_robots_parser(domain):
    """Fetch and parse robots.txt for a domain"""
    parsed = urlparse(domain)
    if not parsed.scheme:
        domain = f"https://{domain}"

    robots_url = urljoin(domain, "/robots.txt")
    parser = RobotFileParser()
    parser.set_url(robots_url)

    try:
        parser.read()
        return parser
    except (RequestException, UnicodeDecodeError) as e:
        logging.warning(f"Failed to fetch robots.txt for {domain}: {e}")
        return None

def get_crawl_delay(parser):
    """Extract crawl delay from robots.txt"""
    if not parser:
        return 1.0

    # Try specific user agent first
    delay = parser.crawl_delay(USER_AGENT)
    if delay is not None:
        return float(delay)

    # Fallback to wildcard
    delay = parser.crawl_delay("*")
    return float(delay) if delay is not None else 1.0

def is_allowed_by_robots(parser, url):
    """Check if URL is allowed by robots.txt"""
    if not parser:
        return True
    return parser.can_fetch(USER_AGENT, url)

def get_common_crawl_urls(domain, max_urls=MAX_URLS_PER_DOMAIN, crawl_delay=1.0):
    """Get list of URLs for a domain from Common Crawl"""
    url_set = set()
    next_page = None
    base_query = f"{CDX_SERVER}/{COMMON_CRAWL_INDEX_NAME}-index?url={domain}/*&output=json"

    try:
        while len(url_set) < max_urls:
            query_url = next_page if next_page else base_query
            response = requests.get(query_url, timeout=30)
            response.raise_for_status()

            for line in response.text.splitlines():
                if not line:
                    continue
                try:
                    record = json.loads(line)
                    url = record.get('url', '')
                    if url and url not in url_set:
                        url_set.add(url)
                        if len(url_set) >= max_urls:
                            break
                except json.JSONDecodeError:
                    continue

            # Parse Link header correctly
            link_header = response.headers.get('Link', '')
            next_page = None
            if link_header:
                links = link_header.split(',')
                for link in links:
                    if 'rel="next"' in link:
                        match = re.search(r'<(.+?)>', link)
                        if match:
                            next_page = match.group(1)
                            break

            if not next_page:
                break

            time.sleep(crawl_delay)  # Rate limit

    except RequestException as e:
        logging.error(f"Common Crawl error for {domain}: {str(e)}")

    return list(url_set)[:max_urls]

def get_URL_list(domain):
    """
    Discover URLs for a domain using Common Crawl, respecting robots.txt
    Returns: (url_list, crawl_delay)
    """
    parser = get_robots_parser(domain)
    crawl_delay = get_crawl_delay(parser)

    common_crawl_urls = get_common_crawl_urls(domain, crawl_delay=crawl_delay)

    filtered_urls = [url for url in common_crawl_urls 
                     if validate_url(url) and is_allowed_by_robots(parser, url)]

    return filtered_urls, crawl_delay

def get_snippet(url):
    """Get page title and description snippet"""
    try:
        response = requests.get(
            url,
            headers={'User-Agent': USER_AGENT},
            timeout=10,
            allow_redirects=True
        )
        response.raise_for_status()

        headers = dict(response.headers)

        # Parse only until we find title/description
        soup = BeautifulSoup(response.text, 'html.parser')

        title = ""
        if soup.title:
            title = soup.title.string.strip()

        description = ""
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            description = meta_desc['content'].strip()

        if not description:
            # Extract first 200 chars of visible text
            visible_text = re.sub(r'\s+', ' ', soup.get_text()).strip()
            description = visible_text[:200]

        snippet = f"{title}\n{description}"
        return headers, snippet

    except (RequestException, AttributeError) as e:
        logging.warning(f"Error extracting snippet from {url}: {e}")
        return {}, ""

def get_fullpage(url):
    """Get full page content using Trafilatura or BeautifulSoup fallback"""
    try:
        downloaded = trafilatura.fetch_url(url)
        content = trafilatura.extract(
            downloaded,
            include_links=False,
            include_tables=False,
            output_format="txt"
        )
        if content:
            return content.strip()
    except Exception as e:
        logging.warning(f"Trafilatura failed for {url}: {e}")

    # Fallback to BeautifulSoup
    try:
        response = requests.get(url, headers={'User-Agent': USER_AGENT}, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup.get_text().strip()
    except Exception as e:
        logging.warning(f"Fallback extraction also failed for {url}: {e}")
        return ""