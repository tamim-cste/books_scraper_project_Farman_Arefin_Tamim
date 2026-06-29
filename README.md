# Books Data Engineering System

A production-ready Scrapy web scraping pipeline that crawls [books.toscrape.com](https://books.toscrape.com), randomly selects 5 categories and 5 books per category, cleans the data, exports it to JSON, CSV, and XML, and stores it in a SQLite database. Deployable via Scrapyd and Docker.

---

## Tech Stack

- **Python 3.12** — Language
- **Scrapy 2.11** — Scraping framework
- **SQLite** — Database
- **Scrapyd** — Spider deployment server
- **Docker + Docker Compose** — Containerization

---

## Project Structure

```
books_scraper_project_Farman_Arefin_Tamim/
├── books_scraper/
│   ├── __init__.py
│   ├── items.py                  # BookItem schema
│   ├── settings.py               # Scrapy config, feeds, pipelines
│   ├── spiders/
│   │   └── books_spider.py       # Main spider
│   └── pipelines/
│       ├── cleaning.py           # Cleans price, availability, whitespace
│       └── database.py           # Saves to SQLite
├── database/                     # books.db generated here after run
├── output/                       # books.json / books.csv / books.xml
├── logs/                         # scrapy.log
├── Dockerfile
├── docker-compose.yml
├── entrypoint.sh
├── scrapy.cfg
├── scrapyd.conf
├── setup.py
└── requirements.txt
```

---

## Local Setup

### 1. Prerequisites

- Python 3.12
- pip

> If Python 3.12 is not installed:
> ```bash
> sudo add-apt-repository ppa:deadsnakes/ppa
> sudo apt update
> sudo apt install python3.12 python3.12-venv
> ```

### 2. Clone and install

```bash
git clone https://github.com/tamim-cste/books_scraper_project_Farman_Arefin_Tamim.git
cd books_scraper_project_Farman_Arefin_Tamim

python3.12 -m venv venv
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Run the spider

```bash
scrapy crawl books
```



## Docker Setup

### Prerequisites

- Docker
- Docker Compose

### Run with Docker

```bash
docker-compose up --build
```

This single command will:
1. Build the Docker image
2. Start Scrapyd
3. Deploy the project egg
4. Schedule and run the spider

Output files will appear in your local `output/` and `database/` folders via volume mount.

### Stop the container

```bash
docker-compose down
```

---

## Running Again (Fresh Run)

JSON, CSV, and XML are overwritten automatically on each run. However, the SQLite database **appends** new records. To start fresh:

```bash
rm -f database/books.db output/books.json output/books.csv output/books.xml
```

Then run locally or via Docker again.

---

## Output Format

Each scraped book contains these fields:

| Field | Type | Description |
|---|---|---|
| title | string | Book title |
| price | float | Price with currency symbol removed |
| availability | boolean | `true` = in stock, `false` = out of stock |
| product_url | string | URL to the book detail page |
| image_url | string | URL to the book cover image |
| category | string | Category name |
| scraped_at | timestamp | Time the record was inserted into DB |

---

## Scrapyd API (inside Docker)

Once the container is running, Scrapyd is accessible at `http://localhost:6800`.

```bash
# Check status
curl http://localhost:6800/daemonstatus.json

# List jobs
curl "http://localhost:6800/listjobs.json?project=books_scraper"

# Schedule spider manually
curl http://localhost:6800/schedule.json \
  -d project=books_scraper \
  -d spider=books
```
