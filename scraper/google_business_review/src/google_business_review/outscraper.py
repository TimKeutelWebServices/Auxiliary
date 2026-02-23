"""Outscraper API client for fetching reviews."""

import os

from core.outscraper_client import PLACE_ID, fetch_place_data

REVIEWS_LIMIT = int(os.getenv("REVIEWS_LIMIT", "20"))


def fetch_reviews(cutoff_unix: int | None = None) -> list[dict]:
    """Fetch reviews for place."""
    if REVIEWS_LIMIT <= 0:
        return []

    params = {
        "query": PLACE_ID,
        "reviewsLimit": REVIEWS_LIMIT,
        "sort": "newest",
        "language": "de",
    }
    if cutoff_unix and cutoff_unix > 0:
        params["cutoff"] = cutoff_unix

    data = fetch_place_data(params)
    reviews = []
    for place in data:
        if isinstance(place, dict):
            reviews.extend(place.get("reviews_data", []))
    return reviews[:REVIEWS_LIMIT]
