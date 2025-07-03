"""Test configuration and fixtures."""

import pytest
from datetime import datetime, timedelta
from pathlib import Path

from insta_trend_tool.config import Config
from insta_trend_tool.models import InstagramPost, TrendAnalysisResult


@pytest.fixture
def sample_config():
    """Sample configuration for testing."""
    return Config(
        instagram_username=None,
        instagram_password=None,
        slack_webhook_url=None,
        default_top_count=10,
        default_days_back=7,
        request_delay_min=0.1,
        request_delay_max=0.2,
        max_retries=2,
        retry_delay=1.0,
        output_dir=Path("test_output"),
        log_level="DEBUG",
    )


@pytest.fixture
def sample_post():
    """Sample Instagram post for testing."""
    return InstagramPost(
        shortcode="ABC123",
        post_url="https://instagram.com/p/ABC123/",
        owner_username="testuser",
        owner_id="12345",
        posted_at=datetime.now() - timedelta(days=1),
        likes=100,
        comments=10,
        caption="Test post #travel #food",
        hashtags=["travel", "food"],
        is_video=False,
        video_view_count=None,
        location="Tokyo",
        is_sponsored=False,
    )


@pytest.fixture
def sample_posts():
    """List of sample posts for testing."""
    base_time = datetime.now()
    return [
        InstagramPost(
            shortcode=f"POST{i}",
            post_url=f"https://instagram.com/p/POST{i}/",
            owner_username=f"user{i}",
            owner_id=str(1000 + i),
            posted_at=base_time - timedelta(hours=i),
            likes=100 - i * 10,
            comments=10 + i,
            caption=f"Test post {i} #test",
            hashtags=["test"],
            is_video=i % 2 == 0,
            video_view_count=200 if i % 2 == 0 else None,
        )
        for i in range(5)
    ]


@pytest.fixture
def sample_analysis_result(sample_posts):
    """Sample trend analysis result for testing."""
    start_date = datetime.now() - timedelta(days=7)
    end_date = datetime.now()
    
    return TrendAnalysisResult(
        hashtag="test",
        start_date=start_date,
        end_date=end_date,
        total_posts_fetched=len(sample_posts),
        posts=sample_posts,
    )