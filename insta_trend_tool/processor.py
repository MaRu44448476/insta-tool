"""Data processing module for filtering and sorting Instagram posts."""

import heapq
import logging
from datetime import datetime
from typing import Optional

from .models import InstagramPost, TrendAnalysisResult


logger = logging.getLogger(__name__)


class TrendProcessor:
    """Processes and analyzes Instagram trend data."""
    
    def merge_results(self, results: list[TrendAnalysisResult]) -> list[InstagramPost]:
        """Merge posts from multiple hashtag results.
        
        Args:
            results: List of TrendAnalysisResult objects
            
        Returns:
            Merged list of all posts
        """
        all_posts = []
        for result in results:
            all_posts.extend(result.posts)
        
        # Remove duplicates based on shortcode
        seen_shortcodes = set()
        unique_posts = []
        
        for post in all_posts:
            if post.shortcode not in seen_shortcodes:
                seen_shortcodes.add(post.shortcode)
                unique_posts.append(post)
            else:
                logger.debug(f"Duplicate post found: {post.shortcode}")
        
        logger.info(f"Merged {len(all_posts)} posts into {len(unique_posts)} unique posts")
        return unique_posts
    
    def filter_posts(
        self,
        posts: list[InstagramPost],
        min_likes: Optional[int] = None,
        min_comments: Optional[int] = None,
        min_engagement: Optional[int] = None,
        exclude_sponsored: bool = False,
    ) -> list[InstagramPost]:
        """Filter posts based on engagement criteria.
        
        Args:
            posts: List of posts to filter
            min_likes: Minimum number of likes
            min_comments: Minimum number of comments
            min_engagement: Minimum total engagement (likes + comments)
            exclude_sponsored: Whether to exclude sponsored posts
            
        Returns:
            Filtered list of posts
        """
        filtered_posts = posts
        
        if min_likes is not None:
            filtered_posts = [p for p in filtered_posts if p.likes >= min_likes]
            logger.info(f"Filtered to {len(filtered_posts)} posts with >= {min_likes} likes")
        
        if min_comments is not None:
            filtered_posts = [p for p in filtered_posts if p.comments >= min_comments]
            logger.info(f"Filtered to {len(filtered_posts)} posts with >= {min_comments} comments")
        
        if min_engagement is not None:
            filtered_posts = [p for p in filtered_posts if p.engagement_score >= min_engagement]
            logger.info(f"Filtered to {len(filtered_posts)} posts with >= {min_engagement} total engagement")
        
        if exclude_sponsored:
            filtered_posts = [p for p in filtered_posts if not p.is_sponsored]
            logger.info(f"Filtered to {len(filtered_posts)} non-sponsored posts")
        
        return filtered_posts
    
    def sort_posts(
        self,
        posts: list[InstagramPost],
        sort_by: str = "engagement",
        reverse: bool = True,
    ) -> list[InstagramPost]:
        """Sort posts by specified criteria.
        
        Args:
            posts: List of posts to sort
            sort_by: Sort criteria ('engagement', 'likes', 'comments', 'date')
            reverse: Whether to sort in descending order
            
        Returns:
            Sorted list of posts
        """
        sort_key_map = {
            "engagement": lambda p: p.engagement_score,
            "likes": lambda p: p.likes,
            "comments": lambda p: p.comments,
            "date": lambda p: p.posted_at,
        }
        
        if sort_by not in sort_key_map:
            logger.warning(f"Invalid sort_by value: {sort_by}. Using 'engagement'")
            sort_by = "engagement"
        
        sorted_posts = sorted(posts, key=sort_key_map[sort_by], reverse=reverse)
        logger.info(f"Sorted {len(sorted_posts)} posts by {sort_by}")
        
        return sorted_posts
    
    def get_top_posts_efficient(
        self,
        posts: list[InstagramPost],
        n: int,
        sort_by: str = "engagement",
    ) -> list[InstagramPost]:
        """Get top N posts efficiently using heap for large datasets.
        
        Args:
            posts: List of posts
            n: Number of top posts to return
            sort_by: Sort criteria
            
        Returns:
            Top N posts sorted by criteria
        """
        if len(posts) <= n:
            return self.sort_posts(posts, sort_by=sort_by)
        
        # Use heap for efficient top-N selection
        sort_key_map = {
            "engagement": lambda p: p.engagement_score,
            "likes": lambda p: p.likes,
            "comments": lambda p: p.comments,
            "date": lambda p: p.posted_at.timestamp() if isinstance(p.posted_at, datetime) else 0,
        }
        
        key_func = sort_key_map.get(sort_by, sort_key_map["engagement"])
        
        # Use negative values for max heap behavior
        top_posts = heapq.nlargest(n, posts, key=key_func)
        
        logger.info(f"Selected top {len(top_posts)} posts from {len(posts)} total")
        return top_posts
    
    def analyze_trends(
        self,
        results: list[TrendAnalysisResult],
        top_n: int = 50,
        min_likes: Optional[int] = None,
    ) -> dict:
        """Analyze trends across all hashtags.
        
        Args:
            results: List of hashtag analysis results
            top_n: Number of top posts to include
            min_likes: Minimum likes filter
            
        Returns:
            Dictionary with analysis results
        """
        # Merge all posts
        all_posts = self.merge_results(results)
        
        # Apply filters
        if min_likes:
            filtered_posts = self.filter_posts(all_posts, min_likes=min_likes)
        else:
            filtered_posts = all_posts
        
        # Get top posts
        top_posts = self.get_top_posts_efficient(filtered_posts, top_n)
        
        # Calculate statistics
        total_engagement = sum(p.engagement_score for p in filtered_posts)
        avg_engagement = total_engagement / len(filtered_posts) if filtered_posts else 0
        
        # Count posts by type
        video_count = sum(1 for p in filtered_posts if p.is_video)
        photo_count = len(filtered_posts) - video_count
        
        # Get most common hashtags (excluding search hashtags)
        hashtag_counts = {}
        search_hashtags = {r.hashtag.lower() for r in results}
        
        for post in filtered_posts:
            for tag in post.hashtags:
                tag_lower = tag.lower()
                if tag_lower not in search_hashtags:
                    hashtag_counts[tag_lower] = hashtag_counts.get(tag_lower, 0) + 1
        
        # Get top co-occurring hashtags
        top_hashtags = sorted(
            hashtag_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:20]
        
        analysis = {
            "summary": {
                "total_posts_analyzed": len(all_posts),
                "filtered_posts": len(filtered_posts),
                "total_engagement": total_engagement,
                "average_engagement": round(avg_engagement, 2),
                "video_posts": video_count,
                "photo_posts": photo_count,
                "hashtags_searched": [r.hashtag for r in results],
            },
            "top_posts": top_posts,
            "top_co_occurring_hashtags": [
                {"hashtag": tag, "count": count}
                for tag, count in top_hashtags
            ],
            "errors": [
                {"hashtag": r.hashtag, "errors": r.error_messages}
                for r in results if r.error_messages
            ],
        }
        
        return analysis