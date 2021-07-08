import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from dotenv import load_dotenv
from sqlalchemy import *
import bs4, re, os, sys, requests


class Mtgtop8Spider(CrawlSpider):
    name = 'mtgtop8'
    allowed_domains = ['mtgtop8.com']
    start_urls = [
            'https://mtgtop8.com/event?e=31299&d=442914&f=MO',
            'https://mtgtop8.com/event?e=31299&d=442915&f=MO',
            'https://mtgtop8.com/event?e=31299&d=442914&f=MO&switch=visual'
#            'https://mtgtop8.com/format?f=ST',
#            'https://mtgtop8.com/format?f=HI',
            ]

    rules = (

        # Extract Links matching the deck URL pattern and extract deck items
        Rule(LinkExtractor(allow=('mtgtop8.com/event?', ), deny=('&switch=visual')), callback='parse_decklist'),

        Rule(LinkExtractor(deny=('/topcards?', '/archetype?' ))),  

        # Non-deck sites
        Rule(LinkExtractor(), callback = 'parse'),

    )

    def parse_decklist(self, response):
        
        # Debugging
        
        debug_parse_maindeck = False
        print_maindeck = True
        print_skipped_column_headers = True

        print_sideboard = False
        
        print_event_data = False
        print_deck_data = False
        print_decklist_data = False
        print_database = False
        
        exec_without_commit = False

        load_database = False

        extract_main_deck = False
        extract_sideboard = False
        extract_metadata = False

        procedural_crawl = False

        # Instantiate
        main_deck = {}
        sideboard = {}
        
        ## Create database engine object

        

        if load_database == True:

            load_dotenv()

            database_url = os.environ.get('DATABASE_URL')
            database_username = os.environ.get('DATABASE_USERNAME')
            database_password = os.environ.get('DATABASE_PASSWORD')
            
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

        #item = scrapy.Item()

        
        # Gotta insert all the beautiful soup extraction stuff here


        #############################################################
        # Parse HTML bs4 object for decklist, sideboard, metadata

        # Open File and read
        #with open ("test_page.html", "r") as raw_file:
        #    html_file=raw_file.read()

        # Parse html into a bs4 object
        #parsed_html = bs4.BeautifulSoup(html_file, 'html.parser')

        parsed_html = bs4.BeautifulSoup(response.text, 'html.parser')
        

        # Test zone for making new method for extracting deck / sideboard
            # Problem is there are 3 columns, with child divs of section headers and cards at same level.
            # Depending on how many cards in columns, distribution of sections will vary between the 3 columns
            # Probably need to combine contents of each column into a single navigable string, then parse accordingly

        # Tentative alternative method of parsing decklist:

            # Get 3 columns into a resultSet
            # Take contents of each column and append to single navigable string object
            # Iterate through single NavigableSTring, skipping column headers and switching to sideboard once past that header


########### BLOCK TO REPLACE OLD MAINDECK AND SIDEBOARD PARSER

        div = parsed_html.find('div', class_='O14', string=re.compile('LANDS'))

        columns = div.parent.parent

        maindeck_column_names = ['LANDS', 'CREATURES', 'INSTANTS and SORC.', 'OTHER SPELLS']
        target_sideboard = False

        # Iterate through div and child divs for 3 columns, each with child divs for either cards or column names
        for child in columns:
            for descendant in child:
                
                # Split out first word (seperates cards/column names from counts)
                text = descendant.get_text().split(" ", 1)

                if any(item in maindeck_column_names for item in text):
                    
                    if debug_parse_maindeck == True: print(f'COLUMN NAME: {text}')
                
                elif any(item in ['SIDEBOARD'] for item in text):
                    
                    if debug_parse_maindeck == True: print(f'SIDEBOARD: {text}')
                    target_sideboard = True

                else:

                    # Get cardname and count from extracted text, for clarity's sake
                    cardname = text[1]
                    count = text[0]

                    # Store cardname and count in either main_deck or sideboard dicts
                    if target_sideboard == True:
                        sideboard[cardname] = count
                    else:
                        main_deck[cardname] = count

                    if debug_parse_maindeck == True: print(f'Count: {count}, Cardname: {cardname}')

        #self.logger.info(f'Found div of type {type(div)} with length {len(div)}')
        #for item in div:
        #    self.logger.info(f'\tFound item in div with contents:\n{item.get_text()}')

        # self.logger.info(f'\n\n Printing test div: \n{div.prettify()}')



        # ----- ETRACT MAIN DECK -----
        

        if extract_main_deck == True:
            

            ###### OLD CODE FOR MAINDECK ###########            
            if debug_parse_maindeck == True: self.logger.info('Parsing Main Deck...')

            # Find Column Header divs for main deck.
            main_deck_html = parsed_html.find_all('div', class_='O14', string=[re.compile('LANDS'), re.compile('CREATURES')])

            if print_maindeck== True: self.logger.info(f'Received main_deck_html with type {type(main_deck_html)} and {len(main_deck_html)} items')

            # Iterate through divs containing main deck
            for category in main_deck_html:

                if debug_parse_maindeck == True: self.logger.info(f'Iteration of main_deck_html\n\t{category}')
                
                # Column headers are siblings of card divs, so find & iterate through siblings
                for card in category.find_next_siblings():
                    
                    # Check if div is just a column header. Skip or add to deck accordingly
                    if card.get_text() == card.find(string=re.compile('OTHER SPELLS')) or \
                       card.get_text() == card.find(string=re.compile('INSTANTS and SORC')) or \
                       card.get_text() == card.find(string=re.compile('CREATURES')):
                           if debug_parse_maindeck == True:
                               self.logger.info(f'\t {card.get_text()} skipping...')
                    else:
                        if debug_parse_maindeck == True: self.logger.info(f'\t {card.get_text()}')
                        
                        # Get text of div contaiing card and add to main_deck
                        text = card.get_text().split(" ", 1)
                        main_deck[text[1]] = text[0]
            
            if debug_parse_maindeck == True: self.logger.info(f'Completed extracting Main Deck')



            if print_maindeck == True:
                self.logger.info('Main Deck Contents: ')
                for key in main_deck: 
                    self.logger.info(f'\t{main_deck[key]} {key}')

        # ---- EXTRACT SIDEBOARD -----
        
        if extract_sideboard == True:

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

        if extract_metadata == True:

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
            
        ###############################################################
        # 

        # item = [main_deck, sideboard, deck_data, event_data]

        # yield item

        if procedural_crawl == True:

            for href in response.xpath('//a/@href').getall():
              yield scrapy.Request(response.urljoin(href), self.parse)

    def parse(self, response):

        for href in response.xpath('//a/@href').getall():
            yield scrapy.Request(response.urljoin(href))
