#!/usr/bin/env python3
"""Publish the dashboard as a read-only web folder.

The folder holds index.html plus data/<appid>.js files with the cached reviews and
written summaries, so it works without server.py: open index.html from the folder
(for example a OneDrive/SharePoint-synced one) or put the folder on any web host.

  python publish.py                      publish every cached game to the folders in publish.json (default: ./web)
  python publish.py --out "D:\\Shared\\SRD" --out web
  python publish.py --apps 5001840,3321460

publish.json (optional, not committed): {"out": ["web", "C:/path/to/synced/folder"], "apps": ["5001840", "3321460"]}
"""
import glob
import json
import os
import shutil
import sys
import time

import server

BASE = os.path.dirname(os.path.abspath(__file__))
INFO_CACHE = os.path.join(server.DATA_DIR, 'appinfo.json')  # last known game names, used when Steam cannot be reached


def read_json(path, default=None):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (OSError, ValueError):
        return default


def js_blob(obj):
    return json.dumps(obj, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')


def game_info(app, known):
    info = server.app_info(app)
    if info.get('error') or not info.get('name'):
        return known.get(app) or {'name': None, 'type': None}
    known[app] = info
    return info


def main():
    args = sys.argv[1:]
    outs, apps = [], None
    i = 0
    while i < len(args):
        if args[i] == '--out' and i + 1 < len(args):
            outs.append(args[i + 1]); i += 2
        elif args[i] == '--apps' and i + 1 < len(args):
            apps = [a for a in args[i + 1].split(',') if a]; i += 2
        else:
            sys.exit(__doc__)
    cfg = read_json(os.path.join(BASE, 'publish.json'), {}) or {}
    outs = outs or cfg.get('out') or ['web']
    apps = apps or [str(a) for a in cfg.get('apps') or []]
    if not apps:
        apps = sorted(os.path.splitext(os.path.basename(p))[0] for p in glob.glob(os.path.join(server.DATA_DIR, '*.json'))
                      if os.path.basename(p) != 'appinfo.json')

    known = read_json(INFO_CACHE, {}) or {}
    topics = read_json(os.path.join(BASE, 'topics.default.json'), {}).get('topics', [])
    games = []
    for app in apps:
        cache = server.load_cache(app)
        if not cache['reviews']:
            print('skip %s: no cached reviews' % app)
            continue
        games.append({
            'app': app, 'info': game_info(app, known), 'data': cache,
            'analysis': read_json(os.path.join(BASE, 'analysis', '%s.json' % app)),
            'analysisKo': read_json(os.path.join(BASE, 'analysis', '%s.ko.json' % app)),
        })
    if not games:
        sys.exit('Nothing to publish: no cached reviews. Run the dashboard and press Update reviews first.')
    os.makedirs(server.DATA_DIR, exist_ok=True)
    with open(INFO_CACHE, 'w', encoding='utf-8') as f:
        json.dump(known, f, ensure_ascii=False)

    generated = int(time.time())
    index = {
        'generated': generated, 'topics': topics,
        'apps': [{'id': g['app'], 'name': g['info'].get('name'), 'type': g['info'].get('type'),
                  'count': len(g['data']['reviews']), 'updated': g['data'].get('updated')} for g in games],
    }
    for out in outs:
        out = out if os.path.isabs(out) else os.path.join(BASE, out)
        dd = os.path.join(out, 'data')
        os.makedirs(dd, exist_ok=True)
        shutil.copyfile(os.path.join(BASE, 'index.html'), os.path.join(out, 'index.html'))
        keep = {'index.js'}
        for g in games:
            name = '%s.js' % g['app']; keep.add(name)
            with open(os.path.join(dd, name), 'w', encoding='utf-8') as f:
                f.write('(window.SRD_APPS = window.SRD_APPS || {})[%s] = %s;\n' % (json.dumps(g['app']), js_blob(
                    {'app': g['app'], 'info': g['info'], 'data': g['data'], 'analysis': g['analysis'], 'analysisKo': g['analysisKo'], 'topics': topics})))
        with open(os.path.join(dd, 'index.js'), 'w', encoding='utf-8') as f:
            f.write('window.SRD_WEB = %s;\n' % js_blob(index))
        for old in glob.glob(os.path.join(dd, '*.js')):  # drop games that are no longer published
            if os.path.basename(old) not in keep:
                os.remove(old)
        size = sum(os.path.getsize(p) for p in glob.glob(os.path.join(dd, '*.js'))) / 1e6
        print('Published %d game(s) to %s (%.1f MB of data)' % (len(games), out, size))
    for a in index['apps']:
        print('  %s  %s  %d reviews' % (a['id'], a['name'], a['count']))


if __name__ == '__main__':
    main()
