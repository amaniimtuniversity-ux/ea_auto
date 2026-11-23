#!/usr/bin/env python3
"""
kathareel — content.ts <-> JSON (by raghv)

Ek hi jagah se content.ts padho aur likho, taaki web UI aur CLI dono same
format par kaam karein. Server isse use karta hai.

  data = load()
  data['chapters'][0]['scenes'][0]['subtitle'] = 'New caption'
  save(data)
"""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONTENT = os.path.join(ROOT, 'src', 'content.ts')

TYPES = ['hook', 'concept', 'steps', 'compare', 'number', 'recap']

# pacing — build_voice.py se match
WORDS_PER_SEC = 2.6
LEAD_S = 3.5
SCENE_PAD_S = 0.9
GAP_S = 0.4
OUTRO_S = 3.7


def _unesc(s):
    return s.replace("\\'", "'").replace('\\\\', '\\')


def _esc(s):
    return (s or '').replace('\\', '\\\\').replace("'", "\\'")


def empty_content(slug='video', title='New Video', tagline='In Hindi, step by step'):
    return {'slug': slug, 'title': title, 'tagline': tagline, 'chapters': []}


def load(path=CONTENT):
    if not os.path.exists(path):
        return empty_content()
    src = open(path, encoding='utf-8').read()

    def top(field):
        m = re.search(rf"\n  {field}:\s*'((?:[^'\\]|\\.)*)'", src)
        return _unesc(m.group(1)) if m else ''

    data = empty_content(top('slug') or 'video', top('title'), top('tagline'))

    for cm in re.finditer(r"\{\s*\n\s*title:\s*'((?:[^'\\]|\\.)*)',\s*\n\s*scenes:\s*\[", src):
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
        for sm in re.finditer(r"\{\s*\n\s*id:\s*'([^']*)',\s*\n?\s*type:\s*'([^']*)'", block):
            nxt = block.find("id:", sm.end())
            seg = block[sm.start(): nxt if nxt > 0 else len(block)]

            def g(field, _s=seg):
                m = re.search(rf"{field}:\s*'((?:[^'\\]|\\.)*)'", _s)
                return _unesc(m.group(1)) if m else ''

            def arr(field):
                m = re.search(rf"{field}:\s*\[(.*?)\]", seg, re.S)
                return [_unesc(x) for x in re.findall(r"'((?:[^'\\]|\\.)*)'", m.group(1))] if m else []

            steps = []
            msteps = re.search(r"steps:\s*\[(.*?)\]\s*,?\s*\n\s*\}", seg, re.S)
            if msteps:
                for lab, note in re.findall(r"label:\s*'((?:[^'\\]|\\.)*)'(?:,\s*note:\s*'((?:[^'\\]|\\.)*)')?",
                                            msteps.group(1)):
                    steps.append({'label': _unesc(lab), 'note': _unesc(note) if note else ''})

            def col(name):
                m = re.search(rf"{name}:\s*\{{\s*label:\s*'((?:[^'\\]|\\.)*)',\s*points:\s*\[(.*?)\]\s*\}}",
                              seg, re.S)
                if not m:
                    return None
                return {'label': _unesc(m.group(1)),
                        'points': [_unesc(x) for x in re.findall(r"'((?:[^'\\]|\\.)*)'", m.group(2))]}

            scenes.append({
                'id': sm.group(1),
                'type': sm.group(2),
                'say': g('say'),
                'subtitle': g('subtitle'),
                'keyword': g('keyword'),
                'bullets': arr('bullets'),
                'steps': steps,
                'left': col('left'),
                'right': col('right'),
                'value': g('value'),
                'unit': g('unit'),
                'caption': g('caption'),
            })
        data['chapters'].append({'title': _unesc(cm.group(1)), 'scenes': scenes})
    return data


def estimate(chapters):
    t = LEAD_S + OUTRO_S
    for ch in chapters:
        for sc in ch.get('scenes', []):
            words = len((sc.get('say') or '').split())
            t += max(1.6, words / WORDS_PER_SEC) + SCENE_PAD_S + GAP_S
    return round(t, 1)


