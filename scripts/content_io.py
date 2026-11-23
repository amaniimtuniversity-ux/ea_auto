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
def _pad_say(base, fillers, per_beat_s, max_words=34, wps=WORDS_PER_SEC):
    """Hint ko target duration tak lamba karo — par ek beat ki word limit ke andar."""
    need = min(max_words, max(6, round(per_beat_s * wps * 0.92)))
    text = base
    for f in fillers:
        if len(text.split()) >= need:
            break
        if len((text + f).split()) <= max_words:
            text += f
    return text


def skeleton(topic, minutes, title=None, tagline=None):
    slug = re.sub(r'[^a-z0-9-]+', '-', (topic or 'video').lower()).strip('-') or 'video'
    title = title or (topic or 'New Video')
    tagline = tagline or 'In Hindi, step by step'

    # target duration se beats nikalo. Har placeholder beat ~14s ka hota hai, par
    # asli narration 22-34s ki honi chahiye — isliye beats kam rakhte hain aur
    # har beat ka hint utna lamba likhte hain ki total target ke aas-paas aaye.
    target_s = max(30.0, minutes * 60)
    beats = max(4, min(40, round(target_s / 14.2)))     # ~14s per beat (34 words + pad)
    parts = max(2, min(7, round(beats / 4)))

    # har beat ka hint: Devanagari Hindi + English tech words (jaise asli script me).
    # Lamba hissa tab jodte hain jab video lambi ho — taaki placeholder ka duration
    # bhi target ke aas-paas rahe.
    per_beat_s = target_s / max(1, beats)

    # in fillers se hint ko target duration tak lamba karte hain — poori Devanagari,
    # thoda thoda karke, taaki ek beat ki limit (~35 words) na toote.
    FILL = {
        'hook': [' यहाँ एक छोटा real example दो — जो viewer के रोज़ के काम से जुड़ा हो।',
                 ' फिर बोलो कि इस video के बाद वो क्या कर पाएगा।'],
        'concept': [' यहाँ definition को अपने शब्दों में दोबारा बोलो।',
                    ' एक आसान example से समझाओ, बिना jargon के।',
                    ' एक common गलतफहमी भी बताओ।'],
        'steps': [' हर step में बोलो कि input क्या जाता है।',
                  ' और output क्या आता है, एक line में।',
                  ' आखिर में बताओ कौन सा step सबसे ज़रूरी है।'],
        'number': [' Number के बाद बोलो कि ये बड़ा है या छोटा।',
                   ' और ये number कहाँ से आया, ताकि भरोसा बने।'],
        'compare': [' दोनों तरफ़ का एक फ़ायदा बोलो।',
                    ' और एक नुकसान भी साफ़ शब्दों में।',
                    ' आखिर में बताओ कब कौन सा option चुनना चाहिए।'],
        'recap': [' तीन बातें एक-एक line में दोहराओ।',
                  ' और एक छोटा homework दे दो viewer को।'],
    }

    say_hints = {
        'hook': ('देखो भाई, यहाँ एक आम situation है। Yahan likho ki viewer ko kya problem hoti hai, '
                 'aur ye topic usse kaise solve karta hai.'),
        'concept': ('अब मुख्य बात। Yahan likho ki {t} asal me hai kya — ek aasan example ke saath, '
                    'bina jargon ke.'),
        'steps': ('अब step by step चलो। Pehle ye hota hai, phir ye, phir ye — har step ek line me '
                  'samjhao.'),
        'number': 'Yahan ek number batao jo poori baat saaf kar de — kitna, kitne percent, kitne log.',
        'compare': 'Farq saaf hai. Ek taraf ye hota hai, doosri taraf ye — dono ko saath rakho.',
        'recap': 'Bas itna yaad rakho. Teen baatein, aur kaam khatam.',
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
                'say': _pad_say(say_hints[t].format(t=title), FILL[t], per_beat_s),
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
