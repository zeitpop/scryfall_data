import json, requests, bs4, re, os, sys
from dotenv import load_dotenv
from sqlalchemy import * 

#########################################
### Initialization

# Debug
print_maindeck = False
print_sideboard = False
print_skipped_column_headers = False
print_event_data = False
print_deck_data = False
print_decklist_data = False
print_database = False
exec_without_commit = False

# Import database credentials
load_dotenv()
database_url = os.environ.get('DATABASE_URL')
database_username = os.environ.get('DATABASE_USERNAME')
database_password = os.environ.get('DATABASE_PASSWORD')

# Create connection string and engine object
connection_string = ("mysql+mysqldb://" + database_username + ":" + database_password + "@" + database_url + "/scryfall")

engine = create_engine(connection_string, echo=False, future=True, pool_pre_ping=True)

# Create MetaData object
meta = MetaData()

# Construct Table objects
events = Table('events', meta, autoload_with=engine)
decks = Table('decks', meta, autoload_with=engine)
decklists = Table('decklists', meta, autoload_with=engine)
cards = Table('cards', meta, autoload_with=engine)

# Instantiate objects to receive processed data

event_data = dict.fromkeys([c.name for c in events.columns])
deck_data = dict.fromkeys([c.name for c in decks.columns])
decklist_data = dict.fromkeys([c.name for c in decklists.columns])

main_deck = {}
sideboard = {}


#############################################################
# Parse HTML bs4 object for decklist, sideboard, metadata

# Open File and read
with open ("test_page.html", "r") as raw_file:
    html_file=raw_file.read()

# Parse html into a bs4 object
parsed_html = bs4.BeautifulSoup(html_file, 'html.parser')


# ----- ETRACT MAIN DECK -----

# Find Column Header divs for main deck.
for category in parsed_html.find_all('div', class_='O14', string=[re.compile('LANDS'), re.compile('CREATURES')]):

    # Column headers are siblings of card divs, so find iterate through siblings
    for card in category.find_next_siblings():
        # test checking for a category header
        if card.get_text() == card.find(string=re.compile('OTHER SPELLS')) or \
           card.get_text() == card.find(string=re.compile('INSTANTS and SORC')):
               if print_skipped_column_headers == True:
                   print("\t", card.get_text(), "skipping...")
        else: 
            # print("\t", card.get_text())
            text = card.get_text().split(" ", 1)
            main_deck[text[1]] = text[0]
        
if print_maindeck == True: 
    print("Main Deck: ")
    for key in main_deck: print("\t",main_deck[key], " ", key)


# ---- EXTRACT SIDEBOARD -----

# Finds Sideboard div
sideboard_results = parsed_html.find('div', class_='O14', string='SIDEBOARD').find_next_siblings()

# Iterate through tags in results for sideboard cards
for div in sideboard_results:
   # print("\t", div.get_text())
   sb_text = div.get_text().split(" ", 1)

   sideboard[sb_text[1]] = sb_text[0]

if print_sideboard == True: 
    print("Sideboard: ")
    for key in sideboard: print("\t", sideboard[key], " ", key)


# ----- EXTRACT METADATA ------

# Create parsed .html object
metadata_results = parsed_html.find_all('div', class_='event_title')


# Extract Deck Author, Title, and Placement in Event
place_title_author = metadata_results[1].get_text().split(' - ', 1)
place_title = place_title_author[0].split(" ", 1)

 # deck_data['event_id'] = how to get event_id after data gets submitted?
deck_data['deck_title'] = place_title[1]
deck_data['deck_format'] = parsed_html.find('div', class_='meta_arch').get_text()
deck_data['placement'] = place_title[0]
deck_data['deck_author'] = place_title_author[1]

# Extract other metadata (Event Date, Event Link)
date_results = parsed_html.find('div', class_='meta_arch')

date_text_results=[]

for i in date_results.next_siblings:
    if isinstance(i, bs4.element.NavigableString):
        continue
    if isinstance(i, bs4.element.Tag):
        date_text_results.append(i.get_text())

# Set event data
event_data['event_name'] = metadata_results[0].get_text()
event_data['event_date'] = date_text_results[0].split(' - ', 1)[1]
event_data['event_format'] = parsed_html.find('div', class_='meta_arch').get_text()
event_data['event_link'] = date_text_results[1]


####################################################################
# Load Extracted Data into Database


# ---- Load Event Data ----

