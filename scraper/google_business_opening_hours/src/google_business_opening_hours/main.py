"""Orchestrate fetching opening hours and storing in Strapi."""

from dotenv import load_dotenv

from google_business_opening_hours import outscraper, strapi

load_dotenv()


def main() -> None:
    """Fetch opening hours from Outscraper and store in Strapi."""
    print("Fetching opening hours …")
    openinghours = outscraper.fetch_opening_hours()
    if openinghours:
        strapi.store_openinghours(openinghours)
    else:
        print("  No opening hours data returned.")

    print("\nDone.")


if __name__ == "__main__":
    main()
