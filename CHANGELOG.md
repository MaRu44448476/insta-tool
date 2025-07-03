# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-07-03

### Added
- Initial release of Instagram Trend Tool
- Core functionality for hashtag-based post fetching
- Support for multiple hashtags search
- Date range filtering (--since, --until)
- Engagement-based ranking and sorting
- Multiple export formats (CSV, JSON, Excel)
- CLI interface with comprehensive options
- Configuration management via .env and YAML files
- Slack notification support
- Instagram login support (optional)
- Rate limiting and error handling
- Progress tracking during fetch operations
- Custom exception classes for better error handling
- Enhanced logging with color support and file rotation
- Comprehensive test suite with pytest
- Docker support (future release)

### Features
- **Data Collection**:
  - Fetch Instagram posts by hashtags
  - Date range filtering
  - Engagement metrics (likes, comments)
  - Video view count support
  - Location and sponsorship detection
  - Duplicate post removal

- **Data Processing**:
  - Engagement-based ranking
  - Multiple filtering options (min likes, comments)
  - Statistical analysis (averages, totals)
  - Co-occurring hashtag analysis
  - Efficient top-N selection for large datasets

- **Export Options**:
  - CSV (Excel compatible with UTF-8 BOM)
  - JSON (structured data with metadata)
  - Excel (multi-sheet with analysis)
  - Console table display

- **Configuration**:
  - Environment variables (.env)
  - YAML configuration files
  - CLI option overrides
  - Default value management

- **Error Handling**:
  - Rate limit detection and backoff
  - Authentication error handling
  - Network error resilience
  - Graceful degradation

- **Logging & Monitoring**:
  - Colored console output
  - File logging with rotation
  - Progress indicators
  - Verbose and quiet modes

### Technical Details
- Python 3.10+ compatibility
- Type hints throughout codebase
- Modular architecture (fetcher, processor, exporter)
- Comprehensive error handling
- Unit and integration tests
- PEP 8 compliant code style
- MIT License

### Dependencies
- instaloader==4.11 (Instagram API)
- pandas==2.2.2 (Data processing)
- click==8.1.7 (CLI framework)
- python-dateutil==2.9.0 (Date parsing)
- python-dotenv==1.0.1 (Environment variables)
- slack-sdk==3.27.1 (Slack notifications)
- pyyaml==6.0.1 (YAML configuration)

### Known Limitations
- Requires public Instagram posts only
- Subject to Instagram's rate limiting
- No real-time data streaming
- Limited to hashtag-based search (no keyword search in captions)

### Security
- No credential storage in code
- Environment variable based configuration
- Secure error message handling
- Input validation and sanitization