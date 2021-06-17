import json, requests, bs4, re, os, sys
from dotenv import load_dotenv
from sqlalchemy import * 

####################
# Initialization

deck_metadata = {}
main_deck = {}
sideboard = {}

# Debug
print_maindeck = False
print_sideboard = False
print_skipped_column_headers = False
print_event_data = False
print_deck_data = False

# To be deprecated?
print_metadata = False


### Init Database

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

# Instantiate objects to receive processed data

event_data = dict.fromkeys([c.name for c in events.columns])
deck_data = dict.fromkeys([c.name for c in decks.columns])

#############################################################
# Parse HTML bs4 object for decklist, sideboard, metadata

# Open File and read
with open ("test_page.html", "r") as raw_file:
    html_file=raw_file.read()

# Parse html into a bs4 object
parsed_html = bs4.BeautifulSoup(html_file, 'html.parser')

# ----- MAIN DECK -----

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



# ---- SIDEBOARD -----

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


# ----- METADATA ------

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

# ------- to be deprecated --------- #
# Insert into metadata dict (to be deprecated)

# deck_metadata['Author'] = place_title_author[1]
# deck_metadata['Placement'] = place_titlei[0]
# deck_metadata['Deck Title'] = place_title[1]
# deck_metadata['Format'] = parsed_html.find('div', class_='meta_arch').get_text()
# --------------------------------------------


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

if print_metadata == True: 
    print("Metadata:")
    for key in deck_metadata: 
        print("\t", key, ": ", deck_metadata[key])


####################################################################
# Load Extracted Data into Database


# ---- Event Data ----

if print_event_data == True: 
    print("Event data: ")
    for key in event_data: print("\t", key, ": ", event_data[key])

# Query database for existing event record

event_query_statement = select(events.c.id).where(events.c.event_name == event_data['event_name'])

with engine.connect() as connection:
        event_query_results = connection.execute(event_query_statement)
        connection.commit() 

event_results = event_query_results.all()
eventExists = len(event_results) != 0

actually_commit = True    

if not eventExists:
    print("Event not yet recorded")
    event_insert_statement = insert(events).values(event_data)
    with engine.connect() as connection:
        event_insert_results = connection.execute(event_insert_statement)
        if actually_commit == True: connection.commit()

    print("Recorded event data")

    # or does it have to go in after we insert event data, we have to get event_id to pass to deckdata
    with engine.connect() as connection:
        event_query_results = connection.execute(event_query_statement)
        connection.commit()


    # Either way we then have to set event_id:
    event_results = event_query_results.all()
    deck_data['event_id'] = [row[0] for row in event_results][0]


elif eventExists:
    print("Event already recorded")
    deck_data['event_id'] = [row[0] for row in event_results][0]

else:
    print("Found ", len(event_results), " matching events")

print("Retrieved event_id ", deck_data['event_id'])

# elseif eventInDatabase:
    # deck_data['event_id'] = event_query_results['event_id']



# ---- Deck Data ----

if print_deck_data == True:
    print("Deck Data: ")
    for key in deck_data: print("\t", key, ": ", deck_data[key])

# if deck is not in database:
deck_statement = insert(decks).values(deck_data)
# else:
#   get deck_id


# ---- Decklist Data ----

# Load decklist into database

    # Can insert multiple rows in a single statement by creating a list of dicts: 
        #https://docs.sqlalchemy.org/en/14/core/tutorial.html#executing-multiple-statements
    # Might have to reorganize how we construct card objects

    # For item in decklist, item =cardname, item(key) = count_maindeck
    # For item in sideboard, item = cardname, item(key) = count_sideboard
    # not this --> decklist_statement = insert(deckilsts).values(decklists_data)


