import json, requests, bs4, re



####################
## Initialization


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
## Parse HTML bs4 object for decklist, sideboard, metadata


## Parse HTML for Main Deck cards and store in main_deck dict

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



## Parse for Sideboard and populate sideboard dict

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


## Parse for metadata and populate deck_metadata dict

metadata_results = parsed_html.find_all('div', class_='event_title')


# Extract Deck Author, Title, and Placement in Event
place_title_author = metadata_results[1].get_text().split(' - ', 1)
place_title = place_title_author[0].split(" ", 1)

deck_metadata['Event'] = metadata_results[0].get_text()
deck_metadata['Author'] = place_title_author[1]
deck_metadata['Placement'] = place_title[0]
deck_metadata['Deck Title'] = place_title[1]
deck_metadata['Format'] = parsed_html.find('div', class_='meta_arch').get_text()

# deck_metadata['Date'] = 

date_results = parsed_html.find('div', class_='meta_arch')

print(type(date_results))
print(date_results)


# Possibly due to weirdly formatted html, the siblings of date_results 
#   are both type Tag and Navigable String, which is not really usable.
#   Trying to find a good way to iterate through results and skip NavigableStrings


for i in date_results.next_siblings:
    if isinstance(i, NavigableString):
        continue
    if isinstance(i, Tag):
        print(type(i))
#
#for dd in date_results:
#    print("--------------------------------------")
#    print(dd.prettify())


if print_metadata == True: 
    for key in deck_metadata: print(key, ": ", deck_metadata[key])

# Also Extract Event Date?????????? or leave to seperate event-level parsing

