#!/usr/bin/env python3
"""
kathareel — voiceover builder (by raghv)

Ye script content.ts ki Hindi lines (`say`) se voiceover banati hai aur
subtitle timings (frame numbers) nikal kar src/timeline.ts me likhti hai.

Do engines:
  edge   (default) Microsoft neural Hindi voices - natural, cloud, free.
         hi-IN-MadhurNeural (male) / hi-IN-SwaraNeural (female)
  piper  (offline) local Hindi voice - no internet needed.
         hi_IN-pratham / hi_IN-priyamvada / hi_IN-rohan (model auto-download)

Kyun Devanagari? Latin-script Hindi ("matlab kya hai") ko Hindi TTS galat bolti hai.
Devanagari likhne par native pronunciation milti hai, aur beech ke English words
(chunk, embed, RAG) bhi sahi bolte hain.

Usage:
  python3 scripts/build_voice.py                  # edge, Madhur, -5% speed
  python3 scripts/build_voice.py --engine piper   # offline
  python3 scripts/build_voice.py --voice hi-IN-SwaraNeural --rate=-8%
  python3 scripts/build_voice.py --check          # sirf timings, audio nahi
"""
import argparse
import asyncio
import json
import os
import re
import shutil
import subprocess
import sys
import wave

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(ROOT, 'voice_cache')
PUBLIC = os.path.join(ROOT, 'public', 'voice')
SR = 48000
FPS = 30

# --- pacing (frames @30fps) ------------------------------------------------
LEAD = 105          # title card hold before the first line (~3.5s)
GAP = 12            # silence between two beats of the same scene
SCENE_PAD = 26      # extra hold at the end of a scene (viewer reads the visual)
OUTRO = 110         # end card hold


# --------------------------------------------------------------------------
# content.ts parsing (no JS runtime needed: we read the literal arrays)
# --------------------------------------------------------------------------
def parse_content(path):
    src = open(path, encoding='utf-8').read()

    def grab_str(field, start=0):
        m = re.search(rf"{field}\s*:\s*'([^']*)'", src[start:])
        return (m.group(1), start + m.end()) if m else (None, start)

    slug, _ = grab_str('slug')
    title, _ = grab_str('title')
    tagline, _ = grab_str('tagline')

    chapters = []
    for cm in re.finditer(r"\{\s*title:\s*'([^']*)',\s*scenes:\s*\[", src):
        ch_title = cm.group(1)
        start = cm.end() - 1
        depth, i = 0, start
        while i < len(src):
            if src[i] == '[':
                depth += 1
            elif src[i] == ']':
                depth -= 1
                if depth == 0:
                    break
            i += 1
        block = src[start:i + 1]
        scenes = []
        for sm in re.finditer(r"\{\s*id:\s*'([^']*)',\s*type:\s*'([^']*)'", block):
            sid, stype = sm.group(1), sm.group(2)
            seg_end = block.find('id:', sm.end())
            seg = block[sm.start(): seg_end if seg_end > 0 else len(block)]
            say_m = re.search(r"say:\s*'((?:[^'\\]|\\.)*)'", seg)
            sub_m = re.search(r"subtitle:\s*'((?:[^'\\]|\\.)*)'", seg)
            kw_m = re.search(r"keyword:\s*'((?:[^'\\]|\\.)*)'", seg)
            scenes.append({
                'id': sid,
                'type': stype,
                'say': (say_m.group(1) if say_m else '').replace("\\'", "'"),
                'subtitle': (sub_m.group(1) if sub_m else '').replace("\\'", "'"),
                'keyword': (kw_m.group(1) if kw_m else '').replace("\\'", "'"),
            })
        chapters.append({'title': ch_title, 'scenes': scenes})
    return {'slug': slug or 'video', 'title': title or '', 'tagline': tagline or '',
            'chapters': chapters}


# --------------------------------------------------------------------------
# audio helpers
# --------------------------------------------------------------------------
def decode(path):
    raw = subprocess.run(
        ['ffmpeg', '-v', 'error', '-i', path, '-f', 'f32le', '-ac', '1', '-ar', str(SR), '-'],
        capture_output=True, check=True).stdout
    import numpy as np
    return np.frombuffer(raw, dtype=np.float32).copy()


