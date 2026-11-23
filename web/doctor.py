#!/usr/bin/env python3
"""
kathareel doctor — "URL khulta nahi" ka kaaran turant batao.

Chalao:
    python3 web/doctor.py

Ye check karta hai:
  1. code purana to nahi (version)
  2. server chal raha hai ya nahi, aur kaun sa port
  3. koi duplicate/zombie server to nahi
  4. ffmpeg + node + npm
  5. tunnel process zinda hai ya nahi
  6. public URL asal me jawab de raha hai ya nahi
"""
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OK, BAD, WARN = '\033[92m\u2713\033[0m', '\033[91m\u2717\033[0m', '\033[93m!\033[0m'


def say(flag, msg, hint=None):
    print(f'  {flag} {msg}')
    if hint:
        print(f'      \033[90m{hint}\033[0m')


def get(url, timeout=10):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'kathareel-doctor'})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read(4000).decode('utf-8', 'replace')
    except Exception as e:  # noqa: BLE001
        return None, str(e)


def port_open(port, host='127.0.0.1'):
    with socket.socket() as s:
        s.settimeout(0.5)
        return s.connect_ex((host, port)) == 0


def procs(pattern):
    out = subprocess.run(['ps', '-eo', 'pid,args'], capture_output=True, text=True).stdout
    return [l for l in out.splitlines() if pattern in l and 'doctor.py' not in l
            and 'grep' not in l]


def main():
    print('\n  \033[1mkathareel doctor\033[0m\n')

    # 1. code version
    srv = os.path.join(ROOT, 'web', 'server.py')
    code = open(srv, encoding='utf-8').read() if os.path.exists(srv) else ''
    m = re.search(r"VERSION = '([^']+)'", code)
    has_tunnel = 'class Tunnel' in code
    print('  code:')
    say(OK if m else WARN, f"server.py version = {m.group(1) if m else 'purana (koi version nahi)'}",
        None if has_tunnel else 'Purana server.py — self-healing tunnel nahi hai. Repo pull karo.')
    if not m:
        say(BAD, 'Ye purana code hai — naya code chahiye',
            'Colab/Kaggle me: !git clone ya notebook ka naya version chalao')

    # 2. toolchain
    print('\n  tools:')
    for tool in ('ffmpeg', 'node', 'npm', 'ssh'):
        p = shutil.which(tool)
        say(OK if p else BAD, f'{tool}: {p or "nahi mila"}',
            None if p else 'pip/apt se install karo — video build fail hogi')

    # 3. servers
    print('\n  processes:')
    srv_procs = procs('web/server.py')
    if not srv_procs:
        say(BAD, 'koi server nahi chal raha', 'python3 web/server.py --port 8000 --public')
    else:
        say(OK if len(srv_procs) == 1 else WARN,
            f'{len(srv_procs)} server process',
            None if len(srv_procs) == 1 else
            'ek se zyada hain — purane band karo: pkill -f "web/server.py"')
        for l in srv_procs:
            print(f'      \033[90m{l.strip()[:100]}\033[0m')

    # 4. local server
    print('\n  local server:')
    port = 8000
    if not port_open(port):
        say(BAD, f'port {port} band hai', 'server start karo')
    else:
        st, body = get(f'http://127.0.0.1:{port}/api/health')
        if st == 200:
            try:
                h = json.loads(body)
                say(OK, f'health 200 · version {h.get("version", "?")} · '
                        f'ffmpeg {h.get("ffmpeg")} · node {h.get("node")}')
                url = h.get('tunnel_url')
                if url:
                    say(OK, f'server ka tunnel URL: {url}')
                else:
                    say(WARN, 'server ne abhi tunnel URL nahi banaya')
            except json.JSONDecodeError:
                say(BAD, 'health JSON nahi hai — purana code ya galat server')

    # 5. tunnels
    print('\n  tunnels:')
    cf = procs('cloudflared')
    lhr = procs('nokey@localhost.run')
    say(OK if cf or lhr else BAD,
        f'cloudflared: {len(cf)} · localhost.run: {len(lhr)}',
        None if cf or lhr else 'tunnel nahi chal raha — --public ke saath start karo')
    if len(cf) > 1:
        say(WARN, f'{len(cf)} cloudflared processes — Cloudflare rate-limit lagata hai',
            'pkill -f cloudflared, phir ek hi restart karo')

    # 6. public URL check
    print('\n  public URL:')
    urls = []
    for f in ('/tmp/kathareel_url.txt', '/tmp/cloudflared.log', '/tmp/lhr.log'):
        try:
            txt = open(f, encoding='utf-8', errors='ignore').read()
            urls += re.findall(r'https://[a-z0-9-]+\.(?:trycloudflare\.com|lhr\.life)', txt)
        except OSError:
            pass
    urls = list(dict.fromkeys(urls))[-3:]
    if not urls:
        say(WARN, 'koi public URL nahi mila logs me')
    for u in urls:
        st, body = get(u + '/api/health', timeout=15)
        if st == 200:
            say(OK, f'{u}  -> 200')
        else:
            short = body.splitlines()[0][:60] if body else 'no response'
            if '1033' in body:
                hint = 'Cloudflare tunnel dead (1033). Naya URL lo — /api/health ya 🔗 button'
            elif '530' in body:
                hint = 'Tunnel bana par server se connect nahi (530). Server chalu hai? port sahi?'
            else:
                hint = 'Ye URL purana hai ya tunnel mar gaya — naya URL lo'
            say(BAD, f'{u}  -> {st or "dead"}', hint)

    print('\n  \033[90mTip: Kaggle par apna proxy URL hamesha chalta hai —\033[0m')
    print('  \033[90m     https://www.kaggle.com/code/<user>/<notebook>/proxy/8000/\033[0m\n')


if __name__ == '__main__':
    main()
