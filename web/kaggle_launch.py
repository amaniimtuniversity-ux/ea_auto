#!/usr/bin/env python3
"""
kathareel studio — Kaggle / Colab launcher (by raghv)

Kaggle notebook me bas ek cell:

    !python web/kaggle_launch.py

Ye khud:
  1. system packages (ffmpeg + Chromium libs) install karta hai
  2. npm install karta hai (Remotion + React)
  3. python packages (fastapi, uvicorn, edge-tts) install karta hai
  4. server ko background me start karta hai + public URL print karta hai

Us URL ko kholo -> poora studio browser me: script edit karo, video banao, video dekho.
Cell return ho jata hai, server chalta rehta hai (notebook band karne tak).
"""
import os
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PORT = int(os.environ.get('KATHAREEL_PORT', '8000'))


def sh(cmd, label, check=True):
    print('\n\033[1;33m\u25b8 %s\033[0m' % label, flush=True)
    p = subprocess.run(cmd, shell=isinstance(cmd, str), cwd=ROOT,
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    out = (p.stdout or '').strip()
    if out:
        print(out[-2500:], flush=True)
    if check and p.returncode != 0:
        print('\n\u26a0 %s fail hua (exit %s) — aage badh raha hoon' % (label, p.returncode), flush=True)
    return p.returncode


def have(binary):
    return shutil.which(binary) is not None


def install_everything():
    print('=' * 72)
    print('  kathareel studio — setup')
    print('=' * 72, flush=True)

    if have('apt-get'):
        sh('apt-get -qq update', 'apt update', check=False)
        sh('apt-get -qq install -y ffmpeg libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 '
           'libcups2 libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3 libxrandr2 '
           'libgbm1 libasound2 2>/dev/null', 'system packages (ffmpeg + chromium libs)', check=False)
    elif not have('ffmpeg'):
        print('\u26a0 ffmpeg nahi mila — voice generation fail hogi. Pehle ffmpeg install karo.', flush=True)

    if not os.path.isdir(os.path.join(ROOT, 'node_modules')):
        sh('npm install --silent', 'npm install (Remotion + React)')

    sh([sys.executable, '-m', 'pip', 'install', '-q', '--upgrade',
        'fastapi', 'uvicorn', 'edge-tts', 'numpy'], 'python packages')

    print(flush=True)
    print('  node     : %s' % ('\u2713' if have('node') else '\u2717'), flush=True)
    print('  ffmpeg   : %s' % ('\u2713' if have('ffmpeg') else '\u2717'), flush=True)
    try:
        import edge_tts  # noqa: F401
        print('  edge-tts : \u2713 (natural Hindi voice)', flush=True)
    except ImportError:
        print('  edge-tts : \u2717 (offline piper voice use hoga)', flush=True)


def start_studio():
    """Server ko background thread me chalao taaki notebook cell block na ho."""
    import threading

    os.makedirs(os.path.join(ROOT, 'out'), exist_ok=True)

    def run():
        sys.argv = ['server.py', '--port', str(PORT), '--public']
        srv = os.path.join(ROOT, 'web', 'server.py')
        code = open(srv, encoding='utf-8').read()
        g = {'__name__': '__main__', '__file__': srv}
        old = os.getcwd()
        os.chdir(ROOT)
        try:
            exec(compile(code, srv, 'exec'), g)
        finally:
            os.chdir(old)

    t = threading.Thread(target=run, daemon=True)
    t.start()
    return t


def main():
    install_everything()

    print('\n' + '=' * 72)
    print('  studio start ho raha hai — 15\u201330 sec me URL aayega')
    print('=' * 72 + '\n', flush=True)

    start_studio()

    import time
    time.sleep(28)

    print('\n' + '=' * 72)
    print('  DO URL milte hain — dono kaam karte hain:')
    print()
    print('  1) STABLE (recommended) — Kaggle ka apna proxy, kabhi nahi marta:')
    print('     https://www.kaggle.com/code/<YOUR-USER>/<YOUR-NOTEBOOK>/proxy/%d/' % PORT)
    print()
    print('  2) PUBLIC — https://....trycloudflare.com  (upar printed)')
    print('     Note: ye free tunnel 2-3 ghante me ya server restart par mar sakta hai.')
    print('     Mara to studio khud naya banata hai — /api/health me current URL milta hai.')
    print('     Isliye roz ke kaam ke liye Kaggle proxy URL hi bookmark karo.')
    print('\n  (server background me chalu hai — notebook band karne tak zinda rahega)')
    print('=' * 72, flush=True)


if __name__ == '__main__':
    main()
