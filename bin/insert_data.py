import json
from sqlalchemy import *
from sqlalchemy import table, create_engine
import sys

####################
## Initialize 
####################

debug = 1 

## Load .json file of data
with open("../data/test_oracle.json") as d:
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

###### Test zone

test_loop = 'disabled'
if test_loop == 'enabled':
    
    for raw_card in data:
        processed_card = dict.fromkeys(columns)
        print(raw_card['name'])
        
        for key in processed_card:
            if key in raw_card and type(raw_card[key]) is list:
                print("value of", raw_card['name'], ", key ", key, " is a list")

    sys.exit("terminating early for testing")

####### Begin real zone

for raw_card in data:
    
    processed_card = dict.fromkeys(columns)
    
    if debug == 1 or 2: print("Processing card: ", raw_card['name'])

    for key in processed_card:
    
        if debug == 2: print("\tSetting key: ", key)
    
        # if key is
        if key == 'scryfall_card_id':
            processed_card[key] = raw_card['id']

        # otherwise, if key is
        elif key == 'set_code':
            processed_card[key] = raw_card['set']
        
        # otherwise if key is
        elif key == 'card_face':
            if debug == 3: print("\t\t\tkey == card_face, setting as NULL")
            # don't set? leave blank? don't have auto-increment setup
            processed_card[key] = 'NULL'
       
        # otherwise if key is
        elif key in raw_card and type(raw_card[key]) == list:
            if debug == 3: print("\t\t\tkey is a list")

            processed_card[key] = ''.join(map(str, raw_card[key]))
        

        #elif key == 'produced_mana':
        #    if debug == 2: print("\tkey == ", key)
        #    if key in raw_card:
        #        # stringify and store
        #        print("\t\tproduced_mana is a key of ", raw_card['name'], ", inserting value: ")
        #        print("\t\t\t", raw_card[key])
        #        processed_card[key] = ''.join(map(str, raw_card[key]))
        #
        #    else:
        #        if debug == 2: print("\t\tproduced_mana is NOT a key of ", raw_card['name'], ", inserting null value")
        #        processed_card[key] = 'NULL' 

        # otherwise if key to fill from proc_card exists within raw_card, pass it directly:
        elif key in raw_card:
           # if debug == 2: print("\t\t ", key, " <-- ", raw_card[key])
            processed_card[key] = raw_card[key]
        if debug == 2: print("\t\t Type: ", type(processed_card[key]), "\n\t\tValue: ", processed_card[key])
 
    if debug == 1 or 2:
        print("\n Processed Card:", processed_card['name'], "\n")

        #for key in processed_card:
            #print("\tKey: ", key)
            #print("\t\tType: ", type(processed_card[key]))
            #print("\t\tValue: ", processed_card[key])

    statement = insert(cards).values(processed_card)
        
    with engine.connect() as connection:
        result = connection.execute(statement)
        connection.commit()


