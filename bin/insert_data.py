import json
from sqlalchemy import text
from sqlalchemy import create_engine
from func_lib import constructINSERT
from func_lib import submitSQL
# constructINSERT(tabe, columns, values


#################################
## Initialization 
#################################

## Initialize SQL connection
engine = create_engine("mysql+mysqldb://root:508774Mw!@localhost/scryfall", echo=True, future=True)


## Load .json file of data 
with open("../data/test_oracle.json") as d:
    data = json.load(d)

print("loaded file as type: ", type(data))



#################################
## Process imported data 
#################################

# initialize columns to pull in
    # get all card-level columns
    # translate local DB columns to match .json data
        # uuid
        # card_faces / etc
    # handle sub-dicts of card-faces
# columns_toMatch = sql.table.cards.getColumns + sql.table.cardFaces.getColumns
#   make this a dict with:
#       columns_toMatch
#           key: value
#           
# for key in card_json
#   cards_SQL = card_json(key)
#   
#   for face in card_jason('card_faces'):
#      cardfaces_SQL = card_json('card_face')(face)
#
#
#
#
# stmt = insert(user_table).values(name='spongebob', fullname="Spongebob Squarepants")


















columns = []

# for each dict 'card' in list 'data'
for card in data:
    
    values = [] # initialize list of per-card values
    print("Reading card ", card['name'])
    
    for key in card: # f --> key

        if type(card[key]) is dict:
            print("\t", key, " is a dict, skipping")
            
            # if it is, cycle though keys/values of sub-dict 'h'
            for h in card[key]:
                print("\t\t" + h, card[key][h], ", skipping")
          
        elif type(card[key]) is list:
            print("\t", key, " is a list, skipping")

        # otherwise, do stuff to top level keys
        else:
            print("\t", key, " is a ", type(key), ", reading...")
            # append key to list of columns, if it isn't there already
            if key not in columns: 
                print("\t\t", key, " not in yet in list of columns, adding..")
                columns.append(key)
           
            if card[key] is not str:
                
                print("\t\t converting to str...")
                card[key] = str(card[key])

            # Add key's value to list of values
            values.append(card[key])
            print("\t\tSuccessfully added to list of values")   

    # after tabuluating all keys and values, submit insert statement
    print("Finished reading card ", card["name"])
   
    # print("Using column names:\n", columns)
    # print("Extracted card values:\n",values)

    # now we check to see if list of columns/values matches the corresponding json object we are parsing

        # 'card' is current card object as dict
        # card["key"] returns key vaue
        # values[0] returns the first value
        # columns[0] returns the first column name, which is a key of'card'

        # so, we want to check to make sure the corresponding value of column[n] is both i[columns[n]] and values[n]
            # i[columns[n]] == values[n]
    
    print("\tChecking that values to insert match original values")
    for ii in range(0, len(columns)):
        # check if the ii'th element in columns keys to a value in 'card' that matches the ii'th element in values
        print("\t\t", columns[ii], "...")

        assert card[columns[ii]] == values[ii], "Mismatched value"

    #if i[columns] == values:
    #    statement = constructINSERT(columns, values)
    #    print('Submitting to database: \n', statement, '\n')
    #else:
    #    print("key/value mismatch after tabulation, exiting")

#print("The result of tabulating columns was: \r", columns, "\r")   

