#!/usr/bin/env python3
"""
kathareel web studio (by raghv)

Kaggle / Colab / laptop par chalta hai aur ek sundar UI deta hai:
  - topic + minutes dalo -> script generate hoti hai
  - script ko UI me hi edit karo (scene add/delete, chapter rename)
  - duration estimate live dikhta hai (target se kam/zyada)
  - "Generate video" dabao -> Hindi voice + render, progress live
  - video browser me play karo, download karo

Chalane ka tarika:
    python3 web/server.py                 # http://127.0.0.1:8000
    python3 web/server.py --port 8080
    python3 web/server.py --public        # Kaggle/Colab public URL (gradio tunnel)

Kaggle par:
    !python3 web/server.py --public
"""
import argparse
import json
import os
import queue
import re
import shutil
import subprocess
import sys
import threading
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))

import content_io  # noqa: E402

from fastapi import FastAPI, HTTPException  # noqa: E402
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse  # noqa: E402
from pydantic import BaseModel  # noqa: E402
import uvicorn  # noqa: E402

VERSION = '1.2'

app = FastAPI(title='kathareel studio')

OUT = os.path.join(ROOT, 'out')
VIDEO = os.path.join(OUT, 'video.mp4')
WEB = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------------------
# job runner (ek waqt me ek build, live log)
# ---------------------------------------------------------------------------
class Job:
    def __init__(self):
        self.lines = []
        self.running = False
        self.ok = None
        self.started = 0.0
        self.step = ''
        self.q = queue.Queue()

    def log(self, msg):
        for line in str(msg).splitlines():
            self.lines.append(line)
            self.q.put(line)
        self.lines = self.lines[-400:]


JOB = Job()
LOCK = threading.Lock()


def run_cmd(cmd, cwd, env=None, label=''):
    JOB.step = label
    JOB.log(f'$ {label or " ".join(cmd)}')
    p = subprocess.Popen(cmd, cwd=cwd, env=env, stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT, text=True, bufsize=1)
    for line in p.stdout:
        JOB.log(line.rstrip())
    p.wait()
    if p.returncode != 0:
        raise RuntimeError(f'{label or cmd[0]} failed ({p.returncode})')


def build_pipeline(engine='edge', voice=None, rate='-5%'):
    """check -> voice -> render"""
    try:
        JOB.running = True
        JOB.ok = None
        JOB.lines = []
        JOB.started = time.time()

        py = sys.executable or 'python3'

        if engine == 'edge':
            JOB.step = 'python packages'
            run_cmd([py, '-m', 'pip', 'install', '-q', 'edge-tts', 'numpy'], ROOT, label='pip install edge-tts')

        JOB.step = 'checking script'
        run_cmd([py, 'scripts/check_content.py'], ROOT, label='check_content.py')

        JOB.step = 'hindi voiceover'
        # '--rate' '-5%' alag arguments ki tarah jaate hain aur argparse unhe flag
        # samajh leta hai -> '--rate=-5%' form zaroori hai.
        voice_cmd = [py, 'scripts/build_voice.py', '--engine', engine, f'--rate={rate}']
        if voice:
            voice_cmd += ['--voice', voice]
        try:
            run_cmd(voice_cmd, ROOT, label='build_voice.py')
        except RuntimeError:
            if engine == 'edge':
                JOB.log('>>> edge-tts fail hui - offline piper se retry')
                run_cmd([py, '-m', 'pip', 'install', '-q', 'piper-tts', 'numpy'], ROOT, label='pip install piper')
                run_cmd([py, 'scripts/build_voice.py', '--engine', 'piper'], ROOT, label='build_voice.py (piper)')
            else:
                raise

        # node_modules gayab hai to render turant fail hoga - pehle install
        if not os.path.isdir(os.path.join(ROOT, 'node_modules')):
            JOB.step = 'npm install'
            run_cmd(['npm', 'install', '--silent'], ROOT, label='npm install')

        JOB.step = 'rendering'
        cores = os.cpu_count() or 2
        cores = min(max(1, cores), 4)
        os.makedirs(OUT, exist_ok=True)
        run_cmd(['npx', 'remotion', 'render', 'src/index.ts', 'Explainer', 'out/video.mp4',
                 f'--concurrency={cores}'], ROOT, label='remotion render')

        JOB.step = 'done'
        JOB.ok = True
        JOB.log(f'✅ video ready ({time.time() - JOB.started:.0f}s)')
    except Exception as e:  # noqa: BLE001
        JOB.ok = False
        JOB.step = 'failed'
        JOB.log(f'❌ {e}')
    finally:
        JOB.running = False


