import json, requests, bs4, re


# Open File and read
with open ("test_page.html", "r") as raw_file:
    html_file=raw_file.read()

# Parse html into a bs4 object
parsed_html = bs4.BeautifulSoup(html_file, 'html.parser')

# Navigate HTML tree to find decklist

# Tree Structure: 

#   <div style="margin:3px;flex:1;" align="left">
#       
#       <div class="O14">10 LANDS</div>
#       <div id="mdara009" class="deck_line chosen_tr" ..Card.. </div>
#       ...
#       <div id="mdara009" class="deck_line chosen_tr" ..Card.. </div>
#   </div>


# !!! Need to find a way to differentiate the sideboard!

    # This at least gets us a block of card types, but 
    # haven't figured out how to step through the results. 
    # Missing something about how .find() vs .find_all() work


# maindeck_results = parsed_html.find_all('div', class_='O14', string=[re.compile('LANDS'), re.compile('CREATURES'), re.compile('INSTANTS'), re.compile('OTHER SPELLS')])
print("Main Deck: ")

# Find Column Header divs 
for category in parsed_html.find_all('div', class_='O14', string=[re.compile('LANDS'), re.compile('CREATURES')]):

    # Column headers are siblings of card divs, so find iterate through siblings
    for card in category.find_next_siblings():
        # test checking for a category header
        if card.get_text() == card.find(string=re.compile('OTHER SPELLS')) or card.get_text() == card.find(string=re.compile('INSTANTS and SORC')):
            print("  ", card.get_text(), " (Skipping)")
        else: 
            print("\t", card.get_text())

        
        

        # print("\t", card.get_text(), " ", type(card), card)
        

#print("maindeck_results Type: ", type(maindeck_results))
#print("maindeck_results: ", maindeck_results)
#for element in maindeck_results:
  
#    for card in element.find_next_siblings():
        #print("card in element.find_next_siblings() Type: ", type(card))
#        print(card.get_text())

# Creatures

# Finds Sideboard div
sideboard_results = parsed_html.find('div', class_='O14', string='SIDEBOARD').find_next_siblings()


print("Sideboard: ")
for div in sideboard_results:
   print("\t", div.get_text())

########## ( Works ) 
# (Works) For now, we won't differentiate sideboard and just get all cards:
# results = parsed_html.find_all('div', class_='deck_line hover_tr')

# main_deck = {}

# for element in results:
#    text = element.get_text().split(" ", 1)
    
#    main_deck[text[1]] = text[0]  


# for key in main_deck:
    # print(main_deck[key], " ", key)
##############



#print(element.prettify())

#print("Card Name: ")
#print("Count: ")

# This 
#if type(results) == bs4.element.ResultSet:
#    for element in results:
#        print(element.prettify())

