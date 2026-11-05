# Steam Review Dashboard

Analyzes Steam reviews for a game: totals, positive/negative ratio by playtime, mentions of game content topics, most-used words, plus a written summary of what players praise and complain about. Filter by language (All / English / Korean / Chinese) and date range.

## Run

Needs Python 3 (nothing else to install). Double-click `run.bat`, or run `python server.py`, then open http://localhost:8765/ (it opens automatically).

Steam does not allow its review API to be called from a web page, so `server.py` downloads the reviews and keeps them in `data/` (not committed). Use **Update reviews** in the page to fetch new ones; it only downloads what is missing.

## Share with the team (read-only web version)

`python publish.py` (or double-click `publish.bat`) turns the cached reviews and written summaries into a folder that needs no server: `index.html` plus `data/<appid>.js` files. Teammates can switch games, change language and date filters, view the summaries and download Excel, but cannot download new reviews.

- Default output is `web/`. To publish somewhere else (for example a OneDrive/SharePoint-synced folder), copy `publish.example.json` to `publish.json` and set `out` (a list, so you can publish to several places at once), or run `python publish.py --out "C:\path\to\folder"`.
- **Opening it:** SharePoint's web view downloads `.html` files instead of showing them, so a SharePoint link alone will not display the page. Teammates either sync/add the folder to OneDrive and double-click `index.html` (opens in their browser, no install), or the same folder is put on any web host (GitHub Pages, an internal web server) where it opens as a normal link.
- Republish after every **Update reviews** (and after Claude refreshes a summary): run `publish.py` again; only the `data/` files and `index.html` change.

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
