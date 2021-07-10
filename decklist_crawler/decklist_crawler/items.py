# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from sqlalchemy import *




class DecklistCrawlerItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()

    sideboard = scrapy.Field()
    main_deck = scrapy.Field()
    event_data = scrapy.Field()
    deck_data = scrapy.Field()

# class Product(scrapy.Item):
#     name = scrapy.Field()
#     price = scrapy.Field()
#     stock = scrapy.Field()
#     tags = scrapy.Field()
#     last_updated = scrapy.Field(serializer=str)