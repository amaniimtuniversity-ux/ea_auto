#!/usr/bin/env python3
"""
kathareel — content checker (by raghv)

Video banane se pehle ye chalao:  python3 scripts/check_content.py

Kya check karta hai:
  1. `say` (narration) Devanagari me hai ya nahi  -> warna Hindi voice galat bolti hai
  2. `subtitle` / `keyword` / steps me Hindi/Devanagari to nahi -> board English-only hai
  3. `say` bahut lamba to nahi (max ~35 words / 25 sec per beat)
  4. subtitle bahut lamba to nahi (max ~48 chars)
  5. scene type valid hai, id duplicate to nahi
  6. chapters 2-5 ke beech, har chapter me kam se kam 1 scene
  7. theme values valid hain (accent / background / layout / transition)

Exit code 0 = sab theek, 1 = kuch fix karna hai.
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONTENT = os.path.join(ROOT, 'src', 'content.ts')

DEVANAGARI = re.compile(r'[\u0900-\u097f]')
LATIN = re.compile(r'[A-Za-z]')
VALID_TYPES = {'hook', 'concept', 'steps', 'compare', 'number', 'recap'}

# web/ aur src/ ke saath same list — warna UI me chuni cheez render par gayab ho jati hai
ACCENTS = {'orange', 'blue', 'green', 'violet', 'pink', 'amber', 'red', 'teal'}
BACKGROUNDS = {'glow', 'grid', 'dots', 'plain', 'mesh'}
TRANSITIONS = {'fade', 'slide', 'pop', 'zoom', 'wipe'}
LAYOUTS = {
    'hook': {'hook', 'quote', 'bigword'},
    'concept': {'concept', 'bullets', 'cards', 'two-col'},
    'steps': {'steps', 'timeline', 'numbered'},
    'compare': {'compare', 'versus', 'table'},
    'number': {'number', 'stat'},
    'recap': {'recap', 'checklist', 'takeaways'},
}

MAX_SAY_WORDS = 35
MAX_SUBTITLE_CHARS = 48
MAX_KEYWORD_CHARS = 24


def load():
    src = open(CONTENT, encoding='utf-8').read()
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

            def g(field):
                m = re.search(rf"{field}:\s*'((?:[^'\\]|\\.)*)'", seg)
                return m.group(1).replace("\\'", "'") if m else ''

            scenes.append({'id': sm.group(1), 'type': sm.group(2), 'say': g('say'),
                           'subtitle': g('subtitle'), 'keyword': g('keyword'),
                           'layout': g('layout'), 'accent': g('accent'),
                           'transition': g('transition')})
        chapters.append({'title': cm.group(1), 'scenes': scenes})
    return chapters


def main():
    if not os.path.exists(CONTENT):
        print('content.ts nahi mila')
        return 1
    src = open(CONTENT, encoding='utf-8').read()
    chapters = load()
    errors, warnings = [], []
    seen_ids = set()

    # poore video ka theme
    m_acc = re.search(r"^  accent:\s*'([^']*)'", src, re.M)
    m_bg = re.search(r"^  background:\s*'([^']*)'", src, re.M)
    if m_bg and m_bg.group(1) not in BACKGROUNDS:
        errors.append(f"background '{m_bg.group(1)}' valid nahi (chuno: {', '.join(sorted(BACKGROUNDS))})")
    if m_acc and m_acc.group(1) not in ACCENTS:
        errors.append(f"accent '{m_acc.group(1)}' valid nahi (chuno: {', '.join(sorted(ACCENTS))})")

    for ci, ch in enumerate(chapters, start=1):
        title = ch['title']
        if not title.strip():
            errors.append(f'chapter {ci}: title khaali hai')
        if DEVANAGARI.search(title):
            errors.append(f'chapter {ci} "{title}": title English hona chahiye (board rule)')
        if len(title) > 14:
            warnings.append(f'chapter {ci} "{title}": title lamba hai ({len(title)} chars) - progress bar me squeeze hoga')
        if not ch['scenes']:
            errors.append(f'chapter {ci} "{title}": koi scene nahi')

        for sc in ch['scenes']:
            sid = sc['id']
            where = f'[{sid}]'
            if sid in seen_ids:
                errors.append(f'{where} duplicate id')
            seen_ids.add(sid)

            if sc['type'] not in VALID_TYPES:
                errors.append(f'{where} type "{sc["type"]}" galat hai (allowed: {", ".join(sorted(VALID_TYPES))})')

            say = sc['say'].strip()
            if not say:
                errors.append(f'{where} say khaali hai - voice nahi banegi')
            else:
                if not DEVANAGARI.search(say):
                    errors.append(f'{where} say me Devanagari nahi hai -> Hindi voice galat bolegi. '
                                  f'Narration Devanagari me likho (English tech words Latin me chalenge).')
                words = len(say.split())
                if words > MAX_SAY_WORDS:
                    warnings.append(f'{where} say lamba hai (~{words} words, {words/2.6:.0f}s) - ek beat me ek idea rakho')

            sub = sc['subtitle'].strip()
            if not sub:
                errors.append(f'{where} subtitle khaali hai (screen par kuch nahi dikhega)')
            else:
                if DEVANAGARI.search(sub):
                    errors.append(f'{where} subtitle me Hindi hai -> board English-only hai')
                if len(sub) > MAX_SUBTITLE_CHARS:
                    warnings.append(f'{where} subtitle {len(sub)} chars - {MAX_SUBTITLE_CHARS} se kam rakho')
                if not LATIN.search(sub):
                    warnings.append(f'{where} subtitle me English nahi hai')

            kw = sc['keyword'].strip()
            if kw:
                if DEVANAGARI.search(kw):
                    errors.append(f'{where} keyword me Hindi hai -> board English-only hai')
                if len(kw) > MAX_KEYWORD_CHARS:
                    warnings.append(f'{where} keyword {len(kw)} chars - chhota rakho')

            if sc.get('layout') and sc['layout'] not in LAYOUTS.get(sc['type'], set()):
                errors.append(f"{where} layout '{sc['layout']}' type '{sc['type']}' ke liye valid nahi "
                              f"(chuno: {', '.join(sorted(LAYOUTS.get(sc['type'], [])))})")
            if sc.get('accent') and sc['accent'] not in ACCENTS:
                errors.append(f"{where} accent '{sc['accent']}' valid nahi")
            if sc.get('transition') and sc['transition'] not in TRANSITIONS:
                errors.append(f"{where} transition '{sc['transition']}' valid nahi")

            if sc['type'] == 'steps' and 'steps:' not in src:
                warnings.append(f'{where} type=steps hai par steps[] nahi mila')

    if len(chapters) < 2:
        warnings.append('sirf 1 chapter hai - progress bar me parts nahi dikhenge')
    if len(chapters) > 5:
        warnings.append(f'{len(chapters)} chapters - 2-5 better rehta hai (progress bar me jagah kam)')

    total_beats = sum(len(c['scenes']) for c in chapters)
    est = total_beats * 12 / 2.6  # ~12 words per beat / 2.6 words per second

    print(f'chapters : {len(chapters)}')
    print(f'beats    : {total_beats}')
    print(f'est len  : ~{est/60:.1f} min (rough - asli length voice banane ke baad milegi)')
    print()

    for w in warnings:
        print(f'  ⚠  {w}')
    for e in errors:
        print(f'  ✗  {e}')

    if errors:
        print(f'\n{len(errors)} error(s), {len(warnings)} warning(s) - pehle errors fix karo.')
        return 1
    if warnings:
        print(f'\n{len(warnings)} warning(s), koi error nahi. Chaho to aise hi aage badho.')
        return 0
    print('✅ sab theek hai - ab:  python3 scripts/build_voice.py')
    return 0


if __name__ == '__main__':
    sys.exit(main())
