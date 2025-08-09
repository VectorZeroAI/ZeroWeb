# ZeroSearch++.py

import psycopg2
import faiss
import numpy as np
import pickle
import logging
from config import DATABASE_CONFIG, FAISS_INDEX_PATH, OPENROUTER_API_KEY, OPENROUTER_MODEL, USE_API
import requests
from ZeroScraper import get_fullpage
from psycopg2.extras import RealDictCursor
from sentence_transformers import SentenceTransformer

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variables
index = None
url_labels = []
EMBEDDING_MODEL = None

def get_embedding_model():
    """Lazy loading of the embedding model to avoid unnecessary loads."""
    global EMBEDDING_MODEL
    if EMBEDDING_MODEL is None:
        EMBEDDING_MODEL = SentenceTransformer('all-MiniLM-L6-v2')
        logger.info("Embedding model loaded")
    return EMBEDDING_MODEL

def get_db_connection():
    """Create a database connection."""
    return psycopg2.connect(**DATABASE_CONFIG)

def load_index():
    """Load the FAISS index from disk."""
    global index
    try:
        index = faiss.read_index(FAISS_INDEX_PATH)
        logger.info(f"FAISS index loaded from {FAISS_INDEX_PATH}")
        return True
    except Exception as e:
        logger.error(f"Failed to load FAISS index: {e}")
        return False

def load_url_labels():
    """Load URL labels from database."""
    global url_labels
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT url FROM scraped_data ORDER BY id")
        url_labels = [row[0] for row in cursor.fetchall()]
        logger.info(f"Loaded {len(url_labels)} URL labels from database")
        return True
    except Exception as e:
        logger.error(f"Error loading URL labels: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def initialize_search():
    """Initialize search functionality by loading index and URL labels."""
    if not load_index():
        return False
    if not load_url_labels():
        return False
    return True

def reload_index():
    """Reload the FAISS index and URL labels from disk."""
    global index, url_labels
    logger.info("Reloading FAISS index and URL labels")
    index = None
    url_labels = []
    return initialize_search()

def search(query, amount=10):
    """
    Search for similar documents using FAISS.
    
    Args:
        query (str): Search query
        amount (int): Number of results to return
        
    Returns:
        list: List of URLs matching the query
    """
    global index, url_labels
    
    if index is None or not url_labels:
        if not initialize_search():
            logger.error("Failed to initialize search")
            return []

    # Embed the query using cached model
    model = get_embedding_model()
    query_embedding = model.encode([query], convert_to_numpy=True).astype('float32')
    
    # Search the index
    try:
        distances, indices = index.search(query_embedding, amount)
        results = [url_labels[i] for i in indices[0] if i < len(url_labels)]
        return results
    except Exception as e:
        logger.error(f"Error during search: {e}")
        return []

def get_full_text_for_report(urls):
    """
    Get full text for URLs, either from DB or by scraping.
    
    Args:
        urls (list): List of URLs to get text for
        
    Returns:
        str: Concatenated full texts
    """
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    full_texts = []
    
    try:
        for url in urls:
            # Check if full text already exists in DB
            cursor.execute(
                "SELECT full_text FROM scraped_data WHERE url = %s", 
                (url,)
            )
            row = cursor.fetchone()
            
            if row and row['full_text']:
                full_texts.append(row['full_text'])
                logger.debug(f"Using cached full text for {url}")
            else:
                # Scrape full text
                logger.info(f"Scraping full text for {url}")
                full_text = get_fullpage(url)
                if full_text:
                    # Save to DB
                    cursor.execute(
                        "UPDATE scraped_data SET full_text = %s WHERE url = %s",
                        (full_text, url)
                    )
                    conn.commit()
                    full_texts.append(full_text)
                else:
                    logger.warning(f"Failed to get full text for {url}")
    except Exception as e:
        logger.error(f"Error getting full text: {e}")
    finally:
        cursor.close()
        conn.close()
    
    return "\n\n".join(full_texts)

def generate_report_with_api(text):
    """
    Generate report using OpenRouter API.
    
    Args:
        text (str): Text to generate report from
        
    Returns:
        str: Generated report
    """
    if not OPENROUTER_API_KEY:
        logger.error("OpenRouter API key not configured")
        return "API key not configured"
    
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": OPENROUTER_MODEL,
        "messages": [
            {
                "role": "user",
                "content": f"Compile the following information into a comprehensive report:\n\n{text}"
            }
        ]
    }
    
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=120
        )
        response.raise_for_status()
        result = response.json()
        return result['choices'][0]['message']['content']
    except Exception as e:
        logger.error(f"Error calling OpenRouter API: {e}")
        return f"Error generating report: {str(e)}"

def generate_report_locally(text):
    """
    Generate report using local model (placeholder).
    
    Args:
        text (str): Text to generate report from
        
    Returns:
        str: Generated report
    """
    # This is a placeholder - in a real implementation you would
    # use a local LLM like llama.cpp or similar
    return f"LOCAL MODEL REPORT (not implemented):\n\n{text[:500]}..."

def report(urls):
    """
    Generate a comprehensive report from a list of URLs.
    
    Args:
        urls (list): List of URLs to generate report from
        
    Returns:
        str: Generated report
    """
    if not urls:
        return "No URLs provided for report generation"
    
    # Get full text for all URLs
    full_text = get_full_text_for_report(urls)
    
    if not full_text:
        return "Failed to retrieve content for report generation"
    
    # Generate report based on configuration
    if USE_API:
        logger.info("Generating report using OpenRouter API")
        return generate_report_with_api(full_text)
    else:
        logger.info("Generating report using local model")
        return generate_report_locally(full_text)

# Initialize on module load
logger.info("ZeroSearch++ module loaded")