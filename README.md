# ZeroWeb
NOT YET DONE!!!

A lokal AI powered Web Search engine.

Uses Semantic similarity search of the webpages
to deside wich URLs to give, or what sites to use
to create a full AI powered report.


Installation Instructions:
Run install_requierements.py
Copy all the modules from the Repo into the the Foulder.
Run main.py to start the Programm.


Module Index for ZeroNet Networking Tools Suite:

1. Interface Module (HTML/JavaScript - Frontend)
- switchTab(tabName): Switches between Search and Index tabs
- toggleSwitch(): Toggles between URL and AI Answer output modes
- addDomain(): Adds domain to scanning list
- showDomains(): Displays current domain list
- startIndexing(): Initiates domain indexing process
- startSearch(): Executes search operation
- simulateIndexingProcess(): Visualizes indexing progress
- simulateSearch(query): Generates mock search results
- updateModuleStatus(moduleId, status): Updates module status indicators

---

2. ZeroCompiler Module (LLM Report Generator)
Class: ZeroCompiler
- compile_response(query): Main compilation function
- get_report_history(): Retrieves past report history
- clear_reports(): Clears all saved reports
- _chunk_content(): Splits content for processing
- _generate_chunk_report(): Creates report for content chunk
- _synthesize_final_report(): Combines individual reports

---

3. ZeroIndex Module (Vector Database Manager)
Class: ZeroIndex
- process_queue(): Processes queue.json entries
- search(query): Performs vector similarity search
- get_urls_by_similarity(): Gets URLs ordered by relevance
- remove_url(): Removes URL from index
- rebuild_index(): Rebuilds entire index
- get_stats(): Returns index statistics
- export_metadata(): Exports metadata for backup

---

4. ZeroOS Module (Sandboxing System)
Class: ZeroOS
- start(): Starts all modules
- shutdown(): Gracefully shuts down system
- start_module(): Starts specific module
- stop_module(): Stops specific module
- restart_module(): Restarts module
- execute_pipeline(): Executes predefined workflows
- get_system_status(): Returns comprehensive status
- send_message(): Inter-module communication
- _monitor_resources(): Resource usage monitoring

---

5. ZeroSkan Module (Domain Scanner)
Class: ZeroSkan
- add_domain(): Adds domain to scanning list
- remove_domain(): Removes domain from list
- scan_all_domains(): Scans all managed domains
- crawl_domain(): Discovers pages within domain
- get_urls_for_scraper(): Provides URLs to scraper
- get_stats(): Returns scanning statistics
- clear_discovered_links(): Clears discovered URLs

---

6. ZeroScraper Module (Content Extractor)
Class: ZeroScraper
- scrape_page(): Extracts title/snippet from URL
- scrape_urls(): Scrapes multiple URLs concurrently
- scrape_from_domain_list(): Processes domain URL lists
- add_to_queue(): Adds results to processing queue
- get_queue_data(): Returns current queue contents
- get_queue_stats(): Returns scraping statistics
- clear_queue(): Clears scraping queue

---

7. ZeroSearch Module (Search Engine)
Class: ZeroSearch
- search_and_extract(): Performs search + content extraction
- get_urls_only(): Returns only URLs without content
- get_search_summary(): Returns search statistics
- rerank_results(): Re-ranks results with custom criteria
- get_content_for_url(): Gets extracted content for URL
- clear_cache(): Clears search cache

Class: ZeroSearchIntegrator
- search_for_compiler(): Prepares content for ZeroCompiler