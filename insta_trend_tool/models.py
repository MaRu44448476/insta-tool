"""Data models for Instagram Trend Tool."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class InstagramPost:
    """Represents an Instagram post with engagement metrics."""
    
    # Basic identifiers
    shortcode: str
    post_url: str
    owner_username: str
    owner_id: str
    
    # Timestamps
    posted_at: datetime
    
    # Engagement metrics
    likes: int
    comments: int
    
    # Content
    caption: str
    hashtags: list[str] = field(default_factory=list)
    
    # Media information
    is_video: bool = False
    video_view_count: Optional[int] = None
    
    # Additional metadata
    location: Optional[str] = None
    is_sponsored: bool = False
    
    @property
    def engagement_score(self) -> int:
        """Calculate total engagement score."""
        return self.likes + self.comments
    
    @property
    def post_type(self) -> str:
        """Get the type of post."""
        return "video" if self.is_video else "photo"
    
    def to_dict(self) -> dict:
        """Convert to dictionary for export."""
        return {
            "post_url": self.post_url,
            "shortcode": self.shortcode,
            "posted_at": self.posted_at.isoformat(),
            "likes": self.likes,
            "comments": self.comments,
            "engagement_score": self.engagement_score,
            "owner_username": self.owner_username,
            "caption": self.caption,
            "hashtags": ", ".join(self.hashtags),
            "post_type": self.post_type,
            "video_views": self.video_view_count if self.is_video else None,
            "location": self.location,
            "is_sponsored": self.is_sponsored,
        }


@dataclass
class TrendAnalysisResult:
    """Results of hashtag trend analysis."""
    
    hashtag: str
    start_date: datetime
    end_date: datetime
    total_posts_fetched: int
    posts: list[InstagramPost] = field(default_factory=list)
    
    # Analysis metadata
    fetch_timestamp: datetime = field(default_factory=datetime.now)
    error_messages: list[str] = field(default_factory=list)
    
    @property
    def total_engagement(self) -> int:
        """Calculate total engagement across all posts."""
        return sum(post.engagement_score for post in self.posts)
    
    @property
    def average_engagement(self) -> float:
        """Calculate average engagement per post."""
        if not self.posts:
            return 0.0
        return self.total_engagement / len(self.posts)
    
    def get_top_posts(self, n: int = 10) -> list[InstagramPost]:
        """Get top N posts by engagement."""
        return sorted(
            self.posts,
            key=lambda p: p.engagement_score,
            reverse=True
        )[:n]
    
    def filter_by_min_likes(self, min_likes: int) -> list[InstagramPost]:
        """Filter posts by minimum likes."""
        return [post for post in self.posts if post.likes >= min_likes]


@dataclass
class FetchProgress:
    """Track progress of fetching operation."""
    
    current_hashtag: str
    total_hashtags: int
    current_hashtag_index: int
    posts_fetched: int
    estimated_total: Optional[int] = None
    
    @property
    def percentage(self) -> float:
        """Calculate completion percentage."""
        if self.total_hashtags == 0:
            return 0.0
        return (self.current_hashtag_index / self.total_hashtags) * 100
    
    def get_status_message(self) -> str:
        """Get human-readable status message."""
        return (
            f"Processing #{self.current_hashtag} "
            f"({self.current_hashtag_index}/{self.total_hashtags}): "
            f"{self.posts_fetched} posts fetched"
        )