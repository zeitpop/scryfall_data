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
#            'https://mtgtop8.com/format?f=ST',
#            'https://mtgtop8.com/format?f=HI',
            ]

    rules = (

        # Extract Links matching the deck URL pattern and extract deck items
        Rule(LinkExtractor(allow=('mtgtop8.com/event?', )), callback='parse_decklist'),

        Rule(LinkExtractor(deny=('/topcards?', '/archetype?' ))),  

        # Non-deck sites
        Rule(LinkExtractor(), callback = 'parse'),

    )

    def parse_decklist(self, response):
        
        # Debugging
        
        print_maindeck = False
        print_sideboard = False
        print_skipped_column_headers = False
        print_event_data = False
        print_deck_data = False
        print_decklist_data = False
        print_database = False
        exec_without_commit = False


        # Instantiate
        main_deck = {}
        sideboard = {}
        
        ## Create database engine object

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
        
        # self.logger.info(type(parsed_html))
        # self.logger.info(type(response.text))

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
            self.logger.info('Main Deck: ')
            for key in main_deck: self.logger.info('\t',main_deck[key], ' ', key)

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
        
        ###############################################################
        # 

        item = [main_deck, sideboard, deck_data, event_data]

        yield item

        for href in response.xpath('//a/@href').getall():
          yield scrapy.Request(response.urljoin(href), self.parse)

    def parse(self, response):

        for href in response.xpath('//a/@href').getall():
            yield scrapy.Request(response.urljoin(href))
