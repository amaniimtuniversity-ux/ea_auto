#!/usr/bin/env python3
"""kathareel demo installer - Kaggle / Colab / Linux me ek hi command se demo chalane ke liye.

Kya karta hai:
  1. project folder banata hai (template/ se)
  2. demo narration (Hinglish voiceover, English board) + demo shots + Demo composition daalta hai
  3. config.ts me lang: 'hi', title, chapters, HUD set karta hai
  4. npm install
  5. TTS chalta hai (edge-tts -> espeak offline fallback)
  6. render karta hai: demo.mp4 + 3 stills

Use:
  python3 kaggle/setup_demo.py --work /kaggle/working/demo
  python3 kaggle/setup_demo.py --work /kaggle/working/demo --skip-render
"""
import argparse, os, re, shutil, subprocess, sys, textwrap

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)


def run(cmd, cwd=None, check=True, env=None):
    print(f'\n$ {" ".join(cmd) if isinstance(cmd, list) else cmd}')
    p = subprocess.run(cmd, cwd=cwd, shell=isinstance(cmd, str), env=env,
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    out = (p.stdout or '').strip()
    if out:
        print(out[-4000:])
    if check and p.returncode != 0:
        raise SystemExit(f'FAILED ({p.returncode}): {cmd}')
    return p.returncode


def apt_install(pkgs):
    """Kaggle / Colab me root hote hain; locally sudo ho to sudo try karo."""
    if shutil.which('apt-get') is None:
        print('apt-get nahi mila - system packages skip')
        return
    base = ['apt-get', 'install', '-y', '-q'] + pkgs
    if os.geteuid() != 0 and shutil.which('sudo'):
        base = ['sudo', '-n'] + base
    run(base, check=False)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--work', default='/kaggle/working/demo', help='project folder (ban jayega)')
    ap.add_argument('--skip-render', action='store_true', help='sirf setup + TTS, render nahi')
    ap.add_argument('--frames', default='', help='render ke bajaye sirf stills ke frame numbers, e.g. 60,420,900')
    ap.add_argument('--force', action='store_true', help='work folder already hai to dobara copy karo')
    a = ap.parse_args()

    work = os.path.abspath(a.work)
    tpl = os.path.join(REPO, 'template')
    assert os.path.isdir(tpl), f'template nahi mila: {tpl}'

    # ---- 1. project copy ----
    if os.path.isdir(work) and os.listdir(work) and not a.force:
        print(f'{work} already bhara hua hai - use kar raha hoon (--force se dobara copy)')
    else:
        os.makedirs(work, exist_ok=True)
        shutil.copytree(tpl, work, dirs_exist_ok=True,
                        ignore=shutil.ignore_patterns('node_modules', 'build*', 'renders', 'stills', 'audio'))
        print(f'project copied -> {work}')

    # ---- 2. narration + demo shots + composition ----
    shutil.copy(os.path.join(REPO, 'demo/narration.txt'), os.path.join(work, 'script/narration.txt'))
    os.makedirs(os.path.join(work, 'src/demo'), exist_ok=True)
    shutil.copy(os.path.join(REPO, 'demo/Demo.tsx'), os.path.join(work, 'src/demo/Demo.tsx'))

    root = os.path.join(work, 'src/Root.tsx')
    src = open(root, encoding='utf-8').read()
    if 'demo/Demo' not in src:
        src = src.replace("import {PreviewOverlay} from './overlay/Preview';",
                          "import {PreviewOverlay} from './overlay/Preview';\nimport {Demo, DEMO_FRAMES} from './demo/Demo';")
        src = src.replace('    <Composition id="Overlay"',
                          '    <Composition id="Demo" component={Demo} durationInFrames={DEMO_FRAMES} fps={FPS} width={W} height={H} />\n    <Composition id="Overlay"')
        open(root, 'w', encoding='utf-8').write(src)
        print('Root.tsx: Demo composition added')

    # ---- 3. config.ts ----
    cfg_path = os.path.join(work, 'src/config.ts')
    cfg = open(cfg_path, encoding='utf-8').read()
    cfg = re.sub(r"slug:\s*'[^']*'", "slug: 'demo'", cfg, count=1)
    cfg = re.sub(r"lang:\s*'(zh|en|hi)'", "lang: 'hi'", cfg, count=1)          # Hinglish voice, English board
    cfg = re.sub(r"title:\s*\{[^}]*\}", "title: {big: 'RAG', rest: '', en: 'Retrieval Augmented Generation', "
                                       "tagline: 'Give the model your sources'}", cfg, count=1)
    cfg = re.sub(r"chapterTech:\s*\[[^\]]*\]", "chapterTech: ['Problem First', 'Pipeline']", cfg, count=1)
    cfg = re.sub(r"  hud:\s*\[.*?\] as HudEntry\[\],", textwrap.dedent("""  hud: [
    {fromS: 'S01', toS: 'S01', text: 'The Problem'},
    {fromS: 'S02', toS: 'S02', text: 'The Gap'},
    {fromS: 'S03', toS: 'S03', text: 'The Fix'},
    {fromS: 'S04', toS: 'S05', text: 'The Pipeline', tech: 'Chunks'},
  ] as HudEntry[],"""), cfg, count=1, flags=re.S)
    open(cfg_path, 'w', encoding='utf-8').write(cfg)
    print("config.ts: lang='hi' (Hinglish voice / English board), title + chapters + HUD set")

    # ---- 4. system deps + npm ----
    apt_install(['espeak-ng', 'ffmpeg'])
    run(['npm', 'install', '--silent'], cwd=work)
    run(['npx', 'tsc', '--noEmit'], cwd=work)

    # ---- 5. TTS: cloud edge-tts, fail hone par espeak offline ----
    env = dict(os.environ, TTS_ENGINE=os.environ.get('TTS_ENGINE', 'edge'))
    rc = run([sys.executable, 'scripts/tts_build.py'], cwd=work, check=False, env=env)
    if rc != 0:
        print('\n⚠ edge-tts nahi chala (Kaggle se aksar block hota hai) - espeak offline voice se retry')
        run([sys.executable, 'scripts/tts_build.py'], cwd=work, check=True,
            env=dict(os.environ, TTS_ENGINE='espeak'))

    # ---- 6. render ----
    if a.frames:
        for f in [x.strip() for x in a.frames.split(',') if x.strip()]:
            run(['npx', 'remotion', 'still', 'src/index.ts', 'Demo', f'demo_f{f}.png', f'--frame={f}'], cwd=work)
        print('\nstills ready:', work)
        return
    if a.skip_render:
        print('\nsetup + TTS done (render skipped). Render:')
        print(f'  cd {work} && npx remotion render src/index.ts Demo demo.mp4 --concurrency=2')
        return
    run(['npx', 'remotion', 'render', 'src/index.ts', 'Demo', 'demo.mp4', '--concurrency=2'], cwd=work)
    for f in ('60', '420', '900'):
        run(['npx', 'remotion', 'still', 'src/index.ts', 'Demo', f'demo_f{f}.png', f'--frame={f}'], cwd=work, check=False)
    size = os.path.getsize(os.path.join(work, 'demo.mp4')) / 1e6
    print(f'\n✅ demo.mp4 ready: {work}/demo.mp4 ({size:.1f} MB)')


if __name__ == '__main__':
    main()
