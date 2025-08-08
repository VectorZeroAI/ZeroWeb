#ZeroScraper.py

import requests
from urllib.robotparser import RobotFileParser
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
import time
import re
import trafilatura
from requests.exceptions import RequestException
import json
from config import COMMON_CRAWL_INDEX_NAME, MAX_URLS_PER_DOMAIN

USER_AGENT = "ZeroWeb/1.0 (Compatible; ZeroScraper; +https://github.com/your-repo)"
CDX_SERVER = "http://index.commoncrawl.org"

def get_robots_parser(domain):
    """Fetch and parse robots.txt for a domain"""
    parser = RobotFileParser()
    robots_url = f"https://{domain}/robots.txt" if not domain.startswith('http') else f"{domain}/robots.txt"
    parser.set_url(robots_url)
    try:
        parser.read()
    except (RequestException, UnicodeDecodeError):
        return None
    return parser

def get_crawl_delay(parser):
    """Extract crawl delay from robots.txt"""
    if not parser:
        return None
    try:
        return parser.crawl_delay(USER_AGENT)
    except AttributeError:
        return None

def is_allowed_by_robots(parser, url):
    """Check if URL is allowed by robots.txt"""
    if not parser:
        return True  # Default allow if no robots.txt
    return parser.can_fetch(USER_AGENT, url)

def get_common_crawl_urls(domain, max_urls=MAX_URLS_PER_DOMAIN):
    """Get list of URLs for a domain from Common Crawl"""
    url_set = set()
    next_page = None
    base_query = f"{CDX_SERVER}/{COMMON_CRAWL_INDEX_NAME}-index?url={domain}/*&output=json"
    
    try:
        while len(url_set) < max_urls:
            query_url = next_page if next_page else base_query
            response = requests.get(query_url, timeout=30)
            response.raise_for_status()
            
            # Process each record in CDX response
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
            
            # Check for pagination
            link_header = response.headers.get('Link', '')
            if 'rel="next"' in link_header:
                next_page = link_header.split(';')[0].strip('<> ')
            else:
                break
                
    except RequestException as e:
        print(f"Common Crawl error: {str(e)}")
    
    return list(url_set)[:max_urls]

def get_URL_list(domain):
    """
    Discover URLs for a domain using Common Crawl, respecting robots.txt
    Returns: (url_list, crawl_delay)
    """
    # Get URLs from Common Crawl
    common_crawl_urls = get_common_crawl_urls(domain)
    
    # Process robots.txt
    parser = get_robots_parser(domain)
    crawl_delay = get_crawl_delay(parser) or 1.0  # Default 1 second delay
    
    # Filter URLs based on robots.txt
    filtered_urls = []
    for url in common_crawl_urls:
        if is_allowed_by_robots(parser, url):
            filtered_urls.append(url)
    
    return filtered_urls, crawl_delay

def get_snippet(url):
    """Get page headers and text snippet"""
    try:
        response = requests.get(
            url,
            headers={'User-Agent': USER_AGENT},
            timeout=10,
            allow_redirects=True
        )
        response.raise_for_status()
        
        # Extract headers
        headers = dict(response.headers)
        
        # Extract snippet
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.title.string.strip() if soup.title else ""
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        description = meta_desc['content'].strip() if meta_desc else ""
        
        if description:
            snippet = f"{title}\n{description}"
        else:
            # Fallback to first 200 chars of visible text
            visible_text = re.sub(r'\s+', ' ', soup.get_text()).strip()
            snippet = f"{title}\n{visible_text[:200]}"
        
        return headers, snippet
        
    except (RequestException, AttributeError):
        return {}, ""

def get_fullpage(url):
    """Get full page content using specialized extraction"""
    try:
        downloaded = trafilatura.fetch_url(url)
        content = trafilatura.extract(
            downloaded,
            include_links=False,
            include_tables=False,
            output_format="txt"
        )
        return content.strip() if content else ""
    except Exception:
        return ""

