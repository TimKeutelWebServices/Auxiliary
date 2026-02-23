"""Outscraper API client — shared request/polling logic."""

import os
import time

import requests

API_KEY = os.environ.get("OUTSCRAPER_API_KEY", "")
PLACE_ID = os.environ.get("GOOGLE_PLACE_ID", "")
BASE_URL = "https://api.app.outscraper.com"


def fetch_place_data(params: dict) -> list:
    """Call Outscraper API and return place data, with automatic polling."""
    resp = requests.get(
        f"{BASE_URL}/maps/reviews-v3",
        headers={"X-API-KEY": API_KEY},
        params=params,
        timeout=60,
    )
    resp.raise_for_status()
    body = resp.json()

    if "data" in body and body["data"]:
        return body["data"]

    request_id = body.get("id")
    if not request_id:
        raise RuntimeError(f"Unexpected response: {body}")

    print(f"Request queued ({request_id}), polling …")
    for attempt in range(30):
        time.sleep(5)
        poll = requests.get(
            f"{BASE_URL}/requests/{request_id}",
            headers={"X-API-KEY": API_KEY},
            timeout=30,
        )
        poll.raise_for_status()
        poll_body = poll.json()
        if poll_body.get("status") == "Success" and poll_body.get("data"):
            return poll_body["data"]
        print(f"  attempt {attempt + 1}/30: {poll_body.get('status', 'unknown')}")

    raise TimeoutError("Request did not complete in time")
