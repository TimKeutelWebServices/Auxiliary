"""Outscraper API client for fetching opening hours."""

from core.outscraper_client import PLACE_ID, fetch_place_data


def fetch_opening_hours() -> dict | None:
    """Fetch opening hours for place using Outscraper."""
    params = {
        "query": PLACE_ID,
        "fields": "working_hours",
        "limit": 1,
        "drop_duplicates": True,
        "ignore_paused": True,
        "extract_emails": False,
        "extract_socials": False,
    }

    data = fetch_place_data(params)

    if data and isinstance(data, list) and len(data) > 0:
        place_data = data[0]

        if "working_hours" in place_data:
            return {
                "opening_hours": place_data["working_hours"],
                "raw": place_data,
            }

    return None
