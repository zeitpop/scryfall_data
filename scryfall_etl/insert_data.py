import json, sys, os, requests
from sqlalchemy import *
from dotenv import load_dotenv

####################
## Initialize 
####################

debug = 1 
commit = False

## Load .json file of data
with open("../data/test_oracle.json") as d:
    data = json.load(d)

## Create database engine object

load_dotenv()

database_url = os.environ.get('DATABASE_URL')
database_username = os.environ.get('DATABASE_USERNAME')
database_password = os.environ.get('DATABASE_PASSWORD')

connection_string = ("mysql+mysqldb://" + database_username + ":" + database_password + "@" + database_url + "/scryfall")

engine = create_engine(connection_string, echo=False, future=True, pool_pre_ping=True)

# Create MetaData object
meta = MetaData()

# Construct Table objects
cards = Table('cards', meta, autoload_with=engine)
card_faces = Table('card_faces', meta, autoload_with=engine)


#####################
## ETL Data
#####################

# Create list of columns    
columns = [column.name for column in cards.columns]

# Iterate through cards in raw data, transform into processed dicts for insertion
for raw_card in data:
    
    processed_card = dict.fromkeys(columns)
    
    if debug == 2: print("Processing card: ", raw_card['name'])

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
        
    # Submit statement to database
    with engine.connect() as connection:
        result = connection.execute(statement)
        if commit == True: connection.commit()


