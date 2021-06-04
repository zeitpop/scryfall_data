import json
from sqlalchemy import *
from sqlalchemy import table, create_engine


####################
## Initialize 
####################

debug = 0

## Load .json file of data
with open("../data/test_oracle.json") as d:
    data = json.load(d)

## Create handle to database
engine = create_engine("mysql+mysqldb://root:508774Mw!@localhost/scryfall", echo=True, future=True)


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

if debug == 1: 
    print("Initializing processed_card...")

    
if debug == 1:
   print("Importing raw card from loaded .json data...")

raw_card = data[1]

for raw_card in data:
    
    processed_card = dict.fromkeys(columns)

    for key in processed_card:
    
        if debug == 1:
            print("\tSetting key: ", key)
    
        if key in raw_card:
            processed_card[key] = raw_card[key]
        elif key == 'scryfall_card_id':
            processed_card[key] = raw_card['id']
        elif key == 'set_code':
            processed_card[key] = raw_card['set']
        elif key == 'card_face':
            # don't set? leave blank? don't have auto-increment setup
            processed_card[key] = 'NULL'

    if debug == 1:
        print("Processed Card:", processed_card['name'])

        #for key in processed_card:
            #print("\tKey: ", key)
            #print("\t\tType: ", type(processed_card[key]))
            #print("\t\tValue: ", processed_card[key])



############################
## Submit to Database
############################

# Construct Statement
statement = insert(cards).values(processed_card)

# Execute and Commit Statement
with engine.connect() as conn:
    result = conn.execute(statement)
    conn.commit()


