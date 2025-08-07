# ZeroWeb
A lokal Semantic Search engine + web Crawler.

This programm uses a web crawler to index the user defined domains.

THE APP DOESNT PROVIDE ANY INTERNET IDENTITY CONSEALMENT, USERS PRIVASY IS USERS RESPONSIBILITY!!

By default, it indexes "Wikipedia, arXiv, github, reddit"


---

System Architecture:
ZeroScraper.py : Provides funktions: "get_snippet(URL);get_fullpage(URL);get_URL_list(domain)"

---

Cofig.py :
Has all the configurations in it.

---

ZeroSkan.py :

Skans the web via using the funktions from the Scraper.py

First gets the list of domains.
Then creates a list of links for every one of the domains.
Then starts to Index the links.

Uses safe threadding via: 
Starting threads that get their job done and close themselfs automaticly. 

All the URLs are saved into a SQLite DB as IDs and can be asigned the snippets that are scraped from a URL.

Each thread gets its portion of the SQLite to fill.

SQLite works in WAL mode, and each thread has a 2 seconds cooldown between scrapes.

The thread then gets the snippets and the headders from each URL one by one.

These are then saved into the SQLite under the URL as the ID

When the work is over, the [list(the threadds numer).json] and the [raw(the threadds numer.json)] are compared to make shure that all the links were scraped. 

If not all were scraped, then the left over ones are scraped, and then again and again untill all of them are scraped.

And then the threadd just closes itself.

---

ZeroIndex.py:

Takes all the raw(numer).json files contents and compiles them into one big "Global_raw" SQLite Data base.

Then all the contents of "Global_raw" are embedded into a FAISS Index, with the URL as the label of the node.

The FAISS index used is:"IVF4096,PQ32x8 with nprobe=8" + memory mapping.

Exposes funktions:

update_global_raw

and

reconstruct_index.

"update_global_raw" checks for new scraped data, and gets it in.

"reconstruct_index" reconstructs the FAISS index based on the "global_raw" DB.

---

ZeroSearch++.py:

Exposes funktions: 
Search(querrie;amount);report(List_of_URLs)

The funktion "search(querrie;amount)" searches the FAISS index and gets the [amount] most similar nodes, of wich the URL is returned.

The funktion "report(List_of_URLs)" uses the funktions provided by "ZeroScraper.py" to get the full page text of each of the URLs from the list, and then uses OpenRouter API to call the model: "tngtech/deepseek-r1t2-chimera:free" to compile a report about the contents of the pages, that captures all the facts from the information in a clear and structured report.

---

ZeroMain.py

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





---

ZeroGUI.py
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

















ZeroSkan.py architecture backup (if I fuck up)





