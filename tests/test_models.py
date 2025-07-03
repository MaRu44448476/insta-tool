"""Tests for data models."""

import pytest
from datetime import datetime, timedelta

from insta_trend_tool.models import InstagramPost, TrendAnalysisResult, FetchProgress


class TestInstagramPost:
    """Test InstagramPost model."""
    
    def test_engagement_score(self, sample_post):
        """Test engagement score calculation."""
        assert sample_post.engagement_score == 110  # 100 likes + 10 comments
    
    def test_post_type_photo(self, sample_post):
        """Test post type for photo."""
        assert sample_post.post_type == "photo"
    
    def test_post_type_video(self, sample_post):
        """Test post type for video."""
        sample_post.is_video = True
        assert sample_post.post_type == "video"
    
    def test_to_dict(self, sample_post):
        """Test conversion to dictionary."""
        result = sample_post.to_dict()
        
        assert result["shortcode"] == "ABC123"
        assert result["likes"] == 100
        assert result["comments"] == 10
        assert result["engagement_score"] == 110
        assert result["hashtags"] == "travel, food"
        assert result["post_type"] == "photo"
        assert result["video_views"] is None
        assert "posted_at" in result


class TestTrendAnalysisResult:
    """Test TrendAnalysisResult model."""
    
    def test_total_engagement(self, sample_analysis_result):
        """Test total engagement calculation."""
        # Posts have likes: 100, 90, 80, 70, 60 and comments: 10, 11, 12, 13, 14
        # Total: (100+90+80+70+60) + (10+11+12+13+14) = 400 + 60 = 460
        assert sample_analysis_result.total_engagement == 460
    
    def test_average_engagement(self, sample_analysis_result):
        """Test average engagement calculation."""
        assert sample_analysis_result.average_engagement == 92.0  # 460 / 5
    
    def test_average_engagement_empty(self):
        """Test average engagement with no posts."""
        result = TrendAnalysisResult(
            hashtag="empty",
            start_date=datetime.now(),
            end_date=datetime.now(),
            total_posts_fetched=0,
            posts=[],
        )
        assert result.average_engagement == 0.0
    
    def test_get_top_posts(self, sample_analysis_result):
        """Test getting top posts."""
        top_3 = sample_analysis_result.get_top_posts(3)
        
        assert len(top_3) == 3
        # First post should have highest engagement (100 + 10 = 110)
        assert top_3[0].shortcode == "POST0"
        assert top_3[0].engagement_score == 110
    
    def test_filter_by_min_likes(self, sample_analysis_result):
        """Test filtering by minimum likes."""
        filtered = sample_analysis_result.filter_by_min_likes(85)
        
        # Only posts with 90 and 100 likes should remain
        assert len(filtered) == 2
        assert all(post.likes >= 85 for post in filtered)


class TestFetchProgress:
    """Test FetchProgress model."""
    
    def test_percentage_calculation(self):
        """Test percentage calculation."""
        progress = FetchProgress(
            current_hashtag="test",
            total_hashtags=4,
            current_hashtag_index=2,
            posts_fetched=10,
        )
        assert progress.percentage == 50.0
    
    def test_percentage_zero_total(self):
        """Test percentage with zero total hashtags."""
        progress = FetchProgress(
            current_hashtag="test",
            total_hashtags=0,
            current_hashtag_index=0,
            posts_fetched=0,
        )
        assert progress.percentage == 0.0
    
    def test_status_message(self):
        """Test status message generation."""
        progress = FetchProgress(
            current_hashtag="travel",
            total_hashtags=5,
            current_hashtag_index=3,
            posts_fetched=25,
        )
        message = progress.get_status_message()
        
        assert "#travel" in message
        assert "(3/5)" in message
        assert "25 posts fetched" in message