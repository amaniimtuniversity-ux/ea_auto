#!/usr/bin/env python3
"""
kathareel — script review (by raghv)

Video banane se PEHLE script dekhna/edit karna. Isse chalta hai:

    python3 scripts/script_review.py                    # mojooda content.ts se script.md banao
    python3 scripts/script_review.py --minutes 3        # 3 min ka target, kam/zyada words batao
    python3 scripts/script_review.py --from-script      # script.md ke edits wapas content.ts me daalo

Workflow:
    1. script.md kholo, `say` / `subtitle` / `keyword` lines edit karo, duration badalna ho
       to `--minutes` dekh lo. Chapter names bhi badal sakte ho.
    2. python3 scripts/script_review.py --from-script   -> src/content.ts update
    3. python3 scripts/check_content.py                 -> galtiyan check
    4. python3 scripts/build_voice.py                   -> voice + timings
    5. npx remotion render src/index.ts Explainer out/video.mp4 --concurrency=2

Duration kaise nikalti hai: Hindi speech ~2.6 words/second (edge-tts, -5% rate),
plus title card 3.5s, har scene ke baad ~0.9s, end card 3.7s.
"""
import argparse
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONTENT = os.path.join(ROOT, 'src', 'content.ts')
SCRIPT = os.path.join(ROOT, 'script.md')

# pacing constants — scripts/build_voice.py se match karte hain
WORDS_PER_SEC = 2.6
LEAD_S = 3.5
SCENE_PAD_S = 0.9
GAP_S = 0.4
OUTRO_S = 3.7


# ---------------------------------------------------------------------------
# content.ts  <->  script.md
# ---------------------------------------------------------------------------
def parse_content(path=CONTENT):
    src = open(path, encoding='utf-8').read()

    def one(field):
        m = re.search(rf"{field}:\s*'((?:[^'\\]|\\.)*)'", src)
        return m.group(1).replace("\\'", "'") if m else ''

    chapters = []
    for cm in re.finditer(r"\{\s*title:\s*'([^']*)',\s*scenes:\s*\[", src):
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
            seg_end = block.find('id:', sm.end())
            seg = block[sm.start(): seg_end if seg_end > 0 else len(block)]

            def g(field, _s=seg):
                m = re.search(rf"{field}:\s*'((?:[^'\\]|\\.)*)'", _s)
                return m.group(1).replace("\\'", "'") if m else ''

            bullets = re.findall(r"'((?:[^'\\]|\\.)*)'", (re.search(r"bullets:\s*\[(.*?)\]", seg, re.S) or
                                                          type('x', (), {'group': lambda *a: ''})()).group(1))
            steps = re.findall(r"label:\s*'((?:[^'\\]|\\.)*)'", seg)
            scenes.append({
                'id': sm.group(1), 'type': sm.group(2),
                'say': g('say'), 'subtitle': g('subtitle'), 'keyword': g('keyword'),
                'bullets': bullets, 'steps': steps,
                'raw': seg,
            })
        chapters.append({'title': cm.group(1), 'scenes': scenes})
    return {'slug': one('slug'), 'title': one('title'), 'tagline': one('tagline'), 'chapters': chapters}


def estimate(chapters):
    """Rough duration in seconds."""
    t = LEAD_S + OUTRO_S
    for ch in chapters:
        for sc in ch['scenes']:
            words = len(sc['say'].split())
            dur = max(1.6, words / WORDS_PER_SEC)
            t += dur + SCENE_PAD_S + GAP_S
    return t