# ---------------------------------------------------------------------------
# models
# ---------------------------------------------------------------------------
class ContentPayload(BaseModel):
    slug: str = 'video'
    title: str = 'New Video'
    tagline: str = 'In Hindi, step by step'
    chapters: list = []


class GeneratePayload(BaseModel):
    topic: str
    minutes: float = 3
    title: str | None = None
    tagline: str | None = None


class BuildPayload(BaseModel):
    engine: str = 'edge'
    voice: str | None = None
    rate: str = '-5%'


@app.get('/', response_class=HTMLResponse)
def index():
    return FileResponse(os.path.join(WEB, 'index.html'))


@app.get('/api/content')
def get_content():
    data = content_io.load()
    data['estimate'] = content_io.estimate(data.get('chapters', []))
    return data


@app.post('/api/content')
def save_content(payload: ContentPayload):
    data = payload.model_dump()
    # safety: khali ya adhoora content purani script ko mita na de
    scenes = sum(len(c.get('scenes', [])) for c in data.get('chapters', []))
    if scenes == 0:
        raise HTTPException(400, 'Content khali hai (0 scenes) — save rok diya, '
                                 'purani script safe hai')
    # check_content.py wali validation — build fail hone se pehle hi pakad lo
    import re as _re
    dev = _re.compile(r'[\u0900-\u097F]')
    problems = []
    for ch in data['chapters']:
        for sc in ch.get('scenes', []):
            where = sc.get('id') or '?'
            say = (sc.get('say') or '').strip()
            if not say:
                problems.append(f'{where}: narration khali hai')
            elif not dev.search(say):
                problems.append(f'{where}: narration Devanagari me likho')
            if not (sc.get('subtitle') or '').strip():
                problems.append(f'{where}: subtitle khali hai')
    if problems:
        raise HTTPException(400, 'Script me problem: ' + '; '.join(problems[:3])
                            + (f' (+{len(problems)-3} more)' if len(problems) > 3 else ''))
    for ch in data['chapters']:
        for sc in ch.get('scenes', []):
            sc.setdefault('bullets', [])
            sc.setdefault('steps', [])
            if not sc.get('steps'):
                sc['steps'] = []
    content_io.save(data)
    data['estimate'] = content_io.estimate(data.get('chapters', []))
    return data


@app.post('/api/generate-script')
def generate_script(payload: GeneratePayload):
    data = content_io.skeleton(payload.topic, payload.minutes, payload.title, payload.tagline)
    content_io.save(data)
    data['estimate'] = content_io.estimate(data['chapters'])
    return data


@app.get('/api/estimate')
def estimate():
    data = content_io.load()
    return {'estimate': content_io.estimate(data.get('chapters', [])),
            'words': sum(len((s.get('say') or '').split()) for c in data['chapters'] for s in c['scenes'])}


@app.post('/api/build')
def build(payload: BuildPayload):
    with LOCK:
        if JOB.running:
            raise HTTPException(409, 'build already running')
        threading.Thread(target=build_pipeline,
                         args=(payload.engine, payload.voice, payload.rate), daemon=True).start()
    return {'started': True}


@app.get('/api/status')
def status():
    return {
        'running': JOB.running,
        'ok': JOB.ok,
        'step': JOB.step,
        'lines': JOB.lines[-120:],
        'has_video': os.path.exists(VIDEO),
        'video_mtime': os.path.getmtime(VIDEO) if os.path.exists(VIDEO) else 0,
        # build ke dauraan purana mp4 pada rehta hai — size 0 dikhao taaki "purani
        # video ready hai" jaisa confusion na ho
        'video_size': 0 if JOB.running else (os.path.getsize(VIDEO) if os.path.exists(VIDEO) else 0),
        'audio_size': _wav_size(),
    }


def _wav_size():
    d = os.path.join(ROOT, 'public', 'voice')
    if not os.path.isdir(d):
        return 0
    return sum(os.path.getsize(os.path.join(d, f)) for f in os.listdir(d) if f.endswith('.wav'))


@app.get('/video')
def video():
    if not os.path.exists(VIDEO):
        raise HTTPException(404, 'video nahi bani abhi')
    return FileResponse(VIDEO, media_type='video/mp4', filename='kathareel-video.mp4')


