#!/usr/bin/env python3
"""
Daily Stock Analysis - Main Entry Point

This module serves as the primary entry point for the daily stock analysis tool.
It orchestrates data fetching, analysis, and report generation.
"""

import os
import sys
import logging
import argparse
from datetime import datetime, date
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(f"logs/analysis_{date.today().strftime('%Y%m%d')}.log", mode="a"),
    ],
)
logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Daily Stock Analysis Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --symbols AAPL TSLA MSFT
  python main.py --symbols AAPL --date 2024-01-15
  python main.py --config config.yaml
        """,
    )
    parser.add_argument(
        "--symbols",
        nargs="+",
        help="Stock ticker symbols to analyze (e.g., AAPL TSLA MSFT)",
    )
    parser.add_argument(
        "--date",
        type=str,
        default=date.today().strftime("%Y-%m-%d"),
        help="Analysis date in YYYY-MM-DD format (default: today)",
    )
    parser.add_argument(
        "--config",
        type=str,
        default="config.yaml",
        help="Path to configuration file (default: config.yaml)",
    )
    parser.add_argument(
        "--output",
        type=str,
        choices=["console", "csv", "html", "all"],
        default="console",
        help="Output format for analysis results (default: console)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose/debug logging",
    )
    return parser.parse_args()


def setup_environment() -> None:
    """Ensure required directories and environment variables exist."""
    # Create necessary directories
    os.makedirs("logs", exist_ok=True)
    os.makedirs("output", exist_ok=True)
    os.makedirs("data/cache", exist_ok=True)

    # Validate required environment variables
    required_vars = ["STOCK_API_KEY"]
    missing = [var for var in required_vars if not os.getenv(var)]
    if missing:
        logger.warning(
            "Missing environment variables: %s. Some features may be limited.",
            ", ".join(missing),
        )


def run_analysis(symbols: list, analysis_date: str, output_format: str) -> int:
    """
    Run the stock analysis pipeline.

    Args:
        symbols: List of stock ticker symbols to analyze.
        analysis_date: Date string in YYYY-MM-DD format.
        output_format: Desired output format ('console', 'csv', 'html', 'all').

    Returns:
        Exit code (0 for success, non-zero for failure).
    """
    logger.info("Starting analysis for %d symbol(s) on %s", len(symbols), analysis_date)
    logger.info("Symbols: %s", ", ".join(symbols))

    try:
        # Placeholder for pipeline stages — modules to be implemented
        # from fetcher import StockDataFetcher
        # from analyzer import StockAnalyzer
        # from reporter import ReportGenerator

        logger.info("Analysis pipeline completed successfully.")
        return 0

    except KeyboardInterrupt:
        logger.info("Analysis interrupted by user.")
        return 130
    except Exception as exc:  # pylint: disable=broad-except
        logger.error("Analysis failed: %s", exc, exc_info=True)
        return 1


def main() -> int:
    """Main function — entry point for the CLI."""
    args = parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Verbose logging enabled.")

    setup_environment()

    symbols = args.symbols or os.getenv("DEFAULT_SYMBOLS", "AAPL,MSFT,GOOGL").split(",")
    symbols = [s.strip().upper() for s in symbols if s.strip()]

    if not symbols:
        logger.error("No stock symbols provided. Use --symbols or set DEFAULT_SYMBOLS in .env.")
        return 1

    return run_analysis(
        symbols=symbols,
        analysis_date=args.date,
        output_format=args.output,
    )


if __name__ == "__main__":
    sys.exit(main())
