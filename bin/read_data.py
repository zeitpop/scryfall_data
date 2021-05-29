import json

# open file, load .json

# for reference: https://realpython.com/python-json/#deserializing-json

# json loads as
# list
# --dict (card)
# -- -- key : value
# -- -- key : value

with open("../data/test_oracle.json") as d:
    oracle = json.load(d)

print("loaded file as type: ", type(oracle))


# define a function for getting column headers
def getlist(dict):
    return list(dict.keys())

# get columns of dict keys
oracle_columns = (getlist(oracle[1]))

# print("ran getlist on contents and returned as type: ", type(oracle_columns))


# works: pul a card and go through its key values
# card1 = oracle[1]
# for i in card1:
#    print(i, card1[i]) 


# oracle is  a list
for i in oracle:
    # goes through each card as dict 'i'
        
    for f in i:
        # goes through each key 'f' of card 'i' and prints the value
        
        print(i[f])       

