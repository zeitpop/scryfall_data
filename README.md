# scryfall_data

Project for learning data engineering skills using data from scryfall

Goals:

[ ] Proof Tech Stack

    [x] mySQL database configuration
    [x] Importing bulk data into Python for ETL
    [x] SQLAlchemy.py for connecting and interacting with database
    [ ] Flask.py for API endpoint
    [ ] Web App to use data

[ ] mySQL database containing data available from scryfall
    
    --- Design Phase
    [ ] Analyze and understand scryfall data (types, fields, etc)
    [ ] Create an Entity Relationship Diagram to map functional dependencies, redundancies, etc
    [ ] Apply normalization to refine database model
    
    --- Create Phase
    [ ] Create .SQL scripts for making tables
    [ ] Write Python script for parsing bulk data and INSERTing into database

[ ] Build data pipeline for automatically adding new data to database

    [ ] Check periodically for new cards from scryfall
    [ ] Validate new data
    [ ] INSERT into database
    
[ ] API Endpoint

[ ] Application(s) to use Data
