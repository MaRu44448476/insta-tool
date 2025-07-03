"""Export functionality for Instagram trend data."""

import csv
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

import pandas as pd
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from .config import Config
from .models import InstagramPost


logger = logging.getLogger(__name__)


class TrendExporter:
    """Handles exporting trend data to various formats."""
    
    def __init__(self, config: Config):
        """Initialize exporter with configuration.
        
        Args:
            config: Application configuration
        """
        self.config = config
        self.slack_client = None
        
        # Initialize Slack client if webhook URL is provided
        if config.slack_webhook_url:
            self.slack_client = WebClient(token="")  # Webhook doesn't need token
    
    def ensure_output_dir(self) -> Path:
        """Ensure output directory exists.
        
        Returns:
            Path to output directory
        """
        output_dir = self.config.output_dir
        output_dir.mkdir(parents=True, exist_ok=True)
        return output_dir
    
    def generate_filename(self, prefix: str, extension: str) -> str:
        """Generate timestamped filename.
        
        Args:
            prefix: Filename prefix
            extension: File extension (without dot)
            
        Returns:
            Generated filename
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{prefix}_{timestamp}.{extension}"
    
    def export_to_csv(
        self,
        posts: list[InstagramPost],
        filename: Optional[str] = None,
        include_header: bool = True,
    ) -> Path:
        """Export posts to CSV file.
        
        Args:
            posts: List of posts to export
            filename: Optional custom filename
            include_header: Whether to include CSV header
            
        Returns:
            Path to exported file
        """
        output_dir = self.ensure_output_dir()
        
        if not filename:
            filename = self.generate_filename("instagram_trends", "csv")
        
        filepath = output_dir / filename
        
        # Prepare data for CSV
        rows = []
        for post in posts:
            row_data = post.to_dict()
            # Flatten nested data for CSV
            row_data["posted_at"] = row_data["posted_at"].replace("T", " ")
            rows.append(row_data)
        
        # Write CSV with UTF-8 BOM for Excel compatibility
        with open(filepath, "w", newline="", encoding="utf-8-sig") as csvfile:
            if not rows:
                logger.warning("No data to export to CSV")
                return filepath
            
            fieldnames = rows[0].keys()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            if include_header:
                writer.writeheader()
            writer.writerows(rows)
        
        logger.info(f"Exported {len(posts)} posts to {filepath}")
        return filepath
    
    def export_to_json(
        self,
        posts: list[InstagramPost],
        analysis_data: Optional[dict] = None,
        filename: Optional[str] = None,
        pretty: bool = True,
    ) -> Path:
        """Export posts and analysis to JSON file.
        
        Args:
            posts: List of posts to export
            analysis_data: Optional analysis results to include
            filename: Optional custom filename
            pretty: Whether to format JSON with indentation
            
        Returns:
            Path to exported file
        """
        output_dir = self.ensure_output_dir()
        
        if not filename:
            filename = self.generate_filename("instagram_trends", "json")
        
        filepath = output_dir / filename
        
        # Prepare export data
        export_data = {
            "metadata": {
                "export_timestamp": datetime.now().isoformat(),
                "total_posts": len(posts),
                "tool_version": "1.0.0",
            },
            "posts": [post.to_dict() for post in posts],
        }
        
        # Add analysis data if provided
        if analysis_data:
            export_data["analysis"] = analysis_data
        
        # Write JSON
        with open(filepath, "w", encoding="utf-8") as jsonfile:
            if pretty:
                json.dump(export_data, jsonfile, ensure_ascii=False, indent=2)
            else:
                json.dump(export_data, jsonfile, ensure_ascii=False)
        
        logger.info(f"Exported {len(posts)} posts to {filepath}")
        return filepath
    
    def export_to_excel(
        self,
        posts: list[InstagramPost],
        analysis_data: Optional[dict] = None,
        filename: Optional[str] = None,
    ) -> Path:
        """Export posts to Excel file with multiple sheets.
        
        Args:
            posts: List of posts to export
            analysis_data: Optional analysis results to include
            filename: Optional custom filename
            
        Returns:
            Path to exported file
        """
        output_dir = self.ensure_output_dir()
        
        if not filename:
            filename = self.generate_filename("instagram_trends", "xlsx")
        
        filepath = output_dir / filename
        
        # Create Excel writer
        with pd.ExcelWriter(filepath, engine="openpyxl") as writer:
            # Posts sheet
            posts_data = [post.to_dict() for post in posts]
            if posts_data:
                df_posts = pd.DataFrame(posts_data)
                df_posts.to_excel(writer, sheet_name="Posts", index=False)
            
            # Analysis sheet if provided
            if analysis_data and "summary" in analysis_data:
                df_summary = pd.DataFrame([analysis_data["summary"]])
                df_summary.to_excel(writer, sheet_name="Summary", index=False)
                
                # Top hashtags sheet
                if "top_co_occurring_hashtags" in analysis_data:
                    df_hashtags = pd.DataFrame(analysis_data["top_co_occurring_hashtags"])
                    df_hashtags.to_excel(writer, sheet_name="Top Hashtags", index=False)
        
        logger.info(f"Exported {len(posts)} posts to Excel file {filepath}")
        return filepath
    
    def format_slack_message(
        self,
        posts: list[InstagramPost],
        analysis_data: Optional[dict] = None,
        top_n: int = 5,
    ) -> dict:
        """Format data for Slack notification.
        
        Args:
            posts: List of posts
            analysis_data: Optional analysis results
            top_n: Number of top posts to include
            
        Returns:
            Slack message payload
        """
        # Get top posts
        top_posts = posts[:top_n]
        
        # Build message blocks
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "📊 Instagram Trend Analysis Results",
                }
            },
        ]
        
        # Add summary if available
        if analysis_data and "summary" in analysis_data:
            summary = analysis_data["summary"]
            blocks.append({
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Total Posts:* {summary.get('total_posts_analyzed', 0)}",
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Avg Engagement:* {summary.get('average_engagement', 0):,.0f}",
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Hashtags:* {', '.join(summary.get('hashtags_searched', []))}",
                    },
                ],
            })
        
        # Add top posts
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Top {len(top_posts)} Posts by Engagement:*",
            }
        })
        
        for i, post in enumerate(top_posts, 1):
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": (
                        f"{i}. *@{post.owner_username}* - "
                        f"❤️ {post.likes:,} | 💬 {post.comments:,}\n"
                        f"   <{post.post_url}|View Post>"
                    ),
                },
            })
        
        return {"blocks": blocks}
    
    def send_slack_notification(
        self,
        posts: list[InstagramPost],
        analysis_data: Optional[dict] = None,
    ) -> bool:
        """Send Slack notification with results.
        
        Args:
            posts: List of posts
            analysis_data: Optional analysis results
            
        Returns:
            True if successful, False otherwise
        """
        if not self.config.slack_webhook_url:
            logger.warning("Slack webhook URL not configured")
            return False
        
        try:
            import requests
            
            payload = self.format_slack_message(posts, analysis_data)
            response = requests.post(
                self.config.slack_webhook_url,
                json=payload,
                timeout=5,
            )
            response.raise_for_status()
            
            logger.info("Successfully sent Slack notification")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send Slack notification: {e}")
            return False
    
    def print_summary_table(
        self,
        posts: list[InstagramPost],
        top_n: int = 10,
    ) -> None:
        """Print summary table to console.
        
        Args:
            posts: List of posts to display
            top_n: Number of posts to show
        """
        if not posts:
            print("\nNo posts to display.")
            return
        
        # Get top posts
        display_posts = posts[:top_n]
        
        # Print header
        print("\n" + "=" * 100)
        print(f"TOP {len(display_posts)} POSTS BY ENGAGEMENT")
        print("=" * 100)
        print(f"{'Rank':<5} {'Username':<20} {'Likes':<10} {'Comments':<10} {'Total':<10} {'Posted':<20} {'URL':<30}")
        print("-" * 100)
        
        # Print posts
        for i, post in enumerate(display_posts, 1):
            print(
                f"{i:<5} "
                f"{post.owner_username[:19]:<20} "
                f"{post.likes:<10,} "
                f"{post.comments:<10,} "
                f"{post.engagement_score:<10,} "
                f"{post.posted_at.strftime('%Y-%m-%d %H:%M'):<20} "
                f"{post.post_url[:29]:<30}"
            )
        
        print("=" * 100)