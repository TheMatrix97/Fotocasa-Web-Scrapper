# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class PropertyItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()


    # Property
    url = scrapy.Field()
    title = scrapy.Field()
    location = scrapy.Field()
    neigborhood = scrapy.Field()
    body = scrapy.Field()
    type = scrapy.Field()

    # Price
    current_price = scrapy.Field()
    last_price = scrapy.Field()
    area_market_price = scrapy.Field()
    square_meters = scrapy.Field()

    # Details
    tags = scrapy.Field()
    bedrooms = scrapy.Field()
    bathrooms = scrapy.Field()
    certification_status = scrapy.Field()
    consumption = scrapy.Field()
    emissions = scrapy.Field()

    # Multimedia
    main_image_url = scrapy.Field()


    # Agents
    seller_logo = scrapy.Field()
    seller_name = scrapy.Field()
    ref_agent = scrapy.Field()
    phone_number = scrapy.Field()

