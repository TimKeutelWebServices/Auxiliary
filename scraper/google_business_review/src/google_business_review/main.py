"""Orchestrate fetching reviews and storing in Strapi."""

from dotenv import load_dotenv

from google_business_review import outscraper, strapi

load_dotenv()


def main() -> None:
    """Fetch reviews from Outscraper and store in Strapi."""
    cutoff_unix = strapi.get_review_cutoff_unix()
    print(f"Fetching reviews (cutoff: {cutoff_unix}) …")

    reviews = outscraper.fetch_reviews(cutoff_unix=cutoff_unix)
    print(f"Got {len(reviews)} reviews\n")
    for review in reviews:
        strapi.store_review(review)

    print("\nDone.")


if __name__ == "__main__":
    main()