if print_event_data == True: 
    print("Event data: ")
    for key in event_data: print("\t", key, ": ", event_data[key])

# Query database for existing event record
event_query_statement = select(events.c.id).where(events.c.event_name == event_data['event_name'])
with engine.connect() as connection:
        event_query_results = connection.execute(event_query_statement)
        connection.commit() 

# Determine if event already in database
event_results = event_query_results.all()
eventExists = len(event_results) != 0

# Submit event data if needed, and get event_id for deck_data
if not eventExists:
    #print("Event not yet recorded")
    
    event_insert_statement = insert(events).values(event_data)
    
    with engine.connect() as connection:
        event_insert_results = connection.execute(event_insert_statement)
        if exec_without_commit == False: connection.commit()
    #print("Recorded event data")

    with engine.connect() as connection:
        event_query_results = connection.execute(event_query_statement)
        if exec_without_commit == False: connection.commit()

    event_results = event_query_results.all()
    deck_data['event_id'] = [row[0] for row in event_results][0]

elif eventExists:
    # print("Event already recorded")
    deck_data['event_id'] = [row[0] for row in event_results][0]

else:
    print("Warning: Found ", len(event_results), " matching events")

# print("Retrieved event_id: ", deck_data['event_id'])


# ---- Load Deck Data ----

if print_deck_data == True:
    print("Deck Data: ")
    for key in deck_data: print("\t", key, ": ", deck_data[key])

# Query if Deck exists already
deck_query_statement = select(decks.c.deck_id).where(decks.c.event_id == deck_data['event_id'] and decks.c.deck_author == deck_data['deck_author'])
with engine.connect() as connection:
    deck_query_results = connection.execute(deck_query_statement)
    if exec_without_commit == False: connection.commit()

deck_results = deck_query_results.all()
deckExists = len(deck_results) != 0

# Load deck_data into Database if necessary, then get deck_id
if deckExists:
    decklist_data['deck_id'] = [row[0] for row in deck_results][0]
    
    if print_database == True: print("Deck already recorded, retrieved deck_id ", decklist_data['deck_id'])

elif not deckExists:
    deck_insert_statement = insert(decks).values(deck_data)

    with engine.connect() as connection:
        deck_insert_results = connection.execute(deck_insert_statement)
        if exec_without_commit == False: connection.commit()

    decklist_data['deck_id'] = deck_insert_results.inserted_primary_key[0]

    if print_database == True: print("Loaded deck_data to database\nRetrieved deck_id ", decklist_data['deck_id'])

else:
    if print_database == True: print("Duplicate Deck data found")


# ---- Load Decklist Data ----

# For decklist data we have 2 dicts:
#   dict (main_deck / sideboard:)
#       <card_name> : count 
#       ...
#       ...

# We want data in Database Format:
# -----+---------+---------+-----------+----------------+-----------------+
# | id | deck_id | card_id | card_name | count_maindeck | count_sideboard |
# +----+---------+---------+-----------+----------------+-----------------+
#
# Which would translate into a dict / row with the column/values as key/values


# Create the list of dicts for submitting to database
decklist_data_values = []
 
# Process main_deck cards
for key in main_deck:
    iter_dict = decklist_data.copy()

    iter_dict['card_name'] = key
    iter_dict['count_maindeck'] = main_deck[key]
    iter_dict['count_sideboard'] =  0

    decklist_data_values.append(iter_dict)

# Process sideboard cards 
for sideboard_card in sideboard:
   
    # Check if given sideboard card is also in main_deck
    if sideboard_card in main_deck:
        
        # If it is, iterate through decklist to find existing entry for card and increment its sideboard_count
        for decklist_item in decklist_data_values: 
            if sideboard_card == decklist_item['card_name']:
                decklist_item['sideboard_count'] += sideboard[sideboard_card]

    # Otherwise append to decklist as its own row
    else: 
        iter_dict = decklist_data.copy()
        iter_dict['card_name'] = sideboard_card
        iter_dict['count_maindeck'] = 0
        iter_dict['count_sideboard'] = sideboard[sideboard_card]
        decklist_data_values.append(iter_dict)       

if print_decklist_data = True: 
    for card_row in decklist_data_values:
        print(card_row)
 
# Submit decklist to database
decklist_insert_statement = insert(decklists).values(decklist_data_values)
with engine.connect() as connection:
    decklist_insert_results = connection.execute(decklist_insert_statement)
    if exec_without_commit == False: connection.commit()

