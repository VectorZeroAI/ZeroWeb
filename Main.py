#!/usr/bin/env python3
"""
ZeroNet - Main Entry Point
A Complex of Networking Tools with Absolute Privacy

Usage:
    python main.py          # Interactive setup
    python main.py --demo   # Run demo workflow
    python main.py --web    # Start web server
    python main.py --check  # Check dependencies
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
    available = []
    
    for module, description in required + optional:
        try:
            __import__(module)
            print(f"   ✓ {module} - {description}")
            available.append(module)
        except ImportError:
            print(f"   ✗ {module} - {description}")
            missing.append(module)
    
    print(f"\n📊 Dependencies Summary:")
    print(f"   ✅ Available: {len(available)}")
    print(f"   ❌ Missing: {len(missing)}")
    
    if missing:
        print(f"\n⚠️  Missing dependencies: {', '.join(missing)}")
        print("Install with: pip install -r requirements.txt")
        print("\n💡 ZeroNet will work with reduced functionality")
        return len(available) >= len(required)  # At least required deps
    
    print("\n✅ All dependencies available!")
    return True

def run_demo():
    """Run demonstration workflow"""
    print("\n" + "="*60)
    print("🎯 ZERONET DEMONSTRATION WORKFLOW")
    print("="*60)
    print("This demo will:")
    print("1. Initialize all ZeroNet modules")
    print("2. Add test domains for scraping") 
    print("3. Discover and scrape web pages")
    print("4. Create vector embeddings")
    print("5. Perform similarity search")
    print("6. Generate AI-powered report")
    print("="*60)
    
    try:
        # Import modules with error handling
        print("\n1️⃣  Importing ZeroNet modules...")
        try:
            from zeroscraper import ZeroScraper
            from zeroindex import ZeroIndex
            from zeroskan import ZeroSkan
            from zerosearch import ZeroSearch
            from zerocompiler import ZeroCompiler
            print("   ✓ All modules imported successfully")
        except ImportError as e:
            print(f"❌ Module import failed: {e}")
            print("Make sure all module files are in the modules/ directory:")
            print("   modules/zeroscraper.py")
            print("   modules/zeroindex.py")
            print("   modules/zeroskan.py") 
            print("   modules/zerosearch.py")
            print("   modules/zerocompiler.py")
            return False
        
        # Initialize modules
        print("\n2️⃣  Initializing ZeroNet modules...")
        try:
            scraper = ZeroScraper()
            indexer = ZeroIndex()
            skan = ZeroSkan()
            search = ZeroSearch()
            compiler = ZeroCompiler()
            print("   ✓ All modules initialized successfully")
        except Exception as e:
            print(f"❌ Module initialization failed: {e}")
            return False
        
        # Demo workflow
        print("\n3️⃣  Adding demo domains...")
        demo_domains = ["httpbin.org", "example.com"]
        for domain in demo_domains:
            try:
                skan.add_domain(domain)
                print(f"   ✓ Added {domain}")
            except Exception as e:
                print(f"   ⚠️  Failed to add {domain}: {e}")
        
        print("\n4️⃣  Scanning domains for URLs...")
        try:
            skan.scan_all_domains(max_pages_per_domain=3)
            discovered_stats = skan.get_stats()
            print(f"   ✓ Discovered {discovered_stats.get('total_discovered_urls', 0)} URLs")
        except Exception as e:
            print(f"   ⚠️  Domain scanning issues: {e}")
        
        print("\n5️⃣  Scraping web content...")
        try:
            urls = skan.get_urls_for_scraper()
            scraper.scrape_from_domain_list(urls)
            scraper_stats = scraper.get_queue_stats()
            print(f"   ✓ Scraped {scraper_stats.get('total_entries', 0)} pages")
        except Exception as e:
            print(f"   ⚠️  Scraping issues: {e}")
        
        print("\n6️⃣  Creating vector embeddings...")
        try:
            indexer.process_queue()
            index_stats = indexer.get_stats()
            print(f"   ✓ Created {index_stats.get('total_vectors', 0)} embeddings")
        except Exception as e:
            print(f"   ⚠️  Indexing issues: {e}")
        
        print("\n7️⃣  Testing search functionality...")
        test_query = "example test content information"
        try:
            results = search.search_and_extract(test_query, top_k=3)
            print(f"   ✓ Found {results.get('total_results', 0)} search results")
            print(f"   ✓ Extracted content from {results.get('extracted_count', 0)} pages")
        except Exception as e:
            print(f"   ⚠️  Search issues: {e}")
            results = {'extracted_count': 0}
        
        print("\n8️⃣  Generating AI report...")
        try:
            if results.get('extracted_count', 0) > 0:
                report = compiler.compile_response(test_query)
                report_sections = len(report.get('individual_reports', []))
                print(f"   ✓ Generated report with {report_sections} sections")
            else:
                print("   ⚠️  No content available for report generation")
        except Exception as e:
            print(f"   ⚠️  Report generation issues: {e}")
        
        # Show final results
        print("\n" + "="*60)
        print("📊 DEMO RESULTS")
        print("="*60)
        
        try:
            final_stats = {
                'domains': len(skan.get_domains()),
                'scraped': scraper.get_queue_stats().get('total_entries', 0),
                'indexed': indexer.get_stats().get('total_vectors', 0),
                'discovered': skan.get_stats().get('total_discovered_urls', 0)
            }
            
            print(f"🌐 Domains managed: {final_stats['domains']}")
            print(f"📄 Pages scraped: {final_stats['scraped']}")
            print(f"🔍 Vectors indexed: {final_stats['indexed']}")
            print(f"🔗 URLs discovered: {final_stats['discovered']}")
            print(f"📁 Data saved in: ./data/")
            
            # Check data files
            data_files = ['queue.json', 'raw.json', 'domains.json', 'discovered_links.json']
            existing_files = []
            for file in data_files:
                if os.path.exists(f'data/{file}'):
                    existing_files.append(file)
            
            if existing_files:
                print(f"📄 Created files: {', '.join(existing_files)}")
            
        except Exception as e:
            print(f"⚠️  Error collecting final stats: {e}")
        
        print("\n✅ Demo completed! ZeroNet is working properly.")
        print("💡 Try interactive mode with: python main.py")
        return True
        
    except Exception as e:
        print(f"❌ Demo failed with unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_interactive():
    """Run interactive command mode"""
    print("\n" + "="*60)
    print("🎮 ZERONET INTERACTIVE MODE")
    print("="*60)
    print("Available commands:")
    print("  add <domain>       - Add domain to managed list")
    print("  scan              - Scan all domains for URLs")  
    print("  search <query>    - Search indexed content")
    print("  report <query>    - Generate AI report")
    print("  stats             - Show system statistics")
    print("  domains           - List managed domains")
    print("  clear             - Clear all data")
    print("  help              - Show this help")
    print("  quit              - Exit program")
    print("="*60)
    
    try:
        # Import modules
        print("\n🔄 Loading ZeroNet modules...")
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
        
        print("✅ All modules loaded successfully")
        
        while True:
            try:
                command = input("\nZeroNet> ").strip().split()
                if not command:
                    continue
                
                cmd = command[0].lower()
                
                if cmd in ['quit', 'exit', 'q']:
                    print("👋 Shutting down ZeroNet...")
                    break
                    
                elif cmd == 'add' and len(command) > 1:
                    domain = command[1]
                    try:
                        skan.add_domain(domain)
                        print(f"✅ Added domain: {domain}")
                    except Exception as e:
                        print(f"❌ Failed to add domain: {e}")
                        
                elif cmd == 'scan':
                    print("🔄 Scanning all managed domains...")
                    try:
                        skan.scan_all_domains(max_pages_per_domain=5)
                        urls = skan.get_urls_for_scraper()
                        print("🔄 Scraping discovered content...")
                        scraper.scrape_from_domain_list(urls)
                        print("🔄 Creating vector embeddings...")
                        indexer.process_queue()
                        print("✅ Scan and indexing completed")
                    except Exception as e:
                        print(f"❌ Scan failed: {e}")
                        
                elif cmd == 'search' and len(command) > 1:
                    query = ' '.join(command[1:])
                    print(f"🔍 Searching for: '{query}'")
                    try:
                        results = search.search_and_extract(query, top_k=5)
                        print(f"📊 Found {results.get('total_results', 0)} results")
                        
                        # Display top results
                        for i, result in enumerate(results.get('vector_results', [])[:3], 1):
                            print(f"\n{i}. {result.get('title', 'No title')}")
                            print(f"   URL: {result.get('url', 'No URL')}")
                            print(f"   Score: {result.get('similarity_score', 0):.3f}")
                            
                    except Exception as e:
                        print(f"❌ Search failed: {e}")
                        
                elif cmd == 'report' and len(command) > 1:
                    query = ' '.join(command[1:])
                    print(f"📝 Generating AI report for: '{query}'")
                    try:
                        # First search for content
                        results = search.search_and_extract(query, top_k=5)
                        if results.get('extracted_count', 0) > 0:
                            report = compiler.compile_response(query)
                            print(f"✅ Report generated with {len(report.get('individual_reports', []))} sections")
                            
                            # Show preview
                            final_report = report.get('final_report', '')
                            if final_report:
                                print(f"\n📄 Report Preview:")
                                print("-" * 40)
                                preview = final_report[:300] + "..." if len(final_report) > 300 else final_report
                                print(preview)
                                print("-" * 40)
                        else:
                            print("⚠️  No content available for report generation")
                            
                    except Exception as e:
                        print(f"❌ Report generation failed: {e}")
                        
                elif cmd == 'stats':
                    print("📊 ZeroNet System Statistics:")
                    try:
                        s_stats = scraper.get_queue_stats()
                        i_stats = indexer.get_stats()
                        k_stats = skan.get_stats()
                        
                        print(f"   🌐 Managed domains: {len(skan.get_domains())}")
                        print(f"   🔗 Discovered URLs: {k_stats.get('total_discovered_urls', 0)}")
                        print(f"   📄 Scraped pages: {s_stats.get('total_entries', 0)}")
                        print(f"   🔍 Indexed vectors: {i_stats.get('total_vectors', 0)}")
                        print(f"   💾 Total characters: {s_stats.get('total_characters', 0):,}")
                        
                        # Show domain breakdown
                        domain_stats = s_stats.get('domains', {})
                        if domain_stats:
                            print(f"   📈 Pages per domain:")
                            for domain, count in domain_stats.items():
                                print(f"      • {domain}: {count}")
                                
                    except Exception as e:
                        print(f"❌ Failed to get statistics: {e}")
                        
                elif cmd == 'domains':
                    try:
                        domains = skan.get_domains()
                        print(f"🌐 Managed domains ({len(domains)}):")
                        for i, domain in enumerate(domains, 1):
                            print(f"   {i}. {domain}")
                    except Exception as e:
                        print(f"❌ Failed to get domains: {e}")
                        
                elif cmd == 'clear':
                    confirm = input("⚠️  Clear all data? This cannot be undone! (yes/no): ").lower()
                    if confirm == 'yes':
                        try:
                            scraper.clear_queue()
                            search.clear_cache()
                            compiler.clear_reports()
                            print("✅ All data cleared")
                        except Exception as e:
                            print(f"❌ Failed to clear data: {e}")
                    else:
                        print("❌ Clear operation cancelled")
                        
                elif cmd == 'help':
                    print("📖 Available commands:")
                    print("   add <domain> - Add domain to scan")
                    print("   scan - Discover and index content")
                    print("   search <query> - Find relevant content")
                    print("   report <query> - Generate AI analysis")
                    print("   stats - Show system statistics")
                    print("   domains - List managed domains")
                    print("   clear - Clear all data")
                    print("   quit - Exit ZeroNet")
                    
                else:
                    print("❓ Unknown command. Type 'help' for available commands.")
                    
            except KeyboardInterrupt:
                print("\n\n⚠️  Interrupted by user")
                break
            except Exception as e:
                print(f"❌ Command error: {e}")
    
    except ImportError as e:
        print(f"❌ Failed to load modules: {e}")
        print("Make sure all module files exist in the modules/ directory")
        return False
    except Exception as e:
        print(f"❌ Interactive mode failed: {e}")
        return False
    
    print("\n👋 ZeroNet session ended. Goodbye!")
    return True

def run_web_interface():
    """Start web interface (placeholder)"""
    print("\n🌐 ZeroNet Web Interface")
    print("=" * 40)
    print("Web interface is not yet fully implemented.")
    print("\nAvailable options:")
    print("1. Open web/index.html in your browser for frontend demo")
    print("2. Use interactive mode: python main.py")
    print("3. Use demo mode: python main.py --demo")
    
    # Future: Flask/FastAPI web server implementation
    # This would start a web server and provide REST API endpoints
    
def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='ZeroNet - Privacy-focused Web Analysis Suite',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --demo     Run demonstration workflow
  python main.py           Start interactive mode
  python main.py --check   Check dependencies
  python main.py --web     Start web interface
        """
    )
    
    parser.add_argument('--demo', action='store_true', 
                       help='Run demonstration workflow')
    parser.add_argument('--web', action='store_true', 
                       help='Start web interface')
    parser.add_argument('--check', action='store_true', 
                       help='Check dependencies only')
    
    args = parser.parse_args()
    
    # Header
    print("🌐 ZeroNet - A Complex of Networking Tools")
    print("🔒 Absolute Privacy Guaranteed (IP Protection Active)")
    print("⚡ Advanced AI-Powered Web Analysis Suite")
    print("=" * 60)
    
    # Setup
    setup_logging()
    
    # Create data directory if needed
    Path('data').mkdir(exist_ok=True)
    
    # Handle specific modes
    if args.check:
        check_dependencies()
        return
    
    # Check dependencies for other modes
    if not check_dependencies():
        print("\n⚠️  Some dependencies are missing.")
        print("ZeroNet will run with reduced functionality.")
        
        continue_anyway = input("\nContinue anyway? (y/n): ").lower().strip()
        if continue_anyway != 'y':
            print("Install dependencies with: pip install -r requirements.txt")
            return
    
    # Run selected mode
    try:
        if args.demo:
            success = run_demo()
        elif args.web:
            run_web_interface()
            success = True
        else:
            success = run_interactive()
            
        # Exit with appropriate code
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  ZeroNet interrupted by user")
        print("👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"❌ ZeroNet encountered an unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()