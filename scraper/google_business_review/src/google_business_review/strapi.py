"""Strapi API client for storing reviews."""

from datetime import datetime, timezone
import os

from core.strapi_client import PLACE_ID, get, post, parse_datetime

REVIEWS_COLLECTION = os.getenv("STRAPI_REVIEWS_COLLECTION", "reviews")


def get_review_cutoff_unix() -> int:
    """Return Unix cutoff timestamp for review sync."""
    resp = get(
        REVIEWS_COLLECTION,
        {
            "filters[place_id][$eq]": PLACE_ID,
            "sort": "updatedAt:desc",
            "pagination[pageSize]": 1,
        },
    )
    if resp.status_code == 200 and resp.json().get("data"):
        updated_at = resp.json()["data"][0].get("updatedAt")
        if updated_at:
            return int(
                datetime.fromisoformat(
                    updated_at.replace("Z", "+00:00")
                ).timestamp()
            )
    return int(os.getenv("REVIEWS_CUTOFF_UNIX", "0"))


def store_review(raw: dict) -> None:
    """Push one review into Strapi."""
    review_id = str(raw.get("review_id", raw.get("review_link", "")))
    if not review_id:
        return

    payload = {
        "data": {
            "place_id": PLACE_ID,
            "review_id": review_id,
            "author_name": raw.get("author_title", ""),
            "rating": raw.get("review_rating"),
            "text": raw.get("review_text", ""),
            "review_url": raw.get("review_link", ""),
            "review_date": parse_datetime(raw.get("review_datetime_utc")),
            "raw": raw,
        }
    }

    resp = post(REVIEWS_COLLECTION, payload)
    if resp.status_code == 201:
        print(f"  ✓ {review_id[:40]}")
    elif resp.status_code == 400:
        print(f"  ↳ skip {review_id[:40]}")
