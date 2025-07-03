"""Command-line interface for Instagram Trend Tool."""

import logging
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import click
from dateutil.parser import parse as parse_date

from .config import load_config
from .exporter import TrendExporter
from .fetcher import InstagramFetcher
from .models import FetchProgress
from .processor import TrendProcessor


# Configure logging
def setup_logging(verbose: bool, log_file: Optional[str] = None) -> None:
    """Set up logging configuration.
    
    Args:
        verbose: Enable verbose logging
        log_file: Optional log file path
    """
    log_level = logging.DEBUG if verbose else logging.INFO
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    handlers = [logging.StreamHandler(sys.stdout)]
    if log_file:
        handlers.append(logging.FileHandler(log_file))
    
    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=handlers,
    )


def validate_date(ctx, param, value):
    """Validate and parse date string."""
    if value is None:
        return value
    
    try:
        return parse_date(value).replace(tzinfo=None)
    except Exception:
        raise click.BadParameter(f"Invalid date format: {value}. Use YYYY-MM-DD")


def progress_callback(progress: FetchProgress) -> None:
    """Display progress during fetching."""
    click.echo(f"\r{progress.get_status_message()}", nl=False)


@click.command()
@click.option(
    "--tags",
    "-t",
    multiple=True,
    required=True,
    help="Hashtags to search (without #). Can specify multiple times.",
)
@click.option(
    "--since",
    callback=validate_date,
    help="Start date (YYYY-MM-DD). Default: 30 days ago",
)
@click.option(
    "--until",
    callback=validate_date,
    help="End date (YYYY-MM-DD). Default: today",
)
@click.option(
    "--top",
    "-n",
    type=int,
    help="Number of top posts to retrieve. Default: 50",
)
@click.option(
    "--min-likes",
    type=int,
    default=0,
    help="Minimum likes filter. Default: 0 (no filter)",
)
@click.option(
    "--output",
    "-o",
    type=click.Choice(["csv", "json", "excel", "all"], case_sensitive=False),
    default="csv",
    help="Output format. Default: csv",
)
@click.option(
    "--login",
    is_flag=True,
    help="Use Instagram login (credentials from .env or config)",
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Enable verbose logging",
)
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True),
    help="Path to config file (YAML)",
)
@click.option(
    "--no-slack",
    is_flag=True,
    help="Disable Slack notification even if configured",
)
@click.option(
    "--output-dir",
    type=click.Path(),
    help="Custom output directory",
)
def main(
    tags: tuple,
    since: Optional[datetime],
    until: Optional[datetime],
    top: Optional[int],
    min_likes: int,
    output: str,
    login: bool,
    verbose: bool,
    config: Optional[str],
    no_slack: bool,
    output_dir: Optional[str],
):
    """Instagram Trend Research Tool
    
    Fetch and analyze trending Instagram posts by hashtags.
    
    Examples:
    
        # Basic usage with single hashtag
        python -m insta_trend_tool.cli --tags travel
        
        # Multiple hashtags with date range
        python -m insta_trend_tool.cli --tags travel --tags food --since 2025-06-01 --until 2025-06-30
        
        # Export top 20 posts as JSON
        python -m insta_trend_tool.cli --tags fashion --top 20 --output json
        
        # Filter by minimum likes
        python -m insta_trend_tool.cli --tags photography --min-likes 1000
    """
    # Load configuration
    app_config = load_config(config)
    
    # Override config with CLI options
    if output_dir:
        app_config.output_dir = Path(output_dir)
    
    # Set up logging
    setup_logging(verbose, app_config.log_file)
    logger = logging.getLogger(__name__)
    
    # Welcome message
    click.echo("\n🔍 Instagram Trend Research Tool")
    click.echo("=" * 50)
    
    # Set default dates if not provided
    if not until:
        until = datetime.now()
    if not since:
        since = until - timedelta(days=app_config.default_days_back)
    
    # Set default top count
    if not top:
        top = app_config.default_top_count
    
    # Validate dates
    if since > until:
        click.echo("Error: Start date must be before end date", err=True)
        sys.exit(1)
    
    # Display search parameters
    click.echo(f"\n📋 Search Parameters:")
    click.echo(f"  • Hashtags: {', '.join(f'#{tag}' for tag in tags)}")
    click.echo(f"  • Period: {since.strftime('%Y-%m-%d')} to {until.strftime('%Y-%m-%d')}")
    click.echo(f"  • Top posts: {top}")
    if min_likes > 0:
        click.echo(f"  • Min likes: {min_likes}")
    click.echo(f"  • Output format: {output}")
    if login or (app_config.instagram_username and app_config.instagram_password):
        click.echo(f"  • Using Instagram login: Yes")
    click.echo("")
    
    try:
        # Initialize components
        fetcher = InstagramFetcher(app_config, progress_callback=progress_callback)
        processor = TrendProcessor()
        exporter = TrendExporter(app_config)
        
        # Fetch posts
        click.echo("🔄 Fetching posts from Instagram...")
        results = fetcher.fetch_multiple_hashtags(
            hashtags=list(tags),
            since_date=since,
            until_date=until,
            max_posts_per_tag=top * 2,  # Fetch extra to account for filtering
        )
        click.echo("")  # New line after progress
        
        # Process and analyze
        click.echo("\n📊 Processing data...")
        analysis = processor.analyze_trends(
            results=results,
            top_n=top,
            min_likes=min_likes if min_likes > 0 else None,
        )
        
        # Get top posts
        top_posts = analysis["top_posts"]
        
        if not top_posts:
            click.echo("\n⚠️  No posts found matching the criteria.")
            sys.exit(0)
        
        # Display summary
        summary = analysis["summary"]
        click.echo(f"\n✅ Analysis Complete!")
        click.echo(f"  • Total posts found: {summary['total_posts_analyzed']}")
        click.echo(f"  • Posts after filtering: {summary['filtered_posts']}")
        click.echo(f"  • Average engagement: {summary['average_engagement']:,.0f}")
        
        # Export results
        click.echo("\n💾 Exporting results...")
        
        export_paths = []
        
        if output in ["csv", "all"]:
            csv_path = exporter.export_to_csv(top_posts)
            export_paths.append(f"  • CSV: {csv_path}")
        
        if output in ["json", "all"]:
            json_path = exporter.export_to_json(top_posts, analysis)
            export_paths.append(f"  • JSON: {json_path}")
        
        if output in ["excel", "all"]:
            excel_path = exporter.export_to_excel(top_posts, analysis)
            export_paths.append(f"  • Excel: {excel_path}")
        
        for path in export_paths:
            click.echo(path)
        
        # Display top posts
        exporter.print_summary_table(top_posts, min(top, 10))
        
        # Send Slack notification if configured
        if app_config.slack_webhook_url and not no_slack:
            click.echo("\n📨 Sending Slack notification...")
            if exporter.send_slack_notification(top_posts, analysis):
                click.echo("  ✓ Slack notification sent")
            else:
                click.echo("  ✗ Failed to send Slack notification", err=True)
        
        # Display errors if any
        if analysis["errors"]:
            click.echo("\n⚠️  Errors encountered:")
            for error_info in analysis["errors"]:
                hashtag = error_info["hashtag"]
                errors = error_info["errors"]
                for error in errors:
                    click.echo(f"  • #{hashtag}: {error}")
        
        click.echo("\n✨ Done!")
        
    except KeyboardInterrupt:
        click.echo("\n\n⛔ Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.exception("Unexpected error occurred")
        click.echo(f"\n❌ Error: {str(e)}", err=True)
        if verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()