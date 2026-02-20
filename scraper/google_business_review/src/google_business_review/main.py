import logging

from dotenv import load_dotenv

from google_business_review.config import load_config
from google_business_review.outscraper_client import fetch_place_details, fetch_reviews
from google_business_review.strapi_client import upsert_entry
from google_business_review.timestamp_tracker import get_last_fetch_timestamp, save_last_fetch_timestamp
from google_business_review.transform import normalize_opening_hours, normalize_reviews


logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def main() -> None:
    load_dotenv()
    config = load_config()
    place_id = config["place_id"]

    # Get last fetch timestamp to filter reviews
    last_fetch = get_last_fetch_timestamp(place_id)
    if last_fetch:
        logger.info(f"Last fetch was at {last_fetch.isoformat()}. Fetching only newer reviews.")
    else:
        logger.info("No previous fetch timestamp found. Fetching all reviews.")

    logger.info("Fetching reviews from Outscraper")
    raw_reviews = fetch_reviews(
        config["outscraper_api_key"], 
        place_id, 
        cutoff_timestamp=last_fetch
    )
    reviews = normalize_reviews(raw_reviews, place_id)

    logger.info("Upserting %s reviews into Strapi", len(reviews))
    for review in reviews:
        upsert_entry(
            config["strapi_url"],
            config["strapi_token"],
            config["reviews_collection"],
            "review_id",
            review["review_id"],
            review,
        )

    # Save timestamp after successful sync
    save_last_fetch_timestamp(place_id)
    logger.info("Updated last fetch timestamp")

    logger.info("Fetching place details for opening hours")
    raw_places = fetch_place_details(config["outscraper_api_key"], place_id)
    opening_hours = normalize_opening_hours(raw_places, place_id)

    if opening_hours:
        logger.info("Upserting opening hours into Strapi")
        upsert_entry(
            config["strapi_url"],
            config["strapi_token"],
            config["openinghours_collection"],
            "place_id",
            opening_hours["place_id"],
            opening_hours,
        )
    else:
        logger.info("No opening hours found for place ID")


if __name__ == "__main__":
    main()
