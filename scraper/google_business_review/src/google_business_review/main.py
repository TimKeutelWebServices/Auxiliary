"""FastAPI service to sync Google Business reviews into Strapi."""

from datetime import datetime, timezone
import os
from threading import Lock
from typing import Any

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import JSONResponse

import google_business_review.outscraper as outscraper
import google_business_review.strapi as strapi

load_dotenv()

app = FastAPI(title="Google Business Review Sync", version="0.1.0")
_RUN_LOCK = Lock()
_LATEST_RUN: dict[str, Any] = {
    "status": "never_run",
    "success": None,
    "started_at": None,
    "ended_at": None,
    "duration_seconds": None,
    "data_source": None,
    "used_cache": None,
    "cutoff_unix": None,
    "fetched_reviews": 0,
    "stored_reviews": 0,
    "skipped_reviews": 0,
    "ignored_reviews": 0,
    "error": None,
}


def _sync_reviews() -> dict[str, Any]:
    """Fetch and store reviews, returning run metadata for API responses."""
    start = datetime.now(timezone.utc)
    try:
        cutoff_unix = strapi.get_review_cutoff_unix()
        reviews = outscraper.fetch_reviews(cutoff_unix=cutoff_unix)

        stored_reviews = 0
        skipped_reviews = 0
        ignored_reviews = 0
        for review in reviews:
            outcome = strapi.store_review(review)
            if outcome == "stored":
                stored_reviews += 1
            elif outcome == "skipped":
                skipped_reviews += 1
            else:
                ignored_reviews += 1

        end = datetime.now(timezone.utc)
        data_source = (
            "outscraper_api_incremental" if cutoff_unix > 0 else "outscraper_api_full"
        )
        if not reviews:
            data_source = "no_new_reviews"

        return {
            "status": "success",
            "success": True,
            "started_at": start.isoformat(),
            "ended_at": end.isoformat(),
            "duration_seconds": round((end - start).total_seconds(), 3),
            "data_source": data_source,
            "used_cache": None,
            "cutoff_unix": cutoff_unix,
            "fetched_reviews": len(reviews),
            "stored_reviews": stored_reviews,
            "skipped_reviews": skipped_reviews,
            "ignored_reviews": ignored_reviews,
            "error": None,
        }
    except Exception as exc:
        end = datetime.now(timezone.utc)
        return {
            "status": "error",
            "success": False,
            "started_at": start.isoformat(),
            "ended_at": end.isoformat(),
            "duration_seconds": round((end - start).total_seconds(), 3),
            "data_source": None,
            "used_cache": None,
            "cutoff_unix": None,
            "fetched_reviews": 0,
            "stored_reviews": 0,
            "skipped_reviews": 0,
            "ignored_reviews": 0,
            "error": str(exc),
        }


@app.post("/sync/reviews")
def trigger_review_sync() -> JSONResponse:
    """Run one sync job and return execution metadata."""
    if not _RUN_LOCK.acquire(blocking=False):
        return JSONResponse(
            status_code=409,
            content={
                "status": "error",
                "success": False,
                "error": "A sync run is already in progress.",
            },
        )

    global _LATEST_RUN
    try:
        result = _sync_reviews()
        _LATEST_RUN = result
    finally:
        _RUN_LOCK.release()

    status_code = 200 if result["success"] else 500
    return JSONResponse(status_code=status_code, content=result)


@app.get("/health")
def health() -> dict[str, Any]:
    """Return API status and metadata for the latest sync execution."""
    status = "ok"
    if _LATEST_RUN["status"] == "error":
        status = "error"
    return {
        "status": status,
        "latest_run": _LATEST_RUN,
    }


def main() -> None:
    """CLI compatibility entrypoint for one-shot sync runs."""
    result = _sync_reviews()
    print(result)
    if not result["success"]:
        raise SystemExit(1)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "google_business_review.main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8000")),
    )
