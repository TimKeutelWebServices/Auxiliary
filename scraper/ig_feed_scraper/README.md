# Instagram Feed Scraper

A Python script and FastAPI service to scrape Instagram feeds using the Instaloader library.

## Features

- Scrape posts from any public Instagram profile
- Scrape posts by hashtag
- Scrape your own Instagram feed (with authentication)
- Download images, videos, captions, and metadata
- **FastAPI REST API** for triggering scrapes
- **Docker support** for easy deployment
- Configurable via environment variables
- No hardcoded credentials

## Setup

### 1. Create a virtual environment

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 2. Install the project with uvicorn

```powershell
pip install -e .
```

This installs the project and all dependencies including uvicorn.

### 3. Configure environment variables

Copy the example environment file and edit it:

```powershell
Copy-Item .env.example .env
```

Edit `.env` and add your settings:

```
# Optional: Add your Instagram credentials for private content or your own feed
IG_USERNAME=your_username
IG_PASSWORD=your_password

# Configure what to scrape
TARGET_PROFILE=instagram
MAX_POSTS=10
OUTPUT_DIR=downloads
```

## Usage

### Option 1: VS Code Debugger (Recommended for Development)

Press **F5** in VS Code to start the FastAPI server with debugging enabled. The server will:
- Start with hot-reload enabled
- Load environment variables from `.env`
- Enable debugging breakpoints
- Run on `http://localhost:8000`

Visit `http://localhost:8000/docs` for interactive API documentation.

#### API Endpoints

**Scrape Profile:**
```powershell
curl -X POST "http://localhost:8000/scrape/profile" `
  -H "Content-Type: application/json" `
  -d '{"profile_name": "instagram", "max_posts": 10}'
```

**Scrape Hashtag:**
```powershell
curl -X POST "http://localhost:8000/scrape/hashtag" `
  -H "Content-Type: application/json" `
  -d '{"hashtag": "python", "max_posts": 5}'
```

**Scrape Your Feed (requires authentication):**
```powershell
curl -X POST "http://localhost:8000/scrape/feed" `
  -H "Content-Type: application/json" `
  -d '{"max_posts": 10}'
```

### Option 2: Direct Script

Run the scraper with default settings from `.env`:

```powershell
python ig_scraper.py
```

### Advanced Usage

You can modify the `main()` function in `ig_scraper.py` to customize behavior:

```python
# Scrape a specific profile
scraper.scrape_profile_feed(
    profile_name="instagram",
    max_posts=20,
    output_dir="downloads"
)

# Scrape by hashtag
scraper.scrape_hashtag(
    hashtag="python",
    max_posts=15,
    output_dir="downloads"
)

# Scrape your own feed (requires authentication)
scraper.scrape_own_feed(
    max_posts=10,
    output_dir="downloads"
)
```

## Output

Downloaded content will be saved in the `downloads/` directory (or as configured):

```
downloads/
├── profile_name/
│   ├── 2024-01-15_12-30-45_UTC.jpg
│   ├── 2024-01-15_12-30-45_UTC.json
│   ├── 2024-01-14_08-20-15_UTC.mp4
│   └── ...
└── hashtag_python/
    ├── 2024-01-15_10-15-30_UTC.jpg
    └── ...
```

Each post includes:
- Image/video files
- JSON metadata (likes, comments, caption, etc.)
- Video thumbnails (if applicable)

## Docker Deployment

### Build and Run with Docker

Build the Docker image:

```powershell
docker build -t ig-scraper-api .
```

Run the container:

```powershell
docker run -d `
  -p 8000:8000 `
  -v ${PWD}/downloads:/app/downloads `
  --env-file .env `
  --name ig-scraper `
  ig-scraper-api
```

### Using Docker Compose (Recommended)

Start the service:

```powershell
docker-compose up -d
```

View logs:

```powershell
docker-compose logs -f
```

Stop the service:

```powershell
docker-compose down
```

The API will be available at `http://localhost:8000` and scraped content will be saved to the `downloads/` directory on your host machine.

## Important Notes

⚠️ **Rate Limiting**: Instagram has rate limits. Avoid scraping too aggressively.

⚠️ **Terms of Service**: Make sure your usage complies with Instagram's Terms of Service.

⚠️ **API Documentation**: Visit `http://localhost:8000/docs` to see the interactive API documentation and test endpoints.

## Troubleshooting

### Rate Limiting

If you get rate-limited:

1. Reduce `MAX_POSTS` to a lower number
2. Add delays between requests
3. Wait before trying again

## License

This project is for educational purposes. Always respect Instagram's Terms of Service and robots.txt.
