"""Strapi API client for storing opening hours."""

import os

from core.strapi_client import PLACE_ID, post

OPENINGHOURS_COLLECTION = os.getenv("STRAPI_OPENINGHOURS_COLLECTION", "openinghours")


def store_openinghours(data: dict) -> None:
    """Push opening hours into Strapi."""
    payload = {
        "data": {
            "place_id": PLACE_ID,
            "opening_hours": data.get("opening_hours"),
            "raw": data.get("raw"),
        }
    }
    resp = post(OPENINGHOURS_COLLECTION, payload)
    if resp.status_code == 201:
        print("  ✓ opening hours stored")
