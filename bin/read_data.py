import json
# import sqlalchemy


def constructINSERT(c, v):
    separator1 = ", "
    separator2 = ", "

    print("received input argument c as type ", type(c))
    print("received input argument v as type ", type(v))

    columnStatement = separator1.join(c)
    valueStatement = separator2.join(v)
    
    print("created columnStatement as type ", type(columnStatement))
    print("created valueStatemenet as type ", type(valueStatement))

    insertStatement = "INSERT INTO table (" + columnStatement + ") \n VALUES (" + valueStatement + "); "

    return insertStatement

# open file, load .json

# for reference: https://realpython.com/python-json/#deserializing-json

# json loads as
# list
# --dict (card)
# -- -- key : value
# -- -- key : value
# -- -- dict
# -- -- -- key : value
# -- -- -- key : value
# -- -- key : value

with open("../data/test_oracle.json") as d:
    oracle = json.load(d)

print("loaded file as type: ", type(oracle))

# initialize columns
columns = []

# for each card 'i' in list 'oracle'
for i in oracle:
    
    # initialize list of per-card values 
    values = []
    print("Reading card ", i['name'])
    # for each key 'f' of card dict 'i'    
    for f in i:

        # key/value level 
        # check types of key 'f' of card dict 'i' is itself a dict
        if type(i[f]) is dict:
            print("\t", f, " is a dict, skipping")
            
            # if it is, cycle though keys/values of sub-dict 'h'
            for h in i[f]:
                print("\t\t" + h, i[f][h], ", skipping")
          
        elif type(i[f]) is list:
            print("\t", f, " is a list, skipping")

        # otherwise, do stuff to top level keys
        else:
            print("\t", f, " is a ", type(f), ", reading...")
            # append key to list of columns, if it isn't there already
            if f not in columns: 
                print("\t\t", f, " not in yet in list of columns, adding..")
                columns.append(f)
           
            if i[f] is not str:
                
                print("\t\t converting to str...")
                i[f] = str(i[f])

            # Add key's value to list of values
            values.append(i[f])
            print("\t\tSuccessfully added to list of values")   

    # after tabuluating all keys and values, submit insert statement
    print("Finished reading card ", i["name"])
   
    # print("Using column names:\n", columns)
    # print("Extracted card values:\n",values)

    # now we check to see if list of columns/values matches the corresponding json object we are parsing

        # i is current card object as dict
        # i["key"] returns key vaue
        # values[0] returns the first value
        # columns[0] returns the first column name, which is a key of i

        # so, we want to check to make sure the corresponding value of column[n] is both i[columns[n]] and values[n]
            # i[columns[n]] == values[n]
    
    print("\tChecking that values to insert match original values")
    for ii in range(0, len(columns)):
        # check if the ii'th element in columns keys to a value in i that matches the ii'th element in values
        if i[columns[ii]] == values[ii]:
            print("\t\t Column: ", columns[ii], "Iterator: ", ii, " Format: value == original value")
            print("\t\t\t", values[ii], " == ", i[columns[ii]])


    #if i[columns] == values:
    #    statement = constructINSERT(columns, values)
    #    print('Submitting to database: \n', statement, '\n')
    #else:
    #    print("key/value mismatch after tabulation, exiting")

#print("The result of tabulating columns was: \r", columns, "\r")   

