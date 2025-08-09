OPENROUTER_API_KEY = "your API key Here"
TREAD_AMOUNT_PER_CORE = "30" #You may even want a lot more, because each one of them is really, REALLY slow.
CORE_AMOUNT = "4" #minimum 2 for the programm to funktion properly.
DOMAINS = ["en.wikipedia.org","arxiv.org"]
MAX_URLS_PER_DOMAIN = 100000000000

DATABASE_CONFIG = {
    'dbname': 'your_database_name',
    'user': 'your_database_user',
    'password': 'your_password',
    'host': 'localhost',  # or your DB server address
    'port': 5432           # default PostgreSQL port
}

#IMPORTANT!!! YOU NEED TO SET UP A POSTGRESQL DB FIRST! Google how that works if you dont know, it is easy.

SCRAPING_THREADS_PER_PROCESS = THREAD_AMOUNT_PER_CORE
MAX_SCRAPING_PROCESSES = CORE_AMOUNT


# FAISS index configuration
FAISS_INDEX_PATH = 'zeroweb_index.faiss'
FAISS_INDEX_CONFIG = {
    'factory': 'IVF4096,PQ32x8',
    'nprobe': 8
}