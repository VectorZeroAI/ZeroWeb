import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
import time
import json
import os
import psutil
import logging
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import webbrowser

class ZeroNetGUI:
    def __init__(self, root, core):
        self.root = root
        self.core = core
        self.root.title("ZeroNet - Privacy-Focused Web Analysis Suite")
        self.root.geometry("1200x800")
        self.root.configure(bg="#f0f0f0")
        
        # Configure styles
        self.style = ttk.Style()
        self.style.configure("TNotebook.Tab", font=("Segoe UI", 10, "bold"), padding=[10, 5])
        self.style.configure("TButton", font=("Segoe UI", 10), padding=6)
        self.style.configure("TLabel", font=("Segoe UI", 10))
        self.style.configure("TFrame", background="#f0f0f0")
        self.style.configure("Header.TLabel", font=("Segoe UI", 14, "bold"))
        
        # Create main layout
        self.create_header()
        self.create_tabs()
        self.create_status_bar()
        
        # Initialize data
        self.domains = []
        self.search_results = []
        self.stats_data = {
            "cpu": [], "memory": [], "disk": [], "time": []
        }
        
        # Start background monitoring
        self.running = True
        self.monitor_thread = threading.Thread(target=self.monitor_resources, daemon=True)
        self.monitor_thread.start()
        
        # Load initial data
        self.load_domains()
    
    def create_header(self):
        """Create the header section with logo and status"""
        header_frame = ttk.Frame(self.root, padding=10)
        header_frame.pack(fill="x", padx=10, pady=5)
        
        # Logo and title
        logo_label = ttk.Label(header_frame, text="🌐 ZeroNet", font=("Segoe UI", 20, "bold"))
        logo_label.pack(side="left")
        
        # Status indicators
        status_frame = ttk.Frame(header_frame)
        status_frame.pack(side="right", fill="y")
        
        privacy_status = ttk.Label(status_frame, text="🔒 Privacy Active", foreground="green")
        privacy_status.pack(anchor="e")
        
        sandbox_status = ttk.Label(status_frame, text="🛡️ Sandbox Active", foreground="blue")
        sandbox_status.pack(anchor="e")
        
        # System stats
        self.cpu_label = ttk.Label(status_frame, text="CPU: 0%")
        self.cpu_label.pack(anchor="e")
        self.mem_label = ttk.Label(status_frame, text="Memory: 0%")
        self.mem_label.pack(anchor="e")
    
    def create_tabs(self):
        """Create the tabbed interface"""
        tab_control = ttk.Notebook(self.root)
        tab_control.pack(expand=True, fill="both", padx=10, pady=(0, 5))
        
        # Create tabs
        self.search_tab = self.create_search_tab(tab_control)
        self.index_tab = self.create_index_tab(tab_control)
        self.domains_tab = self.create_domains_tab(tab_control)
        self.stats_tab = self.create_stats_tab(tab_control)
        self.settings_tab = self.create_settings_tab(tab_control)
        
        # Add tabs to notebook
        tab_control.add(self.search_tab, text="🔍 Search")
        tab_control.add(self.index_tab, text="📊 Index")
        tab_control.add(self.domains_tab, text="🌐 Domains")
        tab_control.add(self.stats_tab, text="📈 Statistics")
        tab_control.add(self.settings_tab, text="⚙️ Settings")
    
    def create_search_tab(self, parent):
        """Create the search interface"""
        tab = ttk.Frame(parent, padding=10)
        
        # Search input
        search_frame = ttk.Frame(tab)
        search_frame.pack(fill="x", pady=5)
        
        ttk.Label(search_frame, text="Search Query:").pack(side="left", padx=(0, 10))
        self.search_entry = ttk.Entry(search_frame, width=50)
        self.search_entry.pack(side="left", fill="x", expand=True)
        self.search_entry.bind("<Return>", lambda e: self.start_search())
        
        search_btn = ttk.Button(search_frame, text="Search", command=self.start_search)
        search_btn.pack(side="left", padx=10)
        
        # AI mode toggle
        ai_frame = ttk.Frame(tab)
        ai_frame.pack(fill="x", pady=5)
        
        self.ai_var = tk.BooleanVar(value=True)
        ai_toggle = ttk.Checkbutton(
            ai_frame, text="AI-Powered Results", 
            variable=self.ai_var, command=self.toggle_ai_mode
        )
        ai_toggle.pack(side="left")
        
        # Results display
        results_frame = ttk.LabelFrame(tab, text="Search Results", padding=10)
        results_frame.pack(fill="both", expand=True, pady=10)
        
        self.results_tree = ttk.Treeview(
            results_frame, 
            columns=("title", "url", "score"), 
            show="headings", 
            selectmode="browse"
        )
        
        # Configure columns
        self.results_tree.heading("title", text="Title", anchor="w")
        self.results_tree.heading("url", text="URL", anchor="w")
        self.results_tree.heading("score", text="Score", anchor="center")
        self.results_tree.column("title", width=300, stretch=True)
        self.results_tree.column("url", width=400, stretch=True)
        self.results_tree.column("score", width=80, anchor="center")
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(results_frame, orient="vertical", command=self.results_tree.yview)
        self.results_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.results_tree.pack(fill="both", expand=True)
        
        # Bind selection event
        self.results_tree.bind("<<TreeviewSelect>>", self.show_result_details)
        
        # Result details
        details_frame = ttk.LabelFrame(tab, text="Result Details", padding=10)
        details_frame.pack(fill="x", pady=10)
        
        self.details_text = scrolledtext.ScrolledText(
            details_frame, wrap=tk.WORD, height=8
        )
        self.details_text.pack(fill="both", expand=True)
        self.details_text.config(state=tk.DISABLED)
        
        return tab
    
    def create_index_tab(self, parent):
        """Create the indexing interface"""
        tab = ttk.Frame(parent, padding=10)
        
        # Indexing controls
        ctrl_frame = ttk.Frame(tab)
        ctrl_frame.pack(fill="x", pady=5)
        
        ttk.Button(ctrl_frame, text="Start Indexing", command=self.start_indexing).pack(side="left", padx=5)
        ttk.Button(ctrl_frame, text="Pause Indexing", command=self.pause_indexing).pack(side="left", padx=5)
        ttk.Button(ctrl_frame, text="Stop Indexing", command=self.stop_indexing).pack(side="left", padx=5)
        
        # Progress and stats
        stats_frame = ttk.LabelFrame(tab, text="Indexing Progress", padding=10)
        stats_frame.pack(fill="x", pady=10)
        
        # Progress bar
        ttk.Label(stats_frame, text="Overall Progress:").pack(anchor="w")
        self.progress_bar = ttk.Progressbar(stats_frame, orient="horizontal", length=600, mode="determinate")
        self.progress_bar.pack(fill="x", pady=5)
        
        # Stats grid
        stats_grid = ttk.Frame(stats_frame)
        stats_grid.pack(fill="x", pady=5)
        
        # Column 1
        col1 = ttk.Frame(stats_grid)
        col1.pack(side="left", fill="both", expand=True, padx=5)
        
        ttk.Label(col1, text="Domains Indexed:").pack(anchor="w")
        self.domains_indexed = ttk.Label(col1, text="0")
        self.domains_indexed.pack(anchor="w")
        
        ttk.Label(col1, text="Pages Scraped:").pack(anchor="w", pady=(10, 0))
        self.pages_scraped = ttk.Label(col1, text="0")
        self.pages_scraped.pack(anchor="w")
        
        # Column 2
        col2 = ttk.Frame(stats_grid)
        col2.pack(side="left", fill="both", expand=True, padx=5)
        
        ttk.Label(col2, text="URLs Discovered:").pack(anchor="w")
        self.urls_discovered = ttk.Label(col2, text="0")
        self.urls_discovered.pack(anchor="w")
        
        ttk.Label(col2, text="Vectors Created:").pack(anchor="w", pady=(10, 0))
        self.vectors_created = ttk.Label(col2, text="0")
        self.vectors_created.pack(anchor="w")
        
        # Column 3
        col3 = ttk.Frame(stats_grid)
        col3.pack(side="left", fill="both", expand=True, padx=5)
        
        ttk.Label(col3, text="Current Domain:").pack(anchor="w")
        self.current_domain = ttk.Label(col3, text="None")
        self.current_domain.pack(anchor="w")
        
        ttk.Label(col3, text="Current URL:").pack(anchor="w", pady=(10, 0))
        self.current_url = ttk.Label(col3, text="None")
        self.current_url.pack(anchor="w")
        
        # Log display
        log_frame = ttk.LabelFrame(tab, text="Indexing Log", padding=10)
        log_frame.pack(fill="both", expand=True, pady=10)
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame, wrap=tk.WORD, height=10
        )
        self.log_text.pack(fill="both", expand=True)
        self.log_text.config(state=tk.DISABLED)
        
        return tab
    
    def create_domains_tab(self, parent):
        """Create the domain management interface"""
        tab = ttk.Frame(parent, padding=10)
        
        # Domain controls
        ctrl_frame = ttk.Frame(tab)
        ctrl_frame.pack(fill="x", pady=5)
        
        ttk.Label(ctrl_frame, text="Domain:").pack(side="left", padx=(0, 10))
        self.domain_entry = ttk.Entry(ctrl_frame, width=40)
        self.domain_entry.pack(side="left", fill="x", expand=True)
        
        ttk.Button(ctrl_frame, text="Add Domain", command=self.add_domain).pack(side="left", padx=5)
        ttk.Button(ctrl_frame, text="Remove Selected", command=self.remove_domain).pack(side="left", padx=5)
        ttk.Button(ctrl_frame, text="Import from File", command=self.import_domains).pack(side="left", padx=5)
        ttk.Button(ctrl_frame, text="Export to File", command=self.export_domains).pack(side="left", padx=5)
        
        # Domain list
        list_frame = ttk.LabelFrame(tab, text="Managed Domains", padding=10)
        list_frame.pack(fill="both", expand=True, pady=10)
        
        self.domain_list = tk.Listbox(
            list_frame, 
            selectmode=tk.SINGLE,
            font=("Segoe UI", 10)
        )
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.domain_list.yview)
        self.domain_list.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.domain_list.pack(fill="both", expand=True)
        
        # Domain stats
        stats_frame = ttk.Frame(tab)
        stats_frame.pack(fill="x", pady=5)
        
        ttk.Label(stats_frame, text="Total Domains:").pack(side="left", padx=(0, 10))
        self.total_domains = ttk.Label(stats_frame, text="0")
        self.total_domains.pack(side="left", padx=(0, 20))
        
        ttk.Label(stats_frame, text="Total URLs Discovered:").pack(side="left", padx=(0, 10))
        self.total_urls = ttk.Label(stats_frame, text="0")
        self.total_urls.pack(side="left")
        
        return tab
    
    def create_stats_tab(self, parent):
        """Create the statistics and monitoring interface"""
        tab = ttk.Frame(parent, padding=10)
        
        # Create notebook for different stats views
        stats_notebook = ttk.Notebook(tab)
        stats_notebook.pack(fill="both", expand=True)
        
        # System Stats tab
        sys_tab = ttk.Frame(stats_notebook, padding=10)
        stats_notebook.add(sys_tab, text="System Performance")
        
        # Create figures
        fig_frame = ttk.Frame(sys_tab)
        fig_frame.pack(fill="both", expand=True)
        
        # CPU Usage
        cpu_frame = ttk.LabelFrame(fig_frame, text="CPU Usage")
        cpu_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        
        self.cpu_fig, self.cpu_ax = plt.subplots(figsize=(5, 3))
        self.cpu_ax.set_title("CPU Utilization")
        self.cpu_ax.set_ylim(0, 100)
        self.cpu_line, = self.cpu_ax.plot([], [], 'r-')
        self.cpu_canvas = FigureCanvasTkAgg(self.cpu_fig, master=cpu_frame)
        self.cpu_canvas.get_tk_widget().pack(fill="both", expand=True)
        
        # Memory Usage
        mem_frame = ttk.LabelFrame(fig_frame, text="Memory Usage")
        mem_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        
        self.mem_fig, self.mem_ax = plt.subplots(figsize=(5, 3))
        self.mem_ax.set_title("Memory Utilization")
        self.mem_ax.set_ylim(0, 100)
        self.mem_line, = self.mem_ax.plot([], [], 'b-')
        self.mem_canvas = FigureCanvasTkAgg(self.mem_fig, master=mem_frame)
        self.mem_canvas.get_tk_widget().pack(fill="both", expand=True)
        
        # Module Stats tab
        mod_tab = ttk.Frame(stats_notebook, padding=10)
        stats_notebook.add(mod_tab, text="Module Performance")
        
        # Module stats treeview
        mod_frame = ttk.LabelFrame(mod_tab, text="Module Statistics")
        mod_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.mod_tree = ttk.Treeview(
            mod_frame, 
            columns=("module", "status", "memory", "cpu", "activity"), 
            show="headings"
        )
        
        # Configure columns
        self.mod_tree.heading("module", text="Module", anchor="w")
        self.mod_tree.heading("status", text="Status", anchor="w")
        self.mod_tree.heading("memory", text="Memory (MB)", anchor="center")
        self.mod_tree.heading("cpu", text="CPU (%)", anchor="center")
        self.mod_tree.heading("activity", text="Last Activity", anchor="w")
        
        self.mod_tree.column("module", width=150)
        self.mod_tree.column("status", width=100)
        self.mod_tree.column("memory", width=100, anchor="center")
        self.mod_tree.column("cpu", width=80, anchor="center")
        self.mod_tree.column("activity", width=150)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(mod_frame, orient="vertical", command=self.mod_tree.yview)
        self.mod_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.mod_tree.pack(fill="both", expand=True)
        
        # Populate with modules
        modules = ["ZeroScraper", "ZeroIndex", "ZeroSkan", "ZeroSearch", "ZeroCompiler", "ZeroOS"]
        for mod in modules:
            self.mod_tree.insert("", "end", values=(mod, "Inactive", "0", "0", "Never"))
        
        # Data Stats tab
        data_tab = ttk.Frame(stats_notebook, padding=10)
        stats_notebook.add(data_tab, text="Data Statistics")
        
        # Data stats
        data_frame = ttk.LabelFrame(data_tab, text="Data Metrics")
        data_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Create a grid of metrics
        metrics = [
            ("Domains Managed", "0"),
            ("URLs Discovered", "0"),
            ("Pages Scraped", "0"),
            ("Vectors Indexed", "0"),
            ("Search Queries", "0"),
            ("AI Reports", "0")
        ]
        
        for i, (label, value) in enumerate(metrics):
            row = i // 3
            col = i % 3
            
            frame = ttk.Frame(data_frame)
            frame.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            
            ttk.Label(frame, text=label, font=("Segoe UI", 10)).pack()
            metric_label = ttk.Label(frame, text=value, font=("Segoe UI", 14, "bold"))
            metric_label.pack(pady=(5, 0))
            
            # Store reference for updating
            setattr(self, f"data_{label.lower().replace(' ', '_')}", metric_label)
        
        # Configure grid
        for i in range(3):
            data_frame.columnconfigure(i, weight=1)
        for i in range(2):
            data_frame.rowconfigure(i, weight=1)
        
        return tab
    
    def create_settings_tab(self, parent):
        """Create the settings interface"""
        tab = ttk.Frame(parent, padding=10)
        
        # General settings
        gen_frame = ttk.LabelFrame(tab, text="General Settings", padding=10)
        gen_frame.pack(fill="x", pady=5)
        
        # Privacy settings
        ttk.Label(gen_frame, text="Privacy Mode:").grid(row=0, column=0, sticky="w", pady=2)
        self.privacy_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(gen_frame, variable=self.privacy_var).grid(row=0, column=1, sticky="w", pady=2)
        
        ttk.Label(gen_frame, text="Sandbox Mode:").grid(row=1, column=0, sticky="w", pady=2)
        self.sandbox_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(gen_frame, variable=self.sandbox_var).grid(row=1, column=1, sticky="w", pady=2)
        
        # Performance settings
        perf_frame = ttk.LabelFrame(tab, text="Performance Settings", padding=10)
        perf_frame.pack(fill="x", pady=5)
        
        ttk.Label(perf_frame, text="Max Threads:").grid(row=0, column=0, sticky="w", pady=2)
        self.threads_var = tk.StringVar(value="5")
        ttk.Spinbox(
            perf_frame, from_=1, to=20, width=5,
            textvariable=self.threads_var
        ).grid(row=0, column=1, sticky="w", pady=2)
        
        ttk.Label(perf_frame, text="Max Pages per Domain:").grid(row=1, column=0, sticky="w", pady=2)
        self.pages_var = tk.StringVar(value="50")
        ttk.Spinbox(
            perf_frame, from_=1, to=500, width=5,
            textvariable=self.pages_var
        ).grid(row=1, column=1, sticky="w", pady=2)
        
        # AI Settings
        ai_frame = ttk.LabelFrame(tab, text="AI Settings", padding=10)
        ai_frame.pack(fill="x", pady=5)
        
        ttk.Label(ai_frame, text="AI Model:").grid(row=0, column=0, sticky="w", pady=2)
        models = ["meta-llama/llama-4-maverick:free", "gpt-3.5-turbo", "gpt-4"]
        self.model_var = tk.StringVar(value=models[0])
        ttk.Combobox(
            ai_frame, textvariable=self.model_var,
            values=models, state="readonly", width=30
        ).grid(row=0, column=1, sticky="w", pady=2)
        
        ttk.Label(ai_frame, text="API Key:").grid(row=1, column=0, sticky="w", pady=2)
        self.api_entry = ttk.Entry(ai_frame, width=40, show="*")
        self.api_entry.grid(row=1, column=1, sticky="we", pady=2)
        
        # Buttons
        btn_frame = ttk.Frame(tab)
        btn_frame.pack(fill="x", pady=10)
        
        ttk.Button(btn_frame, text="Save Settings", command=self.save_settings).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Reset to Defaults", command=self.reset_settings).pack(side="left", padx=5)
        
        return tab
    
    def create_status_bar(self):
        """Create the status bar at the bottom"""
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(
            self.root, textvariable=self.status_var,
            relief="sunken", anchor="w", padding=(10, 5)
        )
        status_bar.pack(side="bottom", fill="x")
    
    def monitor_resources(self):
        """Background thread to monitor system resources"""
        while self.running:
            # Get system stats
            cpu = psutil.cpu_percent()
            mem = psutil.virtual_memory().percent
            
            # Update labels
            self.cpu_label.config(text=f"CPU: {cpu:.1f}%")
            self.mem_label.config(text=f"Memory: {mem:.1f}%")
            
            # Update stats data
            now = datetime.now().strftime("%H:%M:%S")
            self.stats_data["cpu"].append(cpu)
            self.stats_data["memory"].append(mem)
            self.stats_data["time"].append(now)
            
            # Keep only last 60 data points
            for key in ["cpu", "memory"]:
                if len(self.stats_data[key]) > 60:
                    self.stats_data[key] = self.stats_data[key][-60:]
            
            if len(self.stats_data["time"]) > 60:
                self.stats_data["time"] = self.stats_data["time"][-60:]
            
            # Update charts
            self.update_charts()
            
            # Sleep before next update
            time.sleep(2)
    
    def update_charts(self):
        """Update the performance charts"""
        if not self.stats_data["time"]:
            return
        
        # Update CPU chart
        self.cpu_line.set_data(range(len(self.stats_data["cpu"])), self.stats_data["cpu"])
        self.cpu_ax.set_xlim(0, len(self.stats_data["cpu"]))
        self.cpu_ax.set_xticks([])
        self.cpu_canvas.draw()
        
        # Update Memory chart
        self.mem_line.set_data(range(len(self.stats_data["memory"])), self.stats_data["memory"])
        self.mem_ax.set_xlim(0, len(self.stats_data["memory"]))
        self.mem_ax.set_xticks([])
        self.mem_canvas.draw()
    
    def load_domains(self):
        """Load domains from file"""
        try:
            with open("domains.json", "r") as f:
                self.domains = json.load(f)
                self.update_domain_list()
        except FileNotFoundError:
            self.domains = ["wikipedia.org", "github.com", "stackoverflow.com"]
            self.update_domain_list()
    
    def update_domain_list(self):
        """Update the domain list display"""
        self.domain_list.delete(0, tk.END)
        for domain in self.domains:
            self.domain_list.insert(tk.END, domain)
        self.total_domains.config(text=str(len(self.domains)))
    
    def add_domain(self):
        """Add a new domain"""
        domain = self.domain_entry.get().strip()
        if domain:
            if domain not in self.domains:
                self.domains.append(domain)
                self.update_domain_list()
                self.status_var.set(f"Added domain: {domain}")
            else:
                self.status_var.set("Domain already exists")
        else:
            self.status_var.set("Please enter a domain")
    
    def remove_domain(self):
        """Remove selected domain"""
        selection = self.domain_list.curselection()
        if selection:
            domain = self.domain_list.get(selection[0])
            self.domains.remove(domain)
            self.update_domain_list()
            self.status_var.set(f"Removed domain: {domain}")
    
    def import_domains(self):
        """Import domains from a file"""
        filepath = filedialog.askopenfilename(
            title="Import Domains",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if filepath:
            try:
                with open(filepath, "r") as f:
                    new_domains = [line.strip() for line in f.readlines()]
                    self.domains.extend(new_domains)
                    self.update_domain_list()
                    self.status_var.set(f"Imported {len(new_domains)} domains")
            except Exception as e:
                messagebox.showerror("Import Error", f"Failed to import domains: {str(e)}")
    
    def export_domains(self):
        """Export domains to a file"""
        filepath = filedialog.asksaveasfilename(
            title="Export Domains",
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if filepath:
            try:
                with open(filepath, "w") as f:
                    f.write("\n".join(self.domains))
                self.status_var.set(f"Exported {len(self.domains)} domains")
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export domains: {str(e)}")
    
    def toggle_ai_mode(self):
        """Toggle AI-powered results"""
        if self.ai_var.get():
            self.status_var.set("AI-powered results enabled")
        else:
            self.status_var.set("AI-powered results disabled")
    
    def start_search(self):
        """Start a search operation"""
        query = self.search_entry.get().strip()
        if not query:
            self.status_var.set("Please enter a search query")
            return
            
        self.status_var.set(f"Searching for: {query}")
        self.results_tree.delete(*self.results_tree.get_children())
        self.details_text.config(state=tk.NORMAL)
        self.details_text.delete(1.0, tk.END)
        self.details_text.config(state=tk.DISABLED)
        
        # In a real implementation, this would call the search module
        # For now, we'll simulate results
        threading.Thread(target=self.simulate_search, args=(query,), daemon=True).start()
    
    def simulate_search(self, query):
        """Simulate search operation with progress"""
        # Simulate search delay
        for i in range(5):
            time.sleep(0.5)
            self.status_var.set(f"Searching... {i+1}/5")
        
        # Generate fake results
        results = []
        for i in range(10):
            results.append({
                "title": f"Result {i+1} about {query}",
                "url": f"https://example.com/{query.replace(' ', '_')}_{i+1}",
                "score": f"{90 - i*5:.1f}",
                "content": f"This is a detailed result about {query}. " * 10
            })
        
        # Update results in the GUI
        self.search_results = results
        self.root.after(0, self.display_search_results, results)
        self.status_var.set(f"Found {len(results)} results for '{query}'")
    
    def display_search_results(self, results):
        """Display search results in the treeview"""
        for result in results:
            self.results_tree.insert("", "end", values=(
                result["title"], result["url"], result["score"]
            ))
    
    def show_result_details(self, event):
        """Show details for the selected search result"""
        selection = self.results_tree.selection()
        if not selection:
            return
            
        item = self.results_tree.item(selection[0])
        index = self.results_tree.index(selection[0])
        
        if index < len(self.search_results):
            result = self.search_results[index]
            self.details_text.config(state=tk.NORMAL)
            self.details_text.delete(1.0, tk.END)
            self.details_text.insert(tk.END, f"Title: {result['title']}\n")
            self.details_text.insert(tk.END, f"URL: {result['url']}\n")
            self.details_text.insert(tk.END, f"Score: {result['score']}\n\n")
            self.details_text.insert(tk.END, result["content"])
            self.details_text.config(state=tk.DISABLED)
    
    def start_indexing(self):
        """Start indexing operation"""
        if not self.domains:
            self.status_var.set("No domains to index. Add domains first.")
            return
            
        self.status_var.set("Starting indexing process...")
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)
        
        # In a real implementation, this would call the indexing module
        threading.Thread(target=self.simulate_indexing, daemon=True).start()
    
    def simulate_indexing(self):
        """Simulate indexing operation with progress"""
        total_domains = len(self.domains)
        total_pages = 0
        total_urls = 0
        total_vectors = 0
        
        # Reset progress
        self.root.after(0, self.progress_bar.config, {"value": 0})
        self.root.after(0, self.domains_indexed.config, {"text": "0"})
        self.root.after(0, self.pages_scraped.config, {"text": "0"})
        self.root.after(0, self.urls_discovered.config, {"text": "0"})
        self.root.after(0, self.vectors_created.config, {"text": "0"})
        
        for i, domain in enumerate(self.domains):
            self.root.after(0, self.current_domain.config, {"text": domain})
            self.root.after(0, self.log_message, f"Processing domain: {domain}")
            
            # Update domain progress
            progress = (i / total_domains) * 100
            self.root.after(0, self.progress_bar.config, {"value": progress})
            self.root.after(0, self.domains_indexed.config, {"text": str(i+1)})
            
            # Simulate domain processing
            for j in range(5):
                time.sleep(0.5)
                self.root.after(0, self.log_message, f"  Discovered {j+1} pages")
                self.root.after(0, self.current_url.config, {"text": f"https://{domain}/page_{j+1}"})
                
                # Update counts
                total_urls += 1
                total_pages += 1
                self.root.after(0, self.urls_discovered.config, {"text": str(total_urls)})
                self.root.after(0, self.pages_scraped.config, {"text": str(total_pages)})
            
            # Simulate vector creation
            time.sleep(1)
            total_vectors += 5
            self.root.after(0, self.log_message, f"  Created 5 vector embeddings")
            self.root.after(0, self.vectors_created.config, {"text": str(total_vectors)})
        
        # Complete progress
        self.root.after(0, self.progress_bar.config, {"value": 100})
        self.root.after(0, self.log_message, "Indexing completed successfully!")
        self.root.after(0, self.current_domain.config, {"text": "None"})
        self.root.after(0, self.current_url.config, {"text": "None"})
        self.status_var.set("Indexing completed successfully!")
    
    def log_message(self, message):
        """Add a message to the log display"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
    
    def pause_indexing(self):
        """Pause indexing operation"""
        self.status_var.set("Indexing paused")
    
    def stop_indexing(self):
        """Stop indexing operation"""
        self.status_var.set("Indexing stopped")
    
    def save_settings(self):
        """Save application settings"""
        self.status_var.set("Settings saved successfully")
        # In a real implementation, this would save to a config file
    
    def reset_settings(self):
        """Reset settings to defaults"""
        self.privacy_var.set(True)
        self.sandbox_var.set(True)
        self.threads_var.set("5")
        self.pages_var.set("50")
        self.model_var.set("meta-llama/llama-4-maverick:free")
        self.api_entry.delete(0, tk.END)
        self.status_var.set("Settings reset to defaults")
    
    def on_close(self):
        """Handle application close"""
        self.running = False
        self.root.destroy()


# Usage example
if __name__ == "__main__":
    # In a real implementation, this would initialize your ZeroNet core
    # For demonstration, we'll create a dummy core
    class DummyCore:
        pass
    
    root = tk.Tk()
    app = ZeroNetGUI(root, DummyCore())
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()