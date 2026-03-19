"""FastAPI service to sync Google Business reviews into Strapi."""

from datetime import datetime, timezone
import logging
import os
from threading import Lock
from typing import Any

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from dotenv import load_dotenv
from fastapi import FastAPI

import google_business_review.outscraper as outscraper
import google_business_review.strapi as strapi

load_dotenv()

# Skip logging for health endpoint
class _SkipHealthCheckFilter(logging.Filter):
    def filter(self, record):
        return "/health" not in record.getMessage()

logging.getLogger("uvicorn.access").addFilter(_SkipHealthCheckFilter())

app = FastAPI(title="Google Business Review Sync", version="0.1.0")
_RUN_LOCK = Lock()
_SCHEDULER: BackgroundScheduler | None = None
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

_SYNC_CRON_ENV = "REVIEW_SYNC_CRON"


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


def _run_sync_job() -> None:
    """Run one sync job if another run is not already in progress."""
    if not _RUN_LOCK.acquire(blocking=False):
        logging.getLogger(__name__).warning(
            "Skipping scheduled sync because a sync run is already in progress."
        )
        return

    global _LATEST_RUN
    try:
        result = _sync_reviews()
        _LATEST_RUN = result
    finally:
        _RUN_LOCK.release()


def _build_scheduler() -> BackgroundScheduler:
    """Create a cron scheduler using environment-based cron configuration."""
    cron_expression = os.getenv(_SYNC_CRON_ENV, "0 * * * *").strip()

    try:
        trigger = CronTrigger.from_crontab(cron_expression)
    except ValueError as exc:
        raise RuntimeError(
            f"Invalid cron expression '{cron_expression}' from {_SYNC_CRON_ENV}."
        ) from exc

    scheduler = BackgroundScheduler()
    scheduler.add_job(
        _run_sync_job,
        trigger=trigger,
        id="google_business_review_sync",
        replace_existing=True,
        coalesce=True,
        max_instances=1,
        misfire_grace_time=300,
    )

    logging.getLogger(__name__).info(
        "Scheduled review sync configured with cron '%s'.",
        cron_expression,
    )
    return scheduler


@app.on_event("startup")
def start_scheduler() -> None:
    """Run an initial sync and start the cron scheduler when the API starts."""
    global _SCHEDULER
    _run_sync_job()
    scheduler = _build_scheduler()
    scheduler.start()
    _SCHEDULER = scheduler


@app.on_event("shutdown")
def stop_scheduler() -> None:
    """Shutdown the cron scheduler when the API stops."""
    global _SCHEDULER
    if _SCHEDULER is not None:
        _SCHEDULER.shutdown(wait=False)
        _SCHEDULER = None


@app.get("/health")
def health() -> dict[str, Any]:
    """Return API status and metadata for the latest sync execution."""
    status = "ok"
    if _LATEST_RUN["status"] == "error":
        status = "error"

    cron_expression = os.getenv(_SYNC_CRON_ENV, "0 * * * *")

    return {
        "status": status,
        "scheduler": {
            "cron": cron_expression,
        },
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