@app.get('/audio')
def audio():
    d = os.path.join(ROOT, 'public', 'voice')
    if not os.path.isdir(d):
        raise HTTPException(404, 'voice nahi bani')
    wavs = [f for f in os.listdir(d) if f.endswith('.wav')]
    if not wavs:
        raise HTTPException(404, 'voice nahi bani')
    latest = max((os.path.join(d, f) for f in wavs), key=os.path.getmtime)
    return FileResponse(latest, media_type='audio/wav')


@app.get('/fonts/{name}')
def font(name: str):
    safe = os.path.basename(name)
    path = os.path.join(ROOT, 'public', 'fonts', safe)
    if not os.path.exists(path):
        raise HTTPException(404, 'font nahi mila')
    return FileResponse(path, media_type='font/ttf')


@app.get('/api/health')
def health():
    return {'ok': True, 'root': ROOT, 'node': shutil.which('node') is not None,
            'ffmpeg': shutil.which('ffmpeg') is not None,
            'tunnel_url': TUNNEL.url, 'version': VERSION}


def _port_open(port, host='127.0.0.1', timeout=0.4):
    import socket
    with socket.socket() as sock:
        sock.settimeout(timeout)
        return sock.connect_ex((host, port)) == 0


URL_FILE = '/tmp/kathareel_url.txt'


class Tunnel:
    """cloudflared ko zinda rakhta hai; mar jaye to naya URL bana kar restart.

    Free quick tunnels ka URL har restart par badalta hai, isliye:
      - URL file me likha jata hai (UI use dikhati hai)
      - tunnel girne par khud dobara khada hota hai
      - /api/health me current URL aata hai
    """

    def __init__(self, port, enabled=True, provider='auto'):
        self.port = port
        self.enabled = enabled
        self.provider = provider          # 'auto' | 'cloudflared' | 'lhr'
        self.url = None
        self.proc = None
        self._stop = threading.Event()
        self._thread = None

    # --- internals -----------------------------------------------------
    def _find_exe(self):
        exe = shutil.which('cloudflared')
        if exe:
            return exe
        if os.path.exists('/tmp/cloudflared'):
            return '/tmp/cloudflared'
        subprocess.run(['bash', '-lc',
                        'curl -fsSL -o /tmp/cloudflared '
                        'https://github.com/cloudflare/cloudflared/releases/latest/download/'
                        'cloudflared-linux-amd64 && chmod +x /tmp/cloudflared'],
                       capture_output=True)
        return '/tmp/cloudflared' if os.path.exists('/tmp/cloudflared') else None

    # ---- provider: localhost.run (ssh, reliable) -----------------------
    def _spawn_lhr(self):
        log = '/tmp/lhr.log'
        open(log, 'w').close()
        self._log = log
        self.proc = subprocess.Popen(
            ['ssh', '-o', 'StrictHostKeyChecking=no', '-o', 'UserKnownHostsFile=/dev/null',
             '-o', 'ServerAliveInterval=20', '-o', 'ExitOnForwardFailure=yes',
             '-R', f'80:localhost:{self.port}', 'nokey@localhost.run'],
            stdout=open(log, 'w'), stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL)
        pat = re.compile(r'https://([a-z0-9]+)\.app\.lhr\.life')
        for _ in range(80):
            if self._stop.is_set():
                return False
            time.sleep(0.5)
            try:
                found = pat.search(open(log, encoding='utf-8', errors='ignore').read())
            except OSError:
                found = None
            if found:
                self.url = found.group(0)
                with open(URL_FILE, 'w') as f:
                    f.write(self.url)
                print(f'  PUBLIC  : {self.url}  (localhost.run)', flush=True)
                return True
            if self.proc.poll() is not None:
                return False
        return False

    def _spawn(self):
        order = ([self.provider] if self.provider != 'auto'
                 else ['cloudflared', 'lhr'])
        for prov in order:
            if prov == 'lhr':
                if shutil.which('ssh') and self._spawn_lhr():
                    return True
            elif self._spawn_cloudflared():
                return True
            if self._stop.is_set():
                return False
        return False

    def _spawn_cloudflared(self):
        exe = self._find_exe()
        if not exe:
            return False
        log = '/tmp/cloudflared.log'
        open(log, 'w').close()
        self._log = log
        self.proc = subprocess.Popen(
            [exe, 'tunnel', '--url', f'http://127.0.0.1:{self.port}', '--no-autoupdate'],
            stdout=open(log, 'w'), stderr=subprocess.STDOUT)
        pat = re.compile(r'https://[a-z0-9-]+\.trycloudflare\.com')
        for _ in range(80):
            if self._stop.is_set():
                return False
            time.sleep(0.5)
            try:
                found = pat.search(open(log, encoding='utf-8', errors='ignore').read())
            except OSError:
                found = None
            if found:
                self.url = found.group(0)
                with open(URL_FILE, 'w') as f:
                    f.write(self.url)
                print(f'  PUBLIC  : {self.url}', flush=True)
                return True
            if self.proc.poll() is not None:
                return False
        return False

    def _run(self):
        backoff = 2
        while not self._stop.is_set():
            ok = self._spawn()
            if ok:
                backoff = 2
            else:
                print('  tunnel start nahi hua — 8s me retry', flush=True)
                time.sleep(8)
                continue
            # process zinda hone se tunnel zinda nahi hota: Cloudflare kabhi
            # "Unauthorized: Tunnel not found" deta hai (tunnel server side delete).
            # Isliye URL ko bhi health-check karte hain.
            while not self._stop.is_set() and self.proc and self.proc.poll() is None:
                time.sleep(5)
                if self._tunnel_dead():
                    print('  tunnel dead ho gaya (Cloudflare ne drop kiya) — restart',
                          flush=True)
                    try:
                        self.proc.terminate()
                    except Exception:  # noqa: BLE001
                        pass
                    break
            if self._stop.is_set():
                break
            print(f'  tunnel gir gaya — {backoff}s me naya URL', flush=True)
            self.url = None
            time.sleep(backoff)
            backoff = min(30, backoff * 2)

    def _tunnel_dead(self):
        """URL ab bhi kaam kar raha hai? Log me 'Tunnel not found' bhi dekh lo."""
        try:
            txt = open(getattr(self, '_log', '/tmp/cloudflared.log'),
                       encoding='utf-8', errors='ignore').read()
            for bad in ('Tunnel not found', 'Unauthorized', 'Permission denied',
                        'remote port forwarding failed'):
                if bad in txt:
                    return True
        except OSError:
            pass
        if not self.url:
            return True
        try:
            import urllib.request
            req = urllib.request.Request(self.url + '/api/health',
                                         headers={'User-Agent': 'kathareel-watch'})
            with urllib.request.urlopen(req, timeout=8) as r:
                return r.status != 200
        except Exception:  # noqa: BLE001
            return True

    # --- public --------------------------------------------------------
    def start(self):
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        return self

    def stop(self):
        self._stop.set()
        if self.proc and self.proc.poll() is None:
            self.proc.terminate()


