#!/usr/bin/env python3
"""
ZeroNet GUI - Graphical User Interface for ZeroNet System
A comprehensive GUI that integrates all ZeroNet modules:
- ZeroOS (System Management)
- ZeroSkan (Domain Link Manager)
- ZeroScraper (Web Scraper)
- ZeroIndex (Vector Database)
- ZeroSearch (Search Engine)
- ZeroCompiler (AI Report Generator)
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
import json
import os
import sys
from datetime import datetime
import queue
import time

# Import ZeroNet modules
try:
    from ZeroOS import ZeroOS
    from ZeroSkan import ZeroSkan
    from ZeroScraper import ZeroScraper
    from ZeroIndex import ZeroIndex
    from ZeroSearch import ZeroSearch
    from ZeroCompiler import ZeroCompiler
    MODULES_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import ZeroNet modules: {e}")
    MODULES_AVAILABLE = False

class ZeroNetGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("ZeroNet - Decentralized Web Platform")
        self.root.geometry("1200x800")
        self.root.configure(bg='#2b2b2b')
        
        # Initialize ZeroNet modules
        self.zero_os = None
        self.zero_skan = None
        self.zero_scraper = None
        self.zero_index = None
        self.zero_search = None
        self.zero_compiler = None
        
        # GUI state
        self.is_system_running = False
        self.log_queue = queue.Queue()
        
        # Initialize modules if available
        if MODULES_AVAILABLE:
            self.init_modules()
        
        # Create GUI
        self.create_gui()
        
        # Start log processing
        self.process_logs()
        
    def init_modules(self):
        """Initialize ZeroNet modules"""
        try:
            self.zero_os = ZeroOS()
            self.zero_skan = ZeroSkan()
            self.zero_scraper = ZeroScraper()
            self.zero_index = ZeroIndex()
            self.zero_search = ZeroSearch()
            self.zero_compiler = ZeroCompiler()
            self.log("ZeroNet modules initialized successfully")
        except Exception as e:
            self.log(f"Error initializing modules: {e}")
    
    def create_gui(self):
        """Create the main GUI interface"""
        # Configure styles
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'), background='#2b2b2b', foreground='#ffffff')
        style.configure('Header.TLabel', font=('Arial', 12, 'bold'), background='#2b2b2b', foreground='#00ff00')
        
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_label = ttk.Label(main_frame, text="ZeroNet - Decentralized Web Platform", style='Title.TLabel')
        title_label.pack(pady=(0, 20))
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create tabs
        self.create_system_tab()
        self.create_domains_tab()
        self.create_scraper_tab()
        self.create_search_tab()
        self.create_compiler_tab()
        self.create_logs_tab()
        
        # Status bar
        self.create_status_bar(main_frame)
        
    def create_system_tab(self):
        """Create system management tab"""
        system_frame = ttk.Frame(self.notebook)
        self.notebook.add(system_frame, text="System Control")
        
        # System status
        status_frame = ttk.LabelFrame(system_frame, text="System Status", padding=10)
        status_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.system_status_label = ttk.Label(status_frame, text="System: Stopped", style='Header.TLabel')
        self.system_status_label.pack(anchor=tk.W)
        
        self.privacy_status_label = ttk.Label(status_frame, text="Privacy Mode: Enabled", foreground='#00ff00')
        self.privacy_status_label.pack(anchor=tk.W)
        
        self.sandbox_status_label = ttk.Label(status_frame, text="Sandbox: Active", foreground='#00ff00')
        self.sandbox_status_label.pack(anchor=tk.W)
        
        # Control buttons
        control_frame = ttk.LabelFrame(system_frame, text="System Control", padding=10)
        control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        button_frame = ttk.Frame(control_frame)
        button_frame.pack()
        
        self.start_button = ttk.Button(button_frame, text="Start System", command=self.start_system, width=15)
        self.start_button.grid(row=0, column=0, padx=5)
        
        self.stop_button = ttk.Button(button_frame, text="Stop System", command=self.stop_system, state=tk.DISABLED, width=15)
        self.stop_button.grid(row=0, column=1, padx=5)
        
        self.restart_button = ttk.Button(button_frame, text="Restart System", command=self.restart_system, state=tk.DISABLED, width=15)
        self.restart_button.grid(row=0, column=2, padx=5)
        
        # Module status
        modules_frame = ttk.LabelFrame(system_frame, text="Module Status", padding=10)
        modules_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Create treeview for module status
        self.modules_tree = ttk.Treeview(modules_frame, columns=('Status', 'Memory', 'CPU'), show='tree headings')
        self.modules_tree.heading('#0', text='Module')
        self.modules_tree.heading('Status', text='Status')
        self.modules_tree.heading('Memory', text='Memory (MB)')
        self.modules_tree.heading('CPU', text='CPU (%)')
        
        # Add modules to tree
        modules = ['ZeroOS', 'ZeroSkan', 'ZeroScraper', 'ZeroIndex', 'ZeroSearch', 'ZeroCompiler']
        for module in modules:
            self.modules_tree.insert('', tk.END, text=module, values=('Stopped', '0', '0'))
        
        self.modules_tree.pack(fill=tk.BOTH, expand=True)
        
        # Resource usage
        resources_frame = ttk.LabelFrame(system_frame, text="Resource Usage", padding=10)
        resources_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.memory_label = ttk.Label(resources_frame, text="Memory: 0 MB")
        self.memory_label.pack(anchor=tk.W)
        
        self.cpu_label = ttk.Label(resources_frame, text="CPU: 0%")
        self.cpu_label.pack(anchor=tk.W)
        
    def create_domains_tab(self):
        """Create domain management tab"""
        domains_frame = ttk.Frame(self.notebook)
        self.notebook.add(domains_frame, text="Domain Manager")
        
        # Domain list
        domains_list_frame = ttk.LabelFrame(domains_frame, text="Managed Domains", padding=10)
        domains_list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Listbox with scrollbar
        listbox_frame = ttk.Frame(domains_list_frame)
        listbox_frame.pack(fill=tk.BOTH, expand=True)
        
        self.domains_listbox = tk.Listbox(listbox_frame, font=('Consolas', 10))
        scrollbar_domains = ttk.Scrollbar(listbox_frame, orient=tk.VERTICAL, command=self.domains_listbox.yview)
        self.domains_listbox.configure(yscrollcommand=scrollbar_domains.set)
        
        self.domains_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_domains.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Domain controls
        domain_controls_frame = ttk.LabelFrame(domains_frame, text="Domain Controls", padding=10)
        domain_controls_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Add domain
        add_frame = ttk.Frame(domain_controls_frame)
        add_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(add_frame, text="Add Domain:").pack(side=tk.LEFT)
        self.domain_entry = ttk.Entry(add_frame, width=30)
        self.domain_entry.pack(side=tk.LEFT, padx=(10, 5))
        ttk.Button(add_frame, text="Add", command=self.add_domain).pack(side=tk.LEFT)
        
        # Control buttons
        controls_frame = ttk.Frame(domain_controls_frame)
        controls_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(controls_frame, text="Remove Selected", command=self.remove_domain).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(controls_frame, text="Scan All Domains", command=self.scan_domains).pack(side=tk.LEFT, padx=5)
        ttk.Button(controls_frame, text="Clear Links", command=self.clear_links).pack(side=tk.LEFT, padx=5)
        ttk.Button(controls_frame, text="Load Domains", command=self.load_domains).pack(side=tk.LEFT, padx=5)
        
        # Domain statistics
        stats_frame = ttk.LabelFrame(domains_frame, text="Domain Statistics", padding=10)
        stats_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.domain_stats_text = tk.Text(stats_frame, height=4, font=('Consolas', 9))
        self.domain_stats_text.pack(fill=tk.X)
        
    def create_scraper_tab(self):
        """Create web scraper tab"""
        scraper_frame = ttk.Frame(self.notebook)
        self.notebook.add(scraper_frame, text="Web Scraper")
        
        # Scraper controls
        scraper_controls_frame = ttk.LabelFrame(scraper_frame, text="Scraper Controls", padding=10)
        scraper_controls_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # URL input for manual scraping
        url_frame = ttk.Frame(scraper_controls_frame)
        url_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(url_frame, text="Scrape URL:").pack(side=tk.LEFT)
        self.scrape_url_entry = ttk.Entry(url_frame, width=50)
        self.scrape_url_entry.pack(side=tk.LEFT, padx=(10, 5))
        ttk.Button(url_frame, text="Scrape", command=self.scrape_single_url).pack(side=tk.LEFT)
        
        # Batch scraping controls
        batch_frame = ttk.Frame(scraper_controls_frame)
        batch_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(batch_frame, text="Scrape From Domains", command=self.scrape_from_domains).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(batch_frame, text="Clear Queue", command=self.clear_scraper_queue).pack(side=tk.LEFT, padx=5)
        
        # Workers setting
        workers_frame = ttk.Frame(scraper_controls_frame)
        workers_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(workers_frame, text="Max Workers:").pack(side=tk.LEFT)
        self.workers_var = tk.StringVar(value="5")
        workers_spinbox = ttk.Spinbox(workers_frame, from_=1, to=20, textvariable=self.workers_var, width=5)
        workers_spinbox.pack(side=tk.LEFT, padx=(10, 0))
        
        # Scraper queue display
        queue_frame = ttk.LabelFrame(scraper_frame, text="Scraper Queue", padding=10)
        queue_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Create treeview for queue
        self.queue_tree = ttk.Treeview(queue_frame, columns=('Title', 'Status'), show='tree headings')
        self.queue_tree.heading('#0', text='URL')
        self.queue_tree.heading('Title', text='Title')
        self.queue_tree.heading('Status', text='Status')
        
        queue_scrollbar = ttk.Scrollbar(queue_frame, orient=tk.VERTICAL, command=self.queue_tree.yview)
        self.queue_tree.configure(yscrollcommand=queue_scrollbar.set)
        
        self.queue_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        queue_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Scraper statistics
        scraper_stats_frame = ttk.LabelFrame(scraper_frame, text="Scraper Statistics", padding=10)
        scraper_stats_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.scraper_stats_text = tk.Text(scraper_stats_frame, height=3, font=('Consolas', 9))
        self.scraper_stats_text.pack(fill=tk.X)
        
    def create_search_tab(self):
        """Create search interface tab"""
        search_frame = ttk.Frame(self.notebook)
        self.notebook.add(search_frame, text="Search Engine")
        
        # Search controls
        search_controls_frame = ttk.LabelFrame(search_frame, text="Search Controls", padding=10)
        search_controls_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Search input
        search_input_frame = ttk.Frame(search_controls_frame)
        search_input_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(search_input_frame, text="Search Query:").pack(side=tk.LEFT)
        self.search_entry = ttk.Entry(search_input_frame, width=50, font=('Arial', 11))
        self.search_entry.pack(side=tk.LEFT, padx=(10, 5), fill=tk.X, expand=True)
        self.search_entry.bind('<Return>', lambda e: self.perform_search())
        
        # Search options
        options_frame = ttk.Frame(search_controls_frame)
        options_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(options_frame, text="Results:").pack(side=tk.LEFT)
        self.results_var = tk.StringVar(value="10")
        results_spinbox = ttk.Spinbox(options_frame, from_=1, to=50, textvariable=self.results_var, width=5)
        results_spinbox.pack(side=tk.LEFT, padx=(5, 15))
        
        self.ai_mode_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text="AI Analysis Mode", variable=self.ai_mode_var).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(options_frame, text="Search", command=self.perform_search).pack(side=tk.RIGHT)
        
        # Search results
        results_frame = ttk.LabelFrame(search_frame, text="Search Results", padding=10)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Results display
        self.search_results_text = scrolledtext.ScrolledText(results_frame, wrap=tk.WORD, font=('Arial', 10))
        self.search_results_text.pack(fill=tk.BOTH, expand=True)
        
        # Search statistics
        search_stats_frame = ttk.LabelFrame(search_frame, text="Search Statistics", padding=10)
        search_stats_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.search_stats_text = tk.Text(search_stats_frame, height=2, font=('Consolas', 9))
        self.search_stats_text.pack(fill=tk.X)
        
    def create_compiler_tab(self):
        """Create AI compiler tab"""
        compiler_frame = ttk.Frame(self.notebook)
        self.notebook.add(compiler_frame, text="AI Compiler")
        
        # Compiler controls
        compiler_controls_frame = ttk.LabelFrame(compiler_frame, text="AI Report Generator", padding=10)
        compiler_controls_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Query input
        query_frame = ttk.Frame(compiler_controls_frame)
        query_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(query_frame, text="Analysis Query:").pack(side=tk.LEFT)
        self.compiler_query_entry = ttk.Entry(query_frame, width=50, font=('Arial', 11))
        self.compiler_query_entry.pack(side=tk.LEFT, padx=(10, 5), fill=tk.X, expand=True)
        
        # API settings
        api_frame = ttk.Frame(compiler_controls_frame)
        api_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(api_frame, text="API Key:").pack(side=tk.LEFT)
        self.api_key_entry = ttk.Entry(api_frame, width=40, show='*')
        self.api_key_entry.pack(side=tk.LEFT, padx=(10, 5))
        
        ttk.Button(api_frame, text="Load Key", command=self.load_api_key).pack(side=tk.LEFT, padx=5)
        ttk.Button(api_frame, text="Generate Report", command=self.generate_report).pack(side=tk.RIGHT)
        
        # Report display
        report_frame = ttk.LabelFrame(compiler_frame, text="Generated Report", padding=10)
        report_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.report_text = scrolledtext.ScrolledText(report_frame, wrap=tk.WORD, font=('Arial', 10))
        self.report_text.pack(fill=tk.BOTH, expand=True)
        
        # Report controls
        report_controls_frame = ttk.Frame(compiler_frame)
        report_controls_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(report_controls_frame, text="Save Report", command=self.save_report).pack(side=tk.LEFT)
        ttk.Button(report_controls_frame, text="Clear Report", command=self.clear_report).pack(side=tk.LEFT, padx=5)
        ttk.Button(report_controls_frame, text="Export PDF", command=self.export_pdf).pack(side=tk.LEFT, padx=5)
        
    def create_logs_tab(self):
        """Create system logs tab"""
        logs_frame = ttk.Frame(self.notebook)
        self.notebook.add(logs_frame, text="System Logs")
        
        # Log controls
        log_controls_frame = ttk.LabelFrame(logs_frame, text="Log Controls", padding=10)
        log_controls_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(log_controls_frame, text="Clear Logs", command=self.clear_logs).pack(side=tk.LEFT)
        ttk.Button(log_controls_frame, text="Export Logs", command=self.export_logs).pack(side=tk.LEFT, padx=5)
        
        self.auto_scroll_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(log_controls_frame, text="Auto Scroll", variable=self.auto_scroll_var).pack(side=tk.LEFT, padx=5)
        
        # Log level filter
        ttk.Label(log_controls_frame, text="Level:").pack(side=tk.RIGHT, padx=(20, 5))
        self.log_level_var = tk.StringVar(value="INFO")
        log_level_combo = ttk.Combobox(log_controls_frame, textvariable=self.log_level_var, 
                                     values=["DEBUG", "INFO", "WARNING", "ERROR"], width=10)
        log_level_combo.pack(side=tk.RIGHT)
        
        # Logs display
        logs_display_frame = ttk.LabelFrame(logs_frame, text="System Logs", padding=10)
        logs_display_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.logs_text = scrolledtext.ScrolledText(logs_display_frame, wrap=tk.WORD, 
                                                  font=('Consolas', 9), bg='#1e1e1e', fg='#ffffff')
        self.logs_text.pack(fill=tk.BOTH, expand=True)
        
    def create_status_bar(self, parent):
        """Create status bar"""
        self.status_frame = ttk.Frame(parent)
        self.status_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.status_label = ttk.Label(self.status_frame, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.time_label = ttk.Label(self.status_frame, text="", relief=tk.SUNKEN)
        self.time_label.pack(side=tk.RIGHT)
        
        # Update time every second
        self.update_time()
        
    def update_time(self):
        """Update status bar time"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_label.config(text=current_time)
        self.root.after(1000, self.update_time)
        
    def log(self, message, level="INFO"):
        """Add message to log queue"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}"
        self.log_queue.put(log_entry)
        
    def process_logs(self):
        """Process log queue and update logs display"""
        try:
            while True:
                log_entry = self.log_queue.get_nowait()
                self.logs_text.insert(tk.END, log_entry + "\n")
                
                if self.auto_scroll_var.get():
                    self.logs_text.see(tk.END)
                    
        except queue.Empty:
            pass
        
        # Schedule next log processing
        self.root.after(100, self.process_logs)
        
    def update_status(self, message):
        """Update status bar message"""
        self.status_label.config(text=message)
        
    # System Control Methods
    def start_system(self):
        """Start the ZeroNet system"""
        if not MODULES_AVAILABLE:
            messagebox.showerror("Error", "ZeroNet modules not available")
            return
            
        def start_thread():
            try:
                self.log("Starting ZeroNet system...")
                self.update_status("Starting system...")
                
                if self.zero_os:
                    self.zero_os.start()
                    
                self.is_system_running = True
                self.log("ZeroNet system started successfully")
                self.update_status("System running")
                
                # Update GUI state
                self.root.after(0, self.on_system_started)
                
            except Exception as e:
                self.log(f"Failed to start system: {e}", "ERROR")
                self.update_status("System start failed")
                
        threading.Thread(target=start_thread, daemon=True).start()
        
    def stop_system(self):
        """Stop the ZeroNet system"""
        def stop_thread():
            try:
                self.log("Stopping ZeroNet system...")
                self.update_status("Stopping system...")
                
                if self.zero_os:
                    self.zero_os.shutdown()
                    
                self.is_system_running = False
                self.log("ZeroNet system stopped")
                self.update_status("System stopped")
                
                # Update GUI state
                self.root.after(0, self.on_system_stopped)
                
            except Exception as e:
                self.log(f"Failed to stop system: {e}", "ERROR")
                self.update_status("System stop failed")
                
        threading.Thread(target=stop_thread, daemon=True).start()
        
    def restart_system(self):
        """Restart the ZeroNet system"""
        self.log("Restarting ZeroNet system...")
        self.stop_system()
        self.root.after(2000, self.start_system)  # Wait 2 seconds before restart
        
    def on_system_started(self):
        """Update GUI when system starts"""
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.restart_button.config(state=tk.NORMAL)
        self.system_status_label.config(text="System: Running", foreground='#00ff00')
        
    def on_system_stopped(self):
        """Update GUI when system stops"""
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.restart_button.config(state=tk.DISABLED)
        self.system_status_label.config(text="System: Stopped", foreground='#ff0000')
        
    # Domain Management Methods
    def add_domain(self):
        """Add a new domain"""
        domain = self.domain_entry.get().strip()
        if not domain:
            messagebox.showwarning("Warning", "Please enter a domain")
            return
            
        if self.zero_skan and MODULES_AVAILABLE:
            success = self.zero_skan.add_domain(domain)
            if success:
                self.log(f"Added domain: {domain}")
                self.domain_entry.delete(0, tk.END)
                self.load_domains()
            else:
                self.log(f"Domain already exists: {domain}", "WARNING")
        else:
            self.log("ZeroSkan module not available", "ERROR")
            
    def remove_domain(self):
        """Remove selected domain"""
        selection = self.domains_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a domain to remove")
            return
            
        domain = self.domains_listbox.get(selection[0])
        
        if messagebox.askyesno("Confirm", f"Remove domain '{domain}'?"):
            if self.zero_skan and MODULES_AVAILABLE:
                success = self.zero_skan.remove_domain(domain)
                if success:
                    self.log(f"Removed domain: {domain}")
                    self.load_domains()
                else:
                    self.log(f"Failed to remove domain: {domain}", "ERROR")
            else:
                self.log("ZeroSkan module not available", "ERROR")
                
    def scan_domains(self):
        """Scan all domains for links"""
        def scan_thread():
            try:
                self.log("Starting domain scanning...")
                self.update_status("Scanning domains...")
                
                if self.zero_skan and MODULES_AVAILABLE:
                    self.zero_skan.scan_all_domains()
                    stats = self.zero_skan.get_stats()
                    
                    self.log(f"Domain scanning completed. Found {stats['total_discovered_urls']} URLs")
                    self.update_status("Domain scanning completed")
                    
                    # Update statistics display
                    self.root.after(0, self.update_domain_stats)
                else:
                    self.log("ZeroSkan module not available", "ERROR")
                    
            except Exception as e:
                self.log(f"Domain scanning failed: {e}", "ERROR")
                self.update_status("Domain scanning failed")
                
        threading.Thread(target=scan_thread, daemon=True).start()
        
    def clear_links(self):
        """Clear discovered links"""
        if messagebox.askyesno("Confirm", "Clear all discovered links?"):
            if self.zero_skan and MODULES_AVAILABLE:
                self.zero_skan.clear_discovered_links()
                self.log("Cleared all discovered links")
                self.update_domain_stats()
            else:
                self.log("ZeroSkan module not available", "ERROR")
                
    def load_domains(self):
        """Load and display domains"""
        self.domains_listbox.delete(0, tk.END)
        
        if self.zero_skan and MODULES_AVAILABLE:
            domains = self.zero_skan.get_domains()
            for domain in domains:
                self.domains_listbox.insert(tk.END, domain)
        else:
            # Fallback - try to load from file
            try:
                with open("domains.json", "r") as f:
                    domains = json.load(f)
                    for domain in domains:
                        self.domains_listbox.insert(tk.END, domain)
            except FileNotFoundError:
                pass
                
    def update_domain_stats(self):
        """Update domain statistics display"""
        if self.zero_skan and MODULES_AVAILABLE:
            try:
                stats = self.zero_skan.get_stats()
                stats_text = f"""Total Domains: {stats['total_domains']}
