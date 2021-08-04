
# ---------------------------------------------------
# Train an LDA model using a Gensim corpus

from gensim.models.ldamodel import LdaModel
from gensim.corpora.dictionary import Dictionary
import pandas as pd
import sys
from dotenv import load_dotenv
import os

# ---------------------------
# Query Database for dataset
# ---------------------------

load_dotenv()
database_url = os.environ.get('DATABASE_URL')
database_username = os.environ.get('DATABASE_USERNAME')
database_password = os.environ.get('DATABASE_PASSWORD')

connection_string = ("mysql+mysqldb://" + database_username + ":" + database_password + "@" + database_url + "/scryfall")

# Query for decklist entries and deck format for Modern decks within a set range of deck_id 
decks_query = "SELECT decklists.deck_id, decklists.card_name, decks.deck_format FROM scryfall.decklists INNER JOIN scryfall.decks ON (decks.deck_id = decklists.deck_id) WHERE decks.deck_format LIKE '%Modern%' AND decks.deck_id > 150 AND decks.deck_id < 2150;"

# Create DataFrame from SQL Query
df = pd.read_sql(decks_query, connection_string)

# -----------------------------
# Pre-Process Data
# -----------------------------


# Get Unique Deck_ids
select_deck_ids = df['deck_id'].unique()
unique_cards= len(df['card_name'].unique())

print(f'Unique Cards: {unique_cards}')
print(f'Unique Decks: {len(select_deck_ids)}')

# Instantiate list of decklists
list_of_decklists = [df['card_name'][df['deck_id']==deck_id].to_list() for deck_id in select_deck_ids]

# Create dictionary and corpus of documents from list_of_decklists
common_dictionary = Dictionary(list_of_decklists)
common_corpus = [common_dictionary.doc2bow(decklist) for decklist in list_of_decklists]


# --------------------------------
# Train Model and Display Results 
# --------------------------------

# Number of topics/archetypes for model to fit
archetypes = 30 

# alpha controls 
alpha_prior = [1.0 / archetypes] * archetypes
beta_prior = [1.0 / archetypes] * unique_cards

passes = 30
chunk_size = 50

# Train the model on the corpus. (later can add id2word=common_dictionary as a parameter to display results better)
ldamodel = LdaModel(common_corpus, num_topics=archetypes, chunksize=chunk_size, iterations=passes, alpha='auto', eta=beta_prior)



# Iterate through list of [topic ids, weights*card ids]
for topic in ldamodel.print_topics(num_topics=archetypes, num_words=15):

    topic_id, topic_cards = topic

    assert type(topic_id) == int, "Received non-int value for topic_id"
    assert type(topic_cards) == str, "Received non-str value for topic_cards"

    print(f'Topic ID: {topic_id}')

    # split string of value/card pairs into list
    split_cards = topic_cards.split(' + ')

    for card in split_cards:
        card_value, card_id = card.split('*')
        
        card_id = int(card_id.strip('\"'))

        print(f'\t{card_value}, {common_dictionary[card_id]}')

        

            


#print(common_dictionary[2])

#my_dict = {'Topic_' + str(i): [token for token, score in ldamodel.show_topic(i, topn=10)] for i in range(0, ldamodel.num_topics)}
#print(my_dict)

save_or_load = False
if save_or_load == True:

    # ---------------------------------------------------
    # Save a model to disk, or reload a pre-trained model

    from gensim.test.utils import datapath

    # Save model to disk.
    temp_file = datapath("model")
    lda.save(temp_file)

    # Load a potentially pretrained model from disk.
    lda = LdaModel.load(temp_file)