TUNNEL = Tunnel(0, enabled=False)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--port', type=int, default=8000)
    ap.add_argument('--host', default='0.0.0.0')
    ap.add_argument('--public', action='store_true', help='public URL banao (Kaggle/Colab)')
    ap.add_argument('--tunnel', default='auto', choices=['auto', 'cloudflared', 'lhr', 'none'])
    a = ap.parse_args()

    # agar port pehle se busy hai to uvicorn chupchaap fail hota hai aur tunnel
    # kisi doosre server ko point karne lagta hai — isliye pehle hi saaf error do
    if _port_open(a.port):
        print(f'\n  ❌ port {a.port} pehle se busy hai.')
        print(f'     Purana server band karo, ya naya port do: --port {a.port + 1}\n')
        sys.exit(1)

    server = threading.Thread(
        target=lambda: uvicorn.run(app, host=a.host, port=a.port, log_level='warning'),
        daemon=True)
    server.start()
    for _ in range(60):
        if _port_open(a.port):
            break
        time.sleep(0.25)

    banner = [f'  local   : http://127.0.0.1:{a.port}']
    if a.public and a.tunnel != 'none':
        TUNNEL.port = a.port
        TUNNEL.enabled = True
        TUNNEL.provider = a.tunnel
        TUNNEL.start()          # pehla URL print khud karega
        banner.append(f'  Kaggle  : https://www.kaggle.com/code/<your-notebook>/proxy/{a.port}/')
        banner.append('  (tunnel girne par naya URL khud ban jata hai — /api/health me dekho)')

    print('\n' + '=' * 74)
    print(f'  kathareel studio — ready  (v{VERSION})')
    for line in banner:
        print(line)
    print('=' * 74 + '\n')

    try:
        while True:
            time.sleep(3600)
    except KeyboardInterrupt:
        print('\nbye')


if __name__ == '__main__':
    main()
