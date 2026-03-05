"""Fetch and filter RSS feeds for AI news."""

import logging
import re
from datetime import datetime, timezone
from typing import TypedDict

import feedparser

logger = logging.getLogger(__name__)

FEEDS = [
    {
        "name": "TechCrunch AI",
        "url": "https://techcrunch.com/category/artificial-intelligence/feed/",
    },
    {
        "name": "The Verge AI",
        "url": "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml",
    },
    {
        "name": "Ars Technica",
        "url": "https://feeds.arstechnica.com/arstechnica/technology-lab",
    },
    {
        "name": "MIT Technology Review",
        "url": "https://www.technologyreview.com/feed/",
    },
]

INCLUDE_KEYWORDS = [
    "agent", "agentic", "llm", "claude", "gpt", "openai", "anthropic",
    "automation", "ai workflow", "machine learning", "neural", "transformer",
    "artificial intelligence", "deep learning", "generative ai", "large language model",
    "copilot", "gemini", "mistral", "llama", "chatbot", "prompt",
]

EXCLUDE_PATTERNS = [
    r"\d+ best .+",
    r"\d+ top .+",
    r"listicle",
    r"deals? of the (day|week)",
    r"sale alert",
]


class Article(TypedDict):
    title: str
    link: str
    summary: str
    source: str
    published: str
    score: int


def _parse_date(entry) -> str:
    """Extract and format the publication date from a feed entry."""
    for attr in ("published_parsed", "updated_parsed"):
        parsed = getattr(entry, attr, None)
        if parsed:
            try:
                dt = datetime(*parsed[:6], tzinfo=timezone.utc)
                return dt.strftime("%Y-%m-%d %H:%M UTC")
            except Exception:
                pass
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def _get_snippet(entry) -> str:
    """Get a plain-text snippet from the entry summary."""
    raw = getattr(entry, "summary", "") or getattr(entry, "description", "") or ""
    # Strip HTML tags
    clean = re.sub(r"<[^>]+>", "", raw)
    clean = re.sub(r"\s+", " ", clean).strip()
    return clean[:500] if clean else "No description available."


def _relevance_score(title: str, summary: str) -> int:
    """Score an article based on keyword matches. Higher = more relevant."""
    text = (title + " " + summary).lower()
    score = 0
    for kw in INCLUDE_KEYWORDS:
        if kw in text:
            score += 1
    return score


def _is_spam(title: str) -> bool:
    """Check if the article title matches spam/listicle patterns."""
    lower = title.lower()
    return any(re.search(pat, lower) for pat in EXCLUDE_PATTERNS)


def fetch_articles(max_articles: int = 10) -> list[Article]:
    """Fetch, filter, and rank articles from all RSS feeds."""
    all_articles: list[Article] = []

    for feed_info in FEEDS:
        name = feed_info["name"]
        url = feed_info["url"]
        logger.info(f"Fetching feed: {name}")

        try:
            parsed = feedparser.parse(url)
            if parsed.bozo and not parsed.entries:
                logger.warning(f"Feed {name} failed: {parsed.bozo_exception}")
                continue

            for entry in parsed.entries:
                title = getattr(entry, "title", "No title")
                link = getattr(entry, "link", "")
                summary = _get_snippet(entry)
                published = _parse_date(entry)

                if _is_spam(title):
                    logger.debug(f"Skipping spam: {title}")
                    continue

                score = _relevance_score(title, summary)
                if score == 0:
                    continue

                all_articles.append(Article(
                    title=title,
                    link=link,
                    summary=summary,
                    source=name,
                    published=published,
                    score=score,
                ))

            logger.info(f"  Got {len(parsed.entries)} entries from {name}")

        except Exception as e:
            logger.error(f"Error fetching {name}: {e}")
            continue

    # Sort by relevance score (descending)
    all_articles.sort(key=lambda a: a["score"], reverse=True)

    # Round-robin selection to ensure source diversity
    selected: list[Article] = []
    by_source: dict[str, list[Article]] = {}
    for a in all_articles:
        by_source.setdefault(a["source"], []).append(a)

    source_names = list(by_source.keys())
    idx = 0
    while len(selected) < max_articles and any(by_source.values()):
        source = source_names[idx % len(source_names)]
        if by_source[source]:
            selected.append(by_source[source].pop(0))
        idx += 1
        # Remove exhausted sources
        source_names = [s for s in source_names if by_source[s]]
        if not source_names:
            break

    logger.info(f"Selected {len(selected)} articles from {len(all_articles)} candidates")
    sources_used = set(a["source"] for a in selected)
    logger.info(f"Sources represented: {', '.join(sources_used)}")
    return selected
