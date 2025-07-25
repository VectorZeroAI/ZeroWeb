<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ZeroNet - Networking Tools Suite</title>
    <style>
        /* ... (same styles as before) ... */
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>ZeroNet</h1>
            <p>A Complex of Networking Tools - Absolute Privacy Guaranteed</p>
        </div>

        <div class="tabs">
            <div class="tab active" onclick="switchTab(this, 'search')">Search</div>
            <div class="tab" onclick="switchTab(this, 'index')">Index</div>
        </div>

        <!-- Search Tab -->
        <div id="search-tab" class="tab-content active">
            <!-- ... (same content as before) ... -->
        </div>

        <!-- Index Tab -->
        <div id="index-tab" class="tab-content">
            <!-- ... (same content as before) ... -->
        </div>

        <!-- Module Status -->
        <div class="module-status">
            <!-- ... (same content as before) ... -->
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

        function switchTab(element, tabName) {
            // Hide all tabs
            document.querySelectorAll('.tab-content').forEach(tab => {
                tab.classList.remove('active');
            });
            document.querySelectorAll('.tab').forEach(tab => {
                tab.classList.remove('active');
            });

            // Show selected tab
            document.getElementById(tabName + '-tab').classList.add('active');
            element.classList.add('active');
        }

        function toggleSwitch() {
            const switchEl = document.getElementById('outputSwitch');
            switchEl.classList.toggle('active');
            aiMode = switchEl.classList.contains('active');
        }

        function addDomain() {
            const input = document.getElementById('domainInput');
            const domain = input.value.trim();
            if (domain && isValidDomain(domain) && !domains.includes(domain)) {
                domains.push(domain);
                input.value = '';
                updateModuleStatus('skan-status', 'Domain added', '#4CAF50');
            } else if (!isValidDomain(domain)) {
                alert('Please enter a valid domain (e.g., example.com)');
            }
        }

        function isValidDomain(domain) {
            return /^([a-z0-9]+(-[a-z0-9]+)*\.)+[a-z]{2,}$/i.test(domain);
        }

        function showDomains() {
            const domainList = document.getElementById('domainList');
            domainList.textContent = 'Current domains:\n' + domains.map(d => '- ' + d).join('\n');
        }

        function startIndexing() {
            if (domains.length === 0) {
                alert('Please add domains first');
                return;
            }
            
            updateModuleStatus('skan-status', 'Collecting URLs...', '#FFC107');
            setTimeout(simulateIndexingProcess, 1000);
        }

        function simulateIndexingProcess() {
            const progressBar = document.getElementById('indexProgress');
            const progressText = document.getElementById('progressText');
            indexingProgress = 0;
            updateModuleStatus('scraper-status', 'Scraping...', '#FFC107');

            const interval = setInterval(() => {
                indexingProgress += Math.random() * 10;
                if (indexingProgress >= 100) {
                    indexingProgress = 100;
                    clearInterval(interval);
                    simulateQueueCreation();
                    updateModuleStatus('scraper-status', 'Complete', '#4CAF50');
                    updateModuleStatus('index-status', 'Vectorizing...', '#FFC107');
                    setTimeout(() => {
                        updateModuleStatus('index-status', 'FAISS Updated', '#4CAF50');
                    }, 2000);
                }
                progressBar.style.width = indexingProgress + '%';
                progressText.textContent = `Indexing Progress: ${Math.round(indexingProgress)}%`;
            }, 500);
        }

        function simulateQueueCreation() {
            // ... (same as before) ...
        }

        function startSearch() {
            const query = document.getElementById('searchQuery').value.trim();
            if (!query) return;
            
            const resultsArea = document.getElementById('searchResults');
            resultsArea.textContent = 'Searching...\n\nZeroSearch++ analyzing query vectors...\n';
            updateModuleStatus('search-status', 'Searching...', '#FFC107');

            setTimeout(() => simulateSearch(query), 1500);
        }

        function simulateSearch(query) {
            const resultsArea = document.getElementById('searchResults');
            const relevantUrls = Array.from(faissDB.keys()).slice(0, 3);
            
            if (relevantUrls.length === 0) {
                resultsArea.textContent += 'No results found. Please index some domains first.';
                updateModuleStatus('search-status', 'No results', '#F44336');
                return;
            }

            resultsArea.textContent += `Found ${relevantUrls.length} relevant pages:\n\n`;

            if (aiMode) {
                updateModuleStatus('compiler-status', 'Generating...', '#FFC107');
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
                    updateModuleStatus('compiler-status', 'Complete', '#4CAF50');
                }, 2000);
            } else {
                relevantUrls.forEach((url, i) => {
                    const data = faissDB.get(url);
                    resultsArea.textContent += `${i + 1}. ${data.title}\n`;
                    resultsArea.textContent += `   ${url}\n`;
                    resultsArea.textContent += `   ${data.snippet}\n\n`;
                });
            }
            updateModuleStatus('search-status', 'Complete', '#4CAF50');
        }

        function updateModuleStatus(moduleId, status, color = '#4CAF50') {
            const indicator = document.getElementById(moduleId);
            const statusEl = document.querySelector(`#${moduleId} + .status-text`);
            
            if (indicator) indicator.style.backgroundColor = color;
            if (statusEl) statusEl.textContent = status;
        }

        // Initialize with some sample data
        simulateQueueCreation();
    </script>
</body>
</html>