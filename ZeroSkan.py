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

# --- Add a global variable to hold the progress callback ---
progress_callback = None

# --- Modify initDB function signature (no change needed for schema, just clarity) ---
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
        cursor.execute(f"SET LOCAL search_path TO {SCHEMA_NAME};")
        # Create the table within the specified schema context
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
            conn.rollback()
    except Exception as e:
        logger.error(f"Unexpected error during DB initialization: {e}", exc_info=True)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# --- Modify insert_urls_into_db to return the count of inserted/total URLs ---
def insert_urls_into_db(domains):
    """
    Inserts URLs from domains into the DB using get_URL_list.
    Assumes the schema and table are already set up correctly.
    Returns the total count of URLs attempted to be inserted.
    """
    conn = None
    cursor = None
    total_urls = 0
    try:
        conn = psycopg2.connect(**DATABASE_CONFIG)
        cursor = conn.cursor()
        cursor.execute(f"SET LOCAL search_path TO {SCHEMA_NAME};")
        for domain in domains:
            logger.info(f"Fetching URLs for domain: {domain}")
            urls, delay = get_URL_list(domain)
            total_urls += len(urls) # Increment total attempted URLs
            for url in urls:
                try:
                    cursor.execute(
                        "INSERT INTO scraped_data (url, crawl_delay) VALUES (%s, %s) ON CONFLICT (url) DO NOTHING",
                        (url, delay)
                    )
                except psycopg2.Error as e:
                    logger.error(f"Database error inserting URL {url}: {e}")
                except Exception as e:
                    logger.error(f"Error processing URL {url} from {domain}: {e}")
            conn.commit()
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
    logger.info(f"All URLs insertion attempt completed. Total URLs attempted: {total_urls}")
    return total_urls # Return the total count


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



def scrape_worker(url_queue, progress_lock, processed_count):
    """
    Worker thread function that scrapes snippets.
    Reports progress via shared variables and a callback.
    """
    global progress_callback # Access the global callback
    while not shutdown_event.is_set():
        try:
            row = url_queue.get(timeout=1)
        except:
            continue
        url = row['url']
        row_id = row['id']
        delay = row.get('crawl_delay', 1.0)
        success = False
        try:
            _, snippet = get_snippet(url)
            update_snippet_in_db(row_id, snippet)
            logger.debug(f"Scraped snippet for {url}")
            success = True
        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")
        finally:
            # Always mark task as done and update progress
            url_queue.task_done()
            with progress_lock:
                processed_count.value += 1
                current_count = processed_count.value
            # Call the progress callback if set
            if progress_callback:
                try:
                    # Pass the current count and a flag indicating success if needed
                    progress_callback(current_count, success)
                except Exception as e:
                    logger.error(f"Error calling progress callback: {e}")

            time.sleep(delay) # Respect crawl delay



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

# --- Modify continuous_scraping_worker to accept and use shared state for progress ---
def continuous_scraping_worker(progress_lock, processed_count):
    """
    Worker function that continuously fetches batches and processes them.
    This replaces the static batch approach for better dynamic load balancing.
    Uses shared state for progress tracking.
    """
    global progress_callback # Access the global callback
    while not shutdown_event.is_set():
        rows = get_unscraped_rows(batch_size=100)
        if not rows:
            logger.info("No more unscraped rows found. Waiting before retry...")
            time.sleep(5)
            continue
        logger.info(f"Processing batch of {len(rows)} URLs")
        url_queue = Queue()
        for row in rows:
            url_queue.put(row)

        # --- Use threading instead of multiprocessing for threads within a process ---
        # --- Share the lock and counter with threads ---
        threads = []
        # Number of threads is defined in config
        num_threads = SCRAPING_THREADS_PER_PROCESS
        for _ in range(num_threads):
            t = threading.Thread(target=scrape_worker, args=(url_queue, progress_lock, processed_count))
            t.start()
            threads.append(t)

        try:
            url_queue.join() # Wait for all tasks in the queue to be processed
        except KeyboardInterrupt:
            shutdown_event.set()

        # Join threads
        for t in threads:
            t.join()

        if shutdown_event.is_set():
            break

def start_scraping_process_continuous(progress_lock, processed_count):
    """
    Starts a process that continuously fetches and processes batches.
    Passes shared state for progress tracking.
    """
    # Pass the shared lock and counter to the worker function
    process = mp.Process(target=continuous_scraping_worker, args=(progress_lock, processed_count))
    process.start()
    return process

def start_scraping(domains, progress_cb=None):
    """
    Main scraping orchestrator using continuous batch processing.
    Accepts a progress callback function: progress_cb(current_count, success_flag).
    """
    global progress_callback
    logger.info("Starting scraping process...")
    progress_callback = progress_cb # Set the global callback

    initDB()
    total_urls = insert_urls_into_db(domains) # Get total URL count

    # --- Create shared state for progress tracking ---
    manager = mp.Manager()
    progress_lock = manager.Lock()
    processed_count = manager.Value('i', 0) # Shared integer counter

    processes = []
    for _ in range(MAX_SCRAPING_PROCESSES):
        # Pass the shared lock and counter to the process starter
        p = start_scraping_process_continuous(progress_lock, processed_count)
        processes.append(p)
        time.sleep(0.1)

    try:
        for p in processes:
            p.join()
    except KeyboardInterrupt:
        logger.info("Terminating scraping processes...")
        shutdown_event.set()
        for p in processes:
            p.terminate()
            p.join()

    logger.info("All scraping processes completed.")
    # Ensure final progress update if callback exists
    if progress_callback and total_urls > 0:
        try:
             # Get the final count one last time
             with progress_lock:
                 final_count = processed_count.value
             progress_callback(final_count, True) # Final call, assume success for completion signal
        except Exception as e:
             logger.error(f"Error calling final progress callback: {e}")

    # Return total_urls for use by the caller (ZeroMain)
    return total_urls

def end_scraping():
    """
    Gracefully shuts down scraping and saves DB.
    """
    logger.info("Shutting down scraping...")
    shutdown_event.set()
    # DB is saved automatically on commit/close in each function
    # No specific DB saving needed here beyond ensuring transactions are committed
    # which the individual functions handle.
