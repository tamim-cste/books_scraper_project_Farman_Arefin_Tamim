"""
Scrapy Item definitions for the Books Data Engineering System.
Defines the data schema for scraped book records.
"""

import scrapy


class BookItem(scrapy.Item):
    """
    Represents a single book record scraped from books.toscrape.com.

    Fields:
        title       -- Book title (string)
        price       -- Book price as a float (currency symbol removed)
        availability -- Boolean indicating in-stock status
        product_url -- Absolute URL to the book's detail page
        image_url   -- Absolute URL to the book cover image
        category    -- Category name the book belongs to
    """

    title = scrapy.Field()
    price = scrapy.Field()
    availability = scrapy.Field()
    product_url = scrapy.Field()
    image_url = scrapy.Field()
    category = scrapy.Field()
