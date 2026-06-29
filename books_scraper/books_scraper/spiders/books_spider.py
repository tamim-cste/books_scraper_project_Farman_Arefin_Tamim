"""
BooksSpider – Core crawler for books.toscrape.com

Strategy
--------
1. Start at the homepage and discover all category links dynamically.
2. For each category, collect every book URL (handling pagination).
3. Randomly select exactly 5 book URLs from the full list.
4. Visit each selected book detail page and yield a BookItem.

Design decisions
----------------
- No hardcoded category names or URLs.
- Pagination is handled generically for every category.
- random.sample is used so the selection is truly random each run.
- All URL resolution uses response.urljoin() to handle relative paths safely.
"""

import logging
import random
from typing import Generator, Iterable
from urllib.parse import urljoin

import scrapy
from scrapy.http import HtmlResponse, Response

from books_scraper.items import BookItem

logger = logging.getLogger(__name__)

BOOKS_PER_CATEGORY: int = 5


class BooksSpider(scrapy.Spider):
    """
    Spider that crawls books.toscrape.com and extracts book data
    from every category, selecting 5 random books per category.
    """

    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/index.html"]

    def parse(self, response: HtmlResponse) -> Generator:
        """
        Entry point – parse the homepage and dispatch category crawls.

        Discovers all category links from the left-hand navigation sidebar,
        then randomly selects 5 categories to scrape.

        Args:
            response: Scrapy response for the homepage.

        Yields:
            Scrapy Request objects for each selected category page.
        """
        category_links = list(response.css(
            "div.side_categories ul li ul li a"
        ))

        if not category_links:
            logger.error("No category links found – page structure may have changed.")
            return

        category_links = random.sample(category_links, min(5, len(category_links)))
        logger.info("Randomly selected %d categories to scrape", len(category_links))

        for link in category_links:
            category_name = link.css("::text").get("").strip()
            category_url = response.urljoin(link.attrib["href"])

            logger.debug("Queueing category: %s -> %s", category_name, category_url)

            yield scrapy.Request(
                url=category_url,
                callback=self._collect_book_urls,
                cb_kwargs={"category": category_name, "book_urls": []},
            )

    def _collect_book_urls(
        self,
        response: HtmlResponse,
        category: str,
        book_urls: list[str],
    ) -> Generator:
        """
        Collect all book URLs within a category, following pagination.

        Args:
            response:   Scrapy response for the current category page.
            category:   Human-readable category name.
            book_urls:  Accumulated list of book URLs (grows across pages).

        Yields:
            - Request to the next page (if pagination exists).
            - Delegates to _select_and_scrape once all pages collected.
        """
        # Each book article has an <h3><a href="..."> pointing to the detail page
        page_book_links = response.css("article.product_pod h3 a::attr(href)").getall()
        for href in page_book_links:
            book_urls.append(response.urljoin(href))

        logger.debug(
            "Category '%s': collected %d URLs so far (page: %s)",
            category,
            len(book_urls),
            response.url,
        )

        # Follow 'next' pagination button if present
        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield scrapy.Request(
                url=response.urljoin(next_page),
                callback=self._collect_book_urls,
                cb_kwargs={"category": category, "book_urls": book_urls},
            )
        else:
            # All pages visited – proceed with random selection
            yield from self._select_and_scrape(category, book_urls)

    def _select_and_scrape(
        self,
        category: str,
        book_urls: list[str],
    ) -> Generator:
        """
        Randomly select up to BOOKS_PER_CATEGORY URLs and request detail pages.

        If a category has fewer books than BOOKS_PER_CATEGORY, all books
        are scraped (no error – edge case handled gracefully).

        Args:
            category:  Human-readable category name.
            book_urls: Complete list of book URLs in the category.

        Yields:
            Scrapy Request objects for each selected book detail page.
        """
        total = len(book_urls)
        sample_size = min(BOOKS_PER_CATEGORY, total)
        selected = random.sample(book_urls, sample_size)

        # logger.info(
        #     "Category '%s': %d books found, selected %d",
        #     category,
        #     total,
        #     sample_size,
        # )

        logger.info(
              "Category '%s': %d books found, randomly selected %d for scraping",
               category,
               total,
               sample_size,
        )

        for url in selected:
            yield scrapy.Request(
                url=url,
                callback=self._parse_book,
                cb_kwargs={"category": category},
            )

    def _parse_book(self, response: HtmlResponse, category: str) -> BookItem:
        """
        Extract all required fields from a book detail page.

        Args:
            response: Scrapy response for a book detail page.
            category: Category name passed via cb_kwargs.

        Yields:
            A populated BookItem.
        """
        item = BookItem()

        item["title"] = response.css("div.product_main h1::text").get("").strip()
        item["price"] = response.css("p.price_color::text").get("").strip()
        item["availability"] = (
            response.css("p.availability::text").getall()[-1].strip()
            if response.css("p.availability::text").getall()
            else ""
        )
        item["product_url"] = response.url
        item["image_url"] = response.urljoin(
            response.css("div.item.active img::attr(src)").get("")
        )
        item["category"] = category

        logger.debug("Scraped: %s [%s]", item["title"], category)

        yield item
