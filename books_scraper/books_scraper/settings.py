"""
Scrapy settings for the Books Data Engineering System.

Configures:
  - Spider behaviour (concurrency, delays, middlewares)
  - Item Pipelines (cleaning + SQLite persistence)
  - Feed Exports  (JSON, CSV, XML)
  - Logging
"""

from pathlib import Path

# ─── Project identity ────────────────────────────────────────────────────────
BOT_NAME = "books_scraper"
SPIDER_MODULES = ["books_scraper.spiders"]
NEWSPIDER_MODULE = "books_scraper.spiders"

# ─── Crawl settings ──────────────────────────────────────────────────────────
ROBOTSTXT_OBEY = True
CONCURRENT_REQUESTS = 8
CONCURRENT_REQUESTS_PER_DOMAIN = 8
DOWNLOAD_DELAY = 0.5
COOKIES_ENABLED = False
TELNETCONSOLE_ENABLED = False

DEFAULT_REQUEST_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en",
}

# ─── Item Pipelines ──────────────────────────────────────────────────────────
# Order: CleaningPipeline must run before DatabasePipeline
ITEM_PIPELINES = {
    "books_scraper.pipelines.cleaning.CleaningPipeline": 100,
    "books_scraper.pipelines.database.SQLitePipeline": 200,
}

# ─── Feed Exports ────────────────────────────────────────────────────────────
OUTPUT_DIR = Path("output")

FEEDS = {
    OUTPUT_DIR / "books.json": {
        "format": "json",
        "encoding": "utf8",
        "indent": 2,
        "overwrite": True,
    },
    OUTPUT_DIR / "books.csv": {
        "format": "csv",
        "encoding": "utf8",
        "overwrite": True,
    },
    OUTPUT_DIR / "books.xml": {
        "format": "xml",
        "encoding": "utf8",
        "overwrite": True,
    },
}

# ─── Database ────────────────────────────────────────────────────────────────
SQLITE_DB_PATH = "database/books.db"

# ─── Logging ─────────────────────────────────────────────────────────────────
LOG_LEVEL = "INFO"
LOG_FILE = "logs/scrapy.log"
LOG_FILE_APPEND = False

# ─── Retry / Timeout ─────────────────────────────────────────────────────────
RETRY_TIMES = 3
DOWNLOAD_TIMEOUT = 30

# ─── Twisted reactor (required for some environments) ────────────────────────
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
