# scryfall_data

Personal project for improving skills with Python, SQL and other data tools using data from Scryfall API. 

So far, I have an EC2-hosted MySQL data base

Data pipeline from Scryfall API to Database
Database



Files:

bin/ ------------------- Directory for <br/>
| - fetch_data.py ------------ Script for retrieving data from Scryfall API <br/>
| - insert.py ---------------- Primary script for ETL of .json from Scryfall to local MySQL database </br>
| - requirements.txt---------- Package requirements bounced from Pip Virtual Environment </br>
| - test.py ------------------ Scratchpad for development </br>
data/-------------------- Directory for cached data during development </br>
   | - oracle_keys.txt --------- List of data field from Scryfall API data </br>
   | - test_default.txt -------- Sample .txt of Scryfall data </br>
   | - test_oracle.json -------- Sample .json of Scryfall data </br>
db_api ------------------ </br>
   | - api_endpoint.py --------- Initialized API, WIP </br>
   | - start_flask.sh ---------- Script for starting Flask web server for API </br>
scraper/ ----------------- </br>
   | - cache_page.py ----------- Takes a URL and caches .html file locally to be parsed without additional traffic </br>
   | - scrape.py --------------- Primary script for scraping an .html page for decklist and metadata </br>
   | - test_page.html ---------- Cached web page </br>
   



[ ] Proof Tech Stack

    -- Data pipeline 
    [x] mySQL database configuration
    [x] Importing bulk data into Python for ETL
    [x] SQLAlchemy.py for connecting and interacting with database
        [x] engine / connection basics, textual SQL interface
        [ ] ORM -- reflecting, tables/columns
        [ ] INSERTing
    [ ] Flask.py for API endpoint
    
    -- Doing things with the data
    [ ] Web App to use data

[ ] Database
    
    --- Design Phase
    [x] Analyze and understand scryfall data (types, fields, etc)
        [x] List all fields and data types
        [x] Translate each field into SQL column data type
    [x] Create an Entity Relationship Diagram to map functional dependencies, redundancies, etc
        https://lucid.app/lucidchart/d717ddde-fd59-4ae4-a171-0693a39b155e
    [-] Apply normalization to refine database model
    
    --- Create Phase
    [x] Create .SQL scripts for making tables
    [x] Write Python script for parsing bulk card data and INSERTing into database
    [x] Run bulk card insert, database in provisionally usable state

[ ] Decklist Data Pipeline
    [ ] identify scrapable source for lists
    [ ] build scraper
    [ ] build ETL to insert scraped decks into database

[ ] Card Data Pipeline
    [ ] Adapt insert_data.py to check for new cards and insert
        [ ] Check for new cards from scryfall
        [ ] Validate new data
        [ ] INSERT into database
    
[ ] API Endpoint

[ ] Application(s) to use Data
