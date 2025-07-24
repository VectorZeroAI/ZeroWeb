import json
import requests
from bs4 import BeautifulSoup
import logging
from typing import Dict, List, Optional, Tuple
import time
from urllib.parse import urljoin, urlparse
import threading
from concurrent.futures import ThreadPoolExecutor
import re

class ZeroSearch:
    """
    ZeroSearch++ - Advanced Search Engine for ZeroNet
    Uses ZeroIndex to find most relevant pages, then scrapes full content
    Saves all scraped content to raw.json for ZeroCompiler processing
    """
    
    def __init__(self, 
                 raw_file="raw.json",
                 max_workers=5,
                 timeout=10,
                 max_content_length=50000):
        
        self.raw_file = raw_file
        self.max_workers = max_workers
        self.timeout = timeout
        self.max_content_length = max_content_length
        
        # Initialize session for full content scraping
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Search state
        self.current_query = ""
        self.search_results = []
        self.raw_content = {}
        
        self.logger = self._setup_logger()
        
        # Initialize ZeroIndex connection
        self.zero_index = None
        self._connect_to_index()
    
    def _setup_logger(self):
        """Setup logging for ZeroSearch++"""
        logger = logging.getLogger('ZeroSearch++')
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('[ZeroSearch++] %(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger
    
    def _connect_to_index(self):
        """Connect to ZeroIndex for vector search"""
        try:
            # In a real implementation, this would import ZeroIndex
            # For now, we'll simulate the connection
            self.logger.info("Connected to ZeroIndex vector database")
        except Exception as e:
            self.logger.error(f"Failed to connect to ZeroIndex: {e}")
    
    def _extract_full_content(self, url: str) -> Optional[Dict]:
        """
        Extract full content from a URL
        
        Args:
            url (str): URL to scrape
            
        Returns:
            Dict: Full content including title, text, metadata
        """
        try:
            self.logger.info(f"Extracting full content from: {url}")
            
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header", "aside"]):
                script.decompose()
            
            # Extract title
            title_tag = soup.find('title')
            title = title_tag.get_text().strip() if title_tag else "No Title"
            
            # Extract main content
            main_content = ""
            
            # Try to find main content areas
            content_selectors = [
                'main', 'article', '.content', '#content', '.main-content',
                '.post-content', '.entry-content', '.article-content'
            ]
            
            content_found = False
            for selector in content_selectors:
                content_elements = soup.select(selector)
                if content_elements:
                    main_content = ' '.join([elem.get_text() for elem in content_elements])
                    content_found = True
                    break
            
            # Fallback: extract all paragraph text
            if not content_found:
                paragraphs = soup.find_all(['p', 'div', 'span'])
                main_content = ' '.join([p.get_text() for p in paragraphs if len(p.get_text().strip()) > 20])
            
            # Clean and limit content
            main_content = re.sub(r'\s+', ' ', main_content).strip()
            if len(main_content) > self.max_content_length:
                main_content = main_content[:self.max_content_length] + "..."
            
            # Extract metadata
            meta_description = ""
            meta_desc_tag = soup.find('meta', attrs={'name': 'description'})
            if meta_desc_tag:
                meta_description = meta_desc_tag.get('content', '').strip()
            
            # Extract keywords
            meta_keywords = ""
            meta_keywords_tag = soup.find('meta', attrs={'name': 'keywords'})
            if meta_keywords_tag:
                meta_keywords = meta_keywords_tag.get('content', '').strip()
            
            # Extract headings
            headings = []
            for heading_tag in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
                heading_text = heading_tag.get_text().strip()
                if heading_text:
                    headings.append({
                        'level': heading_tag.name,
                        'text': heading_text
                    })
            
            return {
                'url': url,
                'title': title,
                'content': main_content,
                'meta_description': meta_description,
                'meta_keywords': meta_keywords,
                'headings': headings,
                'content_length': len(main_content),
                'extraction_timestamp': time.time()
            }
            
        except requests.RequestException as e:
            self.logger.error(f"Request failed for {url}: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Content extraction failed for {url}: {e}")
            return None
    
    def _simulate_vector_search(self, query: str, top_k: int = 10) -> List[Dict]:
        """
        Simulate vector search results from ZeroIndex
        In real implementation, this would call ZeroIndex.search()
        
        Args:
            query (str): Search query
            top_k (int): Number of results to return
            
        Returns:
            List[Dict]: Simulated search results
        """
        # Simulated results - in real implementation, this would be:
        # return self.zero_index.search(query, top_k)
        
        simulated_results = [
            {
                'url': 'https://en.wikipedia.org/wiki/Artificial_intelligence',
                'title': 'Artificial Intelligence - Wikipedia',
                'snippet': 'Artificial intelligence (AI) is intelligence demonstrated by machines...',
                'similarity_score': 0.95
            },
            {
                'url': 'https://stackoverflow.com/questions/tagged/machine-learning',
                'title': 'Machine Learning Questions - Stack Overflow',
                'snippet': 'Find answers to machine learning questions...',
                'similarity_score': 0.87
            },
            {
                'url': 'https://github.com/topics/artificial-intelligence',
                'title': 'AI Projects on GitHub',
                'snippet': 'Discover artificial intelligence projects...',
                'similarity_score': 0.82
            }
        ]
        
        # Filter based on query relevance (simplified simulation)
        query_lower = query.lower()
        relevant_results = []
        
        for result in simulated_results:
            title_lower = result['title'].lower()
            snippet_lower = result['snippet'].lower()
            
            # Simple relevance scoring
            relevance = 0
            for word in query_lower.split():
                if word in title_lower:
                    relevance += 2
                if word in snippet_lower:
                    relevance += 1
            
            if relevance > 0:
                result['relevance'] = relevance
                relevant_results.append(result)
        
        # Sort by relevance and limit results
        relevant_results.sort(key=lambda x: x.get('relevance', 0), reverse=True)
        return relevant_results[:top_k]
    
    def search_and_extract(self, query: str, top_k: int = 10, extract_full_content: bool = True) -> Dict:
        """
        Main search function: Vector search + full content extraction
        
        Args:
            query (str): Search query
            top_k (int): Number of results to return
            extract_full_content (bool): Whether to extract full content
            
        Returns:
            Dict: Search results and extracted content
        """
        self.logger.info(f"Starting search for: '{query}'")
        self.current_query = query
        
        # Step 1: Vector search using ZeroIndex
        self.logger.info("Step 1: Performing vector search...")
        vector_results = self._simulate_vector_search(query, top_k)
        
        if not vector_results:
            self.logger.warning("No results found in vector search")
            return {
                'query': query,
                'vector_results': [],
                'extracted_content': {},
                'total_results': 0
            }
        
        self.logger.info(f"Found {len(vector_results)} relevant pages")
        self.search_results = vector_results
        
        # Step 2: Extract full content if requested
        extracted_content = {}
        
        if extract_full_content:
            self.logger.info("Step 2: Extracting full content...")
            
            urls_to_extract = [result['url'] for result in vector_results]
            
            # Use threading for parallel content extraction
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                future_to_url = {
                    executor.submit(self._extract_full_content, url): url 
                    for url in urls_to_extract
                }
                
                for future in future_to_url:
                    url = future_to_url[future]
                    try:
                        content = future.result(timeout=self.timeout + 5)
                        if content:
                            extracted_content[url] = content
                            self.logger.info(f"Extracted content from: {url}")
                        else:
                            self.logger.warning(f"Failed to extract content from: {url}")
                    except Exception as e:
                        self.logger.error(f"Content extraction error for {url}: {e}")
            
            # Save extracted content to raw.json
            self.raw_content = extracted_content
            self._save_raw_content()
        
        self.logger.info(f"Search completed: {len(extracted_content)} pages with full content")
        
        return {
            'query': query,
            'vector_results': vector_results,
            'extracted_content': extracted_content,
            'total_results': len(vector_results),
            'extracted_count': len(extracted_content)
        }
    
    def _save_raw_content(self):
        """Save extracted content to raw.json for ZeroCompiler"""
        try:
            with open(self.raw_file, 'w', encoding='utf-8') as f:
                json.dump(self.raw_content, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Saved {len(self.raw_content)} pages to {self.raw_file}")
            
        except Exception as e:
            self.logger.error(f"Failed to save raw content: {e}")
    
    def get_urls_only(self, query: str, top_k: int = 10) -> List[str]:
        """
        Get only URLs without extracting full content
        
        Args:
            query (str): Search query
            top_k (int): Number of URLs to return
            
        Returns:
            List[str]: List of relevant URLs
        """
        results = self.search_and_extract(query, top_k, extract_full_content=False)
        return [result['url'] for result in results['vector_results']]
    
    def get_search_summary(self) -> Dict:
        """
        Get summary of current search results
        
        Returns:
            Dict: Search summary statistics
        """
        if not self.search_results:
            return {'status': 'no_search_performed'}
        
        total_content_length = sum(
            content.get('content_length', 0) 
            for content in self.raw_content.values()
        )
        
        return {
            'query': self.current_query,
            'total_results': len(self.search_results),
            'extracted_pages': len(self.raw_content),
            'total_content_length': total_content_length,
            'average_content_length': total_content_length / len(self.raw_content) if self.raw_content else 0,
            'top_result': self.search_results[0] if self.search_results else None
        }
    
    def clear_cache(self):
        """Clear search cache and temporary data"""
        self.search_results = []
        self.raw_content = {}
        self.current_query = ""
        
        # Remove raw.json file
        try:
            import os
            if os.path.exists(self.raw_file):
                os.remove(self.raw_file)
            self.logger.info("Cache cleared")
        except Exception as e:
            self.logger.error(f"Failed to clear cache: {e}")
    
    def get_content_for_url(self, url: str) -> Optional[Dict]:
        """
        Get extracted content for a specific URL
        
        Args:
            url (str): URL to get content for
            
        Returns:
            Dict: Content data for the URL
        """
        return self.raw_content.get(url)
    
    def rerank_results(self, custom_query: str = None) -> List[Dict]:
        """
        Re-rank search results based on additional criteria
        
        Args:
            custom_query (str): Additional query for re-ranking
            
        Returns:
            List[Dict]: Re-ranked results
        """
        if not self.search_results:
            return []
        
        query_to_use = custom_query or self.current_query
        
        if not query_to_use:
            return self.search_results
        
        # Re-rank based on content analysis
        reranked_results = []
        
        for result in self.search_results:
            url = result['url']
            content = self.raw_content.get(url, {})
            
            # Calculate new relevance score
            relevance_score = result.get('similarity_score', 0)
            
            if content:
                # Boost score based on content quality
                content_text = content.get('content', '').lower()
                query_words = query_to_use.lower().split()
                
                # Count query word occurrences in content
                word_count = sum(content_text.count(word) for word in query_words)
                content_boost = min(word_count * 0.1, 0.5)  # Max boost of 0.5
                
                # Boost for longer, more comprehensive content
                content_length = content.get('content_length', 0)
                length_boost = min(content_length / 10000 * 0.2, 0.3)  # Max boost of 0.3
                
                relevance_score += content_boost + length_boost
            
            result['reranked_score'] = relevance_score
            reranked_results.append(result)
        
        # Sort by new relevance score
        reranked_results.sort(key=lambda x: x.get('reranked_score', 0), reverse=True)
        
        self.logger.info(f"Re-ranked {len(reranked_results)} results")
        return reranked_results

# Integration with ZeroNet modules
class ZeroSearchIntegrator:
    """
    Integration layer for ZeroSearch++ with other ZeroNet modules
    """
    
    def __init__(self):
        self.zero_search = ZeroSearch()
        self.logger = logging.getLogger('ZeroSearchIntegrator')
    
    def search_for_compiler(self, query: str, top_k: int = 10) -> str:
        """
        Search and prepare content for ZeroCompiler
        
        Args:
            query (str): Search query
            top_k (int): Number of results
            
        Returns:
            str: Path to raw.json file for ZeroCompiler
        """
        self.logger.info(f"Preparing search results for ZeroCompiler: '{query}'")
        
        # Perform search with full content extraction
        results = self.zero_search.search_and_extract(query, top_k, extract_full_content=True)