#!/usr/bin/env python3
"""Build demo.html: a single self-contained copy of the dashboard with a snapshot
of the cached reviews baked in, so it can be opened or hosted anywhere without
server.py. Usage: python build_demo.py [appid]   (default 3321460)
"""
import json
import os
import sys

import server

BASE = os.path.dirname(os.path.abspath(__file__))


def read(path):
    with open(os.path.join(BASE, path), 'r', encoding='utf-8') as f:
        return f.read()


def main():
    app = sys.argv[1] if len(sys.argv) > 1 else '3321460'
    data = server.load_cache(app)
    if not data['reviews']:
        sys.exit('No cached reviews for app %s. Run the dashboard and press Update reviews first.' % app)
    try:
        analysis = json.loads(read('analysis/%s.json' % app))
    except OSError:
        analysis = None
    payload = {
        'app': app,
        'info': server.app_info(app),
        'data': data,
        'analysis': analysis,
        'topics': json.loads(read('topics.default.json'))['topics'],
    }
    blob = json.dumps(payload, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
    html = read('index.html')
    marker = '<script src="https://cdnjs.cloudflare.com/ajax/libs/xlsx'
    if marker not in html:
        sys.exit('index.html layout changed: could not find the script marker')

    def embed(extra):
        return '<script>window.SRD_EMBED = ' + blob + ';' + extra + '</script>\n' + marker

    write('demo.html', html.replace(marker, embed(''), 1))
    # Fragment for hosts that wrap the page in their own document (e.g. Claude artifacts);
    # such hosts block file downloads, so the Excel/export buttons are hidden.
    frag = html.replace(marker, embed('window.SRD_NO_DOWNLOADS = true;'), 1)
    for tag in ('<!DOCTYPE html>', '<html lang="en">', '<head>', '</head>', '<body>', '</body>', '</html>',
                '<meta charset="UTF-8">', '<meta name="viewport" content="width=device-width, initial-scale=1.0">'):
        frag = frag.replace(tag, '', 1)
    write('demo-fragment.html', frag.strip() + '\n')
    print('%d reviews' % len(data['reviews']))


def write(name, text):
    path = os.path.join(BASE, name)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(text)
    print('Wrote %s (%.1f MB)' % (path, os.path.getsize(path) / 1e6))


if __name__ == '__main__':
    main()