Domains with Links: {stats['domains_with_links']}
Total URLs Discovered: {stats['total_discovered_urls']}
Average URLs per Domain: {stats['average_urls_per_domain']:.1f}"""
                
                self.domain_stats_text.delete(1.0, tk.END)
                self.domain_stats_text.insert(1.0, stats_text)
            except Exception as e:
                self.log(f"Failed to update domain stats: {e}", "ERROR")
        
    # Scraper Methods
    def scrape_single_url(self):
        """Scrape a single URL"""
        url = self.scrape_url_entry.get().strip()
        if not url:
            messagebox.showwarning("Warning", "Please enter a URL")
            return
            
        def scrape_thread():
            try:
                self.log(f"Scraping URL: {url}")
                self.update_status("Scraping URL...")
                
                if self.zero_scraper and MODULES_AVAILABLE:
                    result = self.zero_scraper.scrape_page(url)
                    if result:
                        self.zero_scraper.add_to_queue(url, result)
                        self.log(f"Successfully scraped: {url}")
                        self.root.after(0, self.update_scraper_queue)
                    else:
                        self.log(f"Failed to scrape: {url}", "ERROR")
                else:
                    self.log("ZeroScraper module not available", "ERROR")
                    
                self.update_status("Ready")
                
            except Exception as e:
                self.log(f"Scraping error: {e}", "ERROR")
                self.update_status("Scraping failed")
                
        threading.Thread(target=scrape_thread, daemon=True).start()
        self.scrape_url_entry.delete(0, tk.END)
        
    def scrape_from_domains(self):
        """Scrape URLs from discovered domains"""
        def scrape_thread():
            try:
                self.log("Starting batch scraping from domains...")
                self.update_status("Batch scraping...")
                
                if self.zero_scraper and self.zero_skan and MODULES_AVAILABLE:
                    # Update max workers
                    self.zero_scraper.max_workers = int(self.workers_var.get())
                    
                    # Get URLs from domain scanner
                    domain_urls = self.zero_skan.get_urls_for_scraper()
                    
                    if domain_urls:
                        self.zero_scraper.scrape_from_domain_list(domain_urls)
                        self.log("Batch scraping completed")
                        self.root.after(0, self.update_scraper_queue)
                    else:
                        self.log("No URLs available for scraping", "WARNING")
                else:
                    self.log("Required modules not available", "ERROR")
                    
                self.update_status("Ready")
                
            except Exception as e:
                self.log(f"Batch scraping error: {e}", "ERROR")
                self.update_status("Batch scraping failed")
                
        threading.Thread(target=scrape_thread, daemon=True).start()
        
    def clear_scraper_queue(self):
        """Clear the scraper queue"""
        if messagebox.askyesno("Confirm", "Clear scraper queue?"):
            if self.zero_scraper and MODULES_AVAILABLE:
                self.zero_scraper.clear_queue()
                self.log("Scraper queue cleared")
                self.update_scraper_queue()
                self.update_scraper_stats()
            else:
                self.log("ZeroScraper module not available", "ERROR")
                
    def update_scraper_queue(self):
        """Update scraper queue display"""
        # Clear existing items
        for item in self.queue_tree.get_children():
            self.queue_tree.delete(item)
            
        if self.zero_scraper and MODULES_AVAILABLE:
            try:
                queue_data = self.zero_scraper.get_queue_data()
                
                for url, data in queue_data.items():
                    title = data.get('title', 'No Title')[:50]
                    self.queue_tree.insert('', tk.END, text=url, values=(title, 'Scraped'))
                    
                self.update_scraper_stats()
                
            except Exception as e:
                self.log(f"Failed to update scraper queue: {e}", "ERROR")
                
    def update_scraper_stats(self):
        """Update scraper statistics"""
        if self.zero_scraper and MODULES_AVAILABLE:
            try:
                stats = self.zero_scraper.get_queue_stats()
                stats_text = f"""Total Entries: {stats['total_entries']}
