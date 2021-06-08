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

# Finds Sideboard div
results = parsed_html.find('div', class_='O14', string='SIDEBOARD').find_next_siblings()


for div in results:
   print(div.get_text())

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

