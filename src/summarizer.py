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


def summarize_article(title: str, snippet: str, clients: list) -> dict:
    """Generate translated title + summary in Spanish, rotating through API keys on failure."""
    if not clients:
        return {"title_es": title, "summary_es": snippet}

    prompt = (
        f"Traduce el titulo y resume la siguiente noticia de tecnologia/IA EN ESPANOL.\n"
        f"Responde EXACTAMENTE con este formato (sin nada mas):\n"
        f"TITULO: <titulo traducido al espanol>\n"
        f"RESUMEN: <resumen de 2-3 frases en espanol>\n\n"
        f"Titulo original: {title}\n"
        f"Contenido: {snippet}"
    )

    for i, client in enumerate(clients):
        try:
            response = client.chat.completions.create(
                model=GROQ_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=400,
            )
            text = response.choices[0].message.content.strip()
            result = _parse_response(text, title, snippet)
            logger.info(f"  Summarized (key {i+1}): {title[:50]}...")
            return result
        except Exception as e:
            logger.warning(f"Groq key {i+1} failed for '{title[:40]}': {e}")
            continue

    logger.warning(f"All Groq keys exhausted for '{title[:40]}'. Using fallback.")
    return {"title_es": title, "summary_es": snippet}


def _parse_response(text: str, original_title: str, fallback_summary: str) -> dict:
    """Parse the TITULO: / RESUMEN: format from Groq response."""
    title_es = original_title
    summary_es = fallback_summary

    lines = text.split("\n")
    titulo_lines = []
    resumen_lines = []
    current = None

    for line in lines:
        upper = line.strip().upper()
        if upper.startswith("TITULO:") or upper.startswith("TÍTULO:"):
            current = "titulo"
            # Get content after the label on the same line
            after = line.split(":", 1)[1].strip() if ":" in line else ""
            if after:
                titulo_lines.append(after)
        elif upper.startswith("RESUMEN:"):
            current = "resumen"
            after = line.split(":", 1)[1].strip() if ":" in line else ""
            if after:
                resumen_lines.append(after)
        elif current == "titulo":
            titulo_lines.append(line.strip())
        elif current == "resumen":
            resumen_lines.append(line.strip())

    if titulo_lines:
        title_es = " ".join(titulo_lines).strip()
    if resumen_lines:
        summary_es = " ".join(resumen_lines).strip()

    return {"title_es": title_es, "summary_es": summary_es}


def summarize_all(articles: list[dict]) -> list[dict]:
    """Add AI-generated summaries and translated titles to all articles."""
    clients = _get_clients()

    for i, article in enumerate(articles):
        result = summarize_article(article["title"], article["summary"], clients)
        article["title_es"] = result["title_es"]
        article["ai_summary"] = result["summary_es"]
        if clients and i < len(articles) - 1:
            time.sleep(1)

    return articles
