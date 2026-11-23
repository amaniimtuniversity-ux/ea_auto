#!/usr/bin/env python3
"""
kathareel — ONE-CELL Kaggle bootstrapper generator.

Ek hi cell me sab kuch: studio files + setup + server + URL.
Koi git clone nahi, koi manual file nahi.

    python3 scripts/make_onecell.py     ->  kathareel_onecell.py

Us file ka content Kaggle cell me paste karo aur chala do.
"""
import base64
import gzip
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILES = ['web/index.html', 'web/server.py', 'web/kaggle_launch.py', 'web/doctor.py',
         'scripts/content_io.py']
OUT = os.path.join(ROOT, 'kathareel_onecell.py')

HEADER = '''# =====================================================================
#  kathareel — Hindi explainer video studio  (by raghv)
#  EK CELL: setup + studio + URL. Kaggle me paste karke chalao.
#
#  Kaggle settings: Internet ON, Accelerator None
# =====================================================================
import base64, gzip, os, shutil, subprocess, sys, threading, time

REPO = 'https://github.com/amaniimtuniversity-ux/ea_auto.git'
ROOT = '/kaggle/working/kathareel'
PORT = 8000

# --- 1. repo (sirf src/ ke liye; fail ho to bhi studio chalega) -------
if not os.path.isdir(os.path.join(ROOT, 'src')):
    os.makedirs(ROOT, exist_ok=True)
    subprocess.run(['git', 'clone', '--depth', '1', REPO, ROOT],
                   capture_output=True)
os.makedirs(os.path.join(ROOT, 'web'), exist_ok=True)
os.makedirs(os.path.join(ROOT, 'scripts'), exist_ok=True)
os.chdir(ROOT)

# --- 2. studio files (embedded, gzip+base64) --------------------------
STUDIO = __STUDIO_JSON__

for _p, _b in STUDIO.items():
    _full = os.path.join(ROOT, _p)
    os.makedirs(os.path.dirname(_full) or ROOT, exist_ok=True)
    open(_full, 'wb').write(gzip.decompress(base64.b64decode(_b)))
print('studio files:', ', '.join(sorted(STUDIO)))

# --- 3. system + python packages --------------------------------------
if not shutil.which('ffmpeg'):
    subprocess.run('apt-get -qq update && apt-get -qq install -y ffmpeg libnss3 '
                   'libnspr4 libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 '
                   'libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3 libxrandr2 '
                   'libgbm1 libasound2', shell=True)
subprocess.run([sys.executable, '-m', 'pip', 'install', '-q', '--upgrade',
                'fastapi', 'uvicorn', 'edge-tts', 'numpy'])
print('ffmpeg:', shutil.which('ffmpeg') is not None,
      '| node:', shutil.which('node') is not None)

# --- 4. server + tunnel (background, cell return ho jata hai) ---------
def _run():
    src = os.path.join(ROOT, 'web', 'server.py')
    g = {'__name__': '__main__', '__file__': src}
    exec(compile(open(src, encoding='utf-8').read(), src, 'exec'), g)

sys.argv = ['server.py', '--port', str(PORT), '--public']
threading.Thread(target=_run, daemon=True).start()
time.sleep(30)

print()
print('=' * 74)
print('  KHOLO (kaggle proxy — hamesha chalta hai):')
print('  https://www.kaggle.com/code/amanraghav1111111/kathareel-kaggle/proxy/%d/' % PORT)
print()
print('  ya upar jo PUBLIC https://.... URL print hua wo bhi kaam karega')
print('=' * 74)
'''


def build():
    blob = {}
    for f in FILES:
        raw = open(os.path.join(ROOT, f), 'rb').read()
        blob[f] = base64.b64encode(gzip.compress(raw, 9)).decode()

    body = HEADER.replace('__STUDIO_JSON__', json.dumps(blob, indent=0))
    with open(OUT, 'w', encoding='utf-8') as fh:
        fh.write(body)
    print('wrote %s — %.1f KB, %d files embedded' % (
        OUT, os.path.getsize(OUT) / 1024, len(FILES)))


if __name__ == '__main__':
    build()
