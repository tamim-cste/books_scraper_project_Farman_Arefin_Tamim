"""
CleaningPipeline – Stage 1 of the item processing pipeline.

Responsibilities:
  - Strip leading/trailing whitespace from all string fields
  - Normalize text (collapse internal whitespace)
  - Remove currency symbols from the price field
  - Convert price to float
  - Normalize availability to a boolean value
"""

import logging
import re

from itemadapter import ItemAdapter

logger = logging.getLogger(__name__)


class CleaningPipeline:
    """
    Cleans and normalises BookItem fields before downstream processing.

    Follows the Single Responsibility Principle: this pipeline only
    transforms data; it does not persist anything.
    """

    # ── Non-numeric characters to strip from price ─────────────────────────
    # Strips everything except digits and decimal point.
    # More robust than a currency symbol list — handles encoding artifacts
    # like "Â£" (UTF-8 mis-decoded £) that a symbol list would miss.
    PRICE_STRIP_PATTERN = re.compile(r"[^\d.]")

    def process_item(self, item, spider):
        """
        Process a single BookItem through all cleaning steps.

        Args:
            item:   The BookItem yielded by the spider.
            spider: The active spider instance (used for logging context).

        Returns:
            The cleaned BookItem.
        """
        adapter = ItemAdapter(item)

        self._strip_whitespace(adapter)
        self._clean_price(adapter, spider)
        self._normalise_availability(adapter)

        return item

    # ── Private helpers ────────────────────────────────────────────────────

    def _strip_whitespace(self, adapter: ItemAdapter) -> None:
        """Strip and collapse whitespace on every string field."""
        for field_name in adapter.field_names():
            value = adapter.get(field_name)
            if isinstance(value, str):
                # Strip outer whitespace then collapse internal runs
                adapter[field_name] = " ".join(value.split())

    def _clean_price(self, adapter: ItemAdapter, spider) -> None:
        """
        Remove all non-numeric characters and convert price to float.

        Uses re.sub(r"[^\\d.]", "") instead of a fixed currency symbol list
        so that encoding artifacts (e.g. "Â£" for £) are also handled
        transparently.

        On failure, sets price to 0.0 and logs a warning.
        """
        raw = adapter.get("price", "")
        cleaned = self.PRICE_STRIP_PATTERN.sub("", str(raw))
        try:
            adapter["price"] = float(cleaned)
        except (ValueError, TypeError):
            logger.warning(
                "Could not parse price %r for book %r; defaulting to 0.0",
                raw,
                adapter.get("title"),
            )
            adapter["price"] = 0.0

    def _normalise_availability(self, adapter: ItemAdapter) -> None:
        """
        Convert availability text to a boolean.

        'In stock' (case-insensitive) → True
        Any other value              → False
        """
        raw = adapter.get("availability", "")
        adapter["availability"] = isinstance(raw, str) and "in stock" in raw.lower()
