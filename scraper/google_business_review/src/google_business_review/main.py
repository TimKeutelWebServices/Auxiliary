"""Orchestrate fetching reviews and storing in Strapi."""

from datetime import datetime, timezone

from dotenv import load_dotenv

from google_business_review import outscraper, strapi

load_dotenv()


def main() -> None:
    """Fetch reviews from Outscraper and store in Strapi."""
    start = datetime.now(timezone.utc)
    cutoff_unix = strapi.get_review_cutoff_unix()
    print(f"[{start.isoformat()}] Fetching reviews (cutoff: {cutoff_unix}) …")

    reviews = outscraper.fetch_reviews(cutoff_unix=cutoff_unix)
    print(f"Got {len(reviews)} reviews\n")
    for review in reviews:
        strapi.store_review(review)

    end = datetime.now(timezone.utc)
    print(f"\n[{end.isoformat()}] Done (took {end - start}).")


if __name__ == "__main__":
    main()
