# Pulso IA

[![Pulso IA](https://github.com/charliebusbus/ai-news-digest/actions/workflows/daily-digest.yml/badge.svg)](https://github.com/charliebusbus/ai-news-digest/actions/workflows/daily-digest.yml)

El pulso diario de la inteligencia artificial. Un agente autonomo que recopila, filtra y resume las noticias de IA mas relevantes cada dia usando Groq (LLaMA 3.3 70B), y publica una web estatica — sin intervencion humana.

**[Ver el digest en vivo](https://charliebusbus.github.io/ai-news-digest/)**

---

## Stack

| Component | Tool | Cost |
|-----------|------|------|
| Scheduler | GitHub Actions (cron) | $0 |
| AI Summaries | Groq API (llama-3.3-70b-versatile) | $0 |
| Hosting | GitHub Pages | $0 |
| Language | Python 3.12 | $0 |
| **Total** | | **$0** |

## How it works

1. **Fetch** — Pulls RSS feeds from TechCrunch, The Verge, Ars Technica, MIT Technology Review
2. **Filter** — Scores articles by AI-related keyword relevance, discards spam/listicles
3. **Summarize** — Sends each article to Groq (LLaMA 3.3 70B) for a 2-3 sentence summary in Spanish
4. **Publish** — Generates a static HTML page and pushes to GitHub Pages

Runs automatically every day at 08:00 UTC via GitHub Actions.

## Fork & Customize

1. Fork this repo
2. Add your `GROQ_API_KEY` as a repository secret (Settings > Secrets > Actions)
3. Enable GitHub Pages (Settings > Pages > Source: main, folder: /docs)
4. Run the workflow manually to test (Actions > Pulso IA > Run workflow)

### Customize feeds

Edit `src/feeds.py` — add or remove entries in the `FEEDS` list.

### Customize keywords

Edit the `INCLUDE_KEYWORDS` list in `src/feeds.py` to match your interests.

### Change language

Edit the prompt in `src/summarizer.py` — change "EN ESPANOL" to your preferred language.

## Project Structure

```
ai-news-digest/
├── .github/workflows/daily-digest.yml  # Cron scheduler
├── docs/                                # GitHub Pages
│   ├── index.html                       # Latest digest
│   ├── style.css                        # Shared styles
│   └── archive/                         # Daily archives
├── src/
│   ├── main.py                          # Entry point
│   ├── feeds.py                         # RSS fetch + filter
│   ├── summarizer.py                    # Groq AI summaries
│   └── generator.py                     # HTML generation
├── requirements.txt
└── README.md
```

## License

MIT
