"""AI News Digest - Main entry point."""

import logging
import sys
from datetime import datetime, timezone

from feeds import fetch_articles
from summarizer import summarize_all
from generator import generate

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def main():
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    logger.info(f"=== AI News Digest - {today} ===")

    # Step 1: Fetch and filter articles
    logger.info("Step 1: Fetching RSS feeds...")
    articles = fetch_articles(max_articles=10)
    logger.info(f"Found {len(articles)} relevant articles")

    if not articles:
        logger.warning("No relevant articles found today. Generating empty page.")

    # Step 2: Summarize with Groq
    logger.info("Step 2: Generating AI summaries...")
    articles = summarize_all(articles)

    # Step 3: Generate HTML
    logger.info("Step 3: Generating HTML pages...")
    generate(articles, date_str=today)

    logger.info(f"=== Done! Processed {len(articles)} articles ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