def trim(x, thr=0.006):
    import numpy as np
    idx = np.where(np.abs(x) > thr)[0]
    if len(idx) == 0:
        return x[:0]
    a, b = max(0, idx[0] - int(0.04 * SR)), min(len(x), idx[-1] + int(0.10 * SR))
    return x[a:b]


def write_wav(path, x, sr=SR):
    import numpy as np
    a = (np.clip(x, -1, 1) * 32767).astype(np.int16)
    stereo = np.stack([a, a], 1)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with wave.open(path, 'wb') as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(stereo.tobytes())


def cache_key(text, voice, rate):
    import hashlib
    return hashlib.sha1(f'{voice}|{rate}|{text}'.encode()).hexdigest()[:16]


# --------------------------------------------------------------------------
# engines
# --------------------------------------------------------------------------
async def edge_synth(text, voice, rate, out):
    try:
        import edge_tts
    except ImportError:
        raise SystemExit(
            'edge-tts installed nahi hai. Install karo:\n'
            '    pip install -q edge-tts numpy\n'
            'ya offline voice use karo:\n'
            '    pip install -q piper-tts && python3 scripts/build_voice.py --engine piper'
        )
    # edge ka endpoint kai baar negative rate (e.g. -5%) par khaali audio deta hai.
    # Strategy: 2 try requested rate par, phir normal speed par — audio ko ffmpeg se
    # slow kar dete hain. Sunne me same lagta hai aur pipeline piper par nahi girti.
    plan = [rate, rate, '+0%', '+0%', '+0%']
    last = None
    for attempt, use_rate in enumerate(plan, start=1):
        try:
            comm = edge_tts.Communicate(text, voice, rate=use_rate, boundary='WordBoundary')
            got = 0
            with open(out, 'wb') as f:
                async for chunk in comm.stream():
                    if chunk['type'] == 'audio' and chunk['data']:
                        f.write(chunk['data'])
                        got += len(chunk['data'])
            if got > 2000:
                if use_rate != rate and rate not in (None, '', '+0%'):
                    _slow_down(out, rate)
                return out
            last = RuntimeError('empty audio')
        except Exception as e:  # endpoint sometimes returns nothing
            last = e
        if attempt < len(plan):
            print(f'   retry {attempt}/{len(plan)} ({type(last).__name__})')
            await asyncio.sleep(1.0 * attempt)
    raise SystemExit(f'edge-tts failed {len(plan)}x: {last}\n'
                     f'Try: --engine piper (offline)')


PIPER_VOICES = {
    'hi_IN-pratham': 'https://huggingface.co/rhasspy/piper-voices/resolve/main/hi/hi_IN/pratham/medium/hi_IN-pratham-medium',
    'hi_IN-priyamvada': 'https://huggingface.co/rhasspy/piper-voices/resolve/main/hi/hi_IN/priyamvada/medium/hi_IN-priyamvada-medium',
    'hi_IN-rohan': 'https://huggingface.co/rhasspy/piper-voices/resolve/main/hi/hi_IN/rohan/medium/hi_IN-rohan-medium',
}



def _slow_pct(rate):
    """'-5%' -> 0.95 ki speed factor."""
    try:
        return 1.0 + float(str(rate).replace('%', '').strip()) / 100.0
    except ValueError:
        return 1.0


def _slow_down(path, rate):
    """Normal-speed audio ko ffmpeg se slow karo (pitch same rehti hai)."""
    factor = _slow_pct(rate)
    if abs(factor - 1.0) < 0.01 or not shutil.which('ffmpeg'):
        return path
    tmp = path + '.slow.mp3'
    r = subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', path,
                        '-filter:a', f'atempo={factor:.3f}', tmp])
    if r.returncode == 0 and os.path.exists(tmp):
        os.replace(tmp, path)
    return path


