# ZeroWeb
A lokal Semantic Search engine + web Crawler.

This programm uses a web crawler to index the user defined domains.
By default, it indexes "Wikipedia, arXiv, github, reddit"


---


System Architecture:
ZeroScraper.py : Provides funktions: "get_snippet(URL);get_fullpage(URL);get_URL_list(domain)"

---

ZeroSkan.py :
Skans the web via using the funktions from the Scraper.py

First gets the list of domains.
Then creates a list of links for every one of the domains.
Then starts to Index the links.

Uses safe threadding via: 
Starting threads that get their job done and close themselfs automaticly. 

Each thread gets a [list(the threadds numer).json] file with [the total amount of links / the amount of threadds] links to get snippets + headders from.

It then gets the snippets and the headders from each URL one by one.

These are then saved in the [raw(the threadds numer).json[ file under the URL as the titel. The format looks like that:

{
  "https://example.com/page1": {
    "title": "Example Title",
    "snippet": "Example snippet text goes here."
  },
  ...
}

When the work is over, the [list(the threadds numer).json] and the [raw(the threadds numer.json)] are compared to make shure that all the links were scraped. 

If not all were scraped, then the left over ones are scraped, and then again and again untill all of them are scraped.

And then the threadd just closes itself.

---

ZeroIndex.py:

Takes all the raw(numer).json files contents and compiles them into one big Global_raw.json .

Then all the contents of Global_raw.json are embedded into a FAISS Index, with the URL as the label of the node.

Exposes funktions:

update_global_raw_json

and

reconstruct_index.

---

ZeroSearch++.py:

Exposes funktions: 
Search(querrie;amount);report(List_of_URLs)

The funktion "search(querrie;amount)" searches the FAISS index and gets the [amount] most similar nodes, of wich the URL is returned.

The funktion "report(List_of_URLs)" uses the funktions provided by "ZeroScraper.py" to get the full page text of each of the URLs from the list, and then uses OpenRouter API to call the model: "tngtech/deepseek-r1t2-chimera:free" to compile a report about the contents of the pages, that captures all the facts from the information in a clear and structured report.

---

ZeroMain.py

Is the main part running all the funktions and interacting with the user via GUI.

