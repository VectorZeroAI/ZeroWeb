# ZeroWeb
A lokal Semantic Search engine + web Crawler.

This programm uses a web crawler to index the user defined domains.

THE APP DOESNT PROVIDE ANY INTERNET IDENTITY CONSEALMENT, USERS PRIVASY IS USERS RESPONSIBILITY!!

So, you can ether start the programm in console mode, or in graphics mode. 
I spend way to much time designing the GUI, so you better use it! 

But whatever, to start the app, you need to run the file "ZeroDoor.py", 
wich runs the app in graphic mode. 

If your feeling nerdy, you can launch the app in console only. 
For it, you need to first run the init




---

#System Architecture:

--- 

#ZeroScraper.py : 
Provides funktions: "get_snippet(URL);get_fullpage(URL);get_URL_list(domain)"

get_URL_list(domain) pseudocode:

Get the list of URLs for the domain
Try:
    get the robots.txt
Expect exeptions as e
If the robots.txt present:
    For each URL in [list of URLs]:
        check if robots.txt allows to scrape, if not, delete from the list.

Save the list of links into the DB with each link getting a separate row and first collum.

Try:
    Get the crawling delay from the robots.txt
expect exeptions as e

if the delay is present:
    put it into the 4 columm for each URL in the domain.

---

#Cofig.py :
Has all the configurations and keys in it.

---

#ZeroSkan.py :

Is the skaner. Uses PostgreSQL DB to save all the scraped data. 

Creates a PostgreSQL DB.
Inputs all the URLs got from all the domains in the config via "get_URL_list" as the first thing in a row. 

Then, launches the configurated by config.py amount of scraper threadds, that each get a part of the DB to fill out.
Also utilises multiprozessing for to offload the scraping to the config defined amount of cores.

The funktion "start_scraping_core" starts a full prozess for enouther core, and fills it with the config defined amount of threads.

These threads scrape the headders and snippets from URLs and input them as the second thing in the same row where the corresponding URL is.

The thread can be shut down at any moment without crashing and without loosing any data, because its loop has a grasefull shutdown mechanism.

Exposes funktions:
"initDB(path)"

"start_scraping_prozess(list of rows)"

"end_scraping"

"end_scraping" saves the DB and shuts dows all the threads.


start_scraper_prozess pseudocode:

def start_scraper_prozess(list of rows):

start enouther prozess, offload it to enouther core.
 
    For each row in [list of rows]
        get_snippet(URL)
        save it into the second collum
        if shutdown request = 1
            shut down
        time.sleep(get from collum 4)

---

#ZeroIndex.py:

Takes the data from the DB and cretes a FAISS Index with it. URLs are made lables in the list.

The Snippet + headder are taken from the DB and embedded. The embedding is saved to the FAISS index and dubbed to the third collum of corresponding row.

The FAISS index used is:"IVF4096,PQ32x8 with nprobe=8" + memory mapping.

Exposes funktions:

"save_index"

"load_index"

"reconstruct_index"

"reconstruct_index" follows this pseudocode:


For each row in the DB: 
    if the collum 3 has the embeding stored in it:
        take the value and input it into FAISS index
    elif the collum 2 has text in it:
        take the text, embedd it, store the embedding into the collum 3 and into the FAISS index
    else
        skip


---

#ZeroSearch++.py:

Exposes funktions: 
Search(querrie;amount);report(List_of_URLs)

The funktion "search(querrie;amount)" searches the FAISS index and gets the [amount] most similar nodes, of wich the URL is returned.

The funktion "report(List_of_URLs)" uses the funktions provided by "ZeroScraper.py" to get the full page text of each of the URLs from the list, and then uses OpenRouter API to call the model: "tngtech/deepseek-r1t2-chimera:free" to compile a report about the contents of the pages, that captures all the facts from the information in a clear and structured report.

report(List_of_URLs) pseudocode:


def get_text_for_report(List_of_URLs):
    For each URL in List_of_URLs:
        if collum 5 in the row corresponding to that link is empty:
            get_full_text(URL)
            save the full text to the columm 5 of the row corresponding to the link.
        else:
            get the text from the collum 5 of the corresponding to the URL row.
    return (full text)

Text = get_text_for_report(List_of_URLs)

if USE_API = 0:
    send to the lokal model:
        "Compile the following information into a comprehensive report [Text]"

else:
    send this to the model in config via openrouter API:
        "Compile the following information into a comprehensive report [Text]"


---

#ZeroMain.py

Has State oriented programminng style.

Has 4 states:
"Halt" state
"Search" state
"Index" state
"Save/shutdown" state

"Halt state" is the state of waiting for something, like commands or parameters.


"Search State" is the state that allows to search and retrive URLs or compile full AI powered reports.


"Index State" is the state in wich the programm indexes the internet.

"Save/shutdown" state is the state that safely saves everything to disk and shuts down the whole prozess with all the threads.

Pseudocode for this programm:

#ZeroMain.py

State = "HALT"

class Main:
    def __init__(self):
        self.state = State
        self.running = True
        self.current_query = None

    def loop(self):
        while self.running:
            if self.state == "HALT":
                self.handle_halt()
            elif self.state == "INDEX":
                self.handle_index()
            elif self.state == "SEARCH":
                self.handle_search()
            elif self.state == "SAVE_SHUTDOWN":
                self.handle_save_shutdown()

    def handle_halt(self):
        # Wait for commands or inputs
        time.sleep(1)

    def handle_index(self):
        # Run indexing logic here
        # Once done or interrupted:
        self.change_state("HALT")

    def handle_search(self):
        while self.state == "SEARCH":
            if self.current_query is None:
                # Request query from GUI or input
                time.sleep(0.5)
                continue
            # perform search with self.current_query
            results = self.perform_search(self.current_query)
            # Return results to GUI or caller
            self.current_query = None
        self.change_state("HALT")

    def handle_save_shutdown(self):
        # Save data and safely shutdown
        self.running = False

    def change_state(self, new_state):
        allowed_states = ["HALT", "INDEX", "SEARCH", "SAVE_SHUTDOWN"]
        if new_state in allowed_states:
            self.state = new_state
            return "done"
        else:
            return "invalid input"

    def insert_query(self, query):
        self.current_query = query

    def perform_search(self, query):
        # Placeholder for search logic
        return ["results"]

# Usage:
# main = Main()
# main.loop()
# main.change_state("SEARCH")
# main.insert_query("example query")



IMPORTANT: The comunation with GUI will be handeled via specialised for each comunication type funkitons, similar to how "change_state" and "insert_querrie" are made.
The ZeroMain.py module will also call comunication funktions from ZeroGUI.py, so place some placeholders there until the ZeroGUI.py is done.


---

#ZeroGUI.py
The GUI has 2 tabs.

One tab is called "Index", the other one is called "Search".

The "Search" tab has:
1. A field where the text is shown.
2. A switch that turns the AI mode on and off.
If the AI mode is on, then the report is provided via OpenRouter API. If the AI mode is off, then only the URLs are provided.
3. A filed to put the users querrie in. 
4. A button to start the search.

The "Index" tab has:
1. A field where the domains are shown, and can be edited. 
2. A button to start the Idexing.
3. A field to edit the maximal threads amount.
4. A remeinder pop up that the user's privasy is users consern, and that the app "Funking doesnt care".
5. A progress bar that roughly estimates how done the idexing is.
6. A Button to Stop the search.





