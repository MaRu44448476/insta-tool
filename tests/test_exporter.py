"""Tests for export functionality."""

import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
import responses

from insta_trend_tool.exporter import TrendExporter


class TestTrendExporter:
    """Test TrendExporter class."""
    
    @pytest.fixture
    def exporter(self, sample_config):
        """Create exporter instance."""
        return TrendExporter(sample_config)
    
    @pytest.fixture
    def temp_output_dir(self, sample_config):
        """Create temporary output directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            sample_config.output_dir = Path(tmpdir)
            yield Path(tmpdir)
    
    def test_ensure_output_dir(self, exporter, temp_output_dir):
        """Test output directory creation."""
        output_dir = exporter.ensure_output_dir()
        
        assert output_dir.exists()
        assert output_dir.is_dir()
    
    def test_generate_filename(self, exporter):
        """Test filename generation."""
        filename = exporter.generate_filename("test", "csv")
        
        assert filename.startswith("test_")
        assert filename.endswith(".csv")
        assert len(filename) > 10  # Should include timestamp
    
    def test_export_to_csv(self, exporter, sample_posts, temp_output_dir):
        """Test CSV export."""
        filepath = exporter.export_to_csv(sample_posts)
        
        assert filepath.exists()
        assert filepath.suffix == ".csv"
        
        # Check file content
        with open(filepath, 'r', encoding='utf-8-sig') as f:
            content = f.read()
            assert "post_url" in content
            assert "shortcode" in content
            assert "POST0" in content
    
    def test_export_to_csv_empty(self, exporter, temp_output_dir):
        """Test CSV export with empty posts."""
        filepath = exporter.export_to_csv([])
        
        assert filepath.exists()
        # File should be created even if empty
    
    def test_export_to_json(self, exporter, sample_posts, temp_output_dir):
        """Test JSON export."""
        analysis_data = {"summary": {"total_posts": len(sample_posts)}}
        filepath = exporter.export_to_json(sample_posts, analysis_data)
        
        assert filepath.exists()
        assert filepath.suffix == ".json"
        
        # Check file content
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            assert "metadata" in data
            assert "posts" in data
            assert "analysis" in data
            assert len(data["posts"]) == len(sample_posts)
    
    def test_export_to_json_no_analysis(self, exporter, sample_posts, temp_output_dir):
        """Test JSON export without analysis data."""
        filepath = exporter.export_to_json(sample_posts)
        
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            assert "analysis" not in data
    
    def test_format_slack_message(self, exporter, sample_posts):
        """Test Slack message formatting."""
        analysis_data = {
            "summary": {
                "total_posts_analyzed": len(sample_posts),
                "average_engagement": 92.0,
                "hashtags_searched": ["test"],
            }
        }
        
        message = exporter.format_slack_message(sample_posts, analysis_data, top_n=3)
        
        assert "blocks" in message
        blocks = message["blocks"]
        
        # Should have header and content blocks
        assert len(blocks) >= 3
        assert blocks[0]["type"] == "header"
    
    @responses.activate
    def test_send_slack_notification_success(self, sample_config, sample_posts):
        """Test successful Slack notification."""
        sample_config.slack_webhook_url = "https://hooks.slack.com/test"
        exporter = TrendExporter(sample_config)
        
        responses.add(
            responses.POST,
            "https://hooks.slack.com/test",
            status=200,
        )
        
        result = exporter.send_slack_notification(sample_posts)
        
        assert result is True
        assert len(responses.calls) == 1
    
    @responses.activate
    def test_send_slack_notification_failure(self, sample_config, sample_posts):
        """Test failed Slack notification."""
        sample_config.slack_webhook_url = "https://hooks.slack.com/test"
        exporter = TrendExporter(sample_config)
        
        responses.add(
            responses.POST,
            "https://hooks.slack.com/test",
            status=500,
        )
        
        result = exporter.send_slack_notification(sample_posts)
        
        assert result is False
    
    def test_send_slack_notification_no_url(self, exporter, sample_posts):
        """Test Slack notification without URL configured."""
        result = exporter.send_slack_notification(sample_posts)
        
        assert result is False
    
    def test_print_summary_table_empty(self, exporter, capsys):
        """Test printing summary table with empty posts."""
        exporter.print_summary_table([])
        
        captured = capsys.readouterr()
        assert "No posts to display" in captured.out
    
    def test_print_summary_table_with_posts(self, exporter, sample_posts, capsys):
        """Test printing summary table with posts."""
        exporter.print_summary_table(sample_posts, top_n=3)
        
        captured = capsys.readouterr()
        assert "TOP 3 POSTS" in captured.out
        assert "Rank" in captured.out
        assert "Username" in captured.out
        assert "POST0" in captured.out  # First post should be shown