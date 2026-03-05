"""Summarize articles using Groq API (llama-3.3-70b-versatile).

Supports multiple API keys for fallback. Set env vars:
  GROQ_API_KEY   - primary key
  GROQ_API_KEY_2 - first fallback
  GROQ_API_KEY_3 - second fallback
  ... up to GROQ_API_KEY_9
"""

import logging
import os
import time

logger = logging.getLogger(__name__)

GROQ_MODEL = "llama-3.3-70b-versatile"


def _get_clients() -> list:
    """Create Groq clients from all available API keys."""
    from groq import Groq

    keys = []
    # Primary key
    primary = os.environ.get("GROQ_API_KEY")
    if primary:
        keys.append(primary)
    # Fallback keys: GROQ_API_KEY_2 through GROQ_API_KEY_9
    for i in range(2, 10):
        key = os.environ.get(f"GROQ_API_KEY_{i}")
        if key:
            keys.append(key)

    if not keys:
        logger.warning("No GROQ_API_KEY found. Using RSS snippets as fallback.")
        return []

    logger.info(f"Loaded {len(keys)} Groq API key(s)")
    clients = []
    for key in keys:
        try:
            clients.append(Groq(api_key=key))
        except Exception as e:
            logger.warning(f"Failed to create Groq client: {e}")
    return clients


def summarize_article(title: str, snippet: str, clients: list) -> str:
    """Generate a 2-3 sentence summary in Spanish, rotating through API keys on failure."""
    if not clients:
        return snippet

    prompt = (
        f"Resume la siguiente noticia de tecnologia/IA en 2-3 frases concisas EN ESPANOL. "
        f"Solo devuelve el resumen, sin introducciones ni comentarios.\n\n"
        f"Titulo: {title}\n"
        f"Contenido: {snippet}"
    )

    for i, client in enumerate(clients):
        try:
            response = client.chat.completions.create(
                model=GROQ_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=300,
            )
            summary = response.choices[0].message.content.strip()
            logger.info(f"  Summarized (key {i+1}): {title[:50]}...")
            return summary
        except Exception as e:
            logger.warning(f"Groq key {i+1} failed for '{title[:40]}': {e}")
            continue

    logger.warning(f"All Groq keys exhausted for '{title[:40]}'. Using snippet fallback.")
    return snippet


def summarize_all(articles: list[dict]) -> list[dict]:
    """Add AI-generated summaries to all articles."""
    clients = _get_clients()

    for i, article in enumerate(articles):
        article["ai_summary"] = summarize_article(
            article["title"], article["summary"], clients
        )
        if clients and i < len(articles) - 1:
            time.sleep(1)

    return articles
