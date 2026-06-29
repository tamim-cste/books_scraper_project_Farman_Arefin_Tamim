# Books Scraper

Scrapy project that crawls [books.toscrape.com](https://books.toscrape.com), cleans the scraped data, and exports it to JSON, CSV, XML, and SQLite.

## Local setup

### Requirements

- Python 3.12+
- `pip`

### Install

```bash
git clone https://github.com/tamim-cste/books_scraper_project_Farman_Arefin_Tamim
cd books_scraper_project_Farman_Arefin_Tamim

python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

pip install -r requirements.txt
mkdir -p output logs database
```

### Run

```bash
scrapy crawl books
```

## Output

- JSON: `output/books.json`
- CSV: `output/books.csv`
- XML: `output/books.xml`
- SQLite database: `database/books.db`
- Log file: `logs/scrapy.log`

## Optional Docker run

```bash
docker compose up --build
```

If you want Scrapyd deployment details or a longer project description, they can be added back as a separate section later.
