# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from sqlalchemy import *


# Pipeline where item containing decklist, event, and deck data will be submitted to database
class DecklistCrawlerPipeline:
    def process_item(self, item, spider):

    	print_database = True

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

	    #decklists_statement = insert(cards).values(item[])

	    # Instantiate objects to receive processed data
	    #event_data = dict.fromkeys([c.name for c in events.columns])
	    #deck_data = dict.fromkeys([c.name for c in decks.columns])
	    #decklist_data = dict.fromkeys([c.name for c in decklists.columns])


	    # assign item subdicts to local dicts to make adapting database code easier
	    	# pretty sure references makes this pretty memory efficient, but should double-check
	    event_data = item['event_data']
	    deck_data = item['deck_data']
	    decklist_data = item['decklist_data']

	    # ---- Load Event Data ----

		# if print_event_data == True: 
		#     print("Event data: ")
		#     for key in event_data: print("\t", key, ": ", event_data[key])

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
		        connection.commit()
		    #print("Recorded event data")

		    with engine.connect() as connection:
		        event_query_results = connection.execute(event_query_statement)
		        connection.commit()

		    event_results = event_query_results.all()
		    deck_data['event_id'] = [row[0] for row in event_results][0]

		elif eventExists:
		    # print("Event already recorded")
		    deck_data['event_id'] = [row[0] for row in event_results][0]

		else:
		    self.logger.info("Warning: Found ", len(event_results), " matching events")

		# print("Retrieved event_id: ", deck_data['event_id'])


		# ---- Load Deck Data ----

		# if print_deck_data == True:
		#     print("Deck Data: ")
		#     for key in deck_data: print("\t", key, ": ", deck_data[key])

		# Query if Deck exists already
		deck_query_statement = select(decks.c.deck_id).where(decks.c.event_id == deck_data['event_id'] and decks.c.deck_author == deck_data['deck_author'])
		with engine.connect() as connection:
		    deck_query_results = connection.execute(deck_query_statement)
		    connection.commit()

		deck_results = deck_query_results.all()
		deckExists = len(deck_results) != 0

		# Load deck_data into Database if necessary, then get deck_id
		if deckExists:
		    decklist_data['deck_id'] = [row[0] for row in deck_results][0]
		    
		    if print_database == True: self.logger.info(f'Deck already recorded, retrieved deck_id {decklist_data['deck_id']}')

		elif not deckExists:
		    deck_insert_statement = insert(decks).values(deck_data)

		    with engine.connect() as connection:
		        deck_insert_results = connection.execute(deck_insert_statement)
		        connection.commit()

		    decklist_data['deck_id'] = deck_insert_results.inserted_primary_key[0]

		    if print_database == True: self.logger.info(f'Loaded deck_data to database\nRetrieved deck_id {decklist_data['deck_id']}')

		else:
		    if print_database == True: self.logger.info(f'Duplicate Deck data found')


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
		        self.logger.info(card_row)
		 
		# Submit decklist to database
		decklist_insert_statement = insert(decklists).values(decklist_data_values)
		with engine.connect() as connection:
		    decklist_insert_results = connection.execute(decklist_insert_statement)
		    connection.commit()


		# Add some validation code to make sure data got submitted OK

    	raise DropItem
