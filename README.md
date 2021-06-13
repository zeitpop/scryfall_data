# scryfall_data

[Scryfall](https://scryfall.com/) is a search engine for the Magic: The Gathering (MTG) card game, with a well documented [public API](https://scryfall.com/docs/api). This repository is for an unaffiliated personal project for improving skills with Databases (SQL/MySQL), Python, and other data tools using data from the Scryfall API. 

So far, I have created a Python script (bin/insert_data.py) for processing data from the Scryfall (currently a bulk .json download) and inserting into an EC2-hosted MySQL database programmatically using SQLalchemy.py. This has given me a consolidated database of the ~20k cards from Scryfall and their gameplay-relevant data. I plan on implementing an automated system for checking for new cards on Scryfall, and adding them to the local database. Caching the Scryfall data in this way (beyond being a fun exercise in database design and implementation!) will allow downstream applications to be more performant while minimizing demand on Scryfall's servers.

In addition, I'm working on a webscraper (scraper/scrape.py) for gently scraping decklists from Pro MTG tournaments and events. Currently, I'm developing the script using a cached .html file to minimize traffic, but I plan on implementing a pipeline for automatically finding and politely scraping decklists from new tournaments as they're posted. The decklists will be keyed to the cards from Scryfall, and allow for eventual analysis of the evolution of Magic's various formats over time. I have initialized an empty Flask.py web server (db_api/) which will be developed into an API for the decklist data, at least for my own applications using the Flask.py library.