def piper_model(name):
    """Download the piper voice once into voice_cache/models (offline afterwards)."""
    d = os.path.join(CACHE, 'models')
    os.makedirs(d, exist_ok=True)
    onnx = os.path.join(d, f'{name}.onnx')
    cfg = onnx + '.json'
    if os.path.exists(onnx) and os.path.exists(cfg):
        return onnx
    base = PIPER_VOICES[name]
    for url, path in ((base + '.onnx', onnx), (base + '.onnx.json', cfg)):
        print(f'   downloading {os.path.basename(path)} ...')
        subprocess.run(['curl', '-sL', '-o', path, url], check=True)
    return onnx


def piper_synth(text, voice, out):
    try:
        from piper import PiperVoice
    except ImportError:
        raise SystemExit('piper chahiye: pip install piper-tts')
    model = piper_model(voice)
    v = PiperVoice.load(model, config_path=model + '.json')
    tmp = out + '.raw.wav'
    with wave.open(tmp, 'wb') as w:
        v.synthesize_wav(text, w)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', tmp, '-ar', str(SR), '-ac', '1', out], check=True)
    os.remove(tmp)
    return out


# --------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--engine', default='edge', choices=['edge', 'piper'])
    ap.add_argument('--voice', default=None, help='edge: hi-IN-MadhurNeural / hi-IN-SwaraNeural; piper: hi_IN-pratham')
    ap.add_argument('--rate', default='-5%', help='edge speed, e.g. -5% (slower) or +0%')
    ap.add_argument('--check', action='store_true', help='only compute timings (no audio download)')
    a = ap.parse_args()

    voice = a.voice or ('hi-IN-MadhurNeural' if a.engine == 'edge' else 'hi_IN-pratham')
    content = parse_content(os.path.join(ROOT, 'src', 'content.ts'))
    os.makedirs(CACHE, exist_ok=True)
    os.makedirs(PUBLIC, exist_ok=True)

    try:
        import numpy as np
    except ImportError:
        raise SystemExit('numpy chahiye:  pip install -q numpy')
    if a.engine == 'piper':
        pass
    # quick dependency check so the failure is a clear message, not a traceback
    if a.engine == 'edge' and not a.check:
        try:
            import edge_tts  # noqa: F401
        except ImportError:
            raise SystemExit(
                'edge-tts installed nahi hai. Do options:\n'
                '  1) natural neural Hindi voice:  pip install -q edge-tts numpy\n'
                '  2) offline voice:               pip install -q piper-tts numpy  ->  '
                'python3 scripts/build_voice.py --engine piper'
            )

    frames = int(LEAD)
    pieces = [(0.0, np.zeros(int(LEAD / FPS * SR), dtype=np.float32))]
    timeline = []
    t = LEAD / FPS

    print(f'engine={a.engine} voice={voice} rate={a.rate if a.engine == "edge" else "-"}')
    for ci, ch in enumerate(content['chapters'], start=1):
        ch_start = frames + 1
        for scene in ch['scenes']:
            sid = scene['id']
            text = scene['say'].strip()
            if not text:
                continue
            if a.check:
                # rough estimate: Hindi speech ~13 chars/sec
                dur = max(1.6, len(text) / 13.0)
                path = None
            else:
                ext = '.mp3' if a.engine == 'edge' else '.wav'
                path = os.path.join(CACHE, cache_key(text, voice, a.rate) + ext)
                if not os.path.exists(path):
                    if a.engine == 'edge':
                        asyncio.run(edge_synth(text, voice, a.rate, path))
                    else:
                        piper_synth(text, voice, path)
                x = trim(decode(path))
                if len(x) == 0:
                    raise SystemExit(f'empty audio for {sid}: {text[:40]}')
                dur = len(x) / SR

            f0 = frames + 1
            f1 = f0 + max(1, int(round(dur * FPS))) - 1
            timeline.append({
                'id': sid,
                'chapter': ci,
                'type': scene['type'],
                'from': f0,
                'to': f1,
                'say': text,
                'subtitle': scene['subtitle'],
                'keyword': scene['keyword'],
            })
            if path:
                pieces.append((t, x))
            # advance
            frames = f1 + SCENE_PAD
            t += dur + SCENE_PAD / FPS
            if scene is not ch['scenes'][-1]:
                pieces.append((t - SCENE_PAD / FPS, np.zeros(int(GAP / FPS * SR), dtype=np.float32)))
                frames += GAP - SCENE_PAD
                t += GAP / FPS - SCENE_PAD / FPS
        ch['from'] = ch_start
        ch['to'] = frames

    total = frames + OUTRO
    chapters = [{'n': i + 1, 'title': c['title'], 'from': c['from'], 'to': c['to']}
                for i, c in enumerate(content['chapters'])]

    # ---- write timeline.ts ----
    ts = ['// AUTO-GENERATED by scripts/build_voice.py — do not edit by hand.',
          '// Regenerate after changing src/content.ts:  python3 scripts/build_voice.py',
          '',
          'export type Beat = {',
          '  id: string; chapter: number; type: string;',
          '  from: number; to: number;',
          '  say: string; subtitle: string; keyword: string;',
          '};',
          '',
          f'export const TOTAL_FRAMES = {total};',
          f'export const FPS = {FPS};',
          '',
          'export const CHAPTERS: {n: number; title: string; from: number; to: number}[] = [']
    for c in chapters:
        ts.append(f"  {{n: {c['n']}, title: '{c['title']}', from: {c['from']}, to: {c['to']}}},")
    ts += ['];', '', 'export const BEATS: Beat[] = [']
    for b in timeline:
        say = b['say'].replace('\\', '\\\\').replace("'", "\\'")
        sub = b['subtitle'].replace("'", "\\'")
        kw = b['keyword'].replace("'", "\\'")
        ts.append(f"  {{id: '{b['id']}', chapter: {b['chapter']}, type: '{b['type']}', "
                  f"from: {b['from']}, to: {b['to']}, say: '{say}', subtitle: '{sub}', keyword: '{kw}'}},")
    ts += ['];', '']
    open(os.path.join(ROOT, 'src', 'timeline.ts'), 'w', encoding='utf-8').write('\n'.join(ts))

    if a.check:
        print(f'total {total} frames = {total / FPS:.1f}s  ({len(timeline)} beats)')
        for b in timeline:
            print(f"  {b['id']:>4} ch{b['chapter']} f{b['from']}-{b['to']}  {b['subtitle']}")
        return

    # ---- mix audio ----
    total_samples = int(total / FPS * SR) + SR
    y = np.zeros(total_samples, dtype=np.float32)
    for start, arr in pieces:
        i = int(start * SR)
        y[i:i + len(arr)] += arr
    y = y[: int(total / FPS * SR)]
    peak = float(np.max(np.abs(y))) or 1.0
    y = y / peak * 0.9
    out_wav = os.path.join(PUBLIC, f"{content['slug']}.wav")
    write_wav(out_wav, y)
    prune_stale_voice(out_wav)
    print(f'\nvoiceover: {out_wav}')
    print(f'timeline : src/timeline.ts  ({total} frames = {total / FPS:.1f}s, {len(timeline)} beats)')
    print(f'chapters : ' + ', '.join(f"{c['title']} f{c['from']}" for c in chapters))


def prune_stale_voice(keep):
    """Purane voiceover WAV hata do — ye ~30 MB each hote hain aur dobara
    ban jaate hain. Workspace 128 MB par cap hai, isliye yahi sabse bada leak tha."""
    keep = os.path.abspath(keep)
    removed, freed = [], 0
    for f in sorted(os.listdir(PUBLIC)):
        if not f.endswith('.wav'):
            continue
        path = os.path.join(PUBLIC, f)
        if os.path.abspath(path) == keep:
            continue
        try:
            size = os.path.getsize(path)
            os.remove(path)
            removed.append(f'{f} ({size / 1e6:.0f} MB)')
            freed += size
        except OSError:
            pass
    if removed:
        print(f'\nprune  : hata diye {len(removed)} purane wav — {freed / 1e6:.0f} MB free')
        for r in removed:
            print(f'         - {r}')


if __name__ == '__main__':
    main()
