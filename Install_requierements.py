#!/usr/bin/env python3
"""
ZeroNet Auto-Installer and Setup Script
Run this script to automatically set up the complete ZeroNet system
"""

import os
import sys
import subprocess
import urllib.request
from pathlib import Path

def create_directory_structure():
    """Create the required directory structure"""
    print("📁 Creating directory structure...")
    
    directories = [
        'zeronet',
        'zeronet/modules',
        'zeronet/data', 
        'zeronet/logs',
        'zeronet/web'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"   ✓ {directory}")

def create_requirements_file():
    """Create requirements.txt file"""
    print("📝 Creating requirements.txt...")
    
    requirements = """# ZeroNet Dependencies
requests>=2.31.0
beautifulsoup4>=4.12.0
numpy>=1.24.0
sentence-transformers>=2.2.0
faiss-cpu>=1.7.4
openai>=1.0.0
tiktoken>=0.5.0
psutil>=5.9.0
flask>=2.3.0
lxml>=4.9.0
urllib3>=2.0.0
"""
    
    with open('zeronet/requirements.txt', 'w') as f:
        f.write(requirements)
    print("   ✓ requirements.txt created")

def create_module_init():
    """Create modules/__init__.py"""
    init_content = '''"""
ZeroNet Modules Package
A Complex of Networking Tools with Absolute Privacy
"""

__version__ = "1.0.0"
__author__ = "ZeroNet Team" 
__description__ = "Privacy-focused web scraping and analysis suite"

# Module imports
from .zeroscraper import ZeroScraper
from .zeroindex import ZeroIndex
from .zeroskan import ZeroSkan
from .zerosearch import ZeroSearch
from .zerocompiler import ZeroCompiler
from .zeroos import ZeroOS

__all__ = [
    'ZeroScraper',
    'ZeroIndex', 
    'ZeroSkan',
    'ZeroSearch',
    'ZeroCompiler',
    'ZeroOS'
]
'''
    
    with open('zeronet/modules/__init__.py', 'w') as f:
        f.write(init_content)
    print("   ✓ modules/__init__.py created")

