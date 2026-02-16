"""
FastAPI endpoint for Instagram scraper.
"""

import os
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field

from ig_scraper import InstagramScraper

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Instagram Feed Scraper API",
    description="API to trigger Instagram feed scraping using Instaloader",
    version="0.1.0"
)


class ScrapeProfileRequest(BaseModel):
    """Request model for scraping a profile."""
    
    profile_name: str = Field(..., description="Instagram username/profile to scrape")
    max_posts: int = Field(10, ge=1, le=100, description="Maximum number of posts to download")
    output_dir: Optional[str] = Field(None, description="Output directory (optional)")


class ScrapeHashtagRequest(BaseModel):
    """Request model for scraping a hashtag."""
    
    hashtag: str = Field(..., description="Hashtag to scrape (without #)")
    max_posts: int = Field(10, ge=1, le=100, description="Maximum number of posts to download")
    output_dir: Optional[str] = Field(None, description="Output directory (optional)")


class ScrapeFeedRequest(BaseModel):
    """Request model for scraping own feed."""
    
    max_posts: int = Field(10, ge=1, le=100, description="Maximum number of posts to download")
    output_dir: Optional[str] = Field(None, description="Output directory (optional)")


class ScrapeResponse(BaseModel):
    """Response model for scrape operations."""
    
    status: str
    message: str
    profile: Optional[str] = None
    max_posts: int
    output_dir: str


def get_scraper() -> InstagramScraper:
    """Get an initialized Instagram scraper instance."""
    ig_username = os.getenv("IG_USERNAME")
    ig_password = os.getenv("IG_PASSWORD")
    session_file = os.getenv("SESSION_FILE", "sessions/session")
    
    # For public profiles, we don't need credentials
    return InstagramScraper(
        username=ig_username,
        password=ig_password,
        session_file=session_file
    )


def scrape_profile_task(profile_name: str, max_posts: int, output_dir: str) -> None:
    """Background task to scrape a profile."""
    scraper = get_scraper()
    scraper.scrape_profile_feed(
        profile_name=profile_name,
        max_posts=max_posts,
        output_dir=output_dir
    )


def scrape_hashtag_task(hashtag: str, max_posts: int, output_dir: str) -> None:
    """Background task to scrape a hashtag."""
    scraper = get_scraper()
    scraper.scrape_hashtag(
        hashtag=hashtag,
        max_posts=max_posts,
        output_dir=output_dir
    )


def scrape_feed_task(max_posts: int, output_dir: str) -> None:
    """Background task to scrape own feed."""
    scraper = get_scraper()
    scraper.scrape_own_feed(max_posts=max_posts, output_dir=output_dir)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Instagram Feed Scraper API",
        "version": "0.1.0",
        "endpoints": {
            "scrape_profile": "/scrape/profile",
            "scrape_hashtag": "/scrape/hashtag",
            "scrape_feed": "/scrape/feed"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.post("/scrape/profile", response_model=ScrapeResponse)
async def scrape_profile(
    request: ScrapeProfileRequest,
    background_tasks: BackgroundTasks
):
    """
    Scrape posts from a specific Instagram profile.
    
    This endpoint triggers a background task to download posts from the specified profile.
    """
    try:
        output_dir = request.output_dir or os.getenv("OUTPUT_DIR", "downloads")
        
        # Add background task
        background_tasks.add_task(
            scrape_profile_task,
            request.profile_name,
            request.max_posts,
            output_dir
        )
        
        return ScrapeResponse(
            status="accepted",
            message=f"Scraping profile '{request.profile_name}' started in background",
            profile=request.profile_name,
            max_posts=request.max_posts,
            output_dir=output_dir
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/scrape/hashtag", response_model=ScrapeResponse)
async def scrape_hashtag(
    request: ScrapeHashtagRequest,
    background_tasks: BackgroundTasks
):
    """
    Scrape posts from a specific hashtag.
    
    This endpoint triggers a background task to download posts with the specified hashtag.
    """
    try:
        output_dir = request.output_dir or os.getenv("OUTPUT_DIR", "downloads")
        
        # Add background task
        background_tasks.add_task(
            scrape_hashtag_task,
            request.hashtag,
            request.max_posts,
            output_dir
        )
        
        return ScrapeResponse(
            status="accepted",
            message=f"Scraping hashtag '#{request.hashtag}' started in background",
            profile=f"hashtag_{request.hashtag}",
            max_posts=request.max_posts,
            output_dir=output_dir
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/scrape/feed", response_model=ScrapeResponse)
async def scrape_feed(
    request: ScrapeFeedRequest,
    background_tasks: BackgroundTasks
):
    """
    Scrape your own Instagram feed.
    
    This endpoint requires authentication (IG_USERNAME and IG_PASSWORD in .env).
    """
    # Check if credentials are configured
    if not os.getenv("IG_USERNAME") or not os.getenv("IG_PASSWORD"):
        raise HTTPException(
            status_code=400,
            detail="Instagram credentials not configured. Set IG_USERNAME and IG_PASSWORD in .env file."
        )
    
    try:
        output_dir = request.output_dir or os.getenv("OUTPUT_DIR", "downloads")
        
        # Add background task
        background_tasks.add_task(
            scrape_feed_task,
            request.max_posts,
            output_dir
        )
        
        return ScrapeResponse(
            status="accepted",
            message="Scraping your feed started in background",
            profile="my_feed",
            max_posts=request.max_posts,
            output_dir=output_dir
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", "8000"))
    host = os.getenv("HOST", "0.0.0.0")
    
    uvicorn.run(app, host=host, port=port)
