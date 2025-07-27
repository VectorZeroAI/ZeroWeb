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