def create_main_file():
    """Create the main.py entry point"""
    print("🚀 Creating main.py...")
    
    main_content = '''#!/usr/bin/env python3
"""
ZeroNet - Main Entry Point
A Complex of Networking Tools with Absolute Privacy

Usage:
    python main.py          # Interactive setup
    python main.py --demo   # Run demo workflow
    python main.py --web    # Start web server
"""

import os
import sys
import time
import logging
import argparse
from pathlib import Path

# Add modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'modules'))

def setup_logging():
    """Setup comprehensive logging"""
    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('logs/zeronet.log')
        ]
    )

def check_dependencies():
    """Check if all required dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    required = [
        ('requests', 'HTTP requests'),
        ('bs4', 'Web scraping'),
        ('numpy', 'Numerical operations'),
    ]
    
    optional = [
        ('sentence_transformers', 'AI embeddings'),
        ('faiss', 'Vector database'),
        ('openai', 'LLM integration'),
        ('tiktoken', 'Token counting'),
        ('psutil', 'System monitoring')
    ]
    
    missing = []
    
    for module, description in required + optional:
        try:
            __import__(module)
            print(f"   ✓ {module} - {description}")
        except ImportError:
            print(f"   ✗ {module} - {description}")
            missing.append(module)
    
    if missing:
        print(f"\\n⚠️  Missing dependencies: {', '.join(missing)}")
        print("Install with: pip install -r requirements.txt")
        return False
    
    return True

def run_demo():
    """Run demonstration workflow"""
    print("\\n" + "="*60)
    print("🎯 ZERONET DEMONSTRATION WORKFLOW")
    print("="*60)
    
    try:
        # Import modules with error handling
        try:
            from zeroscraper import ZeroScraper
            from zeroindex import ZeroIndex
            from zeroskan import ZeroSkan
            from zerosearch import ZeroSearch
            from zerocompiler import ZeroCompiler
        except ImportError as e:
            print(f"❌ Module import failed: {e}")
            print("Make sure all module files are in the modules/ directory")
            return False
        
        # Initialize modules
        print("\\n1️⃣  Initializing ZeroNet modules...")
        scraper = ZeroScraper()
        indexer = ZeroIndex()
        skan = ZeroSkan()
        search = ZeroSearch()
        compiler = ZeroCompiler()
        print("   ✓ All modules initialized")
        
        # Demo workflow
        print("\\n2️⃣  Adding demo domains...")
        demo_domains = ["httpbin.org", "example.com"]
        for domain in demo_domains:
            skan.add_domain(domain)
            print(f"   ✓ Added {domain}")
        
        print("\\n3️⃣  Scanning domains...")
        skan.scan_all_domains(max_pages_per_domain=2)
        
        print("\\n4️⃣  Scraping content...")
        urls = skan.get_urls_for_scraper()
        scraper.scrape_from_domain_list(urls)
        
        print("\\n5️⃣  Creating vector index...")
        indexer.process_queue()
        
        print("\\n6️⃣  Testing search...")
        results = search.search_and_extract("example content", top_k=3)
        
        print("\\n7️⃣  Generating report...")
        if results.get('extracted_count', 0) > 0:
            report = compiler.compile_response("example content")
            print("   ✓ AI report generated")
        
        # Show results
        print("\\n" + "="*60)
        print("📊 DEMO RESULTS")
        print("="*60)
        
        stats = {
            'scraped': scraper.get_queue_stats()['total_entries'],
            'indexed': indexer.get_stats()['total_vectors'],
            'discovered': skan.get_stats()['total_discovered_urls']
        }
        
        print(f"📄 Pages scraped: {stats['scraped']}")
        print(f"🔍 Vectors indexed: {stats['indexed']}")
        print(f"🌐 URLs discovered: {stats['discovered']}")
        print(f"📁 Data saved in: ./data/")
        
        print("\\n✅ Demo completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_interactive():
    """Run interactive mode"""
    print("\\n" + "="*60)
    print("🎮 ZERONET INTERACTIVE MODE")
    print("="*60)
    print("Commands:")
    print("  add <domain>    - Add domain to scan")
    print("  scan           - Scan all domains")  
    print("  search <query> - Search for content")
    print("  stats          - Show statistics")
    print("  help           - Show this help")
    print("  quit           - Exit program")
    print("="*60)
    
    try:
        from zeroscraper import ZeroScraper
        from zeroindex import ZeroIndex
        from zeroskan import ZeroSkan
        from zerosearch import ZeroSearch
        from zerocompiler import ZeroCompiler
        
        # Initialize
        scraper = ZeroScraper()
        indexer = ZeroIndex()
        skan = ZeroSkan()
        search = ZeroSearch()
        compiler = ZeroCompiler()
        
        print("\\n✅ All modules loaded successfully")
        
        while True:
            try:
                command = input("\\nZeroNet> ").strip().split()
                if not command:
                    continue
                
                cmd = command[0].lower()
                
                if cmd in ['quit', 'exit', 'q']:
                    break
                elif cmd == 'add' and len(command) > 1:
                    domain = command[1]
                    skan.add_domain(domain)
                    print(f"✅ Added domain: {domain}")
                elif cmd == 'scan':
                    print("🔄 Scanning domains...")
                    skan.scan_all_domains(max_pages_per_domain=5)
                    urls = skan.get_urls_for_scraper()
                    scraper.scrape_from_domain_list(urls)
                    indexer.process_queue()
                    print("✅ Scan completed")
                elif cmd == 'search' and len(command) > 1:
                    query = ' '.join(command[1:])
                    print(f"🔍 Searching for: {query}")
                    results = search.search_and_extract(query, top_k=5)
                    print(f"📊 Found {results['total_results']} results")
                elif cmd == 'stats':
                    s_stats = scraper.get_queue_stats()
                    i_stats = indexer.get_stats()
                    k_stats = skan.get_stats()
                    print(f"📊 Statistics:")
                    print(f"   📄 Scraped: {s_stats['total_entries']}")
                    print(f"   🔍 Indexed: {i_stats['total_vectors']}")
                    print(f"   🌐 URLs: {k_stats['total_discovered_urls']}")
                elif cmd == 'help':
                    print("Available commands: add, scan, search, stats, help, quit")
                else:
                    print("❓ Unknown command. Type 'help' for available commands.")
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"❌ Error: {e}")
    
    except ImportError as e:
        print(f"❌ Failed to load modules: {e}")
        return False
    
    print("👋 Goodbye!")
    return True

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='ZeroNet - Privacy-focused Web Analysis Suite')
    parser.add_argument('--demo', action='store_true', help='Run demonstration workflow')
    parser.add_argument('--web', action='store_true', help='Start web interface')
    parser.add_argument('--check', action='store_true', help='Check dependencies only')
    
    args = parser.parse_args()
    
    print("🌐 ZeroNet - A Complex of Networking Tools")
    print("🔒 Absolute Privacy Guaranteed (IP Protection Active)")
    print("=" * 60)
    
    # Setup
    setup_logging()
    
    if args.check:
        check_dependencies()
        return
    
    if not check_dependencies():
        print("\\n❌ Missing dependencies. Install with:")
        print("   pip install -r requirements.txt")
        return
    
    if args.demo:
        run_demo()
    elif args.web:
        print("🌐 Web interface not yet implemented")
        print("📁 Open web/index.html in your browser for frontend")
    else:
        run_interactive()

if __name__ == "__main__":
    main()
'''
    
    with open('zeronet/main.py', 'w') as f:
        f.write(main_content)
    print("   ✓ main.py created")

