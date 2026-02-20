from datetime import datetime


def normalize_reviews(raw_reviews: list[dict], place_id: str) -> list[dict]:
    if not raw_reviews:
        return []
    
    normalized = []
    for item in raw_reviews:
        if not isinstance(item, dict):
            continue
        # Support multiple field name variations
        review_id = str(
            item.get("review_id") or 
            item.get("reviewId") or 
            item.get("google_id") or 
            ""
        )
        if not review_id:
            continue
        normalized.append(
            {
                "place_id": place_id,
                "review_id": review_id,
                "author_name": item.get("author_name") or item.get("author_title"),
                "rating": item.get("review_rating") or item.get("rating"),
                "text": item.get("review_text") or item.get("text"),
                "review_url": item.get("review_link") or item.get("review_url"),
                "review_date": _parse_date(
                    item.get("review_timestamp") or 
                    item.get("published_at") or 
                    item.get("date")
                ),
                "raw": item,
            }
        )
    return normalized


def normalize_opening_hours(raw_places: list[dict], place_id: str) -> dict | None:
    if not raw_places:
        return None
    
    # Handle nested structure if API returns list of lists or list of dicts
    item = raw_places[0]
    if isinstance(item, list):
        if not item:
            return None
        item = item[0]
    
    if not isinstance(item, dict):
        return None
    
    # Check multiple possible field names for opening hours
    opening_hours = (
        item.get("working_hours") or 
        item.get("opening_hours") or 
        item.get("openingHours") or
        item.get("other_hours")
    )
    if not opening_hours:
        return None
    return {
        "place_id": place_id,
        "opening_hours": opening_hours,
        "raw": item,
    }


def _parse_date(value: str | int | None) -> str | None:
    if not value:
        return None
    try:
        # Handle Unix timestamp (integer)
        if isinstance(value, int):
            return datetime.fromtimestamp(value).isoformat()
        # Handle ISO format string
        if isinstance(value, str):
            return datetime.fromisoformat(value.replace("Z", "+00:00")).isoformat()
        return None
    except (ValueError, OSError):
        return str(value) if value else None
