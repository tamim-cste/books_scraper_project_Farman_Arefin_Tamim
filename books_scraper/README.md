# 📚 Enterprise Web Scraping Pipeline — Books Data Engineering System

A production-ready Scrapy application that crawls [books.toscrape.com](https://books.toscrape.com), extracts structured book data across all categories, and exports it to JSON, CSV, XML, and SQLite — deployable via Scrapyd and Docker.

---

## Features

- Dynamically discovers **all book categories** (no hardcoded URLs or names)
- Selects exactly **5 random books per category** on every run
- Extracts: `title`, `price`, `availability`, `product_url`, `image_url`, `category`
- Cleans data via a dedicated **Item Pipeline** (normalise text, strip currency, boolean availability)
- Exports to **JSON**, **CSV**, and **XML** simultaneously via Scrapy Feed Exports
- Persists all records to **SQLite** through a pipeline
- Fully **Dockerized** with a multi-stage `Dockerfile`
- Deployable via **Scrapyd** (schedule and monitor spiders via HTTP API)
- Follows **OOP, SOLID, and DRY** principles throughout

---

## Tech Stack

| Layer | Technology |
|---|---|
| Scraping Framework | Scrapy 2.11 |
| Language | Python 3.12 |
| Database | SQLite (via stdlib `sqlite3`) |
| Deployment | Scrapyd 2.4 + scrapyd-client |
| Containerization | Docker + Docker Compose |
| Data Adapter | itemadapter |

---

## Project Structure

```
books_scraper/
├── books_scraper/
│   ├── __init__.py
│   ├── items.py              # BookItem schema
│   ├── settings.py           # All Scrapy settings, feeds, pipelines
│   ├── spiders/
│   │   ├── __init__.py
│   │   └── books_spider.py   # Main crawler (BooksSpider)
│   └── pipelines/
│       ├── __init__.py
│       ├── cleaning.py       # CleaningPipeline (stage 1)
│       └── database.py       # SQLitePipeline (stage 2)
├── output/                   # Generated: books.json / .csv / .xml / .db
├── logs/                     # Generated: scrapy.log
├── Dockerfile
├── docker-compose.yml
├── scrapy.cfg                # Scrapyd deploy target
├── scrapyd.conf              # Scrapyd server config
├── setup.py                  # Required for egg packaging
├── requirements.txt
└── README.md
```

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────┐
│                   BooksSpider                       │
│                                                     │
│  parse()  ──► _collect_book_urls()  ──► paginate   │
│                       │                             │
│               _select_and_scrape()  (random 5)     │
│                       │                             │
│               _parse_book()  ──► BookItem{}         │
└───────────────────────┬─────────────────────────────┘
                        │ yields BookItem
                        ▼
          ┌─────────────────────────┐
          │    CleaningPipeline     │  strip ► normalize ► price→float ► avail→bool
          └────────────┬────────────┘
                       │
          ┌────────────▼────────────┐
          │     SQLitePipeline      │  INSERT into books table
          └────────────┬────────────┘
                       │
          ┌────────────▼────────────┐
          │    Scrapy Feed Exports  │  → books.json / books.csv / books.xml
          └─────────────────────────┘
```

---

## Installation Guide

### Prerequisites

- Python 3.12+
- pip
- Docker & Docker Compose (for containerized deployment)

### Local Setup

```bash
# 1. Clone the repository
git clone https://github.com/tamim-cste/books_scraper_project_Farman_Arefin_Tamim
cd books_scraper_project_Farman_Arefin_Tamim/books_scraper

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create required directories
mkdir -p output logs
```

---

## Running the Spider Locally

```bash
# From the project root (where scrapy.cfg lives)
scrapy crawl books
```

Output files will appear in the `output/` directory:

```
output/
├── books.json
├── books.csv
├── books.xml
└── books.db
```

Logs are written to `logs/scrapy.log`.

---

## Docker Setup Guide

### Build the image

```bash
docker build -t books_scraper .
```

### Run Scrapyd inside Docker

```bash
docker-compose up -d scrapyd
```

Scrapyd is now available at **http://localhost:6800**.

### Deploy the project and schedule the spider

```bash
# Deploy the egg to the running Scrapyd container
docker exec books_scrapyd scrapyd-deploy local -p books_scraper

# Schedule the spider via Scrapyd API
curl http://localhost:6800/schedule.json \
  -d project=books_scraper \
  -d spider=books
```

Or use the all-in-one command (builds, deploys, runs):

```bash
docker-compose up
```

---

## Scrapyd Deployment Guide

Scrapyd exposes a JSON API for spider management.

### Key endpoints

| Action | Method | Endpoint |
|---|---|---|
| Daemon status | GET | `/daemonstatus.json` |
| List projects | GET | `/listprojects.json` |
| List spiders | GET | `/listspiders.json?project=books_scraper` |
| Schedule spider | POST | `/schedule.json` |
| List jobs | GET | `/listjobs.json?project=books_scraper` |
| Cancel job | POST | `/cancel.json` |

### Example: schedule and monitor

```bash
# Schedule
curl http://localhost:6800/schedule.json \
  -d project=books_scraper \
  -d spider=books

# Check status (use jobid from schedule response)
curl "http://localhost:6800/listjobs.json?project=books_scraper"
```

---

## Output Format Description

### JSON (`output/books.json`)
Array of objects:
```json
[
  {
    "title": "A Light in the Attic",
    "price": 51.77,
    "availability": true,
    "product_url": "https://books.toscrape.com/catalogue/...",
    "image_url": "https://books.toscrape.com/media/cache/...",
    "category": "Poetry"
  }
]
```

### CSV (`output/books.csv`)
Standard comma-separated, UTF-8, with header row.

### XML (`output/books.xml`)
Standard Scrapy XML feed format with `<items>` root and `<item>` children.

---

## Database Configuration

- **Engine:** SQLite (file-based, zero-config)
- **File path:** `output/books.db` (configurable via `SQLITE_DB_PATH` in `settings.py`)
- **Table:** `books`

| Column | Type | Notes |
|---|---|---|
| id | INTEGER | Auto-increment primary key |
| title | TEXT | |
| price | REAL | Cleaned float |
| availability | INTEGER | 1 = in stock, 0 = not |
| product_url | TEXT | |
| image_url | TEXT | |
| category | TEXT | |

### Inspect the database

```bash
sqlite3 output/books.db "SELECT * FROM books LIMIT 5;"
```

---

## Design Decisions

- **Dynamic category discovery:** The spider reads category links from the DOM sidebar at runtime — no hardcoded URLs.
- **Pagination handled generically:** `_collect_book_urls` follows `li.next a` links recursively for any category depth.
- **random.sample for selection:** Guarantees exactly N unique books per category without repetition.
- **Pipeline separation:** `CleaningPipeline` and `SQLitePipeline` follow SRP — one transforms, one persists. Their priority order (100, 200) is enforced in `settings.py`.
- **Feed Exports via settings.py:** All three export formats are configured declaratively, keeping the spider clean.
- **Multi-stage Docker build:** Separates build-time (gcc, headers) and runtime (slim) dependencies, reducing the final image size.

---

## Known Limitations

- The spider is single-domain and targets `books.toscrape.com` only.
- SQLite is not suitable for high-concurrency writes; swap `SQLitePipeline` with a `PostgresPipeline` for production scale.
- No incremental/delta crawling — each run replaces output files (`overwrite: True`).
- Scrapyd does not support authentication out of the box; do not expose port 6800 publicly without a reverse proxy + auth layer.
