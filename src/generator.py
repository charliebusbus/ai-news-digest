"""Generate static HTML pages for the AI News Digest."""

import logging
import os
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

DOCS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "docs")
ARCHIVE_DIR = os.path.join(DOCS_DIR, "archive")
REPO_URL = "https://github.com/{owner}/ai-news-digest"


def _get_repo_url() -> str:
    """Try to determine the GitHub repo URL."""
    owner = os.environ.get("GITHUB_REPOSITORY_OWNER", "")
    repo = os.environ.get("GITHUB_REPOSITORY", "")
    if repo:
        return f"https://github.com/{repo}"
    if owner:
        return f"https://github.com/{owner}/ai-news-digest"
    return "https://github.com/ai-news-digest"


def _get_archive_entries() -> list[dict]:
    """List existing archive files."""
    entries = []
    if not os.path.exists(ARCHIVE_DIR):
        return entries
    for fname in sorted(os.listdir(ARCHIVE_DIR), reverse=True):
        if fname.endswith(".html") and fname != "index.html":
            date_str = fname.replace(".html", "")
            entries.append({"date": date_str, "file": f"archive/{fname}"})
    return entries[:30]  # Last 30 days


def _article_html(article: dict) -> str:
    """Render a single article card."""
    summary = article.get("ai_summary", article.get("summary", ""))
    return f"""
        <article class="card">
            <div class="card-source">{article['source']}</div>
            <h2 class="card-title">
                <a href="{article['link']}" target="_blank" rel="noopener">{article['title']}</a>
            </h2>
            <p class="card-summary">{summary}</p>
            <div class="card-meta">
                <span class="card-date">{article['published']}</span>
            </div>
        </article>"""


def _page_html(articles: list[dict], date_str: str, archive_entries: list[dict],
               repo_url: str, is_index: bool = True) -> str:
    """Generate a full HTML page."""
    css_path = "style.css" if is_index else "../style.css"
    index_link = "" if is_index else '<a href="../index.html" class="back-link">&larr; Volver al inicio</a>'

    articles_html = "\n".join(_article_html(a) for a in articles)

    if not articles:
        articles_html = """
        <div class="empty-state">
            <p>No se encontraron noticias relevantes de IA para hoy.</p>
            <p>El agente volvera a buscar manana.</p>
        </div>"""

    archive_html = ""
    if is_index and archive_entries:
        links = "\n".join(
            f'                <li><a href="{e["file"]}">{e["date"]}</a></li>'
            for e in archive_entries
        )
        archive_html = f"""
        <section class="archive-section">
            <h2>Archivo</h2>
            <ul class="archive-list">
{links}
            </ul>
        </section>"""

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="AI News Digest - Resumen diario de noticias de IA generado automaticamente">
    <meta property="og:title" content="AI News Digest - {date_str}">
    <meta property="og:description" content="Las noticias mas relevantes de IA, resumidas automaticamente cada dia.">
    <meta property="og:type" content="website">
    <title>AI News Digest - {date_str}</title>
    <link rel="stylesheet" href="{css_path}">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
</head>
<body>
    <div class="container">
        <header>
            {index_link}
            <div class="header-content">
                <div class="logo-section">
                    <div class="logo-icon">
                        <svg width="32" height="32" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <rect width="32" height="32" rx="8" fill="#6366F1"/>
                            <path d="M8 16C8 11.5817 11.5817 8 16 8C20.4183 8 24 11.5817 24 16" stroke="white" stroke-width="2.5" stroke-linecap="round"/>
                            <path d="M11 16C11 13.2386 13.2386 11 16 11C18.7614 11 21 13.2386 21 16" stroke="white" stroke-width="2.5" stroke-linecap="round"/>
                            <circle cx="16" cy="16" r="2" fill="white"/>
                            <path d="M16 18V24" stroke="white" stroke-width="2.5" stroke-linecap="round"/>
                        </svg>
                    </div>
                    <div>
                        <h1>AI News Digest</h1>
                        <p class="subtitle">{date_str}</p>
                    </div>
                </div>
                <span class="badge">Actualizado automaticamente con IA</span>
            </div>
        </header>

        <main>
            {articles_html}
        </main>

        {archive_html}

        <footer>
            <div class="footer-content">
                <p>Generado automaticamente por un agente de IA. 0 intervencion humana.</p>
                <p><a href="{repo_url}" target="_blank" rel="noopener">Codigo fuente</a></p>
            </div>
        </footer>
    </div>
</body>
</html>"""


def generate(articles: list[dict], date_str: str | None = None):
    """Generate index.html and archive page."""
    if date_str is None:
        date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    os.makedirs(ARCHIVE_DIR, exist_ok=True)

    repo_url = _get_repo_url()
    archive_entries = _get_archive_entries()

    # Generate archive page for today
    archive_path = os.path.join(ARCHIVE_DIR, f"{date_str}.html")
    archive_html = _page_html(articles, date_str, [], repo_url, is_index=False)
    with open(archive_path, "w", encoding="utf-8") as f:
        f.write(archive_html)
    logger.info(f"Generated archive page: {archive_path}")

    # Refresh archive entries (now includes today)
    archive_entries = _get_archive_entries()

    # Generate index.html
    index_path = os.path.join(DOCS_DIR, "index.html")
    index_html = _page_html(articles, date_str, archive_entries, repo_url, is_index=True)
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(index_html)
    logger.info(f"Generated index page: {index_path}")
