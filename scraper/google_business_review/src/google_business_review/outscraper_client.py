from datetime import datetime

from outscraper import ApiClient


def fetch_reviews(
    api_key: str, 
    place_id: str, 
    cutoff_timestamp: datetime | None = None
) -> list[dict]:
    """
    Fetch reviews from Outscraper API.
    
    Args:
        api_key: Outscraper API key
        place_id: Google place ID
        cutoff_timestamp: Only fetch reviews newer than this timestamp
    """
    # Fetch from API
    client = ApiClient(api_key)
    
    # Prepare API parameters
    params = {
        "reviews_limit": 20,
    }
    
    # Add cutoff parameter if timestamp is provided
    # Outscraper expects Unix timestamp in seconds
    if cutoff_timestamp:
        cutoff_unix = int(cutoff_timestamp.timestamp())
        params["cutoff"] = cutoff_unix
    
    # Pass place_id as a list to avoid multiple API requests
    results = client.google_maps_reviews([place_id], **params)
    if not results:
        return []
    # Extract reviews_data from the first result
    if isinstance(results, list) and len(results) > 0:
        first_result = results[0]
        if isinstance(first_result, dict):
            return first_result.get("reviews_data") or []
    return []


def fetch_place_details(api_key: str, place_id: str) -> list[dict]:
    """Fetch place details from Outscraper API.
    
    Args:
        api_key: Outscraper API key
        place_id: Google place ID
    """
    client = ApiClient(api_key)
    results = client.google_maps_search([place_id])
    return results or []
