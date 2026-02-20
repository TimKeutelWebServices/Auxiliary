# Google Business Review Sync

Fetch reviews and opening hours from a Google place ID using Outscraper and store them in Strapi.

## Requirements

- Python 3.11+
- Outscraper API key
- Strapi v4 REST API token
- Virtual environment at `../.venv` (shared with parent scraper project)

## Environment

Create a `.env` file (see `.env.example`) and set:

- OUTSCRAPER_API_KEY
- GOOGLE_PLACE_ID
- STRAPI_URL
- STRAPI_TOKEN
- STRAPI_REVIEWS_COLLECTION
- STRAPI_OPENINGHOURS_COLLECTION

## Setup

1. **Generate Strapi schemas**:
   ```bash
   uv run gbr-schema
   ```
   This creates `schema.reviews.json` and `schema.openinghours.json`. Copy them to your Strapi project:
   - `schema.reviews.json` → `src/api/reviews/content-types/reviews/schema.json`
   - `schema.openinghours.json` → `src/api/openinghours/content-types/openinghours/schema.json`

2. **Run locally**:
   ```bash
   uv pip install -e .
   uv run gbr-sync
   ```

## Docker

```bash
docker compose up -d --build
```

The `ofelia` service runs as a daemon and triggers the job at 3:00 every morning.
The app container is created and stopped; Ofelia starts it on schedule and it exits when done.
