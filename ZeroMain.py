# ZeroMain.py

import logging
import signal
import sys
import time
from enum import Enum
from typing import List, Optional

from config import DEFAULT_DOMAINS
from ZeroSkan import start_scraping, end_scraping, initDB
from ZeroIndex import reconstruct_index, save_index, load_index
from ZeroSearch import search, report, initialize_search

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class State(Enum):
    HALT = "halt"
    SEARCH = "search"
    INDEX = "index"
    SAVE_SHUTDOWN = "save_shutdown"

class ZeroWeb:
    def __init__(self):
        self.state = State.HALT
        self.scraping_processes = []
        self.index_loaded = False
        logger.info("ZeroWeb initialized in HALT state")

    def transition_to(self, new_state: State):
        """Transition to a new state with proper cleanup"""
        logger.info(f"Transitioning from {self.state.value} to {new_state.value}")
        self.state = new_state

    def handle_halt_state(self):
        """Handle HALT state - wait for commands"""
        logger.info("Entering HALT state - waiting for commands")
        # In a real implementation, this would wait for GUI events or CLI commands
        time.sleep(1)

    def start_indexing(self, domains: List[str] = None):
        """Start the indexing process"""
        if domains is None:
            domains = DEFAULT_DOMAINS
        
        logger.info(f"Starting indexing for domains: {domains}")
        try:
            # This would typically be run in a separate thread/process for GUI responsiveness
            start_scraping(domains)
            logger.info("Indexing completed")
        except Exception as e:
            logger.error(f"Error during indexing: {e}")

    def handle_index_state(self, domains: List[str] = None):
        """Handle INDEX state"""
        logger.info("Entering INDEX state")
        self.start_indexing(domains)
        self.transition_to(State.HALT)

    def load_search_index(self):
        """Load the search index if not already loaded"""
        if not self.index_loaded:
            logger.info("Loading search index...")
            try:
                if initialize_search():
                    self.index_loaded = True
                    logger.info("Search index loaded successfully")
                else:
                    logger.error("Failed to load search index")
            except Exception as e:
                logger.error(f"Error loading search index: {e}")

    def perform_search(self, query: str, amount: int = 10, ai_mode: bool = False):
        """Perform a search and optionally generate AI report"""
        if not self.index_loaded:
            self.load_search_index()
            
        if not self.index_loaded:
            logger.error("Cannot perform search - index not loaded")
            return None

        try:
            logger.info(f"Performing search for query: '{query}'")
            urls = search(query, amount)
            
            if ai_mode:
                logger.info("Generating AI report...")
                result = report(urls)
                return result
            else:
                return urls
        except Exception as e:
            logger.error(f"Error during search: {e}")
            return None

    def handle_search_state(self, query: str, amount: int = 10, ai_mode: bool = False):
        """Handle SEARCH state"""
        logger.info("Entering SEARCH state")
        result = self.perform_search(query, amount, ai_mode)
        self.transition_to(State.HALT)
        return result

    def handle_save_shutdown_state(self):
        """Handle SAVE/SHUTDOWN state"""
        logger.info("Entering SAVE/SHUTDOWN state")
        try:
            logger.info("Saving index...")
            save_index()
            logger.info("Stopping scraping processes...")
            end_scraping()
            logger.info("Shutdown complete")
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
        finally:
            self.transition_to(State.HALT)

    def run_command(self, command: str, **kwargs):
        """Process a command and transition states accordingly"""
        if command == "index":
            self.transition_to(State.INDEX)
            domains = kwargs.get('domains', DEFAULT_DOMAINS)
            self.handle_index_state(domains)
        elif command == "search":
            self.transition_to(State.SEARCH)
            query = kwargs.get('query')
            amount = kwargs.get('amount', 10)
            ai_mode = kwargs.get('ai_mode', False)
            result = self.handle_search_state(query, amount, ai_mode)
            return result
        elif command == "save":
            self.transition_to(State.SAVE_SHUTDOWN)
            self.handle_save_shutdown_state()
        elif command == "load_index":
            self.load_search_index()
        else:
            logger.warning(f"Unknown command: {command}")
            self.transition_to(State.HALT)

    def run(self):
        """Main run loop"""
        logger.info("ZeroWeb main loop started")
        try:
            while True:
                if self.state == State.HALT:
                    self.handle_halt_state()
                elif self.state == State.INDEX:
                    # In practice, this would be triggered by a command
                    pass
                elif self.state == State.SEARCH:
                    # In practice, this would be triggered by a command
                    pass
                elif self.state == State.SAVE_SHUTDOWN:
                    # In practice, this would be triggered by a command
                    pass
                time.sleep(0.1)  # Prevent busy waiting
        except KeyboardInterrupt:
            logger.info("Received interrupt signal")
            self.run_command("save")
        except Exception as e:
            logger.error(f"Unexpected error in main loop: {e}")
            self.run_command("save")

def signal_handler(sig, frame):
    """Handle shutdown signals"""
    logger.info("Received shutdown signal")
    sys.exit(0)

def main():
    """Main entry point"""
    # Set up signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Create and run the main application
    app = ZeroWeb()
    
    # Example usage:
    # app.run_command("index", domains=["wikipedia.org"])
    # result = app.run_command("search", query="machine learning", ai_mode=True)
    # app.run_command("save")
    
    # For now, just run the main loop
    app.run()

if __name__ == "__main__":
    main()