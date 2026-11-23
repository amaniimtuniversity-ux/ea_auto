#!/usr/bin/env python3
"""
Build kathareel_studio.ipynb (Kaggle notebook).

Studio ki files (web/*.py, web/index.html, scripts/content_io.py) notebook me
gzip+base64 embed ho jati hain — isliye notebook self-contained rehta hai aur
GitHub push ka intezaar nahi karna padta. Notebook phir bhi repo clone karta hai
(Remotion ke src/ ke liye).

    python3 scripts/make_notebook.py
"""
import base64
import gzip
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILES = ['web/index.html', 'web/server.py', 'web/kaggle_launch.py', 'scripts/content_io.py']
OUT = os.path.join(ROOT, 'kathareel_studio.ipynb')


def md(*lines):
    return {"cell_type": "markdown", "metadata": {},
            "source": [l + "\n" for l in lines[:-1]] + [lines[-1]]}


def code(*lines):
    return {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [],
            "source": [l + "\n" for l in lines[:-1]] + [lines[-1]]}


def _studio_literal(blob):
    """STUDIO = { ... } ko notebook cell ki lines me todo."""
    lines = json.dumps(blob, indent=0).splitlines()
    return ['STUDIO = ' + lines[0]] + lines[1:]


def build():
    blob = {}
    for f in FILES:
        raw = open(os.path.join(ROOT, f), 'rb').read()
        blob[f] = base64.b64encode(gzip.compress(raw, 9)).decode()

    cells = [
        md("# kathareel — Hindi explainer video, browser se",
           "",
           "**by raghv** · Topic do → script banti hai → browser me edit karo → video render.",
           "Narration Devanagari Hindi + English tech words; on-screen text sirf English.",
           "",
           "### Kaggle settings",
           "",
           "| Setting | Value |",
           "|---|---|",
           "| Internet | **ON** (Hindi neural voice + npm) |",
           "| Accelerator | **None** (CPU kaafi hai — 2D scenes) |",
           "| Persistence | Files only |",
           "",
           "Cell **1 → 2 → 3** chalao. Cell 3 URL dega — wahi kholo."),

        code("# 1 · repo + system deps + packages   (~3-4 min pehli baar)",
             "import os, shutil, subprocess, sys",
             "",
             "REPO = 'https://github.com/amaniimtuniversity-ux/ea_auto.git'",
             "ROOT = '/kaggle/working/kathareel'",
             "",
             "if not os.path.isdir(os.path.join(ROOT, 'src')):",
             "    subprocess.run(['git', 'clone', '--depth', '1', REPO, ROOT], check=True)",
             "os.chdir(ROOT)",
             "",
             "subprocess.run('apt-get -qq update && apt-get -qq install -y ffmpeg libnss3 libnspr4 '",
             "               'libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 libxkbcommon0 '",
             "               'libxcomposite1 libxdamage1 libxfixes3 libxrandr2 libgbm1 libasound2',",
             "               shell=True)",
             "subprocess.run([sys.executable, '-m', 'pip', 'install', '-q', '--upgrade',",
             "                'fastapi', 'uvicorn', 'edge-tts', 'numpy'])",
             "if not os.path.isdir(os.path.join(ROOT, 'node_modules')):",
             "    subprocess.run('npm install --silent', shell=True)",
             "",
             "print('root  :', ROOT)",
             "print('ffmpeg:', shutil.which('ffmpeg') is not None,",
             "      '| node:', shutil.which('node') is not None)"),

        code(*(["# 2 · latest studio files (repo se naye ho sakte hain — ye override karte hain)",
                "#    gzip+base64, isliye GitHub push ka intezaar nahi karna padta",
                "import base64, gzip, os",
                ]
               + _studio_literal(blob) + [
             "",
             "for path, payload in STUDIO.items():",
             "    full = os.path.join(ROOT, path)",
             "    os.makedirs(os.path.dirname(full) or ROOT, exist_ok=True)",
             "    open(full, 'wb').write(gzip.decompress(base64.b64decode(payload)))",
             "    print('wrote', path)",
             "",
             "print('\\n\u2705 ready — ab cell 3 chalao')"])),

        md("## Studio start",
           "",
           "URL milne me ~30 sec. Cell return ho jayega, server background me zinda rahega.",
           "",
           "- **Public URL** (`https://....trycloudflare.com`) → kahin se bhi khulta hai, sabse aasan",
           "- **Kaggle proxy** → `https://www.kaggle.com/code/<user>/<notebook>/proxy/8000/`"),

        code("# 3 · STUDIO START -> URL milega",
             "!python web/kaggle_launch.py"),

        md("## Studio kaise use karna hai",
           "",
           "1. **Topic** (`Photosynthesis`, `Git rebase`, `RAG`) + **minutes** → **Generate script**",
           "2. Har scene edit: Hindi narration (Devanagari), English caption, keyword, bullets",
           "3. **Length** meter dekho — target se kam/zyada to words add/cut karo",
           "4. **Generate video** → Hindi voice + render (3 min video ≈ 3–4 min CPU par)",
           "5. Video usi page par chalti hai + mp4 download",
           "",
           "**Review-first:** script bina dekhe/edit kiye video nahi banti."),

        md("## Bina UI ke (terminal se)",
           "",
           "```bash",
           "./scripts/make_video.sh --minutes 3     # script.md banegi — edit karo",
           "./scripts/make_video.sh --build         # voice + render -> out/video.mp4",
           "```"),

        code("# 4 · (optional) sirf script banao, terminal se",
             "!./scripts/make_video.sh --minutes 3",
             "print('\\nscript.md edit karo, phir: !./scripts/make_video.sh --build')"),
    ]

    nb = {"cells": cells,
          "metadata": {
              "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
              "language_info": {"name": "python", "version": "3.11"},
              "kaggle": {"accelerator": "none", "dataSources": [], "isInternetEnabled": True,
                         "language": "python", "sourceType": "notebook"},
          },
          "nbformat": 4, "nbformat_minor": 4}
    json.dump(nb, open(OUT, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    print('wrote %s — %d cells, %.1f KB' % (OUT, len(cells), os.path.getsize(OUT) / 1024))


if __name__ == '__main__':
    build()
