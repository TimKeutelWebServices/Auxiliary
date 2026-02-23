"""Orchestrate fetching opening hours and storing in Strapi."""

from datetime import datetime, timezone

from dotenv import load_dotenv

from google_business_opening_hours import outscraper, strapi

load_dotenv()


def main() -> None:
    """Fetch opening hours from Outscraper and store in Strapi."""
    start = datetime.now(timezone.utc)
    print(f"[{start.isoformat()}] Fetching opening hours …")
    openinghours = outscraper.fetch_opening_hours()
    if openinghours:
        strapi.store_openinghours(openinghours)
    else:
        print("  No opening hours data returned.")

    end = datetime.now(timezone.utc)
    print(f"\n[{end.isoformat()}] Done (took {end - start}).")


if __name__ == "__main__":
    main()
