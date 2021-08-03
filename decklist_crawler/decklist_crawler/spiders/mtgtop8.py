import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from dotenv import load_dotenv
from sqlalchemy import *
import bs4, re, os, sys, requests
from decklist_crawler.items import pageItem

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

        # Allow the main indicator of a page with a deck, deny the visual view, set callback function
        Rule(LinkExtractor(allow=('mtgtop8.com/event?', ), deny=('&switch=visual')), callback='parse_decklist'),

        # Deny a few link categories that get appear early in pages but don't yield many pages with decks
        Rule(LinkExtractor(deny=('/topcards?', '/archetype?', '/dec?', '/mtgo?' '/search?' ))),  

        # Set callback function for all other (non-deck) pages
        Rule(LinkExtractor(), callback = 'parse'),

    )

    # Callback Function for pages with decklists
    def parse_decklist(self, response):
        
        # Debugging
        
        # Enable Debug statements for code parsing html for data
        debug_parse_decklist = False
        debug_parse_metadata = False

        # Enable debug statements printing data extracted from parsed html
        print_parsed_decklist = True
        print_event_data = True
        print_deck_data = True

        #
        print_decklist_data = False
        print_database = False
        
        exec_without_commit = False

        load_database = True

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

        # Parse html into a bs4 object

        self.logger.info('Parsing response...')
        parsed_html = bs4.BeautifulSoup(response.text, 'html.parser')
        

        # ----- EXTRACT DECKLIST ------ #

        # Create NavigableString object containing the 3 columns with headers and cards
        div = parsed_html.find('div', class_='O14', string=re.compile('LANDS'))
        columns = div.parent.parent

        maindeck_column_names = ['LANDS', 'CREATURES', 'INSTANTS and SORC.', 'OTHER SPELLS']
        target_sideboard = False

        # Iterate through div and child divs for 3 columns, each with child divs for either cards or column names
        for child in columns:
            for descendant in child:
                
                # Split out first word (seperates cards/column names from counts)
                text = descendant.get_text().split(" ", 1)

                # Logic for checking if iteration is a column header or a card, and if card goes in sideboard
                if any(item in maindeck_column_names for item in text):
                    if debug_parse_decklist == True: self.logger.info(f'COLUMN NAME: {text}')
                elif any(item in ['SIDEBOARD'] for item in text):
                    if debug_parse_decklist == True: self.logger.info(f'SIDEBOARD: {text}')
                    
                    # If iteration is sideboard column header, future cards will be stored in sideboard dict
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
                    if debug_parse_decklist == True: self.logger.info(f'Count: {count}, Cardname: {cardname}')

           # Debug for results of decklist / extraction
            if print_parsed_decklist == True:
                self.logger.info('Decklist: ')
                self.logger.info('\tMain Deck: ')
                for key in main_deck: self.logger.info(f'\t\t {main_deck[key]} {key}')
                self.logger.info('\tSideboard: ')
                for key in sideboard: self.logger.info(f'\t\t {sideboard[key]} {key}')


        # ----- EXTRACT METADATA ------

        # Create parsed .html object
        metadata_results = parsed_html.find_all('div', class_='event_title')
      
        metadata_results_text = []

        # decks are organized within events, so may have divs with arrows for navigating between decks in event
        for item in metadata_results:
            if str(item.get_text()) == '→' or str(item.get_text()) == '←':
                continue
            else:
                metadata_results_text.append(item.get_text())
        
        # Extract Deck Author, Title, and Placement in Event
        place_title_author = metadata_results_text[1].split(' - ', 1)
        if debug_parse_metadata == True: self.logger.info(f'\nplace_title_author:\n{place_title_author}')

        place_title = place_title_author[0].split(" ", 1)
        if debug_parse_metadata == True: self.logger.info(f'\nplace_title:\n{place_title}')
        
        # Store deck data in dict
        deck_data['deck_title'] = place_title[1]
        deck_data['deck_format'] = parsed_html.find('div', class_='meta_arch').get_text()
        deck_data['placement'] = place_title[0]
        deck_data['deck_author'] = place_title_author[1]
    
        if print_deck_data == True:
            self.logger.info('Deck Data: ')
            for key in deck_data:
                self.logger.info(f'\t{key} {deck_data[key]}')

        

        # Extract other metadata (Event Date, Event Link)
        date_results = parsed_html.find('div', class_='meta_arch')
        
        date_text_results=[]
        
        for i in date_results.next_siblings:
            if isinstance(i, bs4.element.NavigableString):
                continue
            if isinstance(i, bs4.element.Tag):
                date_text_results.append(i.get_text())
    
        if debug_parse_metadata == True: 
            self.logger.info('date_text_results:') 
            for item in date_text_results:
                self.logger.info(f'\t{item}')


        # Set Event Data
        event_data['event_name'] = metadata_results_text[0]

        # Sometimes the div containing event date also has players in event '234 players - 1/2/21'
        if '-' in date_text_results[0]:
            event_data['event_date'] = date_text_results[0].split(' - ', 1)[1]
        else:
            event_data['event_date'] = date_text_results[0]

        event_data['event_format'] = parsed_html.find('div', class_='meta_arch').get_text()
        event_data['event_link'] = date_text_results[1]
        

        if print_event_data == True:
            self.logger.info(f'Event Data:')
            for key in event_data:
                self.logger.info(f'\t{key} {event_data[key]}')            


        # Instantiate item for export
        item = pageItem()
        

        # transfer scraped data to item for export
        item['decklist'] = main_deck
        item['sideboard'] = sideboard
        item['deck_data'] = deck_data
        item['event_data'] = event_data

        yield item

        # Find links and yield request objects to engine
        for href in response.xpath('//a/@href').getall():
          yield scrapy.Request(response.urljoin(href), self.parse)

    # Callback Function for pages without decklist
    def parse(self, response):

        # Find links and yield request objects to engine
        for href in response.xpath('//a/@href').getall():
            yield scrapy.Request(response.urljoin(href))
