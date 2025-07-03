"""Custom exceptions for Instagram Trend Tool."""


class InstagramTrendToolError(Exception):
    """Base exception for Instagram Trend Tool."""
    pass


class ConfigurationError(InstagramTrendToolError):
    """Raised when there's a configuration error."""
    pass


class AuthenticationError(InstagramTrendToolError):
    """Raised when Instagram authentication fails."""
    pass


class FetchError(InstagramTrendToolError):
    """Raised when post fetching fails."""
    pass


class RateLimitError(FetchError):
    """Raised when rate limit is exceeded."""
    pass


class HashtagNotFoundError(FetchError):
    """Raised when hashtag is not found or doesn't exist."""
    pass


class ExportError(InstagramTrendToolError):
    """Raised when export operation fails."""
    pass


class ValidationError(InstagramTrendToolError):
    """Raised when input validation fails."""
    pass