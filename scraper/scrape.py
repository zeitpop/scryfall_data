import json, requests, bs4, re, os
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
print_metadata = False


# Open File and read
with open ("test_page.html", "r") as raw_file:
    html_file=raw_file.read()

# Parse html into a bs4 object
parsed_html = bs4.BeautifulSoup(html_file, 'html.parser')

    # Tree Structure of parsed .html file: 
        # 3 divs for each column
    #   <div style="margin:3px;flex:1;" align="left">
    #       
    #       # Divs to section card types within column 
    #       <div class="O14">10 LANDS</div>
            
            # divs for card name and count within section (siblings of section divs) 
    #       <div id="mdara009" class="deck_line chosen_tr" ..4 .. Thoughtseize .. </div>
    #       ...
    #       <div id="mdara009" class="deck_line chosen_tr" ..2 .. Ruin Crab.. </div>
    #   </div>
    # 
    # Note: Lands and Sideboard are own column, creatures, instants, sorcs and others share middle column



#############################################################
# Parse HTML bs4 object for decklist, sideboard, metadata


### Parse HTML for Main Deck cards and store in main_deck dict

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



### Parse for Sideboard and populate sideboard dict

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


### Parse for metadata and populate deck_metadata dict

metadata_results = parsed_html.find_all('div', class_='event_title')


# Extract Deck Author, Title, and Placement in Event
place_title_author = metadata_results[1].get_text().split(' - ', 1)
place_title = place_title_author[0].split(" ", 1)

# Insert into metadata dict
deck_metadata['Event'] = metadata_results[0].get_text()
deck_metadata['Author'] = place_title_author[1]
deck_metadata['Placement'] = place_title[0]
deck_metadata['Deck Title'] = place_title[1]
deck_metadata['Format'] = parsed_html.find('div', class_='meta_arch').get_text()


# Extract other metadata (Event Date, Event Link)
date_results = parsed_html.find('div', class_='meta_arch')

date_text_results=[]

for i in date_results.next_siblings:
    if isinstance(i, bs4.element.NavigableString):
        continue
    if isinstance(i, bs4.element.Tag):
        date_text_results.append(i.get_text())


deck_metadata['event_link'] = date_text_results[1]
deck_metadata['event_date'] = date_text_results[0].split(' - ', 1)[1]

if print_metadata == True: 
    print("Metadata:")
    for key in deck_metadata: 
        print("\t", key, ": ", deck_metadata[key])


####################################################################
# Load Extracted Data into Database

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

### Event Data

# 
for c in events.columns:
    print(c.name)

# Check if event is already in database and either
    # Get event ID
    # Load Event data into database

### Deck Data

# Check if deck is already in database
# Load deck into database

### Decklist Data

# Load decklist into database

