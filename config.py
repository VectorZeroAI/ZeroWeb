OPENROUTER_API_KEY = "your_API_key_Here"
OPENROUTER_MODEL = "tngtech/deepseek-r1t2-chimera:free"
USE_API = True  # Set to False for local reports 
USE_LOCAL_LLM = False
LOCAL_LLM_MODEL_PATH = "input path to your model here."
LOCAL_LLM_N_CTX = 2048
LOCAL_LLM_N_THREADS = 8

THREAD_AMOUNT_PER_CORE = 30
CORE_AMOUNT = 4

# Scraping configuration
COMMON_CRAWL_INDEX_NAME = "CC-MAIN-2024-26"  # Update to current Common Crawl index
MAX_URLS_PER_DOMAIN = 1000  # I recommend increasing

# Database configuration (PostgreSQL DB) look in for a guide on Youtube
DATABASE_CONFIG = {
    'dbname': 'your_database_name',
    'user': 'your_database_user',
    'password': 'your_password',
    'host': 'localhost',
    'port': 5432
}


#Dont change this!!!
SCRAPING_THREADS_PER_PROCESS = THREAD_AMOUNT_PER_CORE
MAX_SCRAPING_PROCESSES = CORE_AMOUNT

# Change at your own risk, this setup is optimised 
# for 1 milion + webpages. 
# FAISS is the name for the library
# go read documentation if you think your a nerd.

FAISS_INDEX_PATH = 'zeroweb_index.faiss'
FAISS_INDEX_CONFIG = {
    'factory': 'IVF4096,PQ32x8',
    'nprobe': 8
}