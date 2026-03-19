# Google Business Review Sync API

Fetch reviews from a Google place ID using Outscraper and store them in Strapi via a FastAPI service.

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
- REVIEW_SYNC_CRON (standard crontab format, e.g. `*/15 * * * *`)

## Setup

1. **Generate Strapi schemas**:
   ```bash
   uv run gbr-schema
   ```
   Copy the generated files to your Strapi project:
   - `generated_strapi_types/review/*` → `<strapi>/src/api/review/`

2. **Run locally**:
   ```bash
   uv pip install -e .
    uv run uvicorn google_business_review.main:app --host 0.0.0.0 --port 8000
   ```

## Scheduler and Endpoint

Review sync runs automatically based on `REVIEW_SYNC_CRON`.
One sync run is also executed immediately on API startup.
The cron expression is validated at startup, and the service fails fast if invalid.

- `GET /health` returns service health plus scheduler configuration and metadata from the latest run.
   If the latest run failed, health status is `error` and the run error is included.

## Docker

```bash
docker compose up -d --build
```

The API is available on `http://localhost:8000`.
