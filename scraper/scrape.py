import json, requests, bs4, re


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


print("Main Deck: ")

main_deck = {}
sideboard = {}

# Find Column Header divs for main deck.
for category in parsed_html.find_all('div', class_='O14', string=[re.compile('LANDS'), re.compile('CREATURES')]):

    # Column headers are siblings of card divs, so find iterate through siblings
    for card in category.find_next_siblings():
        # test checking for a category header
        if card.get_text() == card.find(string=re.compile('OTHER SPELLS')) or \
           card.get_text() == card.find(string=re.compile('INSTANTS and SORC')):
               print("\t", card.get_text(), "skipping...")
        else: 
            # print("\t", card.get_text())
            text = card.get_text().split(" ", 1)
            main_deck[text[1]] = text[0]
        
for key in main_deck:
    print("\t",main_deck[key], " ", key)

        # print("\t", card.get_text(), " ", type(card), card)


# Finds Sideboard div
sideboard_results = parsed_html.find('div', class_='O14', string='SIDEBOARD').find_next_siblings()

print("Sideboard: ")

for div in sideboard_results:
   # print("\t", div.get_text())
   sb_text = div.get_text().split(" ", 1)

   sideboard[sb_text[1]] = sb_text[0]

for key in sideboard:
    print("\t", sideboard[key], " ", key)

 




