# Steam Review Dashboard

Analyzes Steam reviews for a game: totals, positive/negative ratio by playtime, mentions of game content topics, most-used words, plus a written summary of what players praise and complain about. Filter by language (All / English / Korean / Chinese) and date range.

## Run

Needs Python 3 (nothing else to install). Double-click `run.bat`, or run `python server.py`, then open http://localhost:8765/ (it opens automatically).

Steam does not allow its review API to be called from a web page, so `server.py` downloads the reviews and keeps them in `data/` (not committed). Use **Update reviews** in the page to fetch new ones; it only downloads what is missing.

## Using it

- **Steam App ID**: Crimson Desert Enhanced is `5001840`. `3321460` (the original) is useful for testing before launch.
- **Manage topics**: add or edit topics and their keywords (English, Korean, Chinese). Changes are saved in your browser; use Export/Import to share a set with teammates. Defaults live in `topics.default.json`.
- **Download Excel**: exports the reviews matching the current language and date filters.
- **Written summary**: `analysis/<appid>.json`, written by Claude from a sample of reviews. Ask Claude to refresh it after new reviews come in.

## Files

- `index.html`: the dashboard (all UI text is in one `I18N` block at the top of the script, ready for a Korean version)
- `server.py`: local helper that serves the page and downloads reviews
- `topics.default.json`: default topics and keywords
- `analysis/`: written summaries
