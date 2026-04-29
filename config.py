"""Configuration management for daily stock analysis.

Loads and validates environment variables and provides
a centralized config object used throughout the application.
"""

import os
from dataclasses import dataclass, field
from typing import List, Optional
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()


@dataclass
class DatabaseConfig:
    """Database connection settings."""
    host: str = field(default_factory=lambda: os.getenv("DB_HOST", "localhost"))
    port: int = field(default_factory=lambda: int(os.getenv("DB_PORT", "5432")))
    name: str = field(default_factory=lambda: os.getenv("DB_NAME", "stock_analysis"))
    user: str = field(default_factory=lambda: os.getenv("DB_USER", "postgres"))
    password: str = field(default_factory=lambda: os.getenv("DB_PASSWORD", ""))

    @property
    def url(self) -> str:
        """Construct a SQLAlchemy-compatible database URL."""
        return (
            f"postgresql://{self.user}:{self.password}"
            f"@{self.host}:{self.port}/{self.name}"
        )


@dataclass
class StockAPIConfig:
    """Settings for the upstream stock data provider."""
    api_key: str = field(default_factory=lambda: os.getenv("STOCK_API_KEY", ""))
    base_url: str = field(
        default_factory=lambda: os.getenv(
            "STOCK_API_BASE_URL", "https://api.example.com/v1"
        )
    )
    timeout: int = field(default_factory=lambda: int(os.getenv("STOCK_API_TIMEOUT", "30")))
    max_retries: int = field(
        default_factory=lambda: int(os.getenv("STOCK_API_MAX_RETRIES", "3"))
    )


@dataclass
class NotificationConfig:
    """Email / webhook notification settings."""
    email_enabled: bool = field(
        default_factory=lambda: os.getenv("EMAIL_ENABLED", "false").lower() == "true"
    )
    smtp_host: str = field(default_factory=lambda: os.getenv("SMTP_HOST", ""))
    smtp_port: int = field(default_factory=lambda: int(os.getenv("SMTP_PORT", "587")))
    smtp_user: str = field(default_factory=lambda: os.getenv("SMTP_USER", ""))
    smtp_password: str = field(default_factory=lambda: os.getenv("SMTP_PASSWORD", ""))
    recipients: List[str] = field(
        default_factory=lambda: [
            addr.strip()
            for addr in os.getenv("NOTIFICATION_RECIPIENTS", "").split(",")
            if addr.strip()
        ]
    )
    webhook_url: Optional[str] = field(
        default_factory=lambda: os.getenv("WEBHOOK_URL") or None
    )


@dataclass
class AnalysisConfig:
    """Parameters controlling the stock analysis logic."""
    # Comma-separated list of ticker symbols to analyse
    tickers: List[str] = field(
        default_factory=lambda: [
            t.strip().upper()
            for t in os.getenv("TICKERS", "AAPL,MSFT,GOOG").split(",")
            if t.strip()
        ]
    )
    lookback_days: int = field(
        default_factory=lambda: int(os.getenv("LOOKBACK_DAYS", "30"))
    )
    # Moving-average windows (short and long)
    ma_short: int = field(default_factory=lambda: int(os.getenv("MA_SHORT", "5")))
    ma_long: int = field(default_factory=lambda: int(os.getenv("MA_LONG", "20")))
    output_dir: str = field(default_factory=lambda: os.getenv("OUTPUT_DIR", "output"))


@dataclass
class AppConfig:
    """Top-level application configuration."""
    debug: bool = field(
        default_factory=lambda: os.getenv("DEBUG", "false").lower() == "true"
    )
    log_level: str = field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO").upper())
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    stock_api: StockAPIConfig = field(default_factory=StockAPIConfig)
    notifications: NotificationConfig = field(default_factory=NotificationConfig)
    analysis: AnalysisConfig = field(default_factory=AnalysisConfig)

    def validate(self) -> None:
        """Raise ValueError for any missing required settings."""
        if not self.stock_api.api_key:
            raise ValueError(
                "STOCK_API_KEY environment variable is required but not set."
            )
        if self.analysis.ma_short >= self.analysis.ma_long:
            raise ValueError(
                f"MA_SHORT ({self.analysis.ma_short}) must be less than "
                f"MA_LONG ({self.analysis.ma_long})."
            )
        if not self.analysis.tickers:
            raise ValueError("TICKERS must contain at least one ticker symbol.")


# Module-level singleton — import this in other modules
config = AppConfig()
