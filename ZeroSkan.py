import os
import time
import threading
import multiprocessing as mp
from queue import Queue
import psycopg2
from psycopg2.extras import RealDictCursor
from config import DATABASE_CONFIG, SCRAPING_THREADS_PER_PROCESS, MAX_SCRAPING_PROCESSES
from ZeroScraper import get_snippet, get_URL_list
import signal
import sys
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global control flag for graceful shutdown
shutdown_event = threading.Event()

def initDB(db_path=None):
    """
    Initializes the PostgreSQL database for storing scraped data.
    Creates the table if it doesn't exist.
    """
    conn = psycopg2.connect(**DATABASE_CONFIG)
    cursor = conn.cursor()

    create_table_query = """
    CREATE TABLE IF NOT EXISTS scraped_data (
        id SERIAL PRIMARY KEY,
        url TEXT UNIQUE NOT NULL,
        snippet TEXT,
        embedding BYTEA,
        crawl_delay REAL DEFAULT 1.0,
        full_text TEXT
    );
    """
    cursor.execute(create_table_query)
    conn.commit()
    cursor.close()
    conn.close()
    logger.info("Database initialized.")


def insert_urls_into_db(domains):
    """
    Inserts URLs from domains into the DB using get_URL_list.
    """
    conn = psycopg2.connect(**DATABASE_CONFIG)
    cursor = conn.cursor()

    for domain in domains:
        logger.info(f"Fetching URLs for domain: {domain}")
        urls, delay = get_URL_list(domain)

        for url in urls:
            try:
                cursor.execute(
                    "INSERT INTO scraped_data (url, crawl_delay) VALUES (%s, %s) ON CONFLICT (url) DO NOTHING",
                    (url, delay)
                )
            except Exception as e:
                logger.error(f"Error inserting URL {url}: {e}")

        conn.commit()

    cursor.close()
    conn.close()
    logger.info("All URLs inserted into DB.")


def get_unscraped_rows(batch_size=1000):
    """
    Fetches a batch of unscraped URLs from the DB.
    """
    conn = psycopg2.connect(**DATABASE_CONFIG)
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    cursor.execute("""
        SELECT id, url, crawl_delay
        FROM scraped_data
        WHERE snippet IS NULL
        LIMIT %s
    """, (batch_size,))

    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


def update_snippet_in_db(row_id, snippet):
    """
    Updates the snippet for a given row in the DB.
    """
    conn = psycopg2.connect(**DATABASE_CONFIG)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE scraped_data
            SET snippet = %s
            WHERE id = %s
        """, (snippet, row_id))
        conn.commit()
    except Exception as e:
        logger.error(f"Error updating snippet for row {row_id}: {e}")
    finally:
        cursor.close()
        conn.close()


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
            update_snippet_in_db(row_id, snippet)
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


def start_scraping(domains):
    """
    Main scraping orchestrator.
    """
    logger.info("Starting scraping process...")
    initDB()

    # Insert URLs into DB
    insert_urls_into_db(domains)

    # Fetch all unscraped rows
    rows = get_unscraped_rows()

    if not rows:
        logger.info("No rows to scrape.")
        return

    # Split rows into chunks for multiprocessing
    chunk_size = max(1, len(rows) // MAX_SCRAPING_PROCESSES)
    row_chunks = [rows[i:i + chunk_size] for i in range(0, len(rows), chunk_size)]

    processes = []
    for chunk in row_chunks:
        p = start_scraping_process(chunk)
        processes.append(p)

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


def end_scraping():
    """
    Gracefully shuts down scraping and saves DB.
    """
    logger.info("Shutting down scraping...")
    shutdown_event.set()
    # DB is saved automatically on commit/close in each function