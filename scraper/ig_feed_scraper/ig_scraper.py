"""
Instagram Feed Scraper using Instaloader

This script scrapes the latest posts from Instagram profiles using Instaloader.
"""

import os
from pathlib import Path
from typing import Optional

import instaloader
from dotenv import load_dotenv


class InstagramScraper:
    """Instagram feed scraper using Instaloader."""

    def __init__(self, username: Optional[str] = None, password: Optional[str] = None, session_file: Optional[str] = None):
        """
        Initialize the Instagram scraper.

        Args:
            username: Instagram username for authentication (optional)
            password: Instagram password for authentication (optional)
            session_file: Path to session file for persistent login (optional)
        """
        self.loader = instaloader.Instaloader(
            download_videos=True,
            download_video_thumbnails=True,
            download_geotags=False,
            download_comments=True,
            save_metadata=True,
            compress_json=False,
        )
        
        self.username = username
        self.password = password
        self.session_file = session_file
        self._logged_in = False
        
        # Try to load session if available
        if session_file and os.path.exists(session_file):
            try:
                self.loader.load_session_from_file(username, session_file)
                self._logged_in = True
                print(f"Loaded session from {session_file}")
            except Exception as e:
                print(f"Failed to load session: {e}")

    def _ensure_login(self) -> None:
        """Login to Instagram if not already logged in."""
        if self._logged_in:
            return
            
        if not self.username or not self.password:
            raise ValueError("Username and password required for authentication")
            
        try:
            self.loader.login(self.username, self.password)
            self._logged_in = True
            print(f"Successfully logged in as {self.username}")
            
            # Save session if session_file is specified
            if self.session_file:
                self.loader.save_session_to_file(self.session_file)
                print(f"Saved session to {self.session_file}")
                
        except instaloader.exceptions.BadCredentialsException:
            print("Error: Invalid credentials")
            raise
        except instaloader.exceptions.TwoFactorAuthRequiredException:
            print("Error: Two-factor authentication required")
            raise
        except Exception as e:
            print(f"Login error: {e}")
            raise

    def scrape_profile_feed(
        self,
        profile_name: str,
        max_posts: int = 10,
        output_dir: str = "downloads"
    ) -> None:
        """
        Scrape posts from a specific Instagram profile.

        Args:
            profile_name: Instagram username/profile to scrape
            max_posts: Maximum number of posts to download
            output_dir: Directory to save downloaded content
        """
        try:
            print(f"Fetching profile: {profile_name}")
            profile = instaloader.Profile.from_username(
                self.loader.context, profile_name
            )
            
            print(f"Profile: {profile.full_name} (@{profile.username})")
            print(f"Followers: {profile.followers}, Following: {profile.followees}")
            print(f"Total posts: {profile.mediacount}")
            
            # Create output directory
            output_path = Path(output_dir) / profile_name
            output_path.mkdir(parents=True, exist_ok=True)
            
            # Download posts
            posts_downloaded = 0
            for post in profile.get_posts():
                if posts_downloaded >= max_posts:
                    break
                
                print(f"Downloading post {posts_downloaded + 1}/{max_posts}...")
                self.loader.download_post(post, target=str(output_path))
                posts_downloaded += 1
            
            print(f"Successfully downloaded {posts_downloaded} posts to {output_path}")
            
        except instaloader.exceptions.ProfileNotExistsException:
            print(f"Error: Profile '{profile_name}' does not exist")
        except Exception as e:
            print(f"Error scraping profile: {e}")
            raise

    def scrape_hashtag(
        self,
        hashtag: str,
        max_posts: int = 10,
        output_dir: str = "downloads"
    ) -> None:
        """
        Scrape posts from a specific hashtag.

        Args:
            hashtag: Hashtag to scrape (without #)
            max_posts: Maximum number of posts to download
            output_dir: Directory to save downloaded content
        """
        try:
            print(f"Fetching hashtag: #{hashtag}")
            hashtag_obj = instaloader.Hashtag.from_name(self.loader.context, hashtag)
            
            # Create output directory
            output_path = Path(output_dir) / f"hashtag_{hashtag}"
            output_path.mkdir(parents=True, exist_ok=True)
            
            # Download posts
            posts_downloaded = 0
            for post in hashtag_obj.get_posts():
                if posts_downloaded >= max_posts:
                    break
                
                print(f"Downloading post {posts_downloaded + 1}/{max_posts}...")
                self.loader.download_post(post, target=str(output_path))
                posts_downloaded += 1
            
            print(f"Successfully downloaded {posts_downloaded} posts to {output_path}")
            
        except Exception as e:
            print(f"Error scraping hashtag: {e}")
            raise

    def scrape_own_feed(self, max_posts: int = 10, output_dir: str = "downloads") -> None:
        """
        Scrape your own Instagram feed (requires authentication).

        Args:
            max_posts: Maximum number of posts to download
            output_dir: Directory to save downloaded content
        """
        # Ensure we're logged in before accessing feed
        self._ensure_login()
        
        try:
            print("Fetching your feed...")
            
            # Create output directory
            output_path = Path(output_dir) / "my_feed"
            output_path.mkdir(parents=True, exist_ok=True)
            
            # Download posts from feed
            posts_downloaded = 0
            for post in self.loader.get_feed_posts():
                if posts_downloaded >= max_posts:
                    break
                
                print(f"Downloading post {posts_downloaded + 1}/{max_posts}...")
                self.loader.download_post(post, target=str(output_path))
                posts_downloaded += 1
            
            print(f"Successfully downloaded {posts_downloaded} posts to {output_path}")
            
        except Exception as e:
            print(f"Error scraping feed: {e}")
            raise


def main():
    """Main function to run the scraper."""
    # Load environment variables
    load_dotenv()
    
    # Get credentials from environment variables (optional)
    ig_username = os.getenv("IG_USERNAME")
    ig_password = os.getenv("IG_PASSWORD")
    
    # Target profile to scrape
    target_profile = os.getenv("TARGET_PROFILE", "instagram")
    max_posts = int(os.getenv("MAX_POSTS", "10"))
    output_dir = os.getenv("OUTPUT_DIR", "downloads")
    
    # Initialize scraper
    scraper = InstagramScraper(username=ig_username, password=ig_password)
    
    # Scrape profile feed
    scraper.scrape_profile_feed(
        profile_name=target_profile,
        max_posts=max_posts,
        output_dir=output_dir
    )
    
    # Example: Scrape hashtag
    # scraper.scrape_hashtag(hashtag="python", max_posts=5, output_dir=output_dir)
    
    # Example: Scrape your own feed (requires login)
    # if ig_username and ig_password:
    #     scraper.scrape_own_feed(max_posts=10, output_dir=output_dir)


if __name__ == "__main__":
    main()
