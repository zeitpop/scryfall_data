# scryfall_data

Project for learning data engineering skills using data from scryfall

Goals:

[ ] Proof Tech Stack

    [x] mySQL database configuration
    [x] Importing bulk data into Python for ETL
    [x] SQLAlchemy.py for connecting and interacting with database
        [x] engine / connection basics, textual SQL interface
        [ ] ORM -- reflecting, tables/columns
        [ ] INSERTing
    [ ] Flask.py for API endpoint
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
    [ ] Write Python script for parsing bulk data and INSERTing into database

[ ] Build data pipeline for automatically adding new data to database

    [ ] Check periodically for new cards from scryfall
    [ ] Validate new data
    [ ] INSERT into database
    
[ ] API Endpoint

[ ] Application(s) to use Data
