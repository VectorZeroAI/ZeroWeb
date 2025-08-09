# ZeroSkan.py
import os
import time
import threading
import multiprocessing as mp
from queue import Queue
import psycopg2
from psycopg2.extras import RealDictCursor
# Import SCHEMA_NAME if defined in config.py, otherwise use 'zeroweb'
try:
    from config import DATABASE_CONFIG, SCRAPING_THREADS_PER_PROCESS, MAX_SCRAPING_PROCESSES, SCHEMA_NAME
except ImportError:
    from config import DATABASE_CONFIG, SCRAPING_THREADS_PER_PROCESS, MAX_SCRAPING_PROCESSES
    SCHEMA_NAME = "zeroweb" # Default schema name if not in config

from ZeroScraper import get_snippet, get_URL_list
import signal
import sys
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global control flag for graceful shutdown
shutdown_event = threading.Event()

def initDB(db_path=None): # db_path is unused based on current implementation, kept for signature compatibility
    """
    Initializes the PostgreSQL database for storing scraped data.
    Ensures the designated schema exists and creates the table within it.
    """
    conn = None
    cursor = None
    try:
        conn = psycopg2.connect(**DATABASE_CONFIG)
        cursor = conn.cursor()

        # Ensure the schema exists
        cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {SCHEMA_NAME};")
        logger.info(f"Schema '{SCHEMA_NAME}' ensured to exist.")

        # Set the search path for this session/connection to the schema
        # This makes subsequent table operations apply to this schema
        # unless fully qualified names are used.
        cursor.execute(f"SET LOCAL search_path TO {SCHEMA_NAME};")

        # Create the table within the specified schema context
        # Using IF NOT EXISTS to prevent errors if the table already exists in the schema
        create_table_query = """
        CREATE TABLE IF NOT EXISTS scraped_data (
            id SERIAL PRIMARY KEY,
            url TEXT UNIQUE NOT NULL,
            snippet TEXT,
            embedding BYTEA, -- Stores pickled numpy array
            crawl_delay REAL DEFAULT 1.0,
            full_text TEXT
        );
        """
        cursor.execute(create_table_query)
        conn.commit()
        logger.info(f"Database table 'scraped_data' initialized within schema '{SCHEMA_NAME}'.")

    except psycopg2.Error as e:
        error_msg = f"Database initialization error: {e}"
        logger.error(error_msg)
        if conn:
            conn.rollback() # Rollback in case of error during setup
    except Exception as e:
        logger.error(f"Unexpected error during DB initialization: {e}", exc_info=True)
    finally:
        # Ensure resources are closed
        if cursor:
            cursor.close()
        if conn:
            conn.close() # Commit was called inside the try block if successful


def insert_urls_into_db(domains):
    """
    Inserts URLs from domains into the DB using get_URL_list.
    Assumes the schema and table are already set up correctly.
    """
    conn = None
    cursor = None
    try:
        conn = psycopg2.connect(**DATABASE_CONFIG)
        # Optionally set schema context for this connection if not handled globally
        # cursor = conn.cursor()
        # cursor.execute(f"SET LOCAL search_path TO {SCHEMA_NAME};")
        # conn.commit() # Commit the search_path setting if needed for the session
        # cursor.close()
        # Better: Assume DATABASE_CONFIG or connection defaults handle schema,
        # or explicitly set it per operation if needed.
        # For simplicity here, rely on setup or config.

        # Reconnect or use existing connection appropriately
        # It's safer to manage the schema context explicitly if not sure about config
        cursor = conn.cursor()
        cursor.execute(f"SET LOCAL search_path TO {SCHEMA_NAME};")

        for domain in domains:
            logger.info(f"Fetching URLs for domain: {domain}")
            urls, delay = get_URL_list(domain)
            for url in urls:
                try:
                    # Use ON CONFLICT to avoid errors if URL already exists
                    cursor.execute(
                        "INSERT INTO scraped_data (url, crawl_delay) VALUES (%s, %s) ON CONFLICT (url) DO NOTHING",
                        (url, delay)
                    )
                except psycopg2.Error as e: # Catch database-specific errors
                    logger.error(f"Database error inserting URL {url}: {e}")
                except Exception as e: # Catch other potential errors from get_URL_list
                    logger.error(f"Error processing URL {url} from {domain}: {e}")
            conn.commit() # Commit after processing each domain's URLs
    except psycopg2.Error as e:
        error_msg = f"Database error in insert_urls_into_db: {e}"
        logger.error(error_msg)
        if conn:
            conn.rollback()
    except Exception as e:
        logger.error(f"Unexpected error in insert_urls_into_db: {e}", exc_info=True)
        if conn:
            conn.rollback()
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    logger.info("All URLs insertion attempt completed.")


def get_unscraped_rows(batch_size=1000):
    """
    Fetches a batch of unscraped URLs from the DB using FOR UPDATE SKIP LOCKED.
    This ensures that multiple processes don't work on the same URLs.
    Assumes the schema and table are correctly set up.
    """
    conn = None
    cursor = None
    rows = []
    try:
        conn = psycopg2.connect(**DATABASE_CONFIG)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(f"SET LOCAL search_path TO {SCHEMA_NAME};")

        # Start a transaction (implicitly started by psycopg2, but good practice to note)
        # cursor.execute("BEGIN;") # Not strictly necessary, but shows intent

        # Select unscraped rows with locking
        cursor.execute("""
            SELECT id, url, crawl_delay
            FROM scraped_data
            WHERE snippet IS NULL
            ORDER BY id
            LIMIT %s
            FOR UPDATE SKIP LOCKED
        """, (batch_size,))
        rows = cursor.fetchall()
        # Commit the transaction to release locks
        conn.commit()
        logger.debug(f"Fetched {len(rows)} unscraped rows.")
    except psycopg2.Error as e:
        error_msg = f"Database error fetching unscraped rows: {e}"
        logger.error(error_msg)
        if conn:
            conn.rollback()
    except Exception as e:
         logger.error(f"Unexpected error fetching unscraped rows: {e}", exc_info=True)
         if conn:
             conn.rollback()
    finally:
        if cursor:
            cursor.close()
        # Don't close conn here if you plan to reuse it within the same process/thread context
        # For this function returning a list, closing is appropriate.
        if conn:
            conn.close()
    return rows


