"""Summarize articles using Groq API (llama-3.3-70b-versatile)."""

import logging
import os
import time

logger = logging.getLogger(__name__)

GROQ_MODEL = "llama-3.3-70b-versatile"


def _get_client():
    """Create Groq client. Returns None if API key is not set."""
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        logger.warning("GROQ_API_KEY not set. Using RSS snippets as fallback.")
        return None
    try:
        from groq import Groq
        return Groq(api_key=api_key)
    except Exception as e:
        logger.error(f"Failed to create Groq client: {e}")
        return None


def summarize_article(title: str, snippet: str, client=None) -> str:
    """Generate a 2-3 sentence summary in Spanish using Groq."""
    if client is None:
        return snippet

    prompt = (
        f"Resume la siguiente noticia de tecnologia/IA en 2-3 frases concisas EN ESPANOL. "
        f"Solo devuelve el resumen, sin introducciones ni comentarios.\n\n"
        f"Titulo: {title}\n"
        f"Contenido: {snippet}"
    )

    try:
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=300,
        )
        summary = response.choices[0].message.content.strip()
        logger.info(f"  Summarized: {title[:50]}...")
        return summary

    except Exception as e:
        logger.warning(f"Groq API error for '{title[:40]}': {e}. Using snippet fallback.")
        return snippet


def summarize_all(articles: list[dict]) -> list[dict]:
    """Add AI-generated summaries to all articles."""
    client = _get_client()

    for i, article in enumerate(articles):
        article["ai_summary"] = summarize_article(
            article["title"], article["summary"], client
        )
        # Small delay between requests to respect rate limits
        if client and i < len(articles) - 1:
            time.sleep(1)

    return articles
