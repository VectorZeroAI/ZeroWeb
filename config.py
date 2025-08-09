OPENROUTER_API_KEY = "your_API_key_Here"
OPENROUTER_MODEL = "tngtech/deepseek-r1t2-chimera:free"
USE_API = True  # Set to False for local reports (not fully implemented)

# Threading configuration (use integers, not strings)
THREAD_AMOUNT_PER_CORE = 30  # Integer value
CORE_AMOUNT = 4  # Integer value

# Scraping configuration
COMMON_CRAWL_INDEX_NAME = "CC-MAIN-2024-26"  # Update to current Common Crawl index
MAX_URLS_PER_DOMAIN = 1000  # Reasonable limit

# Database configuration
DATABASE_CONFIG = {
    'dbname': 'your_database_name',
    'user': 'your_database_user',
    'password': 'your_password',
    'host': 'localhost',
    'port': 5432
}

# Process configuration (use correct variable names)
SCRAPING_THREADS_PER_PROCESS = THREAD_AMOUNT_PER_CORE
MAX_SCRAPING_PROCESSES = CORE_AMOUNT

# FAISS index configuration
FAISS_INDEX_PATH = 'zeroweb_index.faiss'
FAISS_INDEX_CONFIG = {
    'factory': 'IVF4096,PQ32x8',
    'nprobe': 8
}