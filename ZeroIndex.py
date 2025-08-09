# ZeroIndex.py

import faiss
import numpy as np
import pickle
import psycopg2
from sentence_transformers import SentenceTransformer
from config import DATABASE_CONFIG, FAISS_INDEX_PATH, FAISS_INDEX_CONFIG
from psycopg2.extras import RealDictCursor
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FAISS index configuration
INDEX_FACTORY_STRING = FAISS_INDEX_CONFIG.get("factory", "IVF4096,PQ32x8")
NPROBE = FAISS_INDEX_CONFIG.get("nprobe", 8)

# Global variables
index = None
url_labels = []
EMBEDDING_MODEL = None

def get_model():
    """Lazy loading of the embedding model to avoid unnecessary loads in subprocesses."""
    global EMBEDDING_MODEL
    if EMBEDDING_MODEL is None:
        EMBEDDING_MODEL = SentenceTransformer('all-MiniLM-L6-v2')
    return EMBEDDING_MODEL

def get_db_connection():
    return psycopg2.connect(**DATABASE_CONFIG)

def embed_text(text):
    """Generate embedding for a given text."""
    model = get_model()
    embedding = model.encode(text, convert_to_numpy=True).astype('float32')
    return embedding

def save_embedding_to_db(row_id, embedding):
    """Save embedding to the third column (embedding) of the corresponding row."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE scraped_data
            SET embedding = %s
            WHERE id = %s
        """, (pickle.dumps(embedding), row_id))
        conn.commit()
    except Exception as e:
        logger.error(f"Error saving embedding for row {row_id}: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

def load_all_rows():
    """Load all rows from the database with id, url, snippet, embedding."""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cursor.execute("SELECT id, url, snippet, embedding FROM scraped_data")
        rows = cursor.fetchall()
        return rows
    except Exception as e:
        logger.error(f"Error loading rows from DB: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

def reconstruct_index():
    """
    Reconstruct FAISS index from database.
    For each row:
        - If embedding exists in DB, load it.
        - Else if snippet exists, embed it and save to DB.
        - Skip otherwise.
    """
    global index, url_labels

    rows = load_all_rows()
    embeddings = []
    url_labels = []

    logger.info("Reconstructing FAISS index...")

    for row in rows:
        row_id = row['id']
        url = row['url']
        snippet = row['snippet']
        db_embedding = pickle.loads(row['embedding']) if row['embedding'] else None

        if db_embedding is not None:
            embeddings.append(db_embedding)
            url_labels.append(url)
        elif snippet:
            embedding = embed_text(snippet)
            save_embedding_to_db(row_id, embedding)
            embeddings.append(embedding)
            url_labels.append(url)
        else:
            continue

    if not embeddings:
        logger.warning("No embeddings found. Index is empty.")
        return

    embeddings = np.vstack(embeddings)
    dimension = embeddings.shape[1]

    # Build FAISS index
    global index
    index = faiss.index_factory(dimension, INDEX_FACTORY_STRING)
    index.train(embeddings)
    index.add(embeddings)
    index.nprobe = NPROBE  # Set nprobe after training

    logger.info(f"FAISS index reconstructed with {len(url_labels)} entries.")

    # Automatically save index after reconstruction
    save_index()

def save_index(path=FAISS_INDEX_PATH):
    """Save FAISS index to disk (not memory-mapped by default)."""
    if index is None:
        logger.warning("No index to save.")
        return

    faiss.write_index(index, path)
    logger.info(f"FAISS index saved to {path}")

def load_index(path=FAISS_INDEX_PATH):
    """Load FAISS index from disk."""
    global index
    try:
        index = faiss.read_index(path)
        index.nprobe = NPROBE
        logger.info(f"FAISS index loaded from {path}")
    except Exception as e:
        logger.error(f"Failed to load FAISS index: {e}")
        index = None