def to_markdown(data):
    chs = data['chapters']
    est = estimate(chs)
    words = sum(len(sc['say'].split()) for ch in chs for sc in ch['scenes'])
    beats = sum(len(ch['scenes']) for ch in chs)

    out = []
    out.append(f"<!-- kathareel script · {beats} scenes · ~{words} words · ~{est:.0f}s -->")
    out.append('')
    out.append('# Script review')
    out.append('')
    out.append(f"**Topic:** {data['title']}  ")
    out.append(f"**Tagline:** {data['tagline']}  ")
    out.append(f"**Length:** ~{int(est // 60)} min {int(est % 60)} sec  ")
    out.append(f"**Scenes:** {beats}")
    out.append('')
    out.append('---')
    out.append('')
    out.append('## Kaise edit karein')
    out.append('')
    out.append('| Line | Bhasha | Rule |')
    out.append('|---|---|---|')
    out.append('| `say:` | **Hindi, Devanagari** + English tech words | yahi bola jayega |')
    out.append('| `sub:` | **English only** | screen par caption (max ~48 chars) |')
    out.append('| `key:` | **English only** | bada word (max ~24 chars) |')
    out.append('')
    out.append('Rules: `say`, `sub`, `key` — teeno **ek hi line** par rakho. '
               'Scene add/remove karne ho to poora block copy karo. Naya scene `id:` unique rakho.')
    out.append('')
    out.append('Edit karke: `python3 scripts/script_review.py --from-script`')
    out.append('')
    out.append('---')

    for ci, ch in enumerate(chs, start=1):
        out.append('')
        out.append(f"## Part {ci} — {ch['title']}")
        out.append('')
        out.append(f"`chapter: {ch['title']}`")
        out.append('')
        for sc in ch['scenes']:
            secs = max(1.6, len(sc['say'].split()) / WORDS_PER_SEC)
            out.append(f"### {sc['id']} · {sc['type']} · ~{secs:.0f}s")
            out.append('')
            out.append(f"`scene: {sc['id']} {sc['type']}`")
            out.append('')
            out.append(f"say: {sc['say']}")
            out.append('')
            out.append(f"sub: {sc['subtitle']}")
            out.append('')
            if sc['keyword']:
                out.append(f"key: {sc['keyword']}")
                out.append('')
            if sc['bullets']:
                out.append(f"bullets: {' | '.join(sc['bullets'])}")
                out.append('')
            if sc['steps']:
                out.append(f"steps: {' | '.join(sc['steps'])}")
                out.append('')
    out.append('')
    out.append('---')
    out.append('')
    out.append(f"_Estimated length: ~{est:.0f}s · target badalna ho to narration lamba/chhota karo "
               f"(har extra 10 words ≈ 4s)._")
    out.append('')
    return '\n'.join(out)


