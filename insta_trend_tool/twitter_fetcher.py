"""Twitter data fetcher using Twitter API v2."""

import logging
import tweepy
from datetime import datetime, timedelta
from typing import Optional, List, Callable
from dataclasses import dataclass

from .config import Config
from .models import InstagramPost, TrendAnalysisResult
from .exceptions import (
    AuthenticationError,
    FetchError,
    HashtagNotFoundError,
    RateLimitError,
)

logger = logging.getLogger(__name__)

@dataclass
class TwitterPost:
    """Twitter post data compatible with InstagramPost structure."""
    
    # Basic identifiers
    shortcode: str  # Tweet ID
    post_url: str
    owner_username: str
    owner_id: str
    
    # Timestamps
    posted_at: datetime
    
    # Engagement metrics
    likes: int
    comments: int  # Reply count
    
    # Content
    caption: str  # Tweet text
    hashtags: List[str]
    
    # Media information
    is_video: bool = False
    
    @property
    def engagement_score(self) -> int:
        """Calculate engagement score."""
        return self.likes + (self.comments * 2)  # Comments weighted more


class TwitterFetcher:
    """Fetches Twitter posts for specified hashtags using Twitter API v2."""
    
    def __init__(self, config: Config, progress_callback: Optional[Callable] = None):
        """Initialize the Twitter fetcher.
        
        Args:
            config: Application configuration with Twitter API credentials
            progress_callback: Optional callback for progress updates
        """
        self.config = config
        self.progress_callback = progress_callback
        
        # Initialize Twitter API client
        if not hasattr(config, 'twitter_bearer_token') or not config.twitter_bearer_token:
            raise AuthenticationError("Twitter Bearer Token is required")
        
        try:
            self.client = tweepy.Client(
                bearer_token=config.twitter_bearer_token,
                wait_on_rate_limit=True
            )
            logger.info("Twitter API client initialized successfully")
        except Exception as e:
            raise AuthenticationError(f"Failed to initialize Twitter API: {e}")
    
    def fetch_hashtag_posts(
        self, 
        hashtag: str, 
        max_results: int = 100, 
        since_date: Optional[datetime] = None
    ) -> TrendAnalysisResult:
        """Fetch Twitter posts for a hashtag.
        
        Args:
            hashtag: Hashtag to search (without #)
            max_results: Maximum number of posts to fetch
            since_date: Start date for posts
            
        Returns:
            TrendAnalysisResult with Twitter posts
        """
        try:
            posts = []
            
            # Prepare search query
            query = f"#{hashtag} -is:retweet lang:ja OR lang:en"
            
            # Date handling
            start_time = since_date.isoformat() if since_date else None
            end_time = datetime.now().isoformat()
            
            # Fetch tweets
            tweets = tweepy.Paginator(
                self.client.search_recent_tweets,
                query=query,
                tweet_fields=['created_at', 'author_id', 'public_metrics', 'entities'],
                user_fields=['username'],
                expansions=['author_id'],
                start_time=start_time,
                end_time=end_time,
                max_results=min(max_results, 100)  # API limit
            ).flatten(limit=max_results)
            
            # Convert tweets to posts
            users_dict = {}
            for tweet in tweets:
                # Get user info
                if hasattr(tweets, 'includes') and 'users' in tweets.includes:
                    for user in tweets.includes['users']:
                        users_dict[user.id] = user.username
                
                username = users_dict.get(tweet.author_id, f"user_{tweet.author_id}")
                
                # Extract hashtags
                hashtags_in_tweet = []
                if hasattr(tweet, 'entities') and 'hashtags' in tweet.entities:
                    hashtags_in_tweet = [tag['tag'] for tag in tweet.entities['hashtags']]
                
                # Create TwitterPost
                post = TwitterPost(
                    shortcode=str(tweet.id),
                    post_url=f"https://twitter.com/{username}/status/{tweet.id}",
                    owner_username=username,
                    owner_id=str(tweet.author_id),
                    posted_at=tweet.created_at,
                    likes=tweet.public_metrics['like_count'],
                    comments=tweet.public_metrics['reply_count'],
                    caption=tweet.text,
                    hashtags=hashtags_in_tweet,
                    is_video=False  # Could be enhanced to check for video
                )
                
                posts.append(post)
            
            # Create analysis result
            result = TrendAnalysisResult(
                hashtag=hashtag,
                start_date=since_date or datetime.now() - timedelta(days=7),
                end_date=datetime.now(),
                total_posts_fetched=len(posts),
                posts=posts
            )
            
            logger.info(f"Fetched {len(posts)} tweets for #{hashtag}")
            return result
            
        except tweepy.TooManyRequests:
            raise RateLimitError("Twitter API rate limit exceeded")
        except tweepy.Unauthorized:
            raise AuthenticationError("Twitter API authentication failed")
        except tweepy.NotFound:
            raise HashtagNotFoundError(f"No tweets found for #{hashtag}")
        except Exception as e:
            raise FetchError(f"Failed to fetch tweets for #{hashtag}: {e}")