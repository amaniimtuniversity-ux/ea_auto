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

# Render layouts — src/components/Scenes.tsx me har naam ka ek component hai.
# `type` = content ka matlab (check_content isse dekhta hai),
# `layout` = screen par kaise dikhe. Default: type ke hisaab se.
LAYOUTS = {
    'hook': ['hook', 'quote', 'bigword'],
    'concept': ['concept', 'bullets', 'cards', 'two-col'],
    'steps': ['steps', 'timeline', 'numbered'],
    'compare': ['compare', 'versus', 'table'],
    'number': ['number', 'stat'],
    'recap': ['recap', 'checklist', 'takeaways'],
}
DEFAULT_LAYOUT = {'hook': 'hook', 'concept': 'concept', 'steps': 'steps',
                  'compare': 'compare', 'number': 'number', 'recap': 'recap'}
ALL_LAYOUTS = sorted({l for v in LAYOUTS.values() for l in v})

# Accent colours — content.ts ke `accent` field se (per-video ya per-scene).
ACCENTS = {
    'orange': '#FF6B2C', 'blue': '#3BC9F5', 'green': '#5BE58B',
    'violet': '#A78BFA', 'pink': '#F472B6', 'amber': '#FBBF24',
    'red': '#FF4D5E', 'teal': '#2DD4BF',
}
# Background styles
BACKGROUNDS = ['glow', 'grid', 'dots', 'plain', 'mesh']
# Scene transition (entry animation)
TRANSITIONS = ['fade', 'slide', 'pop', 'zoom', 'wipe']
DEFAULT_TRANSITION = 'fade'


def clean_accent(name, fallback=None):
    """Sirf valid accent names. Galat naam render todta hai, isliye yahan filter."""
    n = (name or '').strip().lower()
    return n if n in ACCENTS else fallback


def clean_background(name):
    n = (name or '').strip().lower()
    return n if n in BACKGROUNDS else 'glow'


def clean_transition(name):
    n = (name or '').strip().lower()
    return n if n in TRANSITIONS else DEFAULT_TRANSITION

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
    data['accent'] = top('accent') or 'orange'
    data['background'] = top('background') or 'glow'

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
                'note': g('note'),
                'layout': g('layout') or DEFAULT_LAYOUT.get(sm.group(2), 'concept'),
                'accent': g('accent') or '',
                'transition': g('transition') or '',
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
        '  /** Screen layout — src/components/Scenes.tsx me har naam ka component hai. */',
        '  layout?: string;',
        '  /** Scene ka apna accent (video ke accent ko override karta hai). */',
        '  accent?: string;',
        '  /** Entry animation: fade | slide | pop | zoom | wipe */',
        '  transition?: string;',
        '  /** Definition / explanation card jo screen par popup ki tarah aata hai. */',
        '  note?: string;',
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
        '  /** Poori video ka accent: orange | blue | green | violet | pink | amber | red | teal */',
        '  accent?: string;',
        '  /** Background: glow | grid | dots | plain | mesh */',
        '  background?: string;',
        '  chapters: Chapter[];',
        '};',
        '',
        'export const CONTENT: VideoContent = {',
        f"  slug: '{_esc(slug)}',",
        f"  title: '{_esc(data.get('title', ''))}',",
        f"  tagline: '{_esc(data.get('tagline', ''))}',",
        f"  accent: '{_esc(clean_accent(data.get('accent'), 'orange'))}',",
        f"  background: '{_esc(clean_background(data.get('background')))}',",
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
            lay = sc.get('layout')
            if lay and lay != DEFAULT_LAYOUT.get(sc.get('type'), 'concept'):
                lines.append(f"          layout: '{_esc(lay)}',")
            acc = clean_accent(sc.get('accent'))
            if acc:
                lines.append(f"          accent: '{acc}',")
            if sc.get('transition'):
                lines.append(f"          transition: '{clean_transition(sc.get('transition'))}',")
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
            if sc.get('note'):
                lines.append(f"          note: '{_esc(sc['note'])}',")
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
    # title hamesha clean: 'BAS' jaisa all-caps ya khaali na rahe
    title = (title or topic or 'New Video').strip()
    if title.isupper() or title.islower():
        title = title.title()
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
        'hook': [' रोज़ की ज़िंदगी से एक छोटा उदाहरण ले लो, तो बात तुरंत समझ आ जाती है।',
                 ' और इस video के बाद तुम यही काम खुद कर पाओगे।'],
        'concept': [' definition को अपने शब्दों में दोहराओ, तो याद रहती है।',
                    ' एक आसान उदाहरण से बात पक्की हो जाती है।',
                    ' और एक आम गलतफ़हमी भी दूर हो जाती है।'],
        'steps': [' हर step में यह भी देखो कि अंदर क्या जाता है और बाहर क्या आता है।',
                  ' आख़िर में सबसे ज़रूरी step पहचान लो, वही सबसे ज़्यादा मायने रखता है।'],
        'number': [' यह number बड़ा है या छोटा, यह समझना भी ज़रूरी है।',
                   ' और यह number कहाँ से आया, यह जानने से भरोसा बनता है।'],
        'compare': [' दोनों तरफ़ का एक फ़ायदा और एक नुकसान साफ़ शब्दों में देखो।',
                    ' आख़िर में तय करो कि कब कौन सा तरीका चुनना चाहिए।'],
        'recap': [' तीन बातें एक-एक line में दोहरा लो, तो सब पक्का हो जाता है।',
                  ' और एक छोटा काम दे देता हूँ, जो तुम आज ही कर सकते हो।'],
    }

    say_hints = {
        'hook': ('देखो भाई, यहाँ एक आम situation है। ज़्यादातर लोग इस problem से रोज़ गुज़रते हैं, '
                 'और उन्हें पता भी नहीं होता कि इसका solution इतना आसान है।'),
        'concept': ('अब मुख्य बात समझो। {t} का मतलब है कि काम को छोटे-छोटे हिस्सों में बाँट देना, '
                    'और हर हिस्से को एक-एक करके सॉल्व करना।'),
        'steps': ('अब step by step चलो। पहले डेटा इकट्ठा होता है, फिर उसे साफ़ किया जाता है, '
                  'और आख़िर में model उससे सीखता है।'),
        'number': ('अब एक number देखो जो पूरी बात साफ़ कर देगा। नब्बे फ़ीसदी से ज़्यादा लोग '
                   'यही गलती करते हैं, और वजह बहुत छोटी है।'),
        'compare': ('फ़र्क साफ़ है। एक तरफ़ पुराना तरीका है जो धीमा है, दूसरी तरफ़ नया तरीका '
                    'जो तेज़ है — दोनों को साथ रखकर देखो।'),
        'recap': ('बस इतना याद रखो। समस्या क्या थी, हल कैसे निकला, और आगे क्या करना है। '
                  'तीन बातें, और काम ख़त्म।'),
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
                'layout': DEFAULT_LAYOUT.get(t, 'concept'),
                'accent': '', 'transition': '',
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

    return {'slug': slug, 'title': title, 'tagline': tagline,
            'accent': 'orange', 'background': 'glow', 'chapters': chapters}
