#!/usr/bin/env python3
"""
kathareel studio — Kaggle / Colab launcher (by raghv)

Kaggle notebook me bas itna chalao:

    !python web/kaggle_launch.py

Ye khud:
  1. system packages (ffmpeg + Chromium libs) install karta hai
  2. npm install karta hai
  3. python packages (fastapi, uvicorn, edge-tts, gradio) install karta hai
  4. public URL banata hai aur screen par print karta hai

Us URL ko kholo -> poora studio (script + voice + video) browser me.
"""
import os
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PORT = int(os.environ.get('KATHAREEL_PORT', '8000'))


def sh(cmd, label, check=True):
    print(f'\n\033[1;33m▸ {label}\033[0m')
    p = subprocess.run(cmd, shell=isinstance(cmd, str), cwd=ROOT,
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    out = (p.stdout or '').strip()
    if out:
        print(out[-2500:])
    if check and p.returncode != 0:
        print(f'\n⚠ {label} fail hua (exit {p.returncode}) — aage badh raha hoon')
    return p.returncode


def have(binary):
    return shutil.which(binary) is not None


def main():
    print('=' * 72)
    print('  kathareel studio — setup')
    print('=' * 72)

    # 1. system packages
    if have('apt-get'):
        sh('apt-get -qq update', 'apt update', check=False)
        sh('apt-get -qq install -y ffmpeg libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 '
           'libcups2 libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3 libxrandr2 '
           'libgbm1 libasound2 2>/dev/null', 'system packages (ffmpeg + chromium libs)', check=False)

    # 2. node deps
    if not os.path.isdir(os.path.join(ROOT, 'node_modules')):
        sh('npm install --silent', 'npm install (Remotion + React)')

    # 3. python deps
    sh([sys.executable, '-m', 'pip', 'install', '-q', '--upgrade',
        'fastapi', 'uvicorn', 'edge-tts', 'numpy', 'gradio'], 'python packages')

    # 4. sanity
    print()
    print(f"  node   : {'✓' if have('node') else '✗'}")
    print(f"  ffmpeg : {'✓' if have('ffmpeg') else '✗'}")
    try:
        import edge_tts  # noqa: F401
        print('  edge-tts: ✓ (natural Hindi voice)')
    except ImportError:
        print('  edge-tts: ✗ (offline piper voice use hoga)')

    print('\n' + '=' * 72)
    print('  studio start ho raha hai — neeche URL aayega (10–20 sec)')
    print('=' * 72 + '\n')

    # 5. serve with a public tunnel
    os.execv(sys.executable, [sys.executable, os.path.join(ROOT, 'web', 'server.py'),
                              '--port', str(PORT), '--public'])


if __name__ == '__main__':
    main()
