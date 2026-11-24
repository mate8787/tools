#!/usr/bin/env python3
"""Build a zip a teammate can unzip and double-click (Windows): dist/SteamReviewDashboard.zip

The zip contains the dashboard, a trimmed copy of this PC's Python (so nothing needs installing),
and the reviews cached so far (more can be downloaded from inside the tool).

  python package.py                      games 5001840 and 3321460
  python package.py --apps 5001840       choose which cached games to include ("--apps none" = no reviews)
"""
import glob
import os
import shutil
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
DIST = os.path.join(BASE, 'dist')
NAME = 'SteamReviewDashboard'
PKG = os.path.join(DIST, NAME)

START_BAT = (
    '@echo off\r\n'
    'cd /d "%~dp0"\r\n'
    'title Steam Review Dashboard (close this window to stop)\r\n'
    'if exist "python\\python.exe" (\r\n'
    '  "python\\python.exe" server.py\r\n'
    ') else (\r\n'
    '  python server.py || py server.py\r\n'
    ')\r\n'
    'pause\r\n'
)

README = """STEAM REVIEW DASHBOARD
======================

1. Right-click the zip > Extract All (do not run it from inside the zip).
2. Open the extracted folder and double-click "Start Steam Review Dashboard.bat".
   A black window opens and your browser shows the dashboard. Keep the black window open while you use it;
   close it to stop the tool. (If Windows says "protected your PC", click More info > Run anyway.)
3. In the page: type a Steam App ID and press Load, choose a "Download window" and press "Update reviews".
   Reviews are saved in the "data" folder next to this file, on your own PC, and only new ones are downloaded next time.

Examples of App IDs: 5001840 = Crimson Desert Enhanced: Charting the Unknown (DLC), 3321460 = Crimson Desert Enhanced.
Language: top right of the page, English / 한국어.
Needs an internet connection to download reviews from Steam. Nothing needs to be installed.

스팀 리뷰 대시보드 (한국어 안내)
1. 압축 파일을 마우스 오른쪽 버튼 > "모두 압축 풀기"로 푼 뒤 (압축 파일 안에서 바로 실행하지 마세요),
2. 폴더 안의 "Start Steam Review Dashboard.bat"을 더블클릭하면 브라우저에 대시보드가 열립니다. 사용하는 동안 검은 창은 닫지 마세요.
3. 스팀 앱 ID를 입력하고 "불러오기" > 다운로드 범위 선택 > "리뷰 업데이트". 리뷰는 이 폴더의 data 폴더(내 PC)에 저장됩니다.
화면 오른쪽 위에서 English / 한국어로 언어를 바꿀 수 있습니다.
"""

PY_SKIP_LIB = {'site-packages', 'test', 'idlelib', 'tkinter', 'turtledemo', 'lib2to3', 'ensurepip', '__pycache__', 'venv'}


def copy_python(dst):
    src = sys.base_prefix
    os.makedirs(dst)
    for f in ('python.exe', 'pythonw.exe', 'python3.dll', 'LICENSE.txt') + tuple(
            os.path.basename(p) for p in glob.glob(os.path.join(src, 'python3*.dll')) + glob.glob(os.path.join(src, 'vcruntime*.dll'))):
        p = os.path.join(src, f)
        if os.path.exists(p):
            shutil.copy2(p, dst)

    def skip_lib(d, names):
        return [n for n in names if n in PY_SKIP_LIB or n.endswith('.pyc')]

    def skip_dlls(d, names):
        return [n for n in names if n.startswith('_test') or 'tcl' in n.lower() or n.lower().startswith('tk') or n == '_tkinter.pyd']
    shutil.copytree(os.path.join(src, 'Lib'), os.path.join(dst, 'Lib'), ignore=skip_lib)
    shutil.copytree(os.path.join(src, 'DLLs'), os.path.join(dst, 'DLLs'), ignore=skip_dlls)


def main():
    apps = ['5001840', '3321460']
    if '--apps' in sys.argv:
        v = sys.argv[sys.argv.index('--apps') + 1]
        apps = [] if v == 'none' else [a for a in v.split(',') if a]
    if os.path.exists(PKG):
        shutil.rmtree(PKG)
    os.makedirs(PKG)
    for f in ('index.html', 'server.py', 'topics.default.json'):
        shutil.copy2(os.path.join(BASE, f), PKG)
    shutil.copytree(os.path.join(BASE, 'analysis'), os.path.join(PKG, 'analysis'))
    os.makedirs(os.path.join(PKG, 'data'))
    for a in apps:
        p = os.path.join(BASE, 'data', '%s.json' % a)
        if os.path.exists(p):
            shutil.copy2(p, os.path.join(PKG, 'data'))
        else:
            print('no cached reviews for %s, skipped' % a)
    copy_python(os.path.join(PKG, 'python'))
    with open(os.path.join(PKG, 'Start Steam Review Dashboard.bat'), 'w', newline='') as f:
        f.write(START_BAT)
    with open(os.path.join(PKG, 'READ ME FIRST.txt'), 'w', encoding='utf-8-sig', newline='\r\n') as f:
        f.write(README)
    zpath = shutil.make_archive(PKG, 'zip', DIST, NAME)
    print('Built %s (%.1f MB)' % (zpath, os.path.getsize(zpath) / 1e6))


if __name__ == '__main__':
    main()