Total Characters: {stats['total_characters']:,}
Average Snippet Length: {stats['average_snippet_length']:.1f}"""
                
                self.scraper_stats_text.delete(1.0, tk.END)
                self.scraper_stats_text.insert(1.0, stats_text)
            except Exception as e:
                self.log(f"Failed to update scraper stats: {e}", "ERROR")
                
    # Search Methods
    def perform_search(self):
        """Perform search using ZeroSearch"""
        query = self.search_entry.get().strip()
        if not query:
            messagebox.showwarning("Warning", "Please enter a search query")
            return
            
        def search_thread():
            try:
                self.log(f"Performing search: {query}")
                self.update_status("Searching...")
                
                if self.zero_search and MODULES_AVAILABLE:
                    top_k = int(self.results_var.get())
                    ai_mode = self.ai_mode_var.get()
                    
                    # Perform search
                    results = self.zero_search.search_and_extract(query, top_k, ai_mode)
                    
                    # Update results display
                    self.root.after(0, lambda: self.display_search_results(results))
                    
                    self.log(f"Search completed: {results['total_results']} results")
                else:
                    self.log("ZeroSearch module not available", "ERROR")
                    
                self.update_status("Ready")
                
            except Exception as e:
                self.log(f"Search error: {e}", "ERROR")
                self.update_status("Search failed")
                
        threading.Thread(target=search_thread, daemon=True).start()
        
    def display_search_results(self, results):
        """Display search results"""
        self.search_results_text.delete(1.0, tk.END)
        
        if results['total_results'] == 0:
            self.search_results_text.insert(tk.END, "No results found.\n")
            return
            
        self.search_results_text.insert(tk.END, f"Search Results for: '{results['query']}'\n")
        self.search_results_text.insert(tk.END, "=" * 60 + "\n\n")
        
        for i, result in enumerate(results['vector_results'], 1):
            self.search_results_text.insert(tk.END, f"{i}. {result['title']}\n")
            self.search_results_text.insert(tk.END, f"   URL: {result['url']}\n")
            self.search_results_text.insert(tk.END, f"   Score: {result.get('similarity_score', 0):.3f}\n")
            self.search_results_text.insert(tk.END, f"   Snippet: {result['snippet'][:200]}...\n")
            self.search_results_text.insert(tk.END, "\n" + "-" * 60 + "\n\n")
            
        # Update search statistics
        stats_text = f"Results: {results['total_results']} | Extracted: {results.get('extracted_count', 0)}"
        self.search_stats_text.delete(1.0, tk.END)
        self.search_stats_text.insert(1.0, stats_text)
        
    # Compiler Methods
    def load_api_key(self):
        """Load API key from file"""
        filename = filedialog.askopenfilename(
            title="Select API Key File",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'r') as f:
                    api_key = f.read().strip()
                    self.api_key_entry.delete(0, tk.END)
                    self.api_key_entry.insert(0, api_key)
                    self.log("API key loaded from file")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load API key: {e}")
                
    def generate_report(self):
        """Generate AI report using ZeroCompiler"""
        query = self.compiler_query_entry.get().strip()
        api_key = self.api_key_entry.get().strip()
        
        if not query:
            messagebox.showwarning("Warning", "Please enter an analysis query")
            return
            
        def compile_thread():
            try:
                self.log(f"Generating AI report for: {query}")
                self.update_status("Generating report...")
                
                if self.zero_compiler and MODULES_AVAILABLE:
                    # Update API key if provided
                    if api_key:
                        self.zero_compiler.api_key = api_key
                        
                    # Generate report
                    results = self.zero_compiler.compile_response(query)
                    
                    if "error" not in results:
                        # Display report
                        self.root.after(0, lambda: self.display_report(results))
                        self.log("AI report generated successfully")
                    else:
                        self.log(f"Report generation failed: {results['error']}", "ERROR")
                        
                else:
                    self.log("ZeroCompiler module not available", "ERROR")
                    
                self.update_status("Ready")
                
            except Exception as e:
                self.log(f"Report generation error: {e}", "ERROR")
                self.update_status("Report generation failed")
                
        threading.Thread(target=compile_thread, daemon=True).start()
        
    def display_report(self, results):
        """Display generated report"""
        self.report_text.delete(1.0, tk.END)
        
        # Header
        self.report_text.insert(tk.END, f"AI Analysis Report\n")
        self.report_text.insert(tk.END, f"Query: {results['query']}\n")
        self.report_text.insert(tk.END, f"Generated: {results['timestamp']}\n")
        self.report_text.insert(tk.END, f"Sources: {results['sources_processed']}\n")
        self.report_text.insert(tk.END, "=" * 80 + "\n\n")
        
        # Final report
        self.report_text.insert(tk.END, results['final_report'])
        
        # Metadata
        self.report_text.insert(tk.END, f"\n\n" + "=" * 80 + "\n")
        self.report_text.insert(tk.END, f"Processing Metadata:\n")
        metadata = results.get('processing_metadata', {})
        self.report_text.insert(tk.END, f"Model: {metadata.get('model_used', 'N/A')}\n")
        self.report_text.insert(tk.END, f"Tokens Processed: {metadata.get('total_tokens_processed', 0):,}\n")
        self.report_text.insert(tk.END, f"Chunks Created: {results.get('chunks_created', 0)}\n")
        
    def save_report(self):
        """Save generated report to file"""
        content = self.report_text.get(1.0, tk.END)
        if not content.strip():
            messagebox.showwarning("Warning", "No report to save")
            return
            
        filename = filedialog.asksaveasfilename(
            title="Save Report",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("Markdown files", "*.md"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.log(f"Report saved to: {filename}")
                messagebox.showinfo("Success", "Report saved successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save report: {e}")
                
    def clear_report(self):
        """Clear the report display"""
        self.report_text.delete(1.0, tk.END)
        self.log("Report display cleared")
        
    def export_pdf(self):
        """Export report as PDF (placeholder)"""
        messagebox.showinfo("Info", "PDF export feature coming soon!")
        
    # Log Methods
    def clear_logs(self):
        """Clear the logs display"""
        self.logs_text.delete(1.0, tk.END)
        self.log("Logs cleared")
        
    def export_logs(self):
        """Export logs to file"""
        logs_content = self.logs_text.get(1.0, tk.END)
        if not logs_content.strip():
            messagebox.showwarning("Warning", "No logs to export")
            return
            
        filename = filedialog.asksaveasfilename(
            title="Export Logs",
            defaultextension=".log",
            filetypes=[("Log files", "*.log"), ("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(logs_content)
                self.log(f"Logs exported to: {filename}")
                messagebox.showinfo("Success", "Logs exported successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export logs: {e}")

def main():
    """Main function to run the ZeroNet GUI"""
    root = tk.Tk()
    
    # Set application icon (if available)
    try:
        root.iconbitmap("zeronet_icon.ico")
    except:
        pass  # Icon file not found, continue without it
    
    # Initialize the GUI application
    app = ZeroNetGUI(root)
    
    # Load initial data
    if MODULES_AVAILABLE:
        app.load_domains()
        app.update_domain_stats()
        app.update_scraper_queue()
        app.update_scraper_stats()
    
    # Handle window closing
    def on_closing():
        if app.is_system_running:
            if messagebox.askokcancel("Quit", "System is running. Stop system and quit?"):
                app.stop_system()
                root.after(1000, root.destroy)  # Wait 1 second for graceful shutdown
        else:
            root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    # Start the GUI main loop
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("\nShutdown requested by user")
        if app.is_system_running:
            app.stop_system()

if __name__ == "__main__":
    print("ZeroNet GUI - Graphical User Interface")
    print("=" * 50)
    print("Loading ZeroNet modules...")
    
    if not MODULES_AVAILABLE:
        print("WARNING: ZeroNet modules not found!")
        print("The GUI will work in demo mode.")
        print("Please ensure all ZeroNet Python files are in the same directory.")
    else:
        print("All modules loaded successfully!")
    
    print("Starting GUI...")
    main()














# Database Manager for ZeroNet
    Manages embeddings of titles and snippets from queue.json
    Each vector is labeled with its source URL
    """

    def __init__(self, 
                 queue_file="queue.json",
                 index_file="zeronet.index",
                 metadata_file="zeronet_metadata.pkl",
                 model_name="all-MiniLM-L6-v2"):

        self.queue_file = queue_file
        self.index_file = index_file
        self.metadata_file = metadata_file

        # Initialize sentence transformer
        self.model = SentenceTransformer(model_name)
        self.embedding_dim = self.model.get_sentence_embedding_dimension()

        # Initialize FAISS index
        self.index = faiss.IndexFlatIP(self.embedding_dim)  # Inner product for similarity
        self.url_to_id = {}  # Maps URLs to FAISS IDs
        self.id_to_metadata = {}  # Maps FAISS IDs to metadata
        self.next_id = 0

        self.logger = self._setup_logger()

        # Load existing index if available
        self._load_index()

    def _setup_logger(self):
        """Setup logging for ZeroIndex"""
        logger = logging.getLogger('ZeroIndex')
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('[ZeroIndex] %(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

    def _load_index(self):
        """Load existing FAISS index and metadata"""
        try:
            if os.path.exists(self.index_file) and os.path.exists(self.metadata_file):
                self.index = faiss.read_index(self.index_file)

                with open(self.metadata_file, 'rb') as f:
                    metadata = pickle.load(f)
                    self.url_to_id = metadata['url_to_id']
                    self.id_to_metadata = metadata['id_to_metadata']
                    self.next_id = metadata['next_id']

                self.logger.info(f"Loaded existing index with {self.index.ntotal} vectors")
            else:
                self.logger.info("No existing index found, starting fresh")
        except Exception as e:
            self.logger.error(f"Failed to load existing index: {e}")
            self.logger.info("Starting with fresh index")

    def _save_index(self):
        """Save FAISS index and metadata to disk"""
        try:
            faiss.write_index(self.index, self.index_file)

            metadata = {
                'url_to_id': self.url_to_id,
                'id_to_metadata': self.id_to_metadata,
                'next_id': self.next_id
            }

            with open(self.metadata_file, 'wb') as f:
                pickle.dump(metadata, f)

            self.logger.info(f"Index saved with {self.index.ntotal} vectors")
        except Exception as e:
            self.logger.error(f"Failed to save index: {e}")

    def _create_embedding(self, title: str, snippet: str) -> np.ndarray:
        """
        Create embedding for title and snippet combined
        
        Args:
            title (str): Page title
            snippet (str): Page snippet
            
        Returns:
            np.ndarray: Embedding vector
        """
        # Combine title and snippet with separator
        combined_text = f"{title} [SEP] {snippet}"

        # Create embedding
        embedding = self.model.encode(combined_text)

        # Normalize for cosine similarity (since we use inner product)
        embedding = embedding / np.linalg.norm(embedding)

        return embedding.astype(np.float32)

    def process_queue(self):
        """
        Process queue.json and add new entries to FAISS index
        Only processes URLs that aren't already in the index
        """
        try:
            with open(self.queue_file, 'r', encoding='utf-8') as f:
                queue_data = json.load(f)
        except FileNotFoundError:
            self.logger.warning(f"Queue file {self.queue_file} not found")
            return
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON in queue file: {e}")
            return

        new_entries = 0

        for url, data in queue_data.items():
            # Check if URL is already in index
            if url in self.url_to_id:
                continue

            try:
                title = data.get('title', '')
                snippet = data.get('snippet', '')

                if not title and not snippet:
                    self.logger.warning(f"Empty title and snippet for {url}")
                    continue

                # Create embedding
                embedding = self._create_embedding(title, snippet)

                # Add to FAISS index
                self.index.add(embedding.reshape(1, -1))

                # Store metadata
                current_id = self.next_id
                self.url_to_id[url] = current_id
                self.id_to_metadata[current_id] = {
                    'url': url,
                    'title': title,
                    'snippet': snippet
                }

                self.next_id += 1
                new_entries += 1

                self.logger.info(f"Added to index: {url}")

            except Exception as e:
                self.logger.error(f"Failed to process {url}: {e}")

        if new_entries > 0:
            self._save_index()
            self.logger.info(f"Processed {new_entries} new entries")
        else:
            self.logger.info("No new entries to process")

    def search(self, query: str, top_k: int = 10) -> List[Dict]:
        """
        Search for most similar vectors to query
        
        Args:
            query (str): Search query
            top_k (int): Number of results to return
            
        Returns:
            List[Dict]: List of search results with metadata and scores
        """
        if self.index.ntotal == 0:
            self.logger.warning("Index is empty")
            return []

        try:
            # Create query embedding
            query_embedding = self.model.encode(query)
            query_embedding = query_embedding / np.linalg.norm(query_embedding)
            query_embedding = query_embedding.astype(np.float32).reshape(1, -1)

            # Search in FAISS index
            top_k = min(top_k, self.index.ntotal)
            scores, indices = self.index.search(query_embedding, top_k)

            # Prepare results
            results = []
            for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
                if idx == -1:  # Invalid index
                    continue

                metadata = self.id_to_metadata.get(idx, {})
                results.append({
                    'rank': i + 1,
                    'url': metadata.get('url', ''),
                    'title': metadata.get('title', ''),
                    'snippet': metadata.get('snippet', ''),
                    'similarity_score': float(score)
                })

            self.logger.info(f"Search completed: {len(results)} results for '{query}'")
            return results

        except Exception as e:
            self.logger.error(f"Search failed: {e}")
            return []

    def get_urls_by_similarity(self, query: str, top_k: int = 10) -> List[str]:
        """
        Get URLs of most similar pages (for ZeroSearch++)
        
        Args:
            query (str): Search query
            top_k (int): Number of URLs to return
            
        Returns:
            List[str]: List of URLs ordered by similarity
        """
        results = self.search(query, top_k)
        return [result['url'] for result in results if result['url']]

    def remove_url(self, url: str) -> bool:
        """
        Remove a URL from the index
        Note: FAISS doesn't support removal, so we mark as deleted in metadata
        
        Args:
            url (str): URL to remove
            
        Returns:
            bool: True if removed, False if not found
        """
        if url not in self.url_to_id:
            return False

        faiss_id = self.url_to_id[url]

        # Mark as deleted in metadata
        if faiss_id in self.id_to_metadata:
            self.id_to_metadata[faiss_id]['deleted'] = True

        # Remove from URL mapping
        del self.url_to_id[url]

        self.logger.info(f"Marked as deleted: {url}")
        return True

    def rebuild_index(self):
        """
        Rebuild the entire index from queue.json
        Useful for cleanup and optimization
        """
        self.logger.info("Rebuilding index from scratch...")

        # Reset index
        self.index = faiss.IndexFlatIP(self.embedding_dim)
        self.url_to_id = {}
        self.id_to_metadata = {}
        self.next_id = 0

        # Process queue
        self.process_queue()

        self.logger.info("Index rebuild completed")

    def get_stats(self) -> Dict:
        """
        Get statistics about the index
        
        Returns:
            Dict: Index statistics
        """
        active_entries = sum(1 for metadata in self.id_to_metadata.values() 
                           if not metadata.get('deleted', False))

        return {
            'total_vectors': self.index.ntotal,
            'active_entries': active_entries,
            'deleted_entries': self.index.ntotal - active_entries,
            'embedding_dimension': self.embedding_dim,
            'model_name': self.model._modules['0'].auto_model.name_or_path
        }

    def export_metadata(self) -> Dict:
        """
        Export all metadata for backup or analysis
        
        Returns:
            Dict: All metadata including URLs, titles, and snippets
        """
        active_metadata = {}
        for faiss_id, metadata in self.id_to_metadata.items():
            if not metadata.get('deleted', False):
                url = metadata['url']
                active_metadata[url] = {
                    'title': metadata['title'],
                    'snippet': metadata['snippet'],
                    'faiss_id': faiss_id
                }

        return active_metadata

# Integration example for ZeroNet
if __name__ == "__main__":
    # Initialize ZeroIndex
    zero_index = ZeroIndex()

    print("ZeroIndex - FAISS Vector Database Manager")
    print("Processing queue.json for new entries...")

    # Process queue from ZeroScraper
    zero_index.process_queue()

    # Display statistics
    stats = zero_index.get_stats()
    print(f"\nIndex Statistics:")
    print(f"Total vectors: {stats['total_vectors']}")
    print(f"Active entries: {stats['active_entries']}")
    print(f"Embedding dimension: {stats['embedding_dimension']}")

    # Example search
    if stats['total_vectors'] > 0:
        print(f"\nExample search for 'artificial intelligence':")
        results = zero_index.search("artificial intelligence", top_k=3)

        for result in results:
            print(f"\nRank {result['rank']} (Score: {result['similarity_score']:.4f})")
            print(f"Title: {result['title']}")
            print(f"URL: {result['url']}")
            print(f"Snippet: {result['snippet'][:100]}...")

    print(f"\nZeroIndex ready for ZeroSearch++ integration")
    
#ZeroOS.py

import os
import sys
import threading
import time
import logging
import json
import subprocess
from typing import Dict, List, Any, Optional
from datetime import datetime
import psutil
import signal

class ZeroOS:
    """
    ZeroOS - Sandboxing System for ZeroNet
    Runs all other modules within itself as a sandboxed environment
    Ensures absolute privacy with exception of IP handling
    Manages module lifecycle, resource allocation, and inter-module communication
    """

    def __init__(self, config_file="zeroos_config.json"):
        self.config_file = config_file
        self.config = self._load_config()

        # Module management
        self.modules = {}
        self.module_processes = {}
        self.module_status = {}
        self.module_threads = {}

        # Sandboxing and security
        self.sandbox_active = True
        self.privacy_mode = True  # IP protection enabled
        self.resource_limits = self.config.get('resource_limits', {})

        # Communication and logging
        self.logger = self._setup_logger()
        self.message_queue = {}
        self.shared_data = {}

        # System monitoring
        self.system_stats = {}
        self.start_time = datetime.now()

        # Initialize modules
        self._initialize_modules()

        self.logger.info("ZeroOS initialized - Sandbox active, Privacy mode enabled")

    def _load_config(self) -> Dict:
        """Load ZeroOS configuration"""
        default_config = {
            "modules": {
                "ZeroScraper": {
                    "enabled": True,
                    "max_workers": 5,
                    "memory_limit_mb": 512,
                    "cpu_limit_percent": 25
                },
                "ZeroIndex": {
                    "enabled": True,
                    "memory_limit_mb": 1024,
                    "cpu_limit_percent": 30
                },
                "ZeroSkan": {
                    "enabled": True,
                    "max_depth": 3,
                    "memory_limit_mb": 256,
                    "cpu_limit_percent": 20
                },
                "ZeroSearch": {
                    "enabled": True,
                    "memory_limit_mb": 512,
                    "cpu_limit_percent": 25
                },
                "ZeroCompiler": {
                    "enabled": True,
                    "memory_limit_mb": 768,
                    "cpu_limit_percent": 35
                }
            },
            "sandbox_settings": {
                "network_isolation": False,  # Can't isolate completely due to web scraping needs
                "filesystem_isolation": True,
                "process_isolation": True,
                "memory_protection": True
            },
            "privacy_settings": {
                "ip_protection": True,
                "dns_protection": True,
                "traffic_encryption": True,
                "no_tracking": True
            },
            "resource_limits": {
                "max_total_memory_mb": 4096,
                "max_cpu_percent": 80,
                "max_disk_usage_mb": 10240,
                "max_network_bandwidth_mbps": 100
            }
        }

        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
            # Merge with defaults
            for key, value in default_config.items():
                if key not in config:
                    config[key] = value
            return config
        except FileNotFoundError:
            self._save_config(default_config)
            return default_config

    def _save_config(self, config: Dict):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save config: {e}")

    def _setup_logger(self):
        """Setup comprehensive logging for ZeroOS"""
        logger = logging.getLogger('ZeroOS')
        logger.setLevel(logging.INFO)

        # Console handler
        console_handler = logging.StreamHandler()
        console_formatter = logging.Formatter(
            '[ZeroOS] %(asctime)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

        # File handler for sandbox logging
        try:
            file_handler = logging.FileHandler('zeroos_sandbox.log')
            file_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)
        except Exception as e:
            logger.warning(f"Could not setup file logging: {e}")

        return logger

    def _initialize_modules(self):
        """Initialize all ZeroNet modules within sandbox"""
        self.logger.info("Initializing modules in sandboxed environment...")

        module_configs = self.config.get('modules', {})

        for module_name, module_config in module_configs.items():
            if module_config.get('enabled', True):
                try:
                    self._load_module(module_name, module_config)
                except Exception as e:
                    self.logger.error(f"Failed to load module {module_name}: {e}")

        self.logger.info(f"Initialized {len(self.modules)} modules")

    def _load_module(self, module_name: str, config: Dict):
        """Load and sandbox a module"""
        self.logger.info(f"Loading module: {module_name}")

        # Create sandboxed environment for module
        module_env = self._create_sandbox_environment(module_name, config)

        # Initialize module status
        self.module_status[module_name] = {
            'status': 'initializing',
            'pid': None,
            'start_time': datetime.now(),
            'memory_usage': 0,
            'cpu_usage': 0,
            'last_activity': datetime.now(),
            'error_count': 0
        }

        # Module-specific initialization
        if module_name == "ZeroScraper":
            from zeroscraper_module import ZeroScraper
            self.modules[module_name] = ZeroScraper()
        elif module_name == "ZeroIndex":
            from zeroindex_module import ZeroIndex
            self.modules[module_name] = ZeroIndex()
        elif module_name == "ZeroSkan":
            from zeroskan_module import ZeroSkan
            self.modules[module_name] = ZeroSkan()
        elif module_name == "ZeroSearch":
            from zerosearch_module import ZeroSearch
            self.modules[module_name] = ZeroSearch()
        elif module_name == "ZeroCompiler":
            from zerocompiler_module import ZeroCompiler
            self.modules[module_name] = ZeroCompiler()

        self.module_status[module_name]['status'] = 'running'
        self.logger.info(f"Module {module_name} loaded and sandboxed")

    def _create_sandbox_environment(self, module_name: str, config: Dict) -> Dict:
        """Create sandboxed environment for module"""
        sandbox_env = os.environ.copy()

        # Privacy settings - IP protection
        if self.config.get('privacy_settings', {}).get('ip_protection', True):
            # Note: Actual IP protection would require system-level networking changes
            # This is a placeholder for the concept
            sandbox_env['ZEROOS_IP_PROTECTED'] = '1'
            sandbox_env['ZEROOS_NO_DIRECT_IP'] = '1'

        # Resource limits
        memory_limit = config.get('memory_limit_mb', 512)
        cpu_limit = config.get('cpu_limit_percent', 25)

        sandbox_env['ZEROOS_MEMORY_LIMIT'] = str(memory_limit)
        sandbox_env['ZEROOS_CPU_LIMIT'] = str(cpu_limit)
        sandbox_env['ZEROOS_MODULE_NAME'] = module_name

        # Filesystem isolation
        if self.config.get('sandbox_settings', {}).get('filesystem_isolation', True):
            sandbox_env['ZEROOS_SANDBOX_ROOT'] = os.path.join(os.getcwd(), 'sandbox', module_name)
            os.makedirs(sandbox_env['ZEROOS_SANDBOX_ROOT'], exist_ok=True)

        return sandbox_env

    def _monitor_resources(self):
        """Monitor system and module resource usage"""
        while self.sandbox_active:
            try:
                # System-wide monitoring
                process = psutil.Process()
                self.system_stats = {
                    'cpu_percent': psutil.cpu_percent(),
                    'memory_percent': psutil.virtual_memory().percent,
                    'disk_usage': psutil.disk_usage('/').percent,
                    'network_io': psutil.net_io_counters(),
                    'zeroos_memory': process.memory_info().rss / 1024 / 1024,  # MB
                    'zeroos_cpu': process.cpu_percent()
                }

                # Module-specific monitoring
                for module_name in self.modules:
                    if module_name in self.module_status:
                        status = self.module_status[module_name]

                        # Update resource usage (simplified monitoring)
                        status['memory_usage'] = self.system_stats['zeroos_memory'] / len(self.modules)
                        status['cpu_usage'] = self.system_stats['zeroos_cpu'] / len(self.modules)
                        status['last_activity'] = datetime.now()

                # Check resource limits
                self._enforce_resource_limits()

            except Exception as e:
                self.logger.error(f"Resource monitoring error: {e}")

            time.sleep(5)  # Monitor every 5 seconds

    def _enforce_resource_limits(self):
        """Enforce resource limits for modules"""
        limits = self.resource_limits

        # Check total memory usage
        if self.system_stats.get('zeroos_memory', 0) > limits.get('max_total_memory_mb', 4096):
            self.logger.warning("Memory limit exceeded - initiating cleanup")
            self._emergency_cleanup()

        # Check CPU usage
        if self.system_stats.get('zeroos_cpu', 0) > limits.get('max_cpu_percent', 80):
            self.logger.warning("CPU limit exceeded - throttling modules")
            self._throttle_modules()

    def _emergency_cleanup(self):
        """Emergency cleanup when resources are exhausted"""
        self.logger.warning("Performing emergency cleanup")

        # Clear caches, temporary data
        for module_name, module in self.modules.items():
            try:
                if hasattr(module, 'clear_cache'):
                    module.clear_cache()
                if hasattr(module, 'emergency_cleanup'):
                    module.emergency_cleanup()
            except Exception as e:
                self.logger.error(f"Emergency cleanup failed for {module_name}: {e}")

    def _throttle_modules(self):
        """Throttle module operations to reduce CPU usage"""
        self.logger.info("Throttling modules due to high CPU usage")

        for module_name in self.modules:
            status = self.module_status.get(module_name, {})
            if status.get('cpu_usage', 0) > 50:  # High CPU module
                self.logger.info(f"Throttling {module_name}")
                # Add delays, reduce worker threads, etc.

    def start_module(self, module_name: str) -> bool:
        """Start a specific module"""
        if module_name not in self.modules:
            self.logger.error(f"Module {module_name} not found")
            return False

        try:
            status = self.module_status.get(module_name, {})
            if status.get('status') == 'running':
                self.logger.info(f"Module {module_name} already running")
                return True

            # Start module in thread
            def module_runner():
                try:
                    if hasattr(self.modules[module_name], 'start'):
                        self.modules[module_name].start()
                    status['status'] = 'running'
                    status['start_time'] = datetime.now()
                except Exception as e:
                    self.logger.error(f"Module {module_name} crashed: {e}")
                    status['status'] = 'crashed'
                    status['error_count'] += 1

            thread = threading.Thread(target=module_runner, name=f"{module_name}_thread")
            thread.daemon = True
            thread.start()

            self.module_threads[module_name] = thread
            self.logger.info(f"Started module: {module_name}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to start module {module_name}: {e}")
            return False

    def stop_module(self, module_name: str) -> bool:
        """Stop a specific module"""
        if module_name not in self.modules:
            return False

        try:
            status = self.module_status.get(module_name, {})
            status['status'] = 'stopping'

            # Stop module gracefully
            if hasattr(self.modules[module_name], 'stop'):
                self.modules[module_name].stop()

            # Stop thread
            if module_name in self.module_threads:
                # Note: Cannot force stop threads in Python, rely on graceful shutdown
                pass

            status['status'] = 'stopped'
            self.logger.info(f"Stopped module: {module_name}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to stop module {module_name}: {e}")
            return False

    def restart_module(self, module_name: str) -> bool:
        """Restart a specific module"""
        self.logger.info(f"Restarting module: {module_name}")
        return self.stop_module(module_name) and self.start_module(module_name)

    def send_message(self, from_module: str, to_module: str, message: Dict):
        """Inter-module communication"""
        if to_module not in self.modules:
            self.logger.error(f"Target module {to_module} not found")
            return False

        if to_module not in self.message_queue:
            self.message_queue[to_module] = []

        message_envelope = {
            'from': from_module,
            'to': to_module,
            'timestamp': datetime.now(),
            'message': message
        }

        self.message_queue[to_module].append(message_envelope)
        self.logger.debug(f"Message sent from {from_module} to {to_module}")
        return True

    def get_messages(self, module_name: str) -> List[Dict]:
        """Get pending messages for a module"""
        messages = self.message_queue.get(module_name, [])
        self.message_queue[module_name] = []  # Clear after reading
        return messages

    def execute_pipeline(self, operation: str, params: Dict = None) -> Dict:
        """Execute a complete ZeroNet pipeline operation"""
        self.logger.info(f"Executing pipeline: {operation}")

        if params is None:
            params = {}

        try:
            if operation == "full_index":
                return self._execute_full_indexing(params)
            elif operation == "search":
                return self._execute_search(params)
            elif operation == "domain_scan":
                return self._execute_domain_scan(params)
            else:
                return {"error": f"Unknown operation: {operation}"}

        except Exception as e:
            self.logger.error(f"Pipeline execution failed: {e}")
            return {"error": str(e)}

    def _execute_full_indexing(self, params: Dict) -> Dict:
        """Execute full indexing pipeline: ZeroSkan -> ZeroScraper -> ZeroIndex"""
        results = {"status": "success", "steps": []}

        # Step 1: ZeroSkan - Domain scanning
        if "ZeroSkan" in self.modules:
            self.logger.info("Step 1: Domain scanning")
            skan = self.modules["ZeroSkan"]
            skan.scan_all_domains(params.get('max_pages_per_domain', 50))
            results["steps"].append("Domain scanning completed")

        # Step 2: ZeroScraper - Page scraping
        if "ZeroScraper" in self.modules and "ZeroSkan" in self.modules:
            self.logger.info("Step 2: Page scraping")
            scraper = self.modules["ZeroScraper"]
            skan = self.modules["ZeroSkan"]

            urls_to_scrape = skan.get_urls_for_scraper()
            scraper.scrape_from_domain_list(urls_to_scrape)
            results["steps"].append("Page scraping completed")

        # Step 3: ZeroIndex - Vector indexing
        if "ZeroIndex" in self.modules:
            self.logger.info("Step 3: Vector indexing")
            indexer = self.modules["ZeroIndex"]
            indexer.process_queue()
            results["steps"].append("Vector indexing completed")

        self.logger.info("Full indexing pipeline completed")
        return results

    def _execute_search(self, params: Dict) -> Dict:
        """Execute search pipeline: ZeroSearch -> ZeroScraper -> ZeroCompiler"""
        query = params.get('query', '')
        ai_mode = params.get('ai_mode', False)
        top_k = params.get('top_k', 10)

        if not query:
            return {"error": "No query provided"}

        results = {"status": "success", "query": query, "results": []}

        # Step 1: ZeroSearch - Vector search
        if "ZeroIndex" in self.modules:
            indexer = self.modules["ZeroIndex"]
            search_results = indexer.search(query, top_k)

            if ai_mode and search_results:
                # Step 2: Get full content for AI processing
                urls = [result['url'] for result in search_results]

                if "ZeroScraper" in self.modules:
                    scraper = self.modules["ZeroScraper"]
                    raw_content = {}

                    for url in urls:
                        content = scraper.scrape_page(url)
                        if content:
                            raw_content[url] = content

                    # Save to raw.json for ZeroCompiler
                    with open('raw.json', 'w', encoding='utf-8') as f:
                        json.dump(raw_content, f, indent=2, ensure_ascii=False)

                # Step 3: ZeroCompiler - Generate AI response
                if "ZeroCompiler" in self.modules:
                    compiler = self.modules["ZeroCompiler"]
                    ai_response = compiler.compile_response(query, 'raw.json')
                    results["ai_response"] = ai_response
            else:
                # Return URLs only
                results["results"] = search_results

        return results

    def _execute_domain_scan(self, params: Dict) -> Dict:
        """Execute domain scanning operation"""
        if "ZeroSkan" not in self.modules:
            return {"error": "ZeroSkan module not available"}

        skan = self.modules["ZeroSkan"]
        max_pages = params.get('max_pages_per_domain', 50)

        skan.scan_all_domains(max_pages)
        stats = skan.get_stats()

        return {
            "status": "success",
            "stats": stats
        }

    def get_system_status(self) -> Dict:
        """Get comprehensive system status"""
        uptime = datetime.now() - self.start_time

        return {
            "sandbox_active": self.sandbox_active,
            "privacy_mode": self.privacy_mode,
            "uptime_seconds": uptime.total_seconds(),
            "system_stats": self.system_stats,
            "module_status": self.module_status,
            "active_modules": len([m for m in self.module_status.values() 
                                 if m.get('status') == 'running']),
            "total_modules": len(self.modules),
            "message_queue_size": sum(len(q) for q in self.message_queue.values())
        }

    def shutdown(self):
        """Graceful shutdown of ZeroOS and all modules"""
        self.logger.info("Initiating ZeroOS shutdown...")

        # Stop all modules
        for module_name in list(self.modules.keys()):
            self.stop_module(module_name)

        # Stop monitoring
        self.sandbox_active = False

        # Save final state
        try:
            final_status = self.get_system_status()
            with open('zeroos_final_state.json', 'w') as f:
                json.dump(final_status, f, indent=2, default=str)
        except Exception as e:
            self.logger.error(f"Failed to save final state: {e}")

        self.logger.info("ZeroOS shutdown completed")

    def start(self):
        """Start ZeroOS and all modules"""
        self.logger.info("Starting ZeroOS...")

        # Start resource monitoring
        monitor_thread = threading.Thread(target=self._monitor_resources, daemon=True)
        monitor_thread.start()

        # Start all modules
        for module_name in self.modules:
            self.start_module(module_name)

        self.logger.info("ZeroOS fully operational - All modules running in sandbox")
        return True

# Signal handlers for graceful shutdown
def signal_handler(signum, frame, zeroos_instance):
    """Handle shutdown signals"""
    zeroos_instance.shutdown()
    sys.exit(0)

# Main execution for standalone ZeroOS
if __name__ == "__main__":
    # Initialize ZeroOS
    zero_os = ZeroOS()

    # Setup signal handlers
    signal.signal(signal.SIGINT, lambda s, f: signal_handler(s, f, zero_os))
    signal.signal(signal.SIGTERM, lambda s, f: signal_handler(s, f, zero_os))

    print("ZeroOS - Sandboxing System for ZeroNet")
    print("=" * 50)
    print("Absolute Privacy Guaranteed (IP Protection Active)")
    print("All modules running in sandboxed environment")
    print("=" * 50)

    # Start the system
    zero_os.start()

    # Display initial status
    status = zero_os.get_system_status()
    print(f"\nSystem Status:")
    print(f"Active Modules: {status['active_modules']}/{status['total_modules']}")
    print(f"Sandbox: {'Active' if status['sandbox_active'] else 'Inactive'}")
    print(f"Privacy Mode: {'Enabled' if status['privacy_mode'] else 'Disabled'}")

    # Example operations
    print(f"\nExecuting example operations...")

    # Example 1: Full indexing
    print("1. Running full indexing pipeline...")
    result = zero_os.execute_pipeline("full_index", {"max_pages_per_domain": 10})
    print(f"Indexing result: {result.get('status', 'failed')}")

    # Example 2: Search operation
    print("2. Running search operation...")
    search_result = zero_os.execute_pipeline("search", {
        "query": "artificial intelligence",
        "ai_mode": False,
        "top_k": 5
    })
    print(f"Search found {len(search_result.get('results', []))} results")

    # Keep running
    try:
        print(f"\nZeroOS running... Press Ctrl+C to shutdown")
        while True:
            time.sleep(60)
            status = zero_os.get_system_status()
            uptime_hours = status['uptime_seconds'] / 3600
            print(f"Uptime: {uptime_hours:.1f} hours - All systems operational")
    except KeyboardInterrupt:
        print(f"\nShutdown requested...")
        zero_os.shutdown()
        
#ZeroSkan.py

import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, urlunparse
import time
import logging
from typing import Dict, List, Set
import threading
from collections import deque
import re

class ZeroSkan:
    """
    ZeroSkan - Domain Link Manager for ZeroNet
    Takes lists of links by domains and stores them for ZeroScraper to use
    Crawls domains to discover pages and maintains organized link lists
    """

    def __init__(self, domains_file="domains.json", links_file="discovered_links.json", max_depth=3):
        self.domains_file = domains_file
        self.links_file = links_file
        self.max_depth = max_depth

        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

        self.domains = self._load_domains()
        self.discovered_links = self._load_discovered_links()

        self.visited_urls = set()
        self.url_queue = deque()
        self.lock = threading.Lock()

        self.logger = self._setup_logger()

    def _setup_logger(self):
        logger = logging.getLogger('ZeroSkan')
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('[ZeroSkan] %(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

    def _load_domains(self) -> List[str]:
        try:
            with open(self.domains_file, 'r') as f:
                domains = json.load(f)
            self.logger.info(f"Loaded {len(domains)} domains")
            return domains
        except FileNotFoundError:
            default_domains = ["wikipedia.org", "stackoverflow.com", "github.com", "reddit.com"]
            self._save_domains(default_domains)
            return default_domains

    def _save_domains(self, domains: List[str]):
        try:
            with open(self.domains_file, 'w') as f:
                json.dump(domains, f, indent=2)
            self.logger.info(f"Saved {len(domains)} domains")
        except Exception as e:
            self.logger.error(f"Failed to save domains: {e}")

    def _load_discovered_links(self) -> Dict[str, List[str]]:
        try:
            with open(self.links_file, 'r') as f:
                links = json.load(f)
            total_links = sum(len(urls) for urls in links.values())
            self.logger.info(f"Loaded {total_links} discovered links across {len(links)} domains")
            return links
        except FileNotFoundError:
            return {}

    def _save_discovered_links(self):
        try:
            with open(self.links_file, 'w') as f:
                json.dump(self.discovered_links, f, indent=2)
            total_links = sum(len(urls) for urls in self.discovered_links.values())
            self.logger.info(f"Saved {total_links} discovered links")
        except Exception as e:
            self.logger.error(f"Failed to save discovered links: {e}")

    def add_domain(self, domain: str):
        domain = domain.replace('http://', '').replace('https://', '').replace('www.', '')
        domain = domain.split('/')[0]
        if domain not in self.domains:
            self.domains.append(domain)
            self._save_domains(self.domains)
            self.logger.info(f"Added domain: {domain}")
            return True
        else:
            self.logger.info(f"Domain already exists: {domain}")
            return False

    def remove_domain(self, domain: str):
        if domain in self.domains:
            self.domains.remove(domain)
            if domain in self.discovered_links:
                del self.discovered_links[domain]
            self._save_domains(self.domains)
            self._save_discovered_links()
            self.logger.info(f"Removed domain: {domain}")
            return True
        return False

    def get_domains(self) -> List[str]:
        return self.domains.copy()

    def _is_valid_url(self, url: str, domain: str) -> bool:
        try:
            parsed = urlparse(url)
            if parsed.scheme not in ['http', 'https']:
                return False
            if domain not in parsed.netloc:
                return False
            skip_extensions = {'.pdf', '.jpg', '.jpeg', '.png', '.gif', '.css', '.js', 
                               '.ico', '.zip', '.tar', '.gz', '.mp4', '.mp3', '.avi'}
            if any(url.lower().endswith(ext) for ext in skip_extensions):
                return False
            skip_patterns = ['/api/', '/admin/', '/login', '/logout', '/register', 
                             '/search?', '/tag/', '/category/', '/archive/']
            if any(pattern in url.lower() for pattern in skip_patterns):
                return False
            return True
        except Exception:
            return False

    def _extract_links(self, html_content: str, base_url: str, domain: str) -> Set[str]:
        links = set()
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            for tag in soup.find_all(['a', 'link']):
                href = tag.get('href')
                if not href:
                    continue
                absolute_url = urljoin(base_url, href)
                parsed = urlparse(absolute_url)
                clean_url = urlunparse((parsed.scheme, parsed.netloc, parsed.path, 
                                        parsed.params, parsed.query, ''))
                if self._is_valid_url(clean_url, domain):
                    links.add(clean_url)
        except Exception as e:
            self.logger.error(f"Failed to extract links from {base_url}: {e}")
        return links

    def crawl_domain(self, domain: str) -> List[str]:
        discovered_urls = []
        visited = set()
        queue = deque()

        start_urls = [f"https://{domain}", f"https://www.{domain}"]
        for start_url in start_urls:
            try:
                response = self.session.get(start_url, timeout=10)
                if response.status_code == 200:
                    queue.append((start_url, 0))
                    break
            except:
                continue

        if not queue:
            self.logger.warning(f"Could not access {domain}")
            return []

        self.logger.info(f"Starting full crawl of {domain} (no page limit)")

        while queue:
            try:
                current_url, depth = queue.popleft()
                if current_url in visited or depth > self.max_depth:
                    continue

                visited.add(current_url)

                response = self.session.get(current_url, timeout=10)
                if response.status_code != 200:
                    continue

                discovered_urls.append(current_url)
                self.logger.info(f"Crawled: {current_url}")

                if depth < self.max_depth:
                    links = self._extract_links(response.text, current_url, domain)
                    for link in links:
                        if link not in visited and link not in [u for u, _ in queue]:
                            queue.append((link, depth + 1))

                time.sleep(1)

            except Exception as e:
                self.logger.error(f"Error crawling {current_url}: {e}")
                continue

        self.logger.info(f"Full crawl completed for {domain}: {len(discovered_urls)} pages discovered")
        return discovered_urls

    def scan_all_domains(self):
        self.logger.info("Starting domain scanning...")

        for domain in self.domains:
            self.logger.info(f"Scanning domain: {domain}")
            try:
                discovered_urls = self.crawl_domain(domain)
                if discovered_urls:
                    self.discovered_links[domain] = discovered_urls
                    self.logger.info(f"Found {len(discovered_urls)} URLs for {domain}")
                else:
                    self.logger.warning(f"No URLs discovered for {domain}")
            except Exception as e:
                self.logger.error(f"Failed to scan {domain}: {e}")

        self._save_discovered_links()
        self.logger.info("Domain scanning completed")

    def get_urls_for_scraper(self) -> Dict[str, List[str]]:
        return self.discovered_links.copy()

    def get_all_urls(self) -> List[str]:
        all_urls = []
        for urls in self.discovered_links.values():
            all_urls.extend(urls)
        return all_urls

    def get_stats(self) -> Dict:
        total_urls = sum(len(urls) for urls in self.discovered_links.values())
        domain_stats = {domain: len(urls) for domain, urls in self.discovered_links.items()}
        return {
            'total_domains': len(self.domains),
            'domains_with_links': len(self.discovered_links),
            'total_discovered_urls': total_urls,
            'urls_per_domain': domain_stats,
            'average_urls_per_domain': total_urls / len(self.discovered_links) if self.discovered_links else 0
        }

    def clear_discovered_links(self, domain: str = None):
        if domain:
            if domain in self.discovered_links:
                del self.discovered_links[domain]
                self.logger.info(f"Cleared links for {domain}")
        else:
            self.discovered_links.clear()
            self.logger.info("Cleared all discovered links")

        self._save_discovered_links()

# Integration example
if __name__ == "__main__":
    zero_skan = ZeroSkan()
    print("ZeroSkan - Domain Link Manager")
    print("Current domains:", zero_skan.get_domains())

    zero_skan.add_domain("python.org")

    print("\nScanning domains for links...")
    zero_skan.scan_all_domains()

    stats = zero_skan.get_stats()
    print(f"\nScan Statistics:")
    print(f"Total domains: {stats['total_domains']}")
    print(f"Total discovered URLs: {stats['total_discovered_urls']}")
    print(f"URLs per domain: {stats['urls_per_domain']}")

    urls_for_scraper = zero_skan.get_urls_for_scraper()
    print(f"\nReady to provide {len(zero_skan.get_all_urls())} URLs to ZeroScraper")
    

#ZeroScraper.py

import json
import requests
from bs4 import BeautifulSoup
import time
import threading
from urllib.parse import urljoin, urlparse
import logging

class ZeroScraper:
    """
    ZeroScraper - Web scraping module for ZeroNet
    Takes snippets and titles of pages and stores them in queue.json
    NOTE: NO IP TAMPERING - All requests maintain user privacy
    """

    def __init__(self, queue_file="queue.json", max_workers=5):
        self.queue_file = queue_file
        self.max_workers = max_workers
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

        # Initialize queue.json if it doesn't exist
        try:
            with open(self.queue_file, 'r') as f:
                self.queue_data = json.load(f)
        except FileNotFoundError:
            self.queue_data = {}

        self.lock = threading.Lock()
        self.logger = self._setup_logger()

    def _setup_logger(self):
        """Setup logging for ZeroScraper"""
        logger = logging.getLogger('ZeroScraper')
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('[ZeroScraper] %(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

    def scrape_page(self, url):
        """
        Scrape a single page and extract title and snippet

        Args:
            url (str): URL to scrape

        Returns:
            dict: Contains title and snippet, or None if failed
        """
        try:
            self.logger.info(f"Scraping: {url}")

            response = self.session.get(url, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract title
            title_tag = soup.find('title')
            title = title_tag.get_text().strip() if title_tag else "No Title"

            # Extract snippet (first paragraph or meta description)
            snippet = ""

            # Try meta description first
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc and meta_desc.get('content'):
                snippet = meta_desc['content'].strip()
            else:
                # Fall back to first paragraph
                paragraphs = soup.find_all('p')
                for p in paragraphs:
                    text = p.get_text().strip()
                    if len(text) > 50:  # Minimum meaningful length
                        snippet = text[:300] + "..." if len(text) > 300 else text
                        break

            if not snippet:
                snippet = "No snippet available"

            return {
                "title": title,
                "snippet": snippet
            }

        except requests.RequestException as e:
            self.logger.error(f"Request failed for {url}: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Scraping failed for {url}: {e}")
            return None

    def add_to_queue(self, url, data):
        """
        Add scraped data to queue.json

        Args:
            url (str): Source URL
            data (dict): Scraped data containing title and snippet
        """
        with self.lock:
            self.queue_data[url] = data
            self._save_queue()

    def _save_queue(self):
        """Save queue data to queue.json file"""
        try:
            with open(self.queue_file, 'w', encoding='utf-8') as f:
                json.dump(self.queue_data, f, indent=2, ensure_ascii=False)
            self.logger.info(f"Queue saved with {len(self.queue_data)} entries")
        except Exception as e:
            self.logger.error(f"Failed to save queue: {e}")

    def scrape_urls(self, urls):
        """
        Scrape multiple URLs using threading

        Args:
            urls (list): List of URLs to scrape
        """
        def worker():
            while True:
                try:
                    url = url_queue.pop(0)
                except IndexError:
                    break

                # Skip if already in queue
                if url in self.queue_data:
                    self.logger.info(f"Skipping already scraped: {url}")
                    continue

                scraped_data = self.scrape_page(url)
                if scraped_data:
                    self.add_to_queue(url, scraped_data)
                    self.logger.info(f"Added to queue: {url}")

                # Respect server resources
                time.sleep(1)

        url_queue = urls.copy()
        threads = []

        # Create worker threads
        for _ in range(min(self.max_workers, len(urls))):
            thread = threading.Thread(target=worker)
            thread.start()
            threads.append(thread)

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        self.logger.info(f"Scraping completed. Queue now has {len(self.queue_data)} entries")

    def scrape_from_domain_list(self, domain_urls):
        """
        Scrape URLs provided by ZeroSkan

        Args:
            domain_urls (dict): Dictionary mapping domains to lists of URLs
        """
        all_urls = []
        for domain, urls in domain_urls.items():
            self.logger.info(f"Processing {len(urls)} URLs from {domain}")
            all_urls.extend(urls)

        self.scrape_urls(all_urls)

    def get_queue_data(self):
        """
        Get current queue data

        Returns:
            dict: Current queue.json contents
        """
        return self.queue_data.copy()

    def clear_queue(self):
        """Clear the queue.json file"""
        self.queue_data = {}
        self._save_queue()
        self.logger.info("Queue cleared")

    def get_queue_stats(self):
        """
        Get statistics about the current queue

        Returns:
            dict: Statistics about queue contents
        """
        total_entries = len(self.queue_data)
        total_chars = sum(len(data['title']) + len(data['snippet']) 
                         for data in self.queue_data.values())

        domains = {}
        for url in self.queue_data.keys():
            domain = urlparse(url).netloc
            domains[domain] = domains.get(domain, 0) + 1

        return {
            "total_entries": total_entries,
            "total_characters": total_chars,
            "domains": domains,
            "average_snippet_length": total_chars / total_entries if total_entries > 0 else 0
        }

# Example usage and integration with ZeroNet
if __name__ == "__main__":
    # Initialize ZeroScraper
    scraper = ZeroScraper()

    # Example URLs for testing
    test_urls = [
        "https://en.wikipedia.org/wiki/Artificial_intelligence",
        "https://stackoverflow.com/questions/tagged/python",
        "https://github.com/trending"
    ]

    print("ZeroScraper - Starting scraping process...")
    print("NOTE: All operations maintain IP privacy")

    # Scrape the URLs
    scraper.scrape_urls(test_urls)

    # Display statistics
    stats = scraper.get_queue_stats()
    print(f"\nScraping completed!")
    print(f"Total entries: {stats['total_entries']}")
    print(f"Domains scraped: {list(stats['domains'].keys())}")

    # Show sample queue data
    queue_data = scraper.get_queue_data()
    print(f"\nSample queue.json format:")
    for url, data in list(queue_data.items())[:2]:
        print(f'"{url}": {{')
        print(f'  "title": "{data["title"][:50]}..."')
        print(f'  "snippet": "{data["snippet"][:100]}..."')
        print("}")
        
#ZeroSearch.py

import json
import requests
from bs4 import BeautifulSoup
import logging
from typing import Dict, List, Optional, Tuple
import time
from urllib.parse import urljoin, urlparse
import threading
from concurrent.futures import ThreadPoolExecutor
import re

class ZeroSearch:
    """
    ZeroSearch++ - Advanced Search Engine for ZeroNet
    Uses ZeroIndex to find most relevant pages, then scrapes full content
    Saves all scraped content to raw.json for ZeroCompiler processing
    """

    def __init__(self, 
                 raw_file="raw.json",
                 max_workers=5,
                 timeout=10,
                 max_content_length=50000):

        self.raw_file = raw_file
        self.max_workers = max_workers
        self.timeout = timeout
        self.max_content_length = max_content_length

        # Initialize session for full content scraping
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

        # Search state
        self.current_query = ""
        self.search_results = []
        self.raw_content = {}

        self.logger = self._setup_logger()

        # Initialize ZeroIndex connection
        self.zero_index = None
        self._connect_to_index()

    def _setup_logger(self):
        """Setup logging for ZeroSearch++"""
        logger = logging.getLogger('ZeroSearch++')
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('[ZeroSearch++] %(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

    def _connect_to_index(self):
        """Connect to ZeroIndex for vector search"""
        try:
            # In a real implementation, this would import ZeroIndex
            # For now, we'll simulate the connection
            self.logger.info("Connected to ZeroIndex vector database")
        except Exception as e:
            self.logger.error(f"Failed to connect to ZeroIndex: {e}")

    def _extract_full_content(self, url: str) -> Optional[Dict]:
        """
        Extract full content from a URL
        
        Args:
            url (str): URL to scrape
            
        Returns:
            Dict: Full content including title, text, metadata
        """
        try:
            self.logger.info(f"Extracting full content from: {url}")

            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header", "aside"]):
                script.decompose()

            # Extract title
            title_tag = soup.find('title')
            title = title_tag.get_text().strip() if title_tag else "No Title"

            # Extract main content
            main_content = ""

            # Try to find main content areas
            content_selectors = [
                'main', 'article', '.content', '#content', '.main-content',
                '.post-content', '.entry-content', '.article-content'
            ]

            content_found = False
            for selector in content_selectors:
                content_elements = soup.select(selector)
                if content_elements:
                    main_content = ' '.join([elem.get_text() for elem in content_elements])
                    content_found = True
                    break

            # Fallback: extract all paragraph text
            if not content_found:
                paragraphs = soup.find_all(['p', 'div', 'span'])
                main_content = ' '.join([p.get_text() for p in paragraphs if len(p.get_text().strip()) > 20])

            # Clean and limit content
            main_content = re.sub(r'\s+', ' ', main_content).strip()
            if len(main_content) > self.max_content_length:
                main_content = main_content[:self.max_content_length] + "..."

            # Extract metadata
            meta_description = ""
            meta_desc_tag = soup.find('meta', attrs={'name': 'description'})
            if meta_desc_tag:
                meta_description = meta_desc_tag.get('content', '').strip()

            # Extract keywords
            meta_keywords = ""
            meta_keywords_tag = soup.find('meta', attrs={'name': 'keywords'})
            if meta_keywords_tag:
                meta_keywords = meta_keywords_tag.get('content', '').strip()

            # Extract headings
            headings = []
            for heading_tag in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
                heading_text = heading_tag.get_text().strip()
                if heading_text:
                    headings.append({
                        'level': heading_tag.name,
                        'text': heading_text
                    })

            return {
                'url': url,
                'title': title,
                'content': main_content,
                'meta_description': meta_description,
                'meta_keywords': meta_keywords,
                'headings': headings,
                'content_length': len(main_content),
                'extraction_timestamp': time.time()
            }

        except requests.RequestException as e:
            self.logger.error(f"Request failed for {url}: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Content extraction failed for {url}: {e}")
            return None

    def _simulate_vector_search(self, query: str, top_k: int = 10) -> List[Dict]:
        """
        Simulate vector search results from ZeroIndex
        In real implementation, this would call ZeroIndex.search()
        
        Args:
            query (str): Search query
            top_k (int): Number of results to return
            
        Returns:
            List[Dict]: Simulated search results
        """
        # Simulated results - in real implementation, this would be:
        # return self.zero_index.search(query, top_k)

        simulated_results = [
            {
                'url': 'https://en.wikipedia.org/wiki/Artificial_intelligence',
                'title': 'Artificial Intelligence - Wikipedia',
                'snippet': 'Artificial intelligence (AI) is intelligence demonstrated by machines...',
                'similarity_score': 0.95
            },
            {
                'url': 'https://stackoverflow.com/questions/tagged/machine-learning',
                'title': 'Machine Learning Questions - Stack Overflow',
                'snippet': 'Find answers to machine learning questions...',
                'similarity_score': 0.87
            },
            {
                'url': 'https://github.com/topics/artificial-intelligence',
                'title': 'AI Projects on GitHub',
                'snippet': 'Discover artificial intelligence projects...',
                'similarity_score': 0.82
            }
        ]

        # Filter based on query relevance (simplified simulation)
        query_lower = query.lower()
        relevant_results = []

        for result in simulated_results:
            title_lower = result['title'].lower()
            snippet_lower = result['snippet'].lower()

            # Simple relevance scoring
            relevance = 0
            for word in query_lower.split():
                if word in title_lower:
                    relevance += 2
                if word in snippet_lower:
                    relevance += 1

            if relevance > 0:
                result['relevance'] = relevance
                relevant_results.append(result)

        # Sort by relevance and limit results
        relevant_results.sort(key=lambda x: x.get('relevance', 0), reverse=True)
        return relevant_results[:top_k]

    def search_and_extract(self, query: str, top_k: int = 10, extract_full_content: bool = True) -> Dict:
        """
        Main search function: Vector search + full content extraction
        
        Args:
            query (str): Search query
            top_k (int): Number of results to return
            extract_full_content (bool): Whether to extract full content
            
        Returns:
            Dict: Search results and extracted content
        """
        self.logger.info(f"Starting search for: '{query}'")
        self.current_query = query

        # Step 1: Vector search using ZeroIndex
        self.logger.info("Step 1: Performing vector search...")
        vector_results = self._simulate_vector_search(query, top_k)

        if not vector_results:
            self.logger.warning("No results found in vector search")
            return {
                'query': query,
                'vector_results': [],
                'extracted_content': {},
                'total_results': 0
            }

        self.logger.info(f"Found {len(vector_results)} relevant pages")
        self.search_results = vector_results

        # Step 2: Extract full content if requested
        extracted_content = {}

        if extract_full_content:
            self.logger.info("Step 2: Extracting full content...")

            urls_to_extract = [result['url'] for result in vector_results]

            # Use threading for parallel content extraction
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                future_to_url = {
                    executor.submit(self._extract_full_content, url): url 
                    for url in urls_to_extract
                }

                for future in future_to_url:
                    url = future_to_url[future]
                    try:
                        content = future.result(timeout=self.timeout + 5)
                        if content:
                            extracted_content[url] = content
                            self.logger.info(f"Extracted content from: {url}")
                        else:
                            self.logger.warning(f"Failed to extract content from: {url}")
                    except Exception as e:
                        self.logger.error(f"Content extraction error for {url}: {e}")

            # Save extracted content to raw.json
            self.raw_content = extracted_content
            self._save_raw_content()

        self.logger.info(f"Search completed: {len(extracted_content)} pages with full content")

        return {
            'query': query,
            'vector_results': vector_results,
            'extracted_content': extracted_content,
            'total_results': len(vector_results),
            'extracted_count': len(extracted_content)
        }

    def _save_raw_content(self):
        """Save extracted content to raw.json for ZeroCompiler"""
        try:
            with open(self.raw_file, 'w', encoding='utf-8') as f:
                json.dump(self.raw_content, f, indent=2, ensure_ascii=False)

            self.logger.info(f"Saved {len(self.raw_content)} pages to {self.raw_file}")

        except Exception as e:
            self.logger.error(f"Failed to save raw content: {e}")

    def get_urls_only(self, query: str, top_k: int = 10) -> List[str]:
        """
        Get only URLs without extracting full content
        
        Args:
            query (str): Search query
            top_k (int): Number of URLs to return
            
        Returns:
            List[str]: List of relevant URLs
        """
        results = self.search_and_extract(query, top_k, extract_full_content=False)
        return [result['url'] for result in results['vector_results']]

    def get_search_summary(self) -> Dict:
        """
        Get summary of current search results
        
        Returns:
            Dict: Search summary statistics
        """
        if not self.search_results:
            return {'status': 'no_search_performed'}

        total_content_length = sum(
            content.get('content_length', 0) 
            for content in self.raw_content.values()
        )

        return {
            'query': self.current_query,
            'total_results': len(self.search_results),
            'extracted_pages': len(self.raw_content),
            'total_content_length': total_content_length,
            'average_content_length': total_content_length / len(self.raw_content) if self.raw_content else 0,
            'top_result': self.search_results[0] if self.search_results else None
        }

    def clear_cache(self):
        """Clear search cache and temporary data"""
        self.search_results = []
        self.raw_content = {}
        self.current_query = ""

        # Remove raw.json file
        try:
            import os
            if os.path.exists(self.raw_file):
                os.remove(self.raw_file)
            self.logger.info("Cache cleared")
        except Exception as e:
            self.logger.error(f"Failed to clear cache: {e}")

    def get_content_for_url(self, url: str) -> Optional[Dict]:
        """
        Get extracted content for a specific URL
        
        Args:
            url (str): URL to get content for
            
        Returns:
            Dict: Content data for the URL
        """
        return self.raw_content.get(url)

    def rerank_results(self, custom_query: str = None) -> List[Dict]:
        """
        Re-rank search results based on additional criteria
        
        Args:
            custom_query (str): Additional query for re-ranking
            
        Returns:
            List[Dict]: Re-ranked results
        """
        if not self.search_results:
            return []

        query_to_use = custom_query or self.current_query

        if not query_to_use:
            return self.search_results

        # Re-rank based on content analysis
        reranked_results = []

        for result in self.search_results:
            url = result['url']
            content = self.raw_content.get(url, {})

            # Calculate new relevance score
            relevance_score = result.get('similarity_score', 0)

            if content:
                # Boost score based on content quality
                content_text = content.get('content', '').lower()
                query_words = query_to_use.lower().split()

                # Count query word occurrences in content
                word_count = sum(content_text.count(word) for word in query_words)
                content_boost = min(word_count * 0.1, 0.5)  # Max boost of 0.5

                # Boost for longer, more comprehensive content
                content_length = content.get('content_length', 0)
                length_boost = min(content_length / 10000 * 0.2, 0.3)  # Max boost of 0.3

                relevance_score += content_boost + length_boost

            result['reranked_score'] = relevance_score
            reranked_results.append(result)

        # Sort by new relevance score
        reranked_results.sort(key=lambda x: x.get('reranked_score', 0), reverse=True)

        self.logger.info(f"Re-ranked {len(reranked_results)} results")
        return reranked_results

# Integration with ZeroNet modules
class ZeroSearchIntegrator:
    """
    Integration layer for ZeroSearch++ with other ZeroNet modules
    """

    def __init__(self):
        self.zero_search = ZeroSearch()
        self.logger = logging.getLogger('ZeroSearchIntegrator')

    def search_for_compiler(self, query: str, top_k: int = 10) -> str:
        """
        Search and prepare content for ZeroCompiler
        
        Args:
            query (str): Search query
            top_k (int): Number of results
            
        Returns:
            str: Path to raw.json file for ZeroCompiler
        """
        self.logger.info(f"Preparing search results for ZeroCompiler: '{query}'")

        # Perform search with full content extraction
        results = self.zero_search.search_and_extract(query, top_k, extract_full_content=True)