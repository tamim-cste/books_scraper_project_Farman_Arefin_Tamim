"""
SQLitePipeline – Stage 2 of the item processing pipeline.

Responsibilities:
  - Create the SQLite database and books table (if they don't exist)
  - Insert each cleaned BookItem as a row
  - Close the connection gracefully when the spider finishes
"""

import logging
import sqlite3

from itemadapter import ItemAdapter
from scrapy import Spider
from scrapy.crawler import Crawler

logger = logging.getLogger(__name__)

# SQL statements – kept as module-level constants (DRY)
CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS books (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    title        TEXT    NOT NULL,
    price        REAL    NOT NULL,
    availability INTEGER NOT NULL,   -- 1 = True, 0 = False
    product_url  TEXT    NOT NULL,
    image_url    TEXT    NOT NULL,
    category     TEXT    NOT NULL,
    scraped_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
"""

INSERT_SQL = """
INSERT INTO books (title, price, availability, product_url, image_url, category)
VALUES (:title, :price, :availability, :product_url, :image_url, :category)
"""


class SQLitePipeline:
    """
    Persists BookItems to a SQLite database.

    Database path is read from settings (SQLITE_DB_PATH).
    Uses context-managed connections for safety.
    """

    def __init__(self, db_path: str):
        """
        Initialise with the resolved database path.

        Args:
            db_path: File system path for the SQLite database file.
        """
        self.db_path = db_path
        self.connection: sqlite3.Connection | None = None
        self.cursor: sqlite3.Cursor | None = None

    # ── Scrapy lifecycle hooks ─────────────────────────────────────────────

    @classmethod
    def from_crawler(cls, crawler: Crawler) -> "SQLitePipeline":
        """
        Factory method – Scrapy calls this to instantiate the pipeline.

        Reads SQLITE_DB_PATH from settings.
        """
        db_path = crawler.settings.get("SQLITE_DB_PATH", "output/books.db")
        return cls(db_path=db_path)

    def open_spider(self, spider: Spider) -> None:
        """Open the database connection and ensure the schema exists."""
        logger.info("SQLitePipeline: opening database at %s", self.db_path)
        self.connection = sqlite3.connect(self.db_path)
        self.cursor = self.connection.cursor()
        self.cursor.execute(CREATE_TABLE_SQL)
        self.connection.commit()

    def close_spider(self, spider: Spider) -> None:
        """Commit any pending transactions and close the connection."""
        if self.connection:
            self.connection.commit()
            self.connection.close()
            logger.info("SQLitePipeline: database connection closed")

    def process_item(self, item, spider: Spider):
        """
        Insert a single BookItem into the database.

        Args:
            item:   A cleaned BookItem.
            spider: The active spider (for logging context).

        Returns:
            The unchanged item so downstream pipelines can process it.
        """
        adapter = ItemAdapter(item)
        row = {
            "title":        adapter["title"],
            "price":        adapter["price"],
            "availability": int(adapter["availability"]),  # SQLite has no BOOLEAN
            "product_url":  adapter["product_url"],
            "image_url":    adapter["image_url"],
            "category":     adapter["category"],
        }
        try:
            self.cursor.execute(INSERT_SQL, row)
        except sqlite3.Error as exc:
            logger.error("DB insert failed for %r: %s", adapter.get("title"), exc)

        return item
