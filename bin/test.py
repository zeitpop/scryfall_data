import json
from sqlalchemy import *
from sqlalchemy import table, create_engine
from func_lib import submitSQL

 ## Load .json file of data
with open("../data/test_oracle.json") as d:
    data = json.load(d)

engine = create_engine("mysql+mysqldb://root:508774Mw!@localhost/scryfall", echo=True, future=True)

test = 'metadata'

####################

if test == 'metadata':

    # https://docs.sqlalchemy.org/en/14/core/reflection.html#

    meta = MetaData()

    cards = Table('cards', meta, autoload_with=engine)
    
    print("cards type: ", type(cards))
    print("cards keys: ", cards.keys())


    #cards_table = meta_data.tables['key']


if test == 'insert':
    
    columns = ["card_id", "arena_id", "lang", "object", "oracle_id", "scryfall_uri", "uri", "card_face_id", "cmc", "color_identity", "color_indicator", "colors", "layout", "loyalty", "mana_cost", "name", "oracle_text", "power", "produced_mana", "toughness", "type_line", "flavor_text", "rarity", "release_at", "reprint", "set_name", "set_type", "set_code"]

   
    print("Initializing processed_card...")
    processed_card = dict.fromkeys(columns)
    print("Initialized card as: ", type(processed_card))

    print("Importing raw card from loaded .json data...")
    raw_card = data[1]
    print("Loaded raw data as: ", type(raw_card))


    print("Beginning data transfer...")
    for key in processed_card:
        print("\tSetting key: ", key)
        if key in raw_card:
            processed_card[key] = raw_card[key]
        elif key == 'card_id':
            processed_card[key] = raw_card['id']
        elif key == 'set_code':
            processed_card[key] = raw_card['set']
        elif key == 'card_face':
            # don't set? leave blank? don't have auto-increment setup
            processed_card[key] = 'NULL'

    print("Processed Card:")

    for key in processed_card:
        print("\tKey: ", key)
        print("\t\tType: ", type(processed_card[key]))
        print("\t\tValue: ", processed_card[key])


    statement = insert(cards).values(processed_card)

    with engine.connect() as conn:
        result = conn.execute(statement)
        conn.commit()






###########################################################################

if test == 'select':

    statement = "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA='scryfall' AND TABLE_NAME='cards';"

    results = submitSQL(engine, statement)



    for i in range(0, len(results)):
        print("Column Name:  ", results[i]._fields, "  Type: ", type(results[i]._fields)) 


#print("Received results type: ", type(results))

#print("/n Results:/n", results)
