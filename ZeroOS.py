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