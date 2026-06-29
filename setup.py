"""
setup.py – required by scrapyd-deploy to build the project egg.
"""

from setuptools import setup, find_packages

setup(
    name="books_scraper",
    version="1.0.0",
    description="Enterprise Web Scraping Pipeline – Books Data Engineering System",
    author="Farman Arefin Tamim",
    packages=find_packages(),
    entry_points={"scrapy": ["settings = books_scraper.settings"]},
    install_requires=[
        "scrapy>=2.11",
        "itemadapter>=0.9",
    ],
)