# ---------------------------------------------------------------------------
# script.md  ->  content.ts
# ---------------------------------------------------------------------------
def from_markdown(text, data):
    """Patch the existing content.ts, keeping structure; replace say/sub/key and chapter titles."""
    chapters = []
    cur_ch = None
    cur_sc = None

    for raw in text.split('\n'):
        line = raw.strip()
        m_ch = re.match(r'^`chapter:\s*(.+?)`$', line)
        if m_ch:
            cur_ch = {'title': m_ch.group(1).strip(), 'scenes': []}
            chapters.append(cur_ch)
            cur_sc = None
            continue
        m_sc = re.match(r'^`scene:\s*(\S+)\s+(\S+?)`$', line)
        if m_sc:
            cur_sc = {'id': m_sc.group(1), 'type': m_sc.group(2), 'say': '', 'subtitle': '',
                      'keyword': '', 'bullets': [], 'steps': []}
            if cur_ch is None:
                cur_ch = {'title': f'Part {len(chapters) + 1}', 'scenes': []}
                chapters.append(cur_ch)
            cur_ch['scenes'].append(cur_sc)
            continue
        if cur_sc is None:
            continue
        if line.startswith('say:'):
            cur_sc['say'] = line[4:].strip()
        elif line.startswith('sub:'):
            cur_sc['subtitle'] = line[4:].strip()
        elif line.startswith('key:'):
            cur_sc['keyword'] = line[4:].strip()
        elif line.startswith('bullets:'):
            cur_sc['bullets'] = [b.strip() for b in line[8:].split('|') if b.strip()]
        elif line.startswith('steps:'):
            cur_sc['steps'] = [b.strip() for b in line[6:].split('|') if b.strip()]

    chapters = [c for c in chapters if c['scenes']]
    if not chapters:
        raise SystemExit('script.md me koi `chapter:` / `scene:` block nahi mila - format mat todo')

    # patch the source: for each scene id present in the file, swap its say/sub/key in place
    src = open(CONTENT, encoding='utf-8').read()
    patched = 0
    for ch in chapters:
        for sc in ch['scenes']:
            sid = re.escape(sc['id'])
            m = re.search(rf"(\{{\s*id:\s*'{sid}',\s*type:\s*'[^']*',)", src)
            if not m:
                continue
            block_start = m.start()
            block_end = src.find('id:', m.end())
            block_end = block_end if block_end > 0 else len(src)
            block = src[block_start:block_end]

            def put(field, value):
                nonlocal block
                esc = value.replace("\\", "\\\\").replace("'", "\\'")
                if re.search(rf"{field}:\s*'(?:[^'\\]|\\.)*'", block):
                    block = re.sub(rf"{field}:\s*'(?:[^'\\]|\\.)*'", f"{field}: '{esc}'", block, count=1)
                elif value:
                    # insert after the type field
                    anchor = re.search(r"type:\s*'[^']*',", block)
                    pos = anchor.end() if anchor else len(block)
                    block = block[:pos] + f"\n      {field}: '{esc}'," + block[pos:]

            put('say', sc['say'])
            put('subtitle', sc['subtitle'])
            if sc['keyword']:
                put('keyword', sc['keyword'])
            if sc['bullets']:
                esc = ', '.join("'" + b.replace("'", "\\'") + "'" for b in sc['bullets'])
                if re.search(r"bullets:\s*\[.*?\]", block, re.S):
                    block = re.sub(r"bullets:\s*\[.*?\]", f"bullets: [{esc}]", block, count=1, flags=re.S)
                else:
                    pos = block.rfind('\n    }')
                    block = block[:pos] + f"\n      bullets: [{esc}]," + block[pos:]
            if sc['steps']:
                esc = ', '.join("{label: '" + s.replace("'", "\\'") + "'}" for s in sc['steps'])
                if re.search(r"steps:\s*\[.*?\]", block, re.S):
                    block = re.sub(r"steps:\s*\[.*?\]", f"steps: [{esc}]", block, count=1, flags=re.S)
            src = src[:block_start] + block + src[block_end:]
            patched += 1

    # chapter titles: replace N-th chapter header (whitespace-tolerant)
    heads = list(re.finditer(r"(\{\s*\n?\s*)title:\s*'([^']*)'(,\s*\n?\s*scenes:\s*\[)", src))
    for m, new in zip(reversed(heads), reversed(chapters)):
        out = src[:m.start()] + m.group(1) + f"title: '{new['title']}'" + m.group(3) + src[m.end():]
        src = out

    open(CONTENT, 'w', encoding='utf-8').write(src)
    return patched, len(chapters)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--from-script', action='store_true', help='script.md ke edits content.ts me daalo')
    ap.add_argument('--minutes', type=float, default=None, help='target length (min) - kitna kam/zyada hai batao')
    ap.add_argument('--out', default=SCRIPT)
    a = ap.parse_args()

    if a.from_script:
        if not os.path.exists(SCRIPT):
            raise SystemExit('script.md nahi mila - pehle bina --from-script chalao')
        data = parse_content()
        patched, nch = from_markdown(open(SCRIPT, encoding='utf-8').read(), data)
        print(f'{patched} scenes update hue, {nch} chapters')
        fresh = parse_content()
        print(f'naya estimate: {estimate(fresh["chapters"]):.0f}s')
        print('\nab ye chalao:')
        print('  python3 scripts/check_content.py')
        print('  python3 scripts/build_voice.py')
        return 0

    data = parse_content()
    md = to_markdown(data)
    open(a.out, 'w', encoding='utf-8').write(md)

    est = estimate(data['chapters'])
    words = sum(len(sc['say'].split()) for ch in data['chapters'] for sc in ch['scenes'])
    print(f'script likh diya : {a.out}')
    print(f'  scenes         : {sum(len(c["scenes"]) for c in data["chapters"])}')
    print(f'  words          : {words}')
    print(f'  estimate       : ~{int(est // 60)}m {int(est % 60)}s')

    if a.minutes:
        target = a.minutes * 60
        diff = est - target
        need_words = int(round(diff / 60 * WORDS_PER_SEC * 60)) if abs(diff) > 5 else 0
        print(f'  target         : {a.minutes:.1f} min')
        if abs(diff) <= 5:
            print('  ✓ target par hai')
        elif diff > 0:
            print(f'  ⚠ {diff:.0f}s ZYADA hai -> ~{int(-need_words)} words hatao')
        else:
            print(f'  ⚠ {-diff:.0f}s KAM hai -> ~{need_words} words add karo')

    print()
    print('Ab:')
    print(f'  1. {os.path.relpath(a.out, ROOT)} kholo, jo badalna hai badlo')
    print('  2. python3 scripts/script_review.py --from-script     # edits wapas code me')
    print('  3. python3 scripts/check_content.py')
    print('  4. python3 scripts/build_voice.py')
    print('  5. npx remotion render src/index.ts Explainer out/video.mp4 --concurrency=2')
    return 0


if __name__ == '__main__':
    sys.exit(main())
