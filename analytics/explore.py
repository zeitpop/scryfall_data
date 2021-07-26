import pandas as pd 
from sqlalchemy import *
from dotenv import load_dotenv
import os, gensim, numpy
from gensim import corpora
from six import iteritems
# Import database credentials
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

# Query for decklist entries and deck format for Modern decks within a set range of deck_id 
decks_query = "SELECT decklists.deck_id, decklists.card_name, decks.deck_format FROM scryfall.decklists INNER JOIN scryfall.decks ON (decks.deck_id = decklists.deck_id) WHERE decks.deck_format LIKE '%Modern%' AND decks.deck_id > 150 AND decks.deck_id < 1150;"

# Create DataFrame from SQL Query
df = pd.read_sql(decks_query, connection_string)

# Get Unique Deck_ids
select_deck_ids = df['deck_id'].unique()

# Construct Corpora Dictionary from list of unique card_names
unique_cards = df['card_name'].unique()
unique_cardlist = [[]]
for item in unique_cards:

    unique_cardlist.append([item])

# print(unique_cardlist)

#dictionary = corpora.Dictionary(unique_cardlist)

# Construct.... Corpus of documents? 
list_of_decklists = [[]]
for id in select_deck_ids:
    filter_matching_ids = (df['deck_id'] == id)
    given_deck = df[filter_matching_ids]
  
    deck_string = ''
    for card in given_deck['card_name'].tolist():
        deck_string += card
    list_of_decklists.append(deck_string)


# Next we create a gensim Corpus. Instead of having a bag of words (cards) model, we take note how many times each card appears in a deck and "uncompress" the decklist description.

# In [5]:
#import numpy as np
#In [6]:
#class MyCorpus(object):
#    def __iter__(self):
#        for line in open('Modern.htm'):
#            decklist = line.replace("\"", "") # remove start and end tokens            
#            decklist = re.split(r"([\d]+)", decklist) # split by numbers and card names
#            decklist = [x.strip() for x in decklist] # remove whitespace
#            decklist = filter(None, decklist) # remove empty words
#            cleaned_decklist = [] 
#            for i in range(len(decklist)/2): # remove numbers, add multiplicities of cards
#                for j in range(int(decklist[i*2])):
#                    cleaned_decklist.append(decklist[i*2+1])
#           yield dictionary.doc2bow(cleaned_decklist)
#corpus_memory_friendly = MyCorpus()

dictionary = corpora.Dictionary(unique_cardlist)

#dictionary = corpora.Dictionary(list_of_decklists)
#once_ids = [tokenid for tokenid, docfreq in iteritems(dictionary.dfs) if docfreq == 1]
#dictionary.filter_tokens(once_ids)  # remove cards that appear only once
#dictionary.compactify()

archetypes = 10

# Control random seed as model is stochastic in case you want to be able to reproduce results
# np.random.seed(1)

#The "Latent Dirichlet" part of the method name comes from the assumption that the latent priors on the per-archetype card distribution and per-decklist archetype distributions are Dirichlet. This allows us to steer the learning of the model.

#By incorporating such priors, we can tell the model how we believe the data actually looks like. If we have a large number of archetypes and are confident that each decklist only falls under one archetype, then setting a low alpha indicates that we prefer each decklist to belong to few, dominating archetypes. We can similarly control the archetype-card sparsity with beta.

alpha_prior = [1.0 / archetypes] * archetypes
beta_prior = [1.0 / archetypes] * len(unique_cards)


# We finally train the model. This could take a couple of minutes.
iterations = 30
lda = gensim.models.ldamodel.LdaModel(corpus=list_of_decklists, id2word=dictionary, num_topics=archetypes, passes=iterations, alpha = alpha_prior, eta = beta_prior)

number_of_top_cards = 16
archetypes_to_inspect = 3
for i in range(archetypes_to_inspect):
    print(("Archetype %i \n %s \n") % (i, lda.print_topic(i, topn=number_of_top_cards)))






