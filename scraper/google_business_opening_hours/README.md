# Google Business Opening Hours Sync

Fetch opening hours from a Google place ID using Outscraper and store them in Strapi.

## Requirements

- Python 3.11+
- Outscraper API key
- Strapi v4 REST API token

## Environment

Create a `.env` file (see `.env.example`) and set:

- OUTSCRAPER_API_KEY
- GOOGLE_PLACE_ID
- STRAPI_URL
- STRAPI_TOKEN
- STRAPI_OPENINGHOURS_COLLECTION

## Setup

1. **Generate Strapi schemas**:
   ```bash
   uv run gboh-schema
   ```
   Copy the generated files to your Strapi project:
   - `generated_strapi_types/openinghour/*` → `<strapi>/src/api/openinghour/`

2. **Run locally**:
   ```bash
   uv pip install -e .
   uv run gboh-sync
   ```

## Docker

```bash
docker compose up -d --build
```

The `ofelia` service runs as a daemon and triggers the job at 3:00 every morning.
The app container is created and stopped; Ofelia starts it on schedule and it exits when done.
