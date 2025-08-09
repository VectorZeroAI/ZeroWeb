# ZeroMain.py
import time
import logging
from typing import List, Optional, Any

# Import the modules we'll be working with
from ZeroSkan import start_scraping, end_scraping
from ZeroIndex import reconstruct_index
from ZeroSearch import search as semantic_search, report as generate_report

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ZeroMain:
    def __init__(self):
        self.state = "HALT"
        self.running = True
        self.current_query = None
        self.current_domains = None
        self.ai_mode = False
        self.search_results = None
        self.indexing_in_progress = False
        
        # Placeholders for GUI communication functions
        self.gui_update_status = self._placeholder_gui_update_status
        self.gui_show_results = self._placeholder_gui_show_results
        self.gui_update_progress = self._placeholder_gui_update_progress
        self.gui_request_domains = self._placeholder_gui_request_domains
        self.gui_request_query = self._placeholder_gui_request_query
        self.gui_request_ai_mode = self._placeholder_gui_request_ai_mode
        
        logger.info("ZeroMain initialized")

    def _placeholder_gui_update_status(self, status: str):
        """Placeholder for GUI status update function"""
        logger.info(f"GUI Status Update: {status}")

    def _placeholder_gui_show_results(self, results: Any):
        """Placeholder for GUI results display function"""
        logger.info(f"GUI Results Display: {results}")

    def _placeholder_gui_update_progress(self, progress: float):
        """Placeholder for GUI progress update function"""
        logger.info(f"GUI Progress Update: {progress}%")

    def _placeholder_gui_request_domains(self) -> List[str]:
        """Placeholder for GUI domains request function"""
        logger.info("GUI Domains Request")
        return ["wikipedia.org", "github.com"]

    def _placeholder_gui_request_query(self) -> str:
        """Placeholder for GUI query request function"""
        logger.info("GUI Query Request")
        return "machine learning"

    def _placeholder_gui_request_ai_mode(self) -> bool:
        """Placeholder for GUI AI mode request function"""
        logger.info("GUI AI Mode Request")
        return False

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
        
        try:
            # Get domains from GUI or use defaults
            if self.current_domains is None:
                self.current_domains = self.gui_request_domains()
            
            if not self.current_domains:
                logger.warning("No domains provided for indexing")
                self.gui_update_status("No domains provided for indexing")
                self.change_state("HALT")
                return
            
            self.gui_update_status(f"Indexing domains: {self.current_domains}")
            
            # Start the indexing process
            self.indexing_in_progress = True
            start_scraping(self.current_domains)
            
            # Reconstruct the FAISS index after scraping
            self.gui_update_status("Reconstructing search index...")
            reconstruct_index()
            
            self.gui_update_status("Indexing completed successfully")
            logger.info("Indexing process completed")
            
        except Exception as e:
            logger.error(f"Error during indexing: {e}")
            self.gui_update_status(f"Indexing failed: {str(e)}")
        finally:
            self.indexing_in_progress = False
            self.current_domains = None
            self.change_state("HALT")

    def handle_search(self):
        """Handle SEARCH state - perform semantic search"""
        logger.info("Entering SEARCH state")
        self.gui_update_status("Starting search...")
        
        try:
            # Get query and AI mode from GUI
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
            
            # Perform semantic search
            results = semantic_search(self.current_query, amount=10)
            
            if self.ai_mode:
                self.gui_update_status("Generating AI report...")
                # Generate AI report from search results
                final_results = generate_report(results)
            else:
                final_results = results
            
            # Display results in GUI
            self.gui_show_results(final_results)
            self.gui_update_status("Search completed")
            
        except Exception as e:
            logger.error(f"Error during search: {e}")
            self.gui_update_status(f"Search failed: {str(e)}")
            self.gui_show_results(f"Search failed: {str(e)}")
        finally:
            # Reset for next search
            self.current_query = None
            self.ai_mode = None
            self.change_state("HALT")

    def handle_save_shutdown(self):
        """Handle SAVE/SHUTDOWN state - save data and shutdown"""
        logger.info("Entering SAVE/SHUTDOWN state")
        self.gui_update_status("Saving data and shutting down...")
        
        try:
            # Save any ongoing work
            end_scraping()
            logger.info("Scraping processes terminated")
            
            self.gui_update_status("Shutdown completed")
            logger.info("Shutdown process completed")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
            self.gui_update_status(f"Shutdown error: {str(e)}")
        finally:
            self.running = False
            self.state = "HALT"

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
        if query:
            self.insert_query(query)
        if ai_mode is not None:
            self.set_ai_mode(ai_mode)
        self.change_state("SEARCH")

    def request_shutdown(self):
        """Request application shutdown"""
        self.change_state("SAVE_SHUTDOWN")

    def get_current_state(self) -> str:
        """Get the current state of the application"""
        return self.state

    def is_indexing(self) -> bool:
        """Check if indexing is currently in progress"""
        return self.indexing_in_progress


# Example usage:
if __name__ == "__main__":
    # Create main application instance
    main_app = ZeroMain()
    
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