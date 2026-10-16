#!/usr/bin/env python3
"""Local helper for the Steam Review Dashboard.

Serves the dashboard and downloads Steam reviews on its behalf (Steam's review
API does not allow requests straight from a web page). Reviews are cached in
./data/<appid>.json. Standard library only.
"""
import json
import os
import sys
import threading
import time
import urllib.parse
import urllib.request
import webbrowser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

BASE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE, 'data')
PORT = int(os.environ.get('PORT', '8765'))
STEAM_URL = 'https://store.steampowered.com/appreviews/%s'
DELAY = 0.3  # seconds between Steam requests

lock = threading.Lock()
state = {'running': False, 'app': None, 'pages': 0, 'fetched': 0, 'new': 0,
         'oldest': None, 'error': None, 'done': False}


def data_path(app):
    return os.path.join(DATA_DIR, '%s.json' % app)


def empty_cache(app):
    return {'app': app, 'summary': None, 'covered': None, 'updated': 0, 'reviews': []}


def load_cache(app):
    try:
        with open(data_path(app), 'r', encoding='utf-8') as f:
            return json.load(f)
    except (OSError, ValueError):
        return empty_cache(app)


def save_cache(app, cache):
    os.makedirs(DATA_DIR, exist_ok=True)
    tmp = data_path(app) + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(cache, f, ensure_ascii=False, separators=(',', ':'))
    os.replace(tmp, data_path(app))


def fetch_page(app, cursor):
    q = urllib.parse.urlencode({
        'json': 1, 'filter': 'recent', 'language': 'all', 'review_type': 'all',
        'purchase_type': 'all', 'filter_offtopic_activity': 0,
        'num_per_page': 100, 'cursor': cursor,
    })
    req = urllib.request.Request((STEAM_URL % app) + '?' + q,
                                 headers={'User-Agent': 'Mozilla/5.0 SteamReviewDashboard'})
    last = None
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode('utf-8'))
        except Exception as e:  # network hiccup / rate limit: back off and retry
            last = e
            time.sleep(2 * (attempt + 1))
    raise RuntimeError('Steam request failed: %s' % last)


def compact(r):
    a = r.get('author', {})
    return {
        'i': r['recommendationid'], 's': a.get('steamid'),
        'g': a.get('num_games_owned', 0), 'n': a.get('num_reviews', 0),
        'p': a.get('playtime_at_review', a.get('playtime_forever', 0)),
        'f': a.get('playtime_forever', 0), 'l': r.get('language'),
        't': r.get('review', ''), 'c': r.get('timestamp_created'),
        'u': 1 if r.get('voted_up') else 0,
        'b': 1 if r.get('steam_purchase') else 0,
        'r': 1 if r.get('received_for_free') else 0,
    }


def sync(app, days):
    """Walk Steam's newest-first review list until the requested window is cached."""
    try:
        cache = load_cache(app)
        known = {r['i']: r for r in cache['reviews']}
        prev_cov = cache.get('covered')  # all reviews newer than this are cached; 0 = everything
        target = int(time.time()) - days * 86400 if days else 0
        cursor, seen_cursors, covered = '*', set(), prev_cov
        pages = 0
        while True:
            page = fetch_page(app, cursor)
            if page.get('query_summary', {}).get('total_reviews') is not None:
                cache['summary'] = page['query_summary']
            revs = page.get('reviews') or []
            pages += 1
            with lock:
                state['pages'] = pages
            if not revs:
                covered = 0  # reached the very end of Steam's list
                break
            new = 0
            for raw in revs:
                rid = raw['recommendationid']
                if rid not in known:
                    known[rid] = compact(raw)
                    new += 1
            oldest = min(r['timestamp_created'] for r in revs)
            with lock:
                state['fetched'] += len(revs)
                state['new'] += new
                state['oldest'] = oldest
            if oldest < target:
                covered = oldest if covered is None else min(covered, oldest)
                break
            if new == 0 and prev_cov is not None and prev_cov <= target:
                break  # everything older is already cached
            if pages % 20 == 0:
                cache['reviews'] = list(known.values())
                save_cache(app, cache)
            cursor = page.get('cursor')
            if not cursor or cursor in seen_cursors:
                covered = 0
                break
            seen_cursors.add(cursor)
            time.sleep(DELAY)
        cache['reviews'] = sorted(known.values(), key=lambda r: -r['c'])
        cache['covered'] = covered
        cache['updated'] = int(time.time())
        save_cache(app, cache)
    except Exception as e:
        with lock:
            state['error'] = str(e)
    finally:
        with lock:
            state['running'] = False
            state['done'] = True


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=BASE, **kw)

    def log_message(self, *a):
        pass

    def end_headers(self):
        self.send_header('Cache-Control', 'no-store')
        super().end_headers()

    def send_json(self, obj, code=200):
        body = json.dumps(obj).encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        url = urllib.parse.urlparse(self.path)
        q = urllib.parse.parse_qs(url.query)
        app = (q.get('app') or [''])[0]
        if url.path in ('/api/data', '/api/sync') and not app.isdigit():
            return self.send_json({'error': 'bad app id'}, 400)
        if url.path == '/api/data':
            try:
                with open(data_path(app), 'rb') as f:
                    body = f.read()
            except OSError:
                body = json.dumps(empty_cache(app)).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif url.path == '/api/sync':
            days = int((q.get('days') or ['0'])[0] or 0)
            with lock:
                if state['running']:
                    return self.send_json({'started': False, 'reason': 'already running'})
                state.update(running=True, app=app, pages=0, fetched=0, new=0,
                             oldest=None, error=None, done=False)
            threading.Thread(target=sync, args=(app, days), daemon=True).start()
            self.send_json({'started': True})
        elif url.path == '/api/status':
            with lock:
                self.send_json(dict(state))
        elif url.path.startswith('/data') or url.path.endswith('.py'):
            self.send_error(404)
        else:
            super().do_GET()


def main():
    srv = ThreadingHTTPServer(('127.0.0.1', PORT), Handler)
    url = 'http://localhost:%d/' % PORT
    print('Steam Review Dashboard running at ' + url)
    print('Press Ctrl+C to stop.')
    if '--no-browser' not in sys.argv:
        threading.Timer(0.8, lambda: webbrowser.open(url)).start()
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
