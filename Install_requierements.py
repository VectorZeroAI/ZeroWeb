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
__author__ = "VectorZero" 
__description__ = "Web scraping and Semantic analysis suite"

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
    print("🚀 main.py is now a separate artifact...")
    print("   ✓ Copy the 'ZeroNet Main.py' artifact to zeronet/main.py")
    
    # Create a placeholder that reminds user to copy the artifact
    placeholder_content = '''#!/usr/bin/env python3
"""
ZeroNet Main Entry Point - PLACEHOLDER

⚠️  IMPORTANT: This is a placeholder file!

To get the complete main.py file:
1. Copy the content from the "ZeroNet Main.py - Entry Point" artifact
2. Replace this file with that content
3. Then run: python main.py --demo

The artifact contains the full-featured main.py with:
- Dependency checking
- Demo workflow
- Interactive mode
- Error handling
- Statistics display
"""

print("❌ This is a placeholder main.py file!")
print("📋 Copy the 'main.py")
print("🔗 Then run: python main.py --demo")
'''
    
    with open('zeronet/main.py', 'w') as f:
        f.write(placeholder_content)
    print("   ⚠️  Placeholder created - copy artifact content to replace it")# Setup
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
        print("1. Copy module files from artifacts to zeronet/modules/:")
        print("   - ZeroScraper artifact → modules/zeroscraper.py")
        print("   - ZeroIndex artifact → modules/zeroindex.py")
        print("   - ZeroSkan artifact → modules/zeroskan.py")
        print("   - ZeroSearch++ artifact → modules/zerosearch.py")
        print("   - ZeroCompiler artifact → modules/zerocompiler.py")
        print("   - ZeroOS artifact → modules/zeroos.py")
        print("2. Copy 'ZeroNet Main.py' artifact → zeronet/main.py")
        print("3. cd zeronet")
        print("4. python main.py --demo")
        print("=" * 50)
        
    except Exception as e:
        print(f"❌ Installation failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()