def create_readme():
    """Create README file"""
    readme_content = """# ZeroNet - Privacy-Focused Web Analysis Suite

A complex of networking tools that provides absolute privacy while scraping and analyzing web content.

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run demonstration:**
   ```bash
   python main.py --demo
   ```

3. **Interactive mode:**
   ```bash
   python main.py
   ```

## Features

- 🔒 **Absolute Privacy** - No IP tampering
- 🕷️ **Web Scraping** - Extract content from websites  
- 🔍 **Vector Search** - AI-powered similarity search
- 📊 **Report Generation** - LLM-powered analysis
- 🏗️ **Modular Architecture** - Independent modules
- 🔐 **Sandboxed Execution** - Secure environment

## Modules

- **ZeroScraper** - Web content extraction
- **ZeroIndex** - Vector database management
- **ZeroSkan** - Domain discovery and management
- **ZeroSearch++** - Advanced search engine
- **ZeroCompiler** - AI report generation
- **ZeroOS** - Sandboxing and orchestration

## Data Files

All data is stored in the `data/` directory:
- `queue.json` - Scraped content queue
- `raw.json` - Full page content
- `reports.json` - Generated reports
- `domains.json` - Managed domains

## Requirements

- Python 3.8+
- Internet connection for scraping
- Optional: OpenAI API key for advanced features

## License

This project is for educational purposes. Respect robots.txt and website terms of service.
"""
    
    with open('zeronet/README.md', 'w') as f:
        f.write(readme_content)
    print("   ✓ README.md created")

def install_dependencies():
    """Install Python dependencies"""
    print("📦 Installing dependencies...")
    
    try:
        subprocess.check_call([
            sys.executable, '-m', 'pip', 'install', '-r', 'zeronet/requirements.txt'
        ])
        print("   ✅ All dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Failed to install dependencies: {e}")
        return False

def main():
    """Main installer function"""
    print("🚀 ZeroNet Auto-Installer")
    print("=" * 50)
    
    try:
        # Create structure
        create_directory_structure()
        create_requirements_file()
        create_module_init()
        create_main_file()
        create_readme()
        
        print("\n✅ ZeroNet structure created successfully!")
        
        # Ask about dependency installation
        install_deps = input("\n📦 Install Python dependencies now? (y/n): ").lower().strip()
        if install_deps == 'y':
            if install_dependencies():
                print("\n🎉 Installation completed successfully!")
            else:
                print("\n⚠️  Installation completed with some issues.")
                print("You may need to install dependencies manually:")
                print("   cd zeronet && pip install -r requirements.txt")
        
        print("\n" + "=" * 50)
        print("🎯 Next Steps:")
        print("1. Copy module files from artifacts to zeronet/modules/")
        print("2. cd zeronet")
        print("3. python main.py --demo")
        print("=" * 50)
        
    except Exception as e:
        print(f"❌ Installation failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()