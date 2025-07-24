import json
import numpy as np
import faiss
import pickle
import os
from sentence_transformers import SentenceTransformer
import logging
from typing import Dict, List, Tuple, Optional

class ZeroIndex:
    """
    ZeroIndex - FAISS Vector Database Manager for ZeroNet
    Manages embeddings of titles and snippets from queue.json
    Each vector is labeled with its source URL
    """
    
    def __init__(self, 
                 queue_file="queue.json",
                 index_file="zeronet.index",
                 metadata_file="zeronet_metadata.pkl",
                 model_name="all-MiniLM-L6-v2"):
        
        self.queue_file = queue_file
        self.index_file = index_file
        self.metadata_file = metadata_file
        
        # Initialize sentence transformer
        self.model = SentenceTransformer(model_name)
        self.embedding_dim = self.model.get_sentence_embedding_dimension()
        
        # Initialize FAISS index
        self.index = faiss.IndexFlatIP(self.embedding_dim)  # Inner product for similarity
        self.url_to_id = {}  # Maps URLs to FAISS IDs
        self.id_to_metadata = {}  # Maps FAISS IDs to metadata
        self.next_id = 0
        
        self.logger = self._setup_logger()
        
        # Load existing index if available
        self._load_index()
    
    def _setup_logger(self):
        """Setup logging for ZeroIndex"""
        logger = logging.getLogger('ZeroIndex')
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('[ZeroIndex] %(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger
    
    def _load_index(self):
        """Load existing FAISS index and metadata"""
        try:
            if os.path.exists(self.index_file) and os.path.exists(self.metadata_file):
                self.index = faiss.read_index(self.index_file)
                
                with open(self.metadata_file, 'rb') as f:
                    metadata = pickle.load(f)
                    self.url_to_id = metadata['url_to_id']
                    self.id_to_metadata = metadata['id_to_metadata']
                    self.next_id = metadata['next_id']
                
                self.logger.info(f"Loaded existing index with {self.index.ntotal} vectors")
            else:
                self.logger.info("No existing index found, starting fresh")
        except Exception as e:
            self.logger.error(f"Failed to load existing index: {e}")
            self.logger.info("Starting with fresh index")
    
    def _save_index(self):
        """Save FAISS index and metadata to disk"""
        try:
            faiss.write_index(self.index, self.index_file)
            
            metadata = {
                'url_to_id': self.url_to_id,
                'id_to_metadata': self.id_to_metadata,
                'next_id': self.next_id
            }
            
            with open(self.metadata_file, 'wb') as f:
                pickle.dump(metadata, f)
            
            self.logger.info(f"Index saved with {self.index.ntotal} vectors")
        except Exception as e:
            self.logger.error(f"Failed to save index: {e}")
    
    def _create_embedding(self, title: str, snippet: str) -> np.ndarray:
        """
        Create embedding for title and snippet combined
        
        Args:
            title (str): Page title
            snippet (str): Page snippet
            
        Returns:
            np.ndarray: Embedding vector
        """
        # Combine title and snippet with separator
        combined_text = f"{title} [SEP] {snippet}"
        
        # Create embedding
        embedding = self.model.encode(combined_text)
        
        # Normalize for cosine similarity (since we use inner product)
        embedding = embedding / np.linalg.norm(embedding)
        
        return embedding.astype(np.float32)
    
    def process_queue(self):
        """
        Process queue.json and add new entries to FAISS index
        Only processes URLs that aren't already in the index
        """
        try:
            with open(self.queue_file, 'r', encoding='utf-8') as f:
                queue_data = json.load(f)
        except FileNotFoundError:
            self.logger.warning(f"Queue file {self.queue_file} not found")
            return
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON in queue file: {e}")
            return
        
        new_entries = 0
        
        for url, data in queue_data.items():
            # Check if URL is already in index
            if url in self.url_to_id:
                continue
            
            try:
                title = data.get('title', '')
                snippet = data.get('snippet', '')
                
                if not title and not snippet:
                    self.logger.warning(f"Empty title and snippet for {url}")
                    continue
                
                # Create embedding
                embedding = self._create_embedding(title, snippet)
                
                # Add to FAISS index
                self.index.add(embedding.reshape(1, -1))
                
                # Store metadata
                current_id = self.next_id
                self.url_to_id[url] = current_id
                self.id_to_metadata[current_id] = {
                    'url': url,
                    'title': title,
                    'snippet': snippet
                }
                
                self.next_id += 1
                new_entries += 1
                
                self.logger.info(f"Added to index: {url}")
                
            except Exception as e:
                self.logger.error(f"Failed to process {url}: {e}")
        
        if new_entries > 0:
            self._save_index()
            self.logger.info(f"Processed {new_entries} new entries")
        else:
            self.logger.info("No new entries to process")
    
    def search(self, query: str, top_k: int = 10) -> List[Dict]:
        """
        Search for most similar vectors to query
        
        Args:
            query (str): Search query
            top_k (int): Number of results to return
            
        Returns:
            List[Dict]: List of search results with metadata and scores
        """
        if self.index.ntotal == 0:
            self.logger.warning("Index is empty")
            return []
        
        try:
            # Create query embedding
            query_embedding = self.model.encode(query)
            query_embedding = query_embedding / np.linalg.norm(query_embedding)
            query_embedding = query_embedding.astype(np.float32).reshape(1, -1)
            
            # Search in FAISS index
            top_k = min(top_k, self.index.ntotal)
            scores, indices = self.index.search(query_embedding, top_k)
            
            # Prepare results
            results = []
            for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
                if idx == -1:  # Invalid index
                    continue
                
                metadata = self.id_to_metadata.get(idx, {})
                results.append({
                    'rank': i + 1,
                    'url': metadata.get('url', ''),
                    'title': metadata.get('title', ''),
                    'snippet': metadata.get('snippet', ''),
                    'similarity_score': float(score)
                })
            
            self.logger.info(f"Search completed: {len(results)} results for '{query}'")
            return results
            
        except Exception as e:
            self.logger.error(f"Search failed: {e}")
            return []
    
    def get_urls_by_similarity(self, query: str, top_k: int = 10) -> List[str]:
        """
        Get URLs of most similar pages (for ZeroSearch++)
        
        Args:
            query (str): Search query
            top_k (int): Number of URLs to return
            
        Returns:
            List[str]: List of URLs ordered by similarity
        """
        results = self.search(query, top_k)
        return [result['url'] for result in results if result['url']]
    
    def remove_url(self, url: str) -> bool:
        """
        Remove a URL from the index
        Note: FAISS doesn't support removal, so we mark as deleted in metadata
        
        Args:
            url (str): URL to remove
            
        Returns:
            bool: True if removed, False if not found
        """
        if url not in self.url_to_id:
            return False
        
        faiss_id = self.url_to_id[url]
        
        # Mark as deleted in metadata
        if faiss_id in self.id_to_metadata:
            self.id_to_metadata[faiss_id]['deleted'] = True
        
        # Remove from URL mapping
        del self.url_to_id[url]
        
        self.logger.info(f"Marked as deleted: {url}")
        return True
    
    def rebuild_index(self):
        """
        Rebuild the entire index from queue.json
        Useful for cleanup and optimization
        """
        self.logger.info("Rebuilding index from scratch...")
        
        # Reset index
        self.index = faiss.IndexFlatIP(self.embedding_dim)
        self.url_to_id = {}
        self.id_to_metadata = {}
        self.next_id = 0
        
        # Process queue
        self.process_queue()
        
        self.logger.info("Index rebuild completed")
    
    def get_stats(self) -> Dict:
        """
        Get statistics about the index
        
        Returns:
            Dict: Index statistics
        """
        active_entries = sum(1 for metadata in self.id_to_metadata.values() 
                           if not metadata.get('deleted', False))
        
        return {
            'total_vectors': self.index.ntotal,
            'active_entries': active_entries,
            'deleted_entries': self.index.ntotal - active_entries,
            'embedding_dimension': self.embedding_dim,
            'model_name': self.model._modules['0'].auto_model.name_or_path
        }
    
    def export_metadata(self) -> Dict:
        """
        Export all metadata for backup or analysis
        
        Returns:
            Dict: All metadata including URLs, titles, and snippets
        """
        active_metadata = {}
        for faiss_id, metadata in self.id_to_metadata.items():
            if not metadata.get('deleted', False):
                url = metadata['url']
                active_metadata[url] = {
                    'title': metadata['title'],
                    'snippet': metadata['snippet'],
                    'faiss_id': faiss_id
                }
        
        return active_metadata

# Integration example for ZeroNet
if __name__ == "__main__":
    # Initialize ZeroIndex
    zero_index = ZeroIndex()
    
    print("ZeroIndex - FAISS Vector Database Manager")
    print("Processing queue.json for new entries...")
    
    # Process queue from ZeroScraper
    zero_index.process_queue()
    
    # Display statistics
    stats = zero_index.get_stats()
    print(f"\nIndex Statistics:")
    print(f"Total vectors: {stats['total_vectors']}")
    print(f"Active entries: {stats['active_entries']}")
    print(f"Embedding dimension: {stats['embedding_dimension']}")
    
    # Example search
    if stats['total_vectors'] > 0:
        print(f"\nExample search for 'artificial intelligence':")
        results = zero_index.search("artificial intelligence", top_k=3)
        
        for result in results:
            print(f"\nRank {result['rank']} (Score: {result['similarity_score']:.4f})")
            print(f"Title: {result['title']}")
            print(f"URL: {result['url']}")
            print(f"Snippet: {result['snippet'][:100]}...")
    
    print(f"\nZeroIndex ready for ZeroSearch++ integration")