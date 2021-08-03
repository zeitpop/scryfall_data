# Example from: https://github.com/hlynurd/lda-for-magic/blob/master/lda-mtg-notebook.ipynb

import os, gensim, numpy, sys
from gensim import corpora
from six import iteritems

with open('Modern.htm', 'r') as f:
    print(f.readline())

import gensim
import re 
from six import iteritems

dictionary = gensim.corpora.Dictionary([x.strip() for x in re.split(r"[\d]+", line.replace("\"", ""))] for line in open('Modern.htm'))
once_ids = [tokenid for tokenid, docfreq in iteritems(dictionary.dfs) if docfreq == 1]
dictionary.filter_tokens(once_ids)  # remove cards that appear only once
dictionary.compactify()  # remove gaps in id sequence after words that were removed

unique_cards = len(dictionary.keys())
print(unique_cards)

import numpy as np


class MyCorpus(object):
    def __iter__(self):
        for line in open('Modern.htm'):
            decklist = line.replace("\"", "") # remove start and end tokens            
            decklist = re.split(r"([\d]+)", decklist) # split by numbers and card names
            decklist = [x.strip() for x in decklist] # remove whitespace
            decklist = filter(None, decklist) # remove empty words
            cleaned_decklist = [] 
            for i in range(len(decklist)/2): # remove numbers, add multiplicities of cards
                for j in range(int(decklist[i*2])):
                    cleaned_decklist.append(decklist[i*2+1])
            yield dictionary.doc2bow(cleaned_decklist)
corpus_memory_friendly = MyCorpus()



archetypes = 30
np.random.seed(1)

alpha_prior = [1.0 / archetypes] * archetypes
beta_prior = [1.0 / archetypes] * unique_cards

iterations = 30
lda = gensim.models.ldamodel.LdaModel(corpus=corpus_memory_friendly, id2word=dictionary, num_topics=archetypes, passes=iterations, alpha = alpha_prior, eta = beta_prior)