# ZeroMain.py
import time
import logging
from typing import List, Optional, Any
# Import the modules we'll be working with
from ZeroSkan import start_scraping, end_scraping
from ZeroIndex import reconstruct_index
from ZeroSearch import search as semantic_search, report as generate_report
import threading

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ZeroMain:
    def __init__(self, gui_instance=None):
        """
        Initializes the ZeroMain application logic.
        :param gui_instance: An instance of ZeroGUI for communication.
                             If None, placeholders are used.
        """
        self.state = "HALT"
        self.running = True
        self.current_query = None
        self.current_domains = None
        self.ai_mode = False
        self.search_results = None
        self.indexing_in_progress = False
        self.gui = gui_instance # Store the GUI instance

        # Assign actual GUI methods or placeholders
        if self.gui:
            self.gui_update_status = self.gui.update_status
            self.gui_show_results = self.gui.show_results
            self.gui_update_progress = self.gui.update_progress
            self.gui_request_domains = self.gui.get_domains_from_gui
            self.gui_request_query = self.gui.get_query_from_gui
            self.gui_request_ai_mode = self.gui.get_ai_mode_from_gui
            self.gui_notify_indexing_complete = self.gui.on_indexing_finished # Or a custom method if needed
        else:
            # Fallback to placeholders if no GUI instance is provided
            self.gui_update_status = self._placeholder_gui_update_status
            self.gui_show_results = self._placeholder_gui_show_results
            self.gui_update_progress = self._placeholder_gui_update_progress
            self.gui_request_domains = self._placeholder_gui_request_domains
            self.gui_request_query = self._placeholder_gui_request_query
            self.gui_request_ai_mode = self._placeholder_gui_request_ai_mode
            self.gui_notify_indexing_complete = self._placeholder_gui_notify_indexing_complete

        logger.info("ZeroMain initialized")

    # --- Placeholder GUI Communication Functions (Fallback) ---
    def _placeholder_gui_update_status(self, status: str):
        """Placeholder for GUI status update function"""
        logger.info(f"GUI Status Update: {status}")

    def _placeholder_gui_show_results(self, results: Any):
        """Placeholder for GUI results display function"""
        logger.info(f"GUI Results Display: {results}") # Log type/info

    def _placeholder_gui_update_progress(self, progress: float):
        """Placeholder for GUI progress update function"""
        logger.debug(f"GUI Progress Update: {progress}%")

    def _placeholder_gui_request_domains(self) -> List[str]:
        """Placeholder for GUI domains request function"""
        logger.info("GUI Domains Request")
        return ["wikipedia.org", "github.com"] # Default fallback

    def _placeholder_gui_request_query(self) -> str:
        """Placeholder for GUI query request function"""
        logger.info("GUI Query Request")
        return "machine learning" # Default fallback

    def _placeholder_gui_request_ai_mode(self) -> bool:
        """Placeholder for GUI AI mode request function"""
        logger.info("GUI AI Mode Request")
        return False # Default fallback

    def _placeholder_gui_notify_indexing_complete(self):
        """Placeholder for GUI indexing completion notification"""
        logger.info("GUI Notified: Indexing process completed (success or failure)")

    # --- Main Application Loop ---
    def loop(self):
        """Main application loop"""
        logger.info("Starting ZeroMain loop")
        while self.running:
            if self.state == "HALT":
                self.handle_halt()
            elif self.state == "INDEX":
                self.handle_index()
            elif self.state == "SEARCH":
                self.handle_search()
            elif self.state == "SAVE_SHUTDOWN":
                self.handle_save_shutdown()
            time.sleep(0.1)  # Prevent busy waiting

    def handle_halt(self):
        """Handle HALT state - wait for commands or inputs"""
        # In a real implementation, this would wait for GUI events or other triggers
        time.sleep(1)

    def handle_index(self):
        """Handle INDEX state - run indexing process"""
        logger.info("Entering INDEX state")
        self.gui_update_status("Starting indexing process...")
        indexing_success = False
        try:
            if self.current_domains is None:
                self.current_domains = self.gui_request_domains()
            if not self.current_domains:
                logger.warning("No domains provided for indexing")
                self.gui_update_status("No domains provided for indexing")
                self.change_state("HALT")
                return
            self.gui_update_status(f"Indexing domains: {', '.join(self.current_domains)}")
            logger.info(f"Domains to index: {self.current_domains}")

            self.indexing_in_progress = True

            # --- Initialize progress tracking variables ---
            total_urls_to_scrape = 0
            scraped_count = 0
            last_reported_progress = 0.0

            # --- Define the progress callback function ---
            def scraping_progress_callback(current_count, success_flag):
                nonlocal scraped_count, total_urls_to_scrape, last_reported_progress
                scraped_count = current_count
                if total_urls_to_scrape > 0:
                    progress_percent = (scraped_count / total_urls_to_scrape) * 100
                    # Only update GUI if progress has changed significantly (e.g., by 1%) to avoid excessive updates
                    if progress_percent - last_reported_progress >= 1.0 or progress_percent >= 100:
                         self.gui_update_progress(progress_percent)
                         last_reported_progress = progress_percent
                         self.gui_update_status(f"Indexing... {scraped_count}/{total_urls_to_scrape} ({progress_percent:.1f}%)")

            # --- Start scraping and get total URL count ---
            self.gui_update_status("Discovering and queuing URLs...")
            # Pass the callback to start_scraping
            total_urls_to_scrape = start_scraping(self.current_domains, progress_cb=scraping_progress_callback)

            if self.state != "INDEX": # Check if interrupted during scraping setup/start
                logger.info("Indexing interrupted during setup.")
                self.gui_update_status("Indexing interrupted.")
                self.indexing_in_progress = False
                self.current_domains = None
                self.gui_notify_indexing_complete()
                return

            # --- Ensure final progress update after scraping completes ---
            if total_urls_to_scrape > 0:
                 final_progress = (scraped_count / total_urls_to_scrape) * 100
                 self.gui_update_progress(final_progress)
                 self.gui_update_status(f"Scraping completed: {scraped_count}/{total_urls_to_scrape} ({final_progress:.1f}%)")
            else:
                 self.gui_update_status("Scraping phase completed.")

            # --- Reconstruct the FAISS index after scraping ---
            self.gui_update_status("Reconstructing search index...")
            logger.info("Starting FAISS index reconstruction...")
            reconstruct_index()
            logger.info("FAISS index reconstruction completed.")
            self.gui_update_status("Indexing completed successfully")
            logger.info("Indexing process completed successfully")
            indexing_success = True

        except Exception as e:
            error_msg = f"Error during indexing: {e}"
            logger.error(error_msg, exc_info=True)
            self.gui_update_status(f"Indexing failed: {str(e)}")
        finally:
            self.indexing_in_progress = False
            self.current_domains = None
            self.gui_notify_indexing_complete()
            self.change_state("HALT")
            logger.debug("Exited INDEX state, returned to HALT")


    def handle_search(self):
        """Handle SEARCH state - perform semantic search"""
        logger.info("Entering SEARCH state")
        self.gui_update_status("Starting search...")
        try:
            # Get query and AI mode from GUI or prior set values
            if self.current_query is None:
                self.current_query = self.gui_request_query()
            if self.ai_mode is None:
                self.ai_mode = self.gui_request_ai_mode()
            if not self.current_query:
                logger.warning("No query provided for search")
                self.gui_update_status("No query provided")
                self.change_state("HALT")
                return

            self.gui_update_status(f"Searching for: {self.current_query}")
            logger.info(f"Performing semantic search for query: '{self.current_query}'")

            # --- Perform semantic search ---
            results = semantic_search(self.current_query, amount=10)
            logger.debug(f"Raw search results (URLs): {results}")
            final_results = results # Default to URL list

            if self.ai_mode:
                self.gui_update_status("Generating AI report...")
                logger.info("AI mode enabled, generating report...")
                # --- Generate AI report from search results ---
                final_results = generate_report(results)
                logger.debug("AI report generation completed.")

            # --- Display results in GUI ---
            self.gui_show_results(final_results)
            self.gui_update_status("Search completed")

        except Exception as e:
            error_msg = f"Error during search: {e}"
            logger.error(error_msg, exc_info=True) # Log full traceback
            self.gui_update_status(f"Search failed: {str(e)}")
            # Show error in results area as well
            self.gui_show_results(f"Search failed: {str(e)}")
        finally:
            # --- Cleanup and State Transition ---
            # Reset for next search
            self.current_query = None
            self.ai_mode = None
            self.change_state("HALT")
            logger.debug("Exited SEARCH state, returned to HALT")

    def handle_save_shutdown(self):
        """Handle SAVE/SHUTDOWN state - save data and shutdown"""
        logger.info("Entering SAVE/SHUTDOWN state")
        self.gui_update_status("Saving data and shutting down...")
        try:
            # --- Save any ongoing work ---
            # This should signal scraping to stop and save state
            end_scraping()
            logger.info("Scraping processes terminated/saved")
            self.gui_update_status("Shutdown completed")
            logger.info("Shutdown process completed successfully")
        except Exception as e:
            error_msg = f"Error during shutdown: {e}"
            logger.error(error_msg, exc_info=True) # Log full traceback
            self.gui_update_status(f"Shutdown error: {str(e)}")
        finally:
            # --- Stop the main loop ---
            self.running = False
            self.state = "HALT"
            logger.info("Application marked for shutdown.")

    # --- State Management and External Triggers ---
    def change_state(self, new_state: str) -> str:
        """Change the current state of the application"""
        allowed_states = ["HALT", "INDEX", "SEARCH", "SAVE_SHUTDOWN"]
        if new_state in allowed_states:
            logger.info(f"Changing state from {self.state} to {new_state}")
            self.state = new_state
            return "done"
        else:
            logger.warning(f"Invalid state change requested: {new_state}")
            return "invalid input"

    def insert_query(self, query: str):
        """Insert a search query"""
        self.current_query = query
        logger.info(f"Query inserted: {query}")

    def set_ai_mode(self, ai_mode: bool):
        """Set AI mode for search results"""
        self.ai_mode = ai_mode
        logger.info(f"AI mode set to: {ai_mode}")

    def set_domains(self, domains: List[str]):
        """Set domains for indexing"""
        self.current_domains = domains
        logger.info(f"Domains set for indexing: {domains}")

        def start_indexing(self, domains: List[str] = None):
        """Start the indexing process"""
        if domains:
            self.set_domains(domains)
        self.change_state("INDEX")

    def start_search(self, query: str = None, ai_mode: bool = None):
        """Start the search process"""
        # Optionally set query and AI mode if provided
        if query:
            self.insert_query(query)
        if ai_mode is not None: # Boolean, so check for None explicitly
            self.set_ai_mode(ai_mode)
        # Transition to SEARCH state, which triggers handle_search
        self.change_state("SEARCH")

    def request_shutdown(self):
        """Request application shutdown"""
        # Transition to SAVE_SHUTDOWN state, which triggers handle_save_shutdown
        self.change_state("SAVE_SHUTDOWN")

    def get_current_state(self) -> str:
        """Get the current state of the application"""
        return self.state

    def is_indexing(self) -> bool:
        """Check if indexing is currently in progress"""
        return self.indexing_in_progress


# Example usage (if run directly):
# This section is usually handled by the main application script that connects GUI and Main
if __name__ == "__main__":
    # Example of how to use the application *without* a GUI
    # Create main application instance
    main_app = ZeroMain() # No GUI instance passed, uses placeholders

    # Example of how to use the application
    # These would typically be called by the GUI
    # Start indexing
    # main_app.start_indexing(["wikipedia.org", "github.com"])
    # Start search
    # main_app.start_search("machine learning", ai_mode=True)
    # Request shutdown
    # main_app.request_shutdown()

    # Run the main loop (this would be started by the GUI)
    # main_app.loop()

    # --- Example usage *with* a GUI (conceptual) ---
    # from ZeroGUI import ZeroGUI
    # gui_app = ZeroGUI(main_app) # Pass main_app instance to GUI
    # main_app.gui = gui_app # Assign GUI instance to main_app (if needed for direct calls)
    # gui_app.run() # Start GUI, which would manage the main_app loop internally or via callbacks
