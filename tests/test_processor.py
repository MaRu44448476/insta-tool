"""Tests for data processing module."""

import pytest
from datetime import datetime, timedelta

from insta_trend_tool.models import InstagramPost, TrendAnalysisResult
from insta_trend_tool.processor import TrendProcessor


class TestTrendProcessor:
    """Test TrendProcessor class."""
    
    @pytest.fixture
    def processor(self):
        """Create processor instance."""
        return TrendProcessor()
    
    @pytest.fixture
    def duplicate_posts(self):
        """Create posts with duplicates for testing."""
        base_time = datetime.now()
        return [
            InstagramPost(
                shortcode="SAME1",
                post_url="https://instagram.com/p/SAME1/",
                owner_username="user1",
                owner_id="1001",
                posted_at=base_time,
                likes=100,
                comments=10,
                caption="Post 1",
                hashtags=["test"],
            ),
            InstagramPost(
                shortcode="SAME1",  # Duplicate shortcode
                post_url="https://instagram.com/p/SAME1/",
                owner_username="user1",
                owner_id="1001",
                posted_at=base_time,
                likes=100,
                comments=10,
                caption="Post 1",
                hashtags=["test"],
            ),
            InstagramPost(
                shortcode="UNIQUE1",
                post_url="https://instagram.com/p/UNIQUE1/",
                owner_username="user2",
                owner_id="1002",
                posted_at=base_time,
                likes=50,
                comments=5,
                caption="Post 2",
                hashtags=["test"],
            ),
        ]
    
    def test_merge_results_no_duplicates(self, processor, sample_analysis_result):
        """Test merging results without duplicates."""
        results = [sample_analysis_result]
        merged = processor.merge_results(results)
        
        assert len(merged) == 5  # All posts from sample
    
    def test_merge_results_with_duplicates(self, processor, duplicate_posts):
        """Test merging results with duplicate posts."""
        result1 = TrendAnalysisResult(
            hashtag="test1",
            start_date=datetime.now(),
            end_date=datetime.now(),
            total_posts_fetched=2,
            posts=duplicate_posts[:2],  # First two posts (one duplicate)
        )
        
        result2 = TrendAnalysisResult(
            hashtag="test2",
            start_date=datetime.now(),
            end_date=datetime.now(),
            total_posts_fetched=1,
            posts=duplicate_posts[2:],  # Last post (unique)
        )
        
        merged = processor.merge_results([result1, result2])
        
        # Should have 2 unique posts (duplicate removed)
        assert len(merged) == 2
        shortcodes = [post.shortcode for post in merged]
        assert "SAME1" in shortcodes
        assert "UNIQUE1" in shortcodes
    
    def test_filter_posts_min_likes(self, processor, sample_posts):
        """Test filtering posts by minimum likes."""
        filtered = processor.filter_posts(sample_posts, min_likes=85)
        
        # Only posts with 90 and 100 likes should remain
        assert len(filtered) == 2
        assert all(post.likes >= 85 for post in filtered)
    
    def test_filter_posts_min_comments(self, processor, sample_posts):
        """Test filtering posts by minimum comments."""
        filtered = processor.filter_posts(sample_posts, min_comments=12)
        
        # Posts have comments: 10, 11, 12, 13, 14
        # Should keep posts with 12, 13, 14 comments
        assert len(filtered) == 3
        assert all(post.comments >= 12 for post in filtered)
    
    def test_filter_posts_min_engagement(self, processor, sample_posts):
        """Test filtering posts by minimum engagement."""
        # Post engagements: 110, 101, 92, 83, 74
        filtered = processor.filter_posts(sample_posts, min_engagement=90)
        
        assert len(filtered) == 3
        assert all(post.engagement_score >= 90 for post in filtered)
    
    def test_filter_posts_exclude_sponsored(self, processor, sample_posts):
        """Test excluding sponsored posts."""
        # Mark one post as sponsored
        sample_posts[0].is_sponsored = True
        
        filtered = processor.filter_posts(sample_posts, exclude_sponsored=True)
        
        assert len(filtered) == 4
        assert all(not post.is_sponsored for post in filtered)
    
    def test_sort_posts_by_engagement(self, processor, sample_posts):
        """Test sorting posts by engagement."""
        sorted_posts = processor.sort_posts(sample_posts, sort_by="engagement")
        
        # Should be in descending order of engagement
        engagements = [post.engagement_score for post in sorted_posts]
        assert engagements == sorted(engagements, reverse=True)
    
    def test_sort_posts_by_likes(self, processor, sample_posts):
        """Test sorting posts by likes."""
        sorted_posts = processor.sort_posts(sample_posts, sort_by="likes")
        
        likes = [post.likes for post in sorted_posts]
        assert likes == sorted(likes, reverse=True)
    
    def test_sort_posts_ascending(self, processor, sample_posts):
        """Test sorting posts in ascending order."""
        sorted_posts = processor.sort_posts(sample_posts, sort_by="likes", reverse=False)
        
        likes = [post.likes for post in sorted_posts]
        assert likes == sorted(likes)
    
    def test_sort_posts_invalid_criteria(self, processor, sample_posts):
        """Test sorting with invalid criteria."""
        # Should fall back to engagement sorting
        sorted_posts = processor.sort_posts(sample_posts, sort_by="invalid")
        
        engagements = [post.engagement_score for post in sorted_posts]
        assert engagements == sorted(engagements, reverse=True)
    
    def test_get_top_posts_efficient_small_dataset(self, processor, sample_posts):
        """Test efficient top posts selection with small dataset."""
        top_3 = processor.get_top_posts_efficient(sample_posts, 3)
        
        assert len(top_3) == 3
        # Should be sorted by engagement
        engagements = [post.engagement_score for post in top_3]
        assert engagements == sorted(engagements, reverse=True)
    
    def test_get_top_posts_efficient_larger_than_dataset(self, processor, sample_posts):
        """Test efficient top posts selection when n > dataset size."""
        top_10 = processor.get_top_posts_efficient(sample_posts, 10)
        
        assert len(top_10) == 5  # All available posts
    
    def test_analyze_trends(self, processor, sample_analysis_result):
        """Test comprehensive trend analysis."""
        analysis = processor.analyze_trends([sample_analysis_result], top_n=3)
        
        assert "summary" in analysis
        assert "top_posts" in analysis
        assert "top_co_occurring_hashtags" in analysis
        assert "errors" in analysis
        
        summary = analysis["summary"]
        assert summary["total_posts_analyzed"] == 5
        assert summary["filtered_posts"] == 5
        assert "average_engagement" in summary
        
        # Should have 3 top posts
        assert len(analysis["top_posts"]) == 3
    
    def test_analyze_trends_with_min_likes(self, processor, sample_analysis_result):
        """Test trend analysis with minimum likes filter."""
        analysis = processor.analyze_trends([sample_analysis_result], top_n=10, min_likes=85)
        
        summary = analysis["summary"]
        assert summary["total_posts_analyzed"] == 5
        assert summary["filtered_posts"] == 2  # Only 2 posts have >= 85 likes
        
        # All returned posts should have >= 85 likes
        for post in analysis["top_posts"]:
            assert post.likes >= 85