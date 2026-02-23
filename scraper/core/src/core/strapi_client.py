"""Strapi API client — shared HTTP helpers."""

from datetime import datetime, timezone
import os

import requests

STRAPI_URL = os.environ.get("STRAPI_URL", "").rstrip("/")
STRAPI_TOKEN = os.environ.get("STRAPI_TOKEN", "")
PLACE_ID = os.environ.get("GOOGLE_PLACE_ID", "")

HEADERS = {
    "Authorization": f"Bearer {STRAPI_TOKEN}",
    "Content-Type": "application/json",
}


def post(collection: str, payload: dict) -> requests.Response:
    """POST data to a Strapi collection."""
    return requests.post(
        f"{STRAPI_URL}/api/{collection}",
        headers=HEADERS,
        json=payload,
        timeout=15,
    )


def get(collection: str, params: dict | None = None) -> requests.Response:
    """GET data from a Strapi collection."""
    return requests.get(
        f"{STRAPI_URL}/api/{collection}",
        headers=HEADERS,
        params=params or {},
        timeout=15,
    )


def parse_datetime(raw: str | int | float | None) -> str | None:
    """Convert datetime to ISO format."""
    if not raw:
        return None
    try:
        if isinstance(raw, (int, float)):
            ts = int(raw) if int(raw) < 10_000_000_000 else int(raw / 1000)
            return datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()
        return datetime.fromisoformat(
            str(raw).replace("Z", "+00:00").replace(" UTC", "+00:00")
        ).isoformat()
    except (ValueError, TypeError):
        return None
