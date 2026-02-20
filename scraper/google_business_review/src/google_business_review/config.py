import os


def get_env(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(f"Missing required env var: {name}")
    return value


def load_config() -> dict:
    return {
        "outscraper_api_key": get_env("OUTSCRAPER_API_KEY"),
        "place_id": get_env("GOOGLE_PLACE_ID"),
        "strapi_url": get_env("STRAPI_URL").rstrip("/"),
        "strapi_token": get_env("STRAPI_TOKEN"),
        "reviews_collection": get_env("STRAPI_REVIEWS_COLLECTION"),
        "openinghours_collection": get_env("STRAPI_OPENINGHOURS_COLLECTION"),
    }
