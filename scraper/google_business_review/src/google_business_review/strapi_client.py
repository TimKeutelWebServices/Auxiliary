import requests


def _headers(token: str) -> dict:
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }


def _request(method: str, url: str, token: str, payload: dict | None = None) -> dict:
    response = requests.request(method, url, headers=_headers(token), json=payload, timeout=30)
    try:
        response.raise_for_status()
    except requests.HTTPError as e:
        if response.status_code == 404:
            raise RuntimeError(
                f"Strapi endpoint not found: {url}. "
                f"Please check that the collection name in your .env matches the Strapi API endpoint. "
                f"For Strapi v4, use plural collection names (e.g., 'reviews' not 'review')."
            ) from e
        elif response.status_code == 400:
            error_detail = ""
            try:
                error_data = response.json()
                error_detail = f"\nError details: {error_data}"
            except Exception:
                error_detail = f"\nResponse text: {response.text[:500]}"
            raise RuntimeError(
                f"Strapi validation error (400 Bad Request) for {method} {url}.{error_detail}"
            ) from e
        raise
    return response.json()


def find_entry(base_url: str, token: str, collection: str, field: str, value: str) -> dict | None:
    url = f"{base_url}/api/{collection}?filters[{field}][$eq]={value}"
    data = _request("GET", url, token)
    items = data.get("data", [])
    if not items:
        return None
    return items[0]


def upsert_entry(base_url: str, token: str, collection: str, field: str, value: str, attributes: dict) -> None:
    existing = find_entry(base_url, token, collection, field, value)
    payload = {"data": attributes}
    if existing:
        entry_id = existing.get("id")
        url = f"{base_url}/api/{collection}/{entry_id}"
        _request("PUT", url, token, payload)
        return

    url = f"{base_url}/api/{collection}"
    _request("POST", url, token, payload)
