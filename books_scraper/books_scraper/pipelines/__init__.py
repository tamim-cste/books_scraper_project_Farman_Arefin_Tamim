"""
Scrapy Item Pipelines for the Books Data Engineering System.

Pipeline execution order (configured in settings.py):
  1. CleaningPipeline  (priority 100) – clean and normalise fields
  2. SQLitePipeline    (priority 200) – persist to SQLite
"""
