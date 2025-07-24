<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ZeroNet - Networking Tools Suite</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            min-height: 100vh;
            color: #fff;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }

        .header {
            text-align: center;
            margin-bottom: 30px;
        }

        .header h1 {
            font-size: 3rem;
            background: linear-gradient(45deg, #00d4ff, #5b86e5);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
        }

        .header p {
            opacity: 0.8;
            font-size: 1.1rem;
        }

        .tabs {
            display: flex;
            margin-bottom: 20px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            padding: 5px;
        }

        .tab {
            flex: 1;
            padding: 15px;
            text-align: center;
            cursor: pointer;
            border-radius: 8px;
            transition: all 0.3s ease;
            font-weight: 600;
        }

        .tab.active {
            background: rgba(255, 255, 255, 0.2);
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
        }

        .tab-content {
            display: none;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            padding: 30px;
            backdrop-filter: blur(10px);
        }

        .tab-content.active {
            display: block;
        }

        .search-section {
            margin-bottom: 30px;
        }

        .search-input {
            width: 100%;
            padding: 15px;
            border: none;
            border-radius: 10px;
            background: rgba(255, 255, 255, 0.9);
            color: #333;
            font-size: 1.1rem;
            margin-bottom: 20px;
        }

        .search-controls {
            display: flex;
            gap: 20px;
            align-items: center;
            margin-bottom: 20px;
        }

        .switch-container {
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .switch {
            position: relative;
            width: 60px;
            height: 30px;
            background: rgba(255, 255, 255, 0.3);
            border-radius: 15px;
            cursor: pointer;
            transition: all 0.3s ease;
        }

        .switch.active {
            background: #00d4ff;
        }

        .switch-thumb {
            position: absolute;
            top: 3px;
            left: 3px;
            width: 24px;
            height: 24px;
            background: white;
            border-radius: 50%;
            transition: all 0.3s ease;
        }

        .switch.active .switch-thumb {
            transform: translateX(30px);
        }

        .btn {
            padding: 12px 25px;
            border: none;
            border-radius: 8px;
            background: linear-gradient(45deg, #00d4ff, #5b86e5);
            color: white;
            cursor: pointer;
            font-weight: 600;
            transition: all 0.3s ease;
        }

        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0, 212, 255, 0.4);
        }

        .results-area {
            background: rgba(0, 0, 0, 0.3);
            border-radius: 10px;
            padding: 20px;
            min-height: 300px;
            font-family: 'Courier New', monospace;
            white-space: pre-wrap;
        }

        .domain-list {
            background: rgba(0, 0, 0, 0.3);
            border-radius: 10px;
            padding: 20px;
            margin: 20px 0;
            min-height: 200px;
        }

        .domain-input {
            width: 100%;
            padding: 10px;
            border: none;
            border-radius: 5px;
            background: rgba(255, 255, 255, 0.9);
            color: #333;
            margin-bottom: 10px;
        }

        .progress-bar {
            width: 100%;
            height: 20px;
            background: rgba(255, 255, 255, 0.2);
            border-radius: 10px;
            overflow: hidden;
            margin: 20px 0;
        }

        .progress-fill {
            height: 100%;
            background: linear-gradient(45deg, #00d4ff, #5b86e5);
            width: 0%;
            transition: width 0.3s ease;
        }

        .module-status {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 30px;
        }

        .module-card {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            padding: 15px;
            text-align: center;
        }

        .module-name {
            font-weight: 600;
            margin-bottom: 5px;
        }

        .module-status-indicator {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            margin: 0 auto;
            background: #4CAF50;
        }

        .status-text {
            font-size: 0.9rem;
            opacity: 0.8;
            margin-top: 5px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>ZeroNet</h1>
            <p>A Complex of Networking Tools - Absolute Privacy Guaranteed</p>
        </div>

        <div class="tabs">
            <div class="tab active" onclick="switchTab('search')">Search</div>
            <div class="tab" onclick="switchTab('index')">Index</div>
        </div>

        <!-- Search Tab -->
        <div id="search-tab" class="tab-content active">
            <div class="search-section">
                <input type="text" class="search-input" id="searchQuery" placeholder="Enter your search query...">
                
                <div class="search-controls">
                    <button class="btn" onclick="startSearch()">Start Search</button>
                    <div class="switch-container">
                        <span>URLs</span>
                        <div class="switch" id="outputSwitch" onclick="toggleSwitch()">
                            <div class="switch-thumb"></div>
                        </div>
                        <span>AI Answer</span>
                    </div>
                </div>
            </div>

            <div class="results-area" id="searchResults">
Search results will appear here...

ZeroNet modules are running in sandboxed environment.
All operations maintain absolute privacy (IP protection enabled).
            </div>
        </div>

        <!-- Index Tab -->
        <div id="index-tab" class="tab-content">
            <div class="search-section">
                <input type="text" class="domain-input" id="domainInput" placeholder="Add domain (e.g., example.com)">
                <div class="search-controls">
                    <button class="btn" onclick="addDomain()">Add Domain</button>
                    <button class="btn" onclick="showDomains()">Show Domains</button>
                    <button class="btn" onclick="startIndexing()">Start Indexing</button>
                </div>
            </div>

            <div class="domain-list" id="domainList">
Current domains:
- wikipedia.org
- stackoverflow.com
- github.com
- reddit.com

Click "Show Domains" to refresh the list.
            </div>

            <div class="progress-bar">
                <div class="progress-fill" id="indexProgress"></div>
            </div>
            <div class="status-text" id="progressText">Indexing Progress: 0%</div>
        </div>

        <!-- Module Status -->
        <div class="module-status">
            <div class="module-card">
                <div class="module-name">ZeroScraper</div>
                <div class="module-status-indicator" id="scraper-status"></div>
                <div class="status-text">Ready</div>
            </div>
            <div class="module-card">
                <div class="module-name">ZeroIndex</div>
                <div class="module-status-indicator" id="index-status"></div>
                <div class="status-text">FAISS DB Active</div>
            </div>
            <div class="module-card">
                <div class="module-name">ZeroSkan</div>
                <div class="module-status-indicator" id="skan-status"></div>
                <div class="status-text">Domain Manager</div>
            </div>
            <div class="module-card">
                <div class="module-name">ZeroOS</div>
                <div class="module-status-indicator" id="os-status"></div>
                <div class="status-text">Sandbox Active</div>
            </div>
            <div class="module-card">
                <div class="module-name">ZeroSearch++</div>
                <div class="module-status-indicator" id="search-status"></div>
                <div class="status-text">Vector Search</div>
            </div>
            <div class="module-card">
                <div class="module-name">ZeroCompiler</div>
                <div class="module-status-indicator" id="compiler-status"></div>
                <div class="status-text">LLM Ready</div>
            </div>
        </div>
    </div>

    <script>
        // Global state
        let domains = ['wikipedia.org', 'stackoverflow.com', 'github.com', 'reddit.com'];
        let aiMode = false;
        let indexingProgress = 0;

        // Simulated data stores
        let queueData = {};
        let rawData = {};
        let faissDB = new Map();

        function switchTab(tabName) {
            // Hide all tabs
            document.querySelectorAll('.tab-content').forEach(tab => {
                tab.classList.remove('active');
            });
            document.querySelectorAll('.tab').forEach(tab => {
                tab.classList.remove('active');
            });

            // Show selected tab
            document.getElementById(tabName + '-tab').classList.add('active');
            event.target.classList.add('active');
        }

        function toggleSwitch() {
            const switchEl = document.getElementById('outputSwitch');
            switchEl.classList.toggle('active');
            aiMode = switchEl.classList.contains('active');
        }

        function addDomain() {
            const input = document.getElementById('domainInput');
            const domain = input.value.trim();
            if (domain && !domains.includes(domain)) {
                domains.push(domain);
                input.value = '';
                updateModuleStatus('skan-status', 'Domain added');
            }
        }

        function showDomains() {
            const domainList = document.getElementById('domainList');
            domainList.textContent = 'Current domains:\n' + domains.map(d => '- ' + d).join('\n');
        }

        function startIndexing() {
            updateModuleStatus('skan-status', 'Collecting URLs...');
            
            // Simulate ZeroSkan collecting URLs
            setTimeout(() => {
                simulateIndexingProcess();
            }, 1000);
        }

        function simulateIndexingProcess() {
            const progressBar = document.getElementById('indexProgress');
            const progressText = document.getElementById('progressText');
            
            indexingProgress = 0;
            updateModuleStatus('scraper-status', 'Scraping...');
            
            const interval = setInterval(() => {
                indexingProgress += Math.random() * 10;
                if (indexingProgress >= 100) {
                    indexingProgress = 100;
                    clearInterval(interval);
                    
                    // Simulate queue.json creation
                    simulateQueueCreation();
                    updateModuleStatus('scraper-status', 'Complete');
                    updateModuleStatus('index-status', 'Vectorizing...');
                    
                    setTimeout(() => {
                        updateModuleStatus('index-status', 'FAISS Updated');
                    }, 2000);
                }
                
                progressBar.style.width = indexingProgress + '%';
                progressText.textContent = `Indexing Progress: ${Math.round(indexingProgress)}%`;
            }, 500);
        }

        function simulateQueueCreation() {
            // Simulate ZeroScraper output
            queueData = {
                "https://wikipedia.org/wiki/Artificial_Intelligence": {
                    "title": "Artificial Intelligence - Wikipedia",
                    "snippet": "Artificial intelligence (AI) is intelligence demonstrated by machines..."
                },
                "https://stackoverflow.com/questions/tagged/python": {
                    "title": "Python Questions - Stack Overflow",
                    "snippet": "Find answers to common Python programming questions..."
                }
            };
            
            // Simulate ZeroIndex processing
            Object.entries(queueData).forEach(([url, data]) => {
                if (!faissDB.has(url)) {
                    // Simulate embedding creation
                    const embedding = new Array(384).fill(0).map(() => Math.random());
                    faissDB.set(url, {
                        vector: embedding,
                        title: data.title,
                        snippet: data.snippet
                    });
                }
            });
        }

        function startSearch() {
            const query = document.getElementById('searchQuery').value.trim();
            if (!query) return;
            
            const resultsArea = document.getElementById('searchResults');
            resultsArea.textContent = 'Searching...\n\nZeroSearch++ analyzing query vectors...\n';
            
            updateModuleStatus('search-status', 'Searching...');
            
            setTimeout(() => {
                simulateSearch(query);
            }, 1500);
        }

        function simulateSearch(query) {
            const resultsArea = document.getElementById('searchResults');
            
            // Simulate ZeroSearch++ finding relevant URLs
            const relevantUrls = Array.from(faissDB.keys()).slice(0, 3);
            
            resultsArea.textContent += `Found ${relevantUrls.length} relevant pages:\n\n`;
            
            if (aiMode) {
                // Simulate AI-powered answer
                updateModuleStatus('compiler-status', 'Generating...');
                
                setTimeout(() => {
                    resultsArea.textContent += `AI-Generated Answer:\n\n`;
                    resultsArea.textContent += `Based on the indexed knowledge base, here's what I found about "${query}":\n\n`;
                    resultsArea.textContent += `The search revealed relevant information from multiple sources. `;
                    resultsArea.textContent += `Key insights include comprehensive coverage of the topic across `;
                    resultsArea.textContent += `different domains in the knowledge base.\n\n`;
                    resultsArea.textContent += `Sources processed:\n`;
                    relevantUrls.forEach((url, i) => {
                        const data = faissDB.get(url);
                        resultsArea.textContent += `${i + 1}. ${data.title}\n   ${url}\n`;
                    });
                    
                    updateModuleStatus('compiler-status', 'Complete');
                }, 2000);
            } else {
                // Return URLs
                relevantUrls.forEach((url, i) => {
                    const data = faissDB.get(url);
                    resultsArea.textContent += `${i + 1}. ${data.title}\n`;
                    resultsArea.textContent += `   ${url}\n`;
                    resultsArea.textContent += `   ${data.snippet}\n\n`;
                });
            }
            
            updateModuleStatus('search-status', 'Complete');
        }

        function updateModuleStatus(moduleId, status) {
            const statusEl = document.querySelector(`#${moduleId} + .status-text`);
            if (statusEl) {
                statusEl.textContent = status;
            }
        }

        // Initialize with some sample data
        simulateQueueCreation();
    </script>
</body>
</html>