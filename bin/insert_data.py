import json
from sqlalchemy import *
from sqlalchemy import table, create_engine
import sys
import requests

####################
## Initialize 
####################

debug = 1 

## Load .json file of data
with open("../data/bulk_data.json") as d:
    data = json.load(d)

## Create handle to database
engine = create_engine("mysql+mysqldb://root:508774Mw!@localhost/scryfall", echo=False, future=True)


# https://docs.sqlalchemy.org/en/14/core/reflection.html#

# Create MetaData object
meta = MetaData()

# Construct Table objects
cards = Table('cards', meta, autoload_with=engine)
card_faces = Table('card_faces', meta, autoload_with=engine)


#####################
## ETL Data
#####################

# Create list of columns, ideally we replace this by pulling column names from table objects metadata    
columns = ["internal_card_id", "scryfall_card_id", "arena_id", "lang", "object", "oracle_id", "scryfall_uri", "uri", "card_face_id", "cmc", "color_identity", "color_indicator", "colors", "layout", "loyalty", "mana_cost", "name", "oracle_text", "power", "produced_mana", "toughness", "type_line", "flavor_text", "rarity", "release_at", "reprint", "set_name", "set_type", "set_code"]


# Iterate through cards in raw data, transform into processed dicts for insertion
for raw_card in data:
    
    processed_card = dict.fromkeys(columns)
    
    if debug == 1 or 2: print("Processing card: ", raw_card['name'])

    for key in processed_card:
    
        if debug == 2: print("\tSetting key: ", key)


        # Assign Key Values
        if key == 'scryfall_card_id': processed_card[key] = raw_card['id']
        elif key == 'set_code': processed_card[key] = raw_card['set']    
        elif key == 'card_face': processed_card[key] = 'NULL'
        elif key in raw_card and type(raw_card[key]) == list: processed_card[key] = ''.join(map(str, raw_card[key])) 
        elif key in raw_card: processed_card[key] = raw_card[key]
    
        if debug == 2: print("\t\t Type: ", type(processed_card[key]), "\n\t\tValue: ", processed_card[key])
 
    if debug == 1 or 2:
        print("\n Processed Card:", processed_card['name'], "\n")

    statement = insert(cards).values(processed_card)
        
    with engine.connect() as connection:
        result = connection.execute(statement)
        connection.commit()


