# ZeroSearch++.py (modifications)
import psycopg2
import faiss
import numpy as np
import pickle
import logging
# --- Import for local LLM ---
try:
    from llama_cpp import Llama
    LOCAL_LLM_AVAILABLE = True
except ImportError:
    LOCAL_LLM_AVAILABLE = False
    logging.warning("llama-cpp-python not found. Local LLM reporting will not be available unless installed.")

from config import (
    DATABASE_CONFIG, FAISS_INDEX_PATH, OPENROUTER_API_KEY, OPENROUTER_MODEL, USE_API,
    # --- Import local LLM config ---
    USE_LOCAL_LLM, LOCAL_LLM_MODEL_PATH, LOCAL_LLM_N_CTX,
    LOCAL_LLM_N_THREADS, LOCAL_LLM_PROMPT_TEMPLATE
)
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
# --- Global variable for local LLM ---
LOCAL_LLM = None

# --- Function to initialize the local LLM ---
def get_local_llm():
    """Lazy loading of the local LLM."""
    global LOCAL_LLM
    if LOCAL_LLM is None and USE_LOCAL_LLM and LOCAL_LLM_AVAILABLE:
        try:
            logger.info(f"Loading local LLM from {LOCAL_LLM_MODEL_PATH}...")
            # Initialize the LLM. Adjust parameters as needed.
            # n_gpu_layers=-1 attempts to offload all layers to GPU if available (requires cuBLAS).
            LOCAL_LLM = Llama(
                model_path=LOCAL_LLM_MODEL_PATH,
                n_ctx=LOCAL_LLM_N_CTX,
                n_threads=LOCAL_LLM_N_THREADS,
                # n_gpu_layers=-1, # Uncomment if you want to use GPU acceleration
                verbose=False # Reduce llama-cpp logs
            )
            logger.info("Local LLM loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load local LLM: {e}")
            LOCAL_LLM = None # Ensure it stays None on failure
    return LOCAL_LLM


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
    return "\n\n---\n\n".join(full_texts) # Join with separators

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
    # Use the prompt template from config if available, otherwise default
    prompt = LOCAL_LLM_PROMPT_TEMPLATE.format(text=text) if '{text}' in LOCAL_LLM_PROMPT_TEMPLATE else f"Compile the following information into a comprehensive report:\n{text}"

    payload = {
        "model": OPENROUTER_MODEL,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
         "max_tokens": 2048 # Adjust as needed
    }
    try:
        # Ensure the URL is correct (remove trailing space if present in original)
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
        return f"Error generating report via API: {str(e)}"

# --- Modified generate_report_locally function ---
def generate_report_locally(text):
    """
    Generate report using a local LLM.
    Args:
        text (str): Text to generate report from
    Returns:
        str: Generated report
    """
    if not USE_LOCAL_LLM:
        return "Local LLM usage is disabled in config."
    if not LOCAL_LLM_AVAILABLE:
         return "Local LLM library (e.g., llama-cpp-python) is not installed."

    llm = get_local_llm()
    if llm is None:
        return "Failed to load local LLM. Check logs and configuration."

    try:
        # Use the prompt template from config if available, otherwise default
        prompt = LOCAL_LLM_PROMPT_TEMPLATE.format(text=text) if '{text}' in LOCAL_LLM_PROMPT_TEMPLATE else f"Compile the following information into a comprehensive report:\n{text}"

        logger.info("Generating report using local LLM...")
        # Generate the report
        # Adjust parameters like max_tokens, temperature, top_p as needed
        output = llm(
            prompt,
            max_tokens=2048, # Adjust based on your needs/model capacity
            temperature=0.7,
            top_p=0.9,
            echo=False,
            stop=[] # Add stop sequences if needed
        )
        report_text = output['choices'][0]['text']
        logger.info("Local LLM report generation completed.")
        return report_text.strip() # Return the generated text, stripped of leading/trailing whitespace

    except Exception as e:
        error_msg = f"Error generating report with local LLM: {e}"
        logger.error(error_msg, exc_info=True) # Log the full traceback
        return error_msg

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

# Initialize on module load (optional logging)
logger.info("ZeroSearch++ module loaded")