def save(data, path=CONTENT):
    """Poora content.ts dobara likhta hai (patch nahi) — isliye format kabhi tootta nahi."""
    slug = data.get('slug') or 'video'
    lines = [
        '/**',
        ' * ============================================================',
        ' *  kathareel — content file (by raghv)',
        f' *  Topic: {data.get("title", "")}',
        ' * ============================================================',
        ' *',
        ' *  `say`      = jo bola jayega -> HINDI, DEVANAGARI me (English tech words Latin me chalenge)',
        ' *  `subtitle` = screen par line -> ENGLISH ONLY, chhota',
        ' *  `keyword`  = bada word       -> ENGLISH ONLY',
        ' *',
        ' *  Ye file web UI se generate hui hai (web/server.py).',
        ' */',
        '',
        "export type SceneType = 'hook' | 'concept' | 'steps' | 'compare' | 'number' | 'recap';",
        '',
        'export type Scene = {',
        '  id: string;',
        '  type: SceneType;',
        '  say: string;',
        '  subtitle: string;',
        '  keyword?: string;',
        '  bullets?: string[];',
        '  steps?: {label: string; note?: string}[];',
        '  left?: {label: string; points: string[]};',
        '  right?: {label: string; points: string[]};',
        '  value?: string;',
        '  unit?: string;',
        '  caption?: string;',
        '};',
        '',
        'export type Chapter = {',
        '  title: string;',
        '  scenes: Scene[];',
        '};',
        '',
        'export type VideoContent = {',
        '  slug: string;',
        '  title: string;',
        '  tagline: string;',
        '  chapters: Chapter[];',
        '};',
        '',
        'export const CONTENT: VideoContent = {',
        f"  slug: '{_esc(slug)}',",
        f"  title: '{_esc(data.get('title', ''))}',",
        f"  tagline: '{_esc(data.get('tagline', ''))}',",
        '  chapters: [',
    ]

    for ch in data.get('chapters', []):
        lines.append('    {')
        lines.append(f"      title: '{_esc(ch.get('title', ''))}',")
        lines.append('      scenes: [')
        for sc in ch.get('scenes', []):
            lines.append('        {')
            lines.append(f"          id: '{_esc(sc.get('id', ''))}',")
            lines.append(f"          type: '{sc.get('type', 'concept')}',")
            lines.append(f"          say: '{_esc(sc.get('say', ''))}',")
            lines.append(f"          subtitle: '{_esc(sc.get('subtitle', ''))}',")
            if sc.get('keyword'):
                lines.append(f"          keyword: '{_esc(sc['keyword'])}',")
            if sc.get('bullets'):
                bl = ', '.join(f"'{_esc(b)}'" for b in sc['bullets'])
                lines.append(f'          bullets: [{bl}],')
            if sc.get('steps'):
                st = ', '.join(
                    "{label: '%s'%s}" % (_esc(s.get('label', '')),
                                         f", note: '{_esc(s['note'])}'" if s.get('note') else '')
                    for s in sc['steps'])
                lines.append(f'          steps: [{st}],')
            for side in ('left', 'right'):
                d = sc.get(side)
                if d:
                    pts = ', '.join(f"'{_esc(p)}'" for p in d.get('points', []))
                    lines.append(f"          {side}: {{label: '{_esc(d.get('label', ''))}', points: [{pts}]}},")
            if sc.get('value'):
                lines.append(f"          value: '{_esc(sc['value'])}',")
            if sc.get('unit'):
                lines.append(f"          unit: '{_esc(sc['unit'])}',")
            if sc.get('caption'):
                lines.append(f"          caption: '{_esc(sc['caption'])}',")
            lines.append('        },')
        lines.append('      ],')
        lines.append('    },')
    lines.append('  ],')
    lines.append('};')
    lines.append('')
    lines.append("export const BUILT_BY = 'built by raghv';")
    lines.append('')

    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, 'w', encoding='utf-8').write('\n'.join(lines))
    return path


# ---------------------------------------------------------------------------
# skeleton generator: topic + minutes -> chapter/beat structure
# ---------------------------------------------------------------------------
def skeleton(topic, minutes, title=None, tagline=None):
    slug = re.sub(r'[^a-z0-9-]+', '-', (topic or 'video').lower()).strip('-') or 'video'
    title = title or (topic or 'New Video')
    tagline = tagline or 'In Hindi, step by step'

    beats = max(4, min(16, round(minutes * 60 / 14)))  # ~14s per beat
    parts = max(2, min(5, round(minutes / 1.2)))

    say_hints = {
        'hook': 'देखो भाई, यहाँ एक आम situation है। यहाँ likho ki viewer ko kya problem पता है, और ये topic उसे क्यों solve करता है।',
        'concept': 'अब मुख्य बात। यहाँ likho ki {t} असल में है क्या, एक आसान example के साथ।',
        'steps': 'अब step by step देखो। पहले ये होता है, फिर ये, फिर ये।',
        'number': 'यहाँ एक number बताओ जो बात साफ कर दे।',
        'compare': 'फर्क साफ है। एक तरफ ये, दूसरी तरफ ये।',
        'recap': 'बस इतना याद रखो। तीन बातें, और काम खत्म।',
    }

    # ONE teaching arc for the whole video, then split across parts:
    #   hook -> concept -> steps -> number -> compare -> recap
    # (short videos get a trimmed arc: hook -> concept -> recap)
    arc_pool = ['concept', 'steps', 'number', 'compare', 'concept', 'steps']
    types = ['hook'] + [arc_pool[i % len(arc_pool)] for i in range(max(0, beats - 2))] + ['recap']

    chapters = []
    made = 0
    per_part = [max(1, beats // parts + (1 if i < beats % parts else 0)) for i in range(parts)]
    for p, n_in in enumerate(per_part):
        ch = {'title': f'Part {p + 1}', 'scenes': []}
        for t in types[made:made + n_in]:
            made += 1
            sc = {
                'id': f's{made}',
                'type': t,
                'say': say_hints[t].format(t=title),
                'subtitle': {'hook': 'The problem', 'concept': title, 'steps': 'Step by step',
                             'number': 'One number', 'compare': 'The difference',
                             'recap': 'Quick recap'}[t],
                'keyword': {'hook': 'Problem', 'concept': title, 'steps': 'How it works',
                            'number': 'By the numbers', 'compare': 'Compare',
                            'recap': 'Remember'}[t],
                'bullets': [], 'steps': [], 'left': None, 'right': None,
                'value': '', 'unit': '', 'caption': '',
            }
            if t == 'steps':
                sc['steps'] = [{'label': 'STEP ONE', 'note': 'what happens'},
                               {'label': 'STEP TWO', 'note': 'what happens'},
                               {'label': 'STEP THREE', 'note': 'what happens'}]
            if t == 'compare':
                sc['left'] = {'label': 'WITHOUT', 'points': ['point one', 'point two']}
                sc['right'] = {'label': 'WITH', 'points': ['point one', 'point two']}
            if t == 'number':
                sc['value'], sc['unit'], sc['caption'] = '3', 'items', 'what the number means'
            if t in ('hook', 'recap', 'concept'):
                sc['bullets'] = ['first point', 'second point', 'third point']
            ch['scenes'].append(sc)
        if ch['scenes']:
            chapters.append(ch)

    return {'slug': slug, 'title': title, 'tagline': tagline, 'chapters': chapters}