def update_snippet_in_db(row_id, snippet):
    """
    Updates the snippet for a given row in the DB.
    Assumes the schema and table are correctly set up.
    """
    conn = None
    cursor = None
    try:
        conn = psycopg2.connect(**DATABASE_CONFIG)
        cursor = conn.cursor()
        cursor.execute(f"SET LOCAL search_path TO {SCHEMA_NAME};")

        cursor.execute("""
            UPDATE scraped_data
            SET snippet = %s
            WHERE id = %s
        """, (snippet, row_id))
        # Check if any row was updated?
        # rows_affected = cursor.rowcount
        # if rows_affected == 0:
        #     logger.warning(f"No rows updated for id {row_id}. Row might not exist.")
        conn.commit()
        logger.debug(f"Snippet updated for row id {row_id}.")
    except psycopg2.Error as e:
        error_msg = f"Database error updating snippet for row {row_id}: {e}"
        logger.error(error_msg)
        if conn:
            conn.rollback()
    except Exception as e:
         logger.error(f"Unexpected error updating snippet for row {row_id}: {e}", exc_info=True)
         if conn:
             conn.rollback()
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# --- Placeholder/Unchanged Functions (for context) ---
# The functions below are not directly related to schema creation but are part of the file.
# Their database interactions now implicitly rely on the schema being correctly set up
# or the DATABASE_CONFIG handling it, or they explicitly set the search_path as shown above.

def scrape_worker(url_queue):
    """
    Worker thread function that scrapes snippets.
    """
    while not shutdown_event.is_set():
        try:
            row = url_queue.get(timeout=1)
        except:
            continue
        url = row['url']
        row_id = row['id']
        delay = row.get('crawl_delay', 1.0)
        try:
            _, snippet = get_snippet(url)
            update_snippet_in_db(row_id, snippet) # This now uses the schema context
            logger.debug(f"Scraped snippet for {url}")
        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")
        time.sleep(delay)
        url_queue.task_done()

def start_scraping_core(rows):
    """
    Starts scraping threads for a given list of rows.
    """
    url_queue = Queue()
    # Add rows to queue
    for row in rows:
        url_queue.put(row)
    # Start threads
    threads = []
    for _ in range(SCRAPING_THREADS_PER_PROCESS):
        t = threading.Thread(target=scrape_worker, args=(url_queue,))
        t.start()
        threads.append(t)
    # Wait for all tasks to complete or shutdown
    try:
        while not url_queue.empty() and not shutdown_event.is_set():
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Received interrupt signal.")
        shutdown_event.set()
    url_queue.join()
    for t in threads:
        t.join()
    logger.info("Scraping core finished.")

def start_scraping_process(rows):
    """
    Starts a new process to run scraping on a subset of rows.
    """
    process = mp.Process(target=start_scraping_core, args=(rows,))
    process.start()
    return process

def continuous_scraping_worker():
    """
    Worker function that continuously fetches batches and processes them.
    This replaces the static batch approach for better dynamic load balancing.
    """
    while not shutdown_event.is_set():
        # Fetch a new batch of unscraped rows
        # This function now correctly uses the schema
        rows = get_unscraped_rows(batch_size=100)
        if not rows:
            logger.info("No more unscraped rows found. Waiting before retry...")
            time.sleep(5)  # Wait before retrying
            continue
        logger.info(f"Processing batch of {len(rows)} URLs")
        # Process this batch
        url_queue = Queue()
        for row in rows:
            url_queue.put(row)
        # Start threads for this batch
        threads = []
        for _ in range(SCRAPING_THREADS_PER_PROCESS):
            t = threading.Thread(target=scrape_worker, args=(url_queue,))
            t.start()
            threads.append(t)
        # Wait for completion or shutdown
        try:
            url_queue.join()
        except KeyboardInterrupt:
            shutdown_event.set()
        # Join threads
        for t in threads:
            t.join()
        if shutdown_event.is_set():
            break

def start_scraping_process_continuous():
    """
    Starts a process that continuously fetches and processes batches.
    """
    process = mp.Process(target=continuous_scraping_worker)
    process.start()
    return process

def start_scraping(domains):
    """
    Main scraping orchestrator using continuous batch processing.
    """
    logger.info("Starting scraping process...")
    # Initialize DB schema and table
    initDB() # This now ensures schema and table exist
    # Insert URLs into DB (now uses schema context)
    insert_urls_into_db(domains)
    # Start continuous scraping processes
    processes = []
    for _ in range(MAX_SCRAPING_PROCESSES):
        p = start_scraping_process_continuous()
        processes.append(p)
        time.sleep(0.1)  # Small delay to stagger process starts
    try:
        # Wait for all processes
        for p in processes:
            p.join()
    except KeyboardInterrupt:
        logger.info("Terminating scraping processes...")
        shutdown_event.set()
        for p in processes:
            p.terminate()
            p.join()
    logger.info("All scraping processes completed.")

def end_scraping():
    """
    Gracefully shuts down scraping and saves DB.
    """
    logger.info("Shutting down scraping...")
    shutdown_event.set()
    # DB is saved automatically on commit/close in each function
    # No specific DB saving needed here beyond ensuring transactions are committed
    # which the individual functions handle.
