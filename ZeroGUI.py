#ZeroGUI.py

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import logging
import threading
import time

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ZeroGUI:
    def __init__(self, main_controller):
        """
        Initializes the GUI.
        :param main_controller: An instance of ZeroMain to interact with.
        """
        self.main_controller = main_controller
        self.root = tk.Tk()
        self.root.title("ZeroWeb - Semantic Search Engine")
        self.root.geometry("800x600")

        # Create tabs
        self.notebook = ttk.Notebook(self.root)
        self.index_tab = ttk.Frame(self.notebook)
        self.search_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.index_tab, text="Index")
        self.notebook.add(self.search_tab, text="Search")
        self.notebook.pack(expand=True, fill='both')

        # Communication placeholders (to be linked to main_controller)
        self.main_controller.gui_update_status = self.update_status
        self.main_controller.gui_show_results = self.show_results
        self.main_controller.gui_update_progress = self.update_progress
        self.main_controller.gui_request_domains = self.get_domains_from_gui
        self.main_controller.gui_request_query = self.get_query_from_gui
        self.main_controller.gui_request_ai_mode = self.get_ai_mode_from_gui

        # Build UI elements
        self.build_index_tab()
        self.build_search_tab()

        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        self.status_bar = tk.Label(self.root, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # Handle closing event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Threading control for periodic updates
        self.update_thread = None
        self.stop_update_thread = threading.Event()
        self.start_periodic_updates()

    def start_periodic_updates(self):
        """Start a background thread for periodic UI updates."""
        self.update_thread = threading.Thread(target=self.periodic_update_loop, daemon=True)
        self.update_thread.start()

    def periodic_update_loop(self):
        """Periodically check for state changes or progress updates."""
        while not self.stop_update_thread.is_set():
            # Example: Check if indexing is done
            if self.main_controller.get_current_state() != "INDEX" and self.start_index_button['state'] == 'disabled':
                self.root.after(0, self.on_indexing_finished)
            time.sleep(0.5) # Check every 500ms

    def build_index_tab(self):
        """Builds the UI elements for the Index tab."""
        # --- Domain List ---
        tk.Label(self.index_tab, text="Domains to Index (one per line):").pack(anchor='w', padx=10, pady=(10, 0))
        self.domain_text = tk.Text(self.index_tab, height=6, width=70)
        self.domain_text.pack(padx=10, pady=5)

        # Populate with default domains or from main controller if available
        default_domains = "wikipedia.org\narxiv.org\ngithub.com\nreddit.com"
        self.domain_text.insert(tk.END, default_domains)

        # --- Max Threads ---
        tk.Label(self.index_tab, text="Max Scraping Threads:").pack(anchor='w', padx=10, pady=(10, 0))
        self.max_threads_var = tk.StringVar(value="4") # Default value
        self.max_threads_entry = tk.Entry(self.index_tab, textvariable=self.max_threads_var, width=10)
        self.max_threads_entry.pack(padx=10, anchor='w')

        # --- Progress Bar ---
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self.index_tab, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(padx=10, pady=10, fill='x')

        # --- Buttons ---
        button_frame = tk.Frame(self.index_tab)
        button_frame.pack(pady=10)
        self.start_index_button = tk.Button(button_frame, text="Start Indexing", command=self.start_indexing)
        self.start_index_button.pack(side=tk.LEFT, padx=5)
        self.stop_index_button = tk.Button(button_frame, text="Stop Indexing", command=self.stop_indexing, state='disabled')
        self.stop_index_button.pack(side=tk.LEFT, padx=5)

        # --- Privacy Reminder ---
        self.privacy_text = tk.Text(self.index_tab, height=4, width=70, wrap=tk.WORD, bg=self.root.cget('bg'), relief='flat', borderwidth=0)
        self.privacy_text.pack(padx=10, pady=10, fill='x')
        privacy_msg = ("REMINDER: This application does not provide any internet identity concealment. "
                       "Your privacy is your responsibility!")
        self.privacy_text.insert(tk.END, privacy_msg)
        self.privacy_text.config(state='disabled') # Make it read-only

    def build_search_tab(self):
        """Builds the UI elements for the Search tab."""
        # --- Query Input ---
        tk.Label(self.search_tab, text="Enter your search query:").pack(anchor='w', padx=10, pady=(10, 0))
        self.query_entry = tk.Entry(self.search_tab, width=70)
        self.query_entry.pack(padx=10, pady=5, fill='x')

        # --- AI Mode Switch ---
        self.ai_mode_var = tk.BooleanVar()
        self.ai_mode_check = tk.Checkbutton(self.search_tab, text="AI-Powered Report (uses API)", variable=self.ai_mode_var)
        self.ai_mode_check.pack(anchor='w', padx=10, pady=5)

        # --- Search Button ---
        self.search_button = tk.Button(self.search_tab, text="Search", command=self.perform_search)
        self.search_button.pack(pady=10)

        # --- Results Display ---
        tk.Label(self.search_tab, text="Results:").pack(anchor='w', padx=10, pady=(10, 0))
        self.results_text = scrolledtext.ScrolledText(self.search_tab, width=70, height=20, wrap=tk.WORD)
        self.results_text.pack(padx=10, pady=5, fill='both', expand=True)

    # --- GUI Interaction Methods (Called by GUI elements) ---
    def start_indexing(self):
        """Triggered by the Start Indexing button."""
        domains_raw = self.domain_text.get("1.0", tk.END).strip()
        if not domains_raw:
            messagebox.showwarning("No Domains", "Please enter at least one domain to index.")
            return
        domains = [d.strip() for d in domains_raw.split('\n') if d.strip()]
        
        # Note: Max threads from GUI is not directly used here as it's set in config.py
        # according to the architecture. This GUI element could update a config variable.
        # For now, we just log it.
        try:
            max_threads = int(self.max_threads_var.get())
            logger.info(f"GUI requested max threads: {max_threads} (not directly used)")
        except ValueError:
            logger.warning("Invalid max threads value in GUI, using default.")
            max_threads = 4
            
        self.start_index_button.config(state='disabled')
        self.stop_index_button.config(state='normal')
        self.progress_var.set(0) # Reset progress
        logger.info("GUI: Starting indexing process.")
        
        # Run indexing in a separate thread to prevent GUI freeze
        threading.Thread(target=self._run_indexing, args=(domains,), daemon=True).start()

    def _run_indexing(self, domains):
        """Internal method to run indexing in a background thread."""
        try:
            self.main_controller.start_indexing(domains)
        except Exception as e:
            logger.error(f"Error during indexing: {e}")
            self.root.after(0, lambda: messagebox.showerror("Indexing Error", f"An error occurred: {e}"))
        finally:
            self.root.after(0, self.on_indexing_finished)

    def on_indexing_finished(self):
        """Called when indexing is finished (success or failure)."""
        self.start_index_button.config(state='normal')
        self.stop_index_button.config(state='disabled')
        self.progress_var.set(100) # Set progress to 100%

    def stop_indexing(self):
        """Triggered by the Stop Indexing button."""
        logger.info("GUI: Requesting indexing stop.")
        # A more graceful stop would require modifications to ZeroMain to have a specific stop signal
        # For now, we'll just disable the button and inform the user
        self.stop_index_button.config(state='disabled')
        self.main_controller.request_shutdown() # This might be too harsh; consider adding a dedicated stop method to ZeroMain

    def perform_search(self):
        """Triggered by the Search button."""
        query = self.query_entry.get().strip()
        if not query:
            messagebox.showwarning("Empty Query", "Please enter a search query.")
            return
        ai_mode = self.ai_mode_var.get()
        self.search_button.config(state='disabled')
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, "Searching...\n")
        logger.info(f"GUI: Performing search for '{query}' with AI mode: {ai_mode}")
        
        # Run search in a separate thread to prevent GUI freeze
        threading.Thread(target=self._run_search, args=(query, ai_mode), daemon=True).start()

    def _run_search(self, query, ai_mode):
        """Internal method to run search in a background thread."""
        try:
            self.main_controller.start_search(query, ai_mode)
        except Exception as e:
            logger.error(f"Error during search: {e}")
            self.root.after(0, lambda: self.show_results(f"Search failed: {str(e)}"))

    # --- Communication Methods (Called by ZeroMain) ---
    def update_status(self, status: str):
        """Called by ZeroMain to update the status bar."""
        logger.debug(f"GUI Status Update: {status}")
        self.status_var.set(status)
        # Do not call update_idletasks here as it can cause issues when called from another thread
        # Instead, use root.after to schedule the update on the main thread
        try:
            self.root.after(0, lambda: self.status_var.set(status))
        except RuntimeError:
            # This can happen if the GUI is being destroyed
            pass

    def show_results(self, results):
        """Called by ZeroMain to display search results."""
        logger.debug(f"GUI Results Display: Type {type(results)}")
        # Schedule the UI update on the main thread
        self.root.after(0, self._update_results_text, results)
        self.root.after(0, lambda: self.search_button.config(state='normal'))

    def _update_results_text(self, results):
        """Internal method to update results text (runs on main thread)."""
        self.results_text.delete(1.0, tk.END)
        if isinstance(results, list):
            # Display list of URLs
            if not results:
                self.results_text.insert(tk.END, "No results found.")
            else:
                for url in results:
                    self.results_text.insert(tk.END, url + "\n")
        elif isinstance(results, str):
            # Display AI report or error message
            self.results_text.insert(tk.END, results)
        else:
            self.results_text.insert(tk.END, f"Unexpected result type: {type(results)}")

    def update_progress(self, progress: float):
        """Called by ZeroMain to update the indexing progress bar."""
        logger.debug(f"GUI Progress Update: {progress}%")
        # Schedule the UI update on the main thread
        try:
            self.root.after(0, lambda p=progress: self.progress_var.set(p))
        except RuntimeError:
            # This can happen if the GUI is being destroyed
            pass

    def get_domains_from_gui(self) -> list:
        """Called by ZeroMain to get the list of domains from the GUI."""
        domains_raw = self.domain_text.get("1.0", tk.END).strip()
        return [d.strip() for d in domains_raw.split('\n') if d.strip()]

    def get_query_from_gui(self) -> str:
        """Called by ZeroMain to get the current search query from the GUI."""
        return self.query_entry.get().strip()

    def get_ai_mode_from_gui(self) -> bool:
        """Called by ZeroMain to get the current AI mode setting from the GUI."""
        return self.ai_mode_var.get()

    def on_closing(self):
        """Handles the window closing event."""
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            logger.info("GUI: Quit requested.")
            self.stop_update_thread.set() # Signal the update thread to stop
            self.main_controller.request_shutdown() # Request graceful shutdown
            self.root.destroy()

    def run(self):
        """Starts the GUI main loop."""
        logger.info("Starting GUI main loop.")
        try:
            self.root.mainloop()
        except Exception as e:
            logger.error(f"Error in GUI main loop: {e}")
        finally:
            self.stop_update_thread.set() # Ensure the update thread is stopped
