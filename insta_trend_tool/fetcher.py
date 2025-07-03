"""Instagram post fetcher module."""

import logging
import random
import time
from datetime import datetime, timedelta
from typing import Callable, Optional

import instaloader
from instaloader import Hashtag, Post, Profile
from instaloader.exceptions import (
    BadResponseException,
    ConnectionException,
    LoginRequiredException,
    ProfileNotExistsException,
    QueryReturnedBadRequestException,
    TooManyRequestsException,
)

from .config import Config
from .exceptions import (
    AuthenticationError,
    FetchError,
    HashtagNotFoundError,
    RateLimitError,
)
from .models import FetchProgress, InstagramPost, TrendAnalysisResult


logger = logging.getLogger(__name__)


class InstagramFetcher:
    """Fetches Instagram posts for specified hashtags."""
    
    def __init__(self, config: Config, progress_callback: Optional[Callable[[FetchProgress], None]] = None):
        """Initialize the fetcher.
        
        Args:
            config: Application configuration
            progress_callback: Optional callback for progress updates
        """
        self.config = config
        self.progress_callback = progress_callback
        self.loader = instaloader.Instaloader(
            quiet=True,
            download_pictures=False,
            download_videos=False,
            download_video_thumbnails=False,
            download_comments=False,
            save_metadata=False,
            compress_json=False,
            post_metadata_txt_pattern="",
            request_timeout=30,
        )
        
        # Set up session if login credentials provided
        if config.instagram_username and config.instagram_password:
            self._login()
    
    def _login(self) -> None:
        """Log in to Instagram if credentials are provided."""
        try:
            self.loader.login(self.config.instagram_username, self.config.instagram_password)
            logger.info(f"Successfully logged in as {self.config.instagram_username}")
        except LoginRequiredException as e:
            logger.error(f"Login required but credentials invalid: {e}")
            raise AuthenticationError(f"Invalid Instagram credentials: {e}")
        except TooManyRequestsException as e:
            logger.error(f"Rate limited during login: {e}")
            raise RateLimitError(f"Rate limited during login: {e}")
        except (ConnectionException, BadResponseException) as e:
            logger.warning(f"Connection error during login: {e}. Continuing without login.")
        except Exception as e:
            logger.warning(f"Unexpected error during login: {e}. Continuing without login.")
    
    def _apply_rate_limit_delay(self) -> None:
        """Apply random delay to avoid rate limiting."""
        delay = random.uniform(self.config.request_delay_min, self.config.request_delay_max)
        time.sleep(delay)
    
    def _convert_post_to_model(self, post: Post, hashtag: str) -> InstagramPost:
        """Convert Instaloader Post to our InstagramPost model.
        
        Args:
            post: Instaloader Post object
            hashtag: The hashtag used to find this post
            
        Returns:
            InstagramPost model instance
        """
        # Extract hashtags from caption
        caption_text = post.caption or ""
        hashtags = [tag.strip("#") for tag in caption_text.split() if tag.startswith("#")]
        
        # Ensure the search hashtag is included
        if hashtag not in hashtags:
            hashtags.append(hashtag)
        
        return InstagramPost(
            shortcode=post.shortcode,
            post_url=f"https://www.instagram.com/p/{post.shortcode}/",
            owner_username=post.owner_username,
            owner_id=str(post.owner_id),
            posted_at=post.date_utc,
            likes=post.likes,
            comments=post.comments,
            caption=caption_text,
            hashtags=hashtags,
            is_video=post.is_video,
            video_view_count=post.video_view_count if post.is_video else None,
            location=post.location.name if post.location else None,
            is_sponsored=post.is_sponsored,
        )
    
    def fetch_hashtag_posts(
        self,
        hashtag: str,
        since_date: datetime,
        until_date: datetime,
        max_posts: Optional[int] = None,
    ) -> TrendAnalysisResult:
        """Fetch posts for a single hashtag within date range.
        
        Args:
            hashtag: Hashtag to search (without #)
            since_date: Start date (inclusive)
            until_date: End date (inclusive)
            max_posts: Maximum number of posts to fetch
            
        Returns:
            TrendAnalysisResult with fetched posts
        """
        result = TrendAnalysisResult(
            hashtag=hashtag,
            start_date=since_date,
            end_date=until_date,
            total_posts_fetched=0,
        )
        
        posts_fetched = 0
        
        try:
            # Get hashtag object
            try:
                hashtag_obj = Hashtag.from_name(self.loader.context, hashtag)
            except ProfileNotExistsException as e:
                error_msg = f"Hashtag #{hashtag} not found or doesn't exist"
                logger.error(error_msg)
                result.error_messages.append(error_msg)
                raise HashtagNotFoundError(error_msg) from e
            
            logger.info(f"Fetching posts for #{hashtag}...")
            
            # Iterate through posts
            for post in hashtag_obj.get_posts():
                # Apply rate limiting
                self._apply_rate_limit_delay()
                
                # Check date range
                if post.date_utc < since_date:
                    break  # Posts are in reverse chronological order
                
                if post.date_utc > until_date:
                    continue
                
                # Convert and add post
                try:
                    instagram_post = self._convert_post_to_model(post, hashtag)
                    result.posts.append(instagram_post)
                    posts_fetched += 1
                    
                    # Update progress if callback provided
                    if self.progress_callback:
                        progress = FetchProgress(
                            current_hashtag=hashtag,
                            total_hashtags=1,
                            current_hashtag_index=1,
                            posts_fetched=posts_fetched,
                        )
                        self.progress_callback(progress)
                    
                    # Check if we've reached the limit
                    if max_posts and posts_fetched >= max_posts:
                        break
                        
                except Exception as e:
                    logger.warning(f"Error processing post {post.shortcode}: {e}")
                    result.error_messages.append(f"Failed to process post {post.shortcode}: {str(e)}")
                    continue
            
            result.total_posts_fetched = posts_fetched
            logger.info(f"Fetched {posts_fetched} posts for #{hashtag}")
            
        except TooManyRequestsException as e:
            error_msg = f"Rate limited while fetching #{hashtag}: {str(e)}"
            logger.error(error_msg)
            result.error_messages.append(error_msg)
            raise RateLimitError(error_msg) from e
        except (ConnectionException, BadResponseException) as e:
            error_msg = f"Connection error while fetching #{hashtag}: {str(e)}"
            logger.error(error_msg)
            result.error_messages.append(error_msg)
            raise FetchError(error_msg) from e
        except (HashtagNotFoundError, RateLimitError):
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            error_msg = f"Unexpected error fetching hashtag #{hashtag}: {str(e)}"
            logger.error(error_msg)
            result.error_messages.append(error_msg)
            raise FetchError(error_msg) from e
        
        return result
    
    def fetch_multiple_hashtags(
        self,
        hashtags: list[str],
        since_date: datetime,
        until_date: datetime,
        max_posts_per_tag: Optional[int] = None,
    ) -> list[TrendAnalysisResult]:
        """Fetch posts for multiple hashtags.
        
        Args:
            hashtags: List of hashtags to search (without #)
            since_date: Start date (inclusive)
            until_date: End date (inclusive)
            max_posts_per_tag: Maximum posts per hashtag
            
        Returns:
            List of TrendAnalysisResult objects
        """
        results = []
        total_hashtags = len(hashtags)
        
        for idx, hashtag in enumerate(hashtags, 1):
            logger.info(f"Processing hashtag {idx}/{total_hashtags}: #{hashtag}")
            
            # Update progress for current hashtag
            if self.progress_callback:
                progress = FetchProgress(
                    current_hashtag=hashtag,
                    total_hashtags=total_hashtags,
                    current_hashtag_index=idx,
                    posts_fetched=0,
                )
                self.progress_callback(progress)
            
            # Fetch posts with retry logic
            for attempt in range(self.config.max_retries):
                try:
                    result = self.fetch_hashtag_posts(
                        hashtag=hashtag,
                        since_date=since_date,
                        until_date=until_date,
                        max_posts=max_posts_per_tag,
                    )
                    results.append(result)
                    break
                except Exception as e:
                    if attempt < self.config.max_retries - 1:
                        logger.warning(
                            f"Attempt {attempt + 1} failed for #{hashtag}: {e}. "
                            f"Retrying in {self.config.retry_delay} seconds..."
                        )
                        time.sleep(self.config.retry_delay)
                    else:
                        logger.error(f"All attempts failed for #{hashtag}: {e}")
                        # Add empty result with error
                        error_result = TrendAnalysisResult(
                            hashtag=hashtag,
                            start_date=since_date,
                            end_date=until_date,
                            total_posts_fetched=0,
                            error_messages=[f"Failed after {self.config.max_retries} attempts: {str(e)}"],
                        )
                        results.append(error_result)
        
        return results