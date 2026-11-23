#!/usr/bin/env python3
"""
kathareel — topic se naya video (by raghv)

Do tarah se use kar sakte ho:

1) Skeleton banao (recommended — phir narration khud likho):
       python3 scripts/new_topic.py --topic "Photosynthesis" --title "Photosynthesis"

   Ye src/content.ts ki copy banata hai jisme tumhare topic ka naam bhara hua hai
   aur har scene ke saath Hindi me likha hai ki kya likhna hai.

2) Seedha Hindi narration bhi do (behtar quality ke liye, khud likho):
       python3 scripts/new_topic.py --topic "Photosynthesis" \
           --say "देखो भाई, पौधा अपना खाना खुद बनाता है|ये process photosynthesis कहलाती है"

   Har `--say` ek scene banta hai, `|` se subtitle ka break. Teeno field aap bhar sakte ho:
       --say "हिंदी line" --subtitle "English caption" --keyword "Keyword"

Baad me hamesha:  python3 scripts/check_content.py && python3 scripts/build_voice.py

Options:
  --topic      slug/folder name (English, chhota: photosynthesis, rag, mysql-joins)
  --title      opening card ka English title
  --tagline    opening card ki English one-line
  --parts      kitne chapters (default 3)
  --out        default: src/content.ts (backup purani file ka .bak banega)
  --force      bina poochhe overwrite
"""
import argparse
import os
import re
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

TEMPLATE_HEADER = """/**
 * ============================================================
 *  kathareel — content file (by raghv)
 *  Topic: {title}
 * ============================================================
 *
 *  `say`      = jo bola jayega  -> HINDI, DEVANAGARI me likho (English tech words Latin me chalenge)
 *  `subtitle` = screen par line -> ENGLISH ONLY, chhota (max ~48 chars)
 *  `keyword`  = bada word       -> ENGLISH ONLY
 *
 *  Scene types: hook | concept | steps | compare | number | recap
 *  Check:  python3 scripts/check_content.py
 *  Voice:  python3 scripts/build_voice.py
 */

export type SceneType = 'hook' | 'concept' | 'steps' | 'compare' | 'number' | 'recap';

export type Scene = {{
  id: string;
  type: SceneType;
  say: string;
  subtitle: string;
  keyword?: string;
  bullets?: string[];
  steps?: {{label: string; note?: string}}[];
  left?: {{label: string; points: string[]}};
  right?: {{label: string; points: string[]}};
  value?: string;
  unit?: string;
  caption?: string;
}};

export type Chapter = {{
  title: string;
  scenes: Scene[];
}};

export type VideoContent = {{
  slug: string;
  title: string;
  tagline: string;
  chapters: Chapter[];
}};

export const CONTENT: VideoContent = {{
  slug: '{slug}',
  title: '{title}',
  tagline: '{tagline}',
  chapters: [
"""

TEMPLATE_FOOTER = """  ],
};

export const BUILT_BY = 'built by raghv';
"""


def scene_block(sid, stype, say, subtitle, keyword, extra=''):
    say = say.replace("'", "\\'")
    subtitle = subtitle.replace("'", "\\'")
    kw = f"\n          keyword: '{keyword}'," if keyword else ''
    return f"""    {{
      id: '{sid}',
      type: '{stype}',{kw}
      say: '{say}',
      subtitle: '{subtitle}',{extra}
    }},
"""


SKELETON = {
    'hook': (
        "देखो भाई, यहाँ एक आम situation है। यहाँ likho ki viewer ko kya problem पता है, "
        "और ये topic उसे क्यों solve करता है।",
        "The problem in one line",
        "Problem",
        ""),
    'concept': (
        "अब मुख्य बात। यहाँ likho ki {title} असल में है क्या, एक आसान example के साथ।",
        "The core idea",
        "{title}",
        ""),
    'steps': (
        "अब step by step देखो। पहले ये होता है, फिर ये, फिर ये।",
        "Step by step",
        "How it works",
        "\n      steps: [{label: 'STEP ONE', note: 'what happens'}, {label: 'STEP TWO', note: 'what happens'}, "
        "{label: 'STEP THREE', note: 'what happens'}],"),
    'compare': (
        "फर्क साफ है। एक तरफ ये, दूसरी तरफ ये।",
        "The difference",
        "Compare",
        "\n      left: {label: 'WITHOUT', points: ['point one', 'point two']},"
        "\n      right: {label: 'WITH', points: ['point one', 'point two']},"),
    'number': (
        "यहाँ एक number बताओ जो बात साफ कर दे।",
        "One number",
        "By the numbers",
        "\n      value: '3',\n      unit: 'items',\n      caption: 'what the number means',"),
    'recap': (
        "बस इतना याद रखो। तीन बातें, और काम खत्म।",
        "Quick recap",
        "Remember",
        "\n      bullets: ['first idea', 'second idea', 'third idea'],"),
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--topic', required=True)
    ap.add_argument('--title', default=None)
    ap.add_argument('--tagline', default='In Hindi, step by step')
    ap.add_argument('--parts', type=int, default=3)
    ap.add_argument('--say', action='append', default=[], help='Hindi narration (repeatable, one per scene)')
    ap.add_argument('--subtitle', action='append', default=[])
    ap.add_argument('--keyword', action='append', default=[])
    ap.add_argument('--out', default=os.path.join(ROOT, 'src', 'content.ts'))
    ap.add_argument('--force', action='store_true')
    a = ap.parse_args()

    slug = re.sub(r'[^a-z0-9-]+', '-', a.topic.lower()).strip('-') or 'video'
    title = a.title or a.topic

    if os.path.exists(a.out) and not a.force:
        bak = a.out + '.bak'
        shutil.copy(a.out, bak)
        print(f'purani file backup: {bak}')

    if a.say:
        # narration provided -> build scenes straight from it
        from collections import OrderedDict
        parts = a.parts
        n = len(a.say)
        per = max(1, -(-n // parts))
        body = []
        idx = 0
        for p in range(parts):
            chunk = a.say[p * per:(p + 1) * per]
            if not chunk:
                continue
            body.append(f"    {{\n      title: 'Part {p + 1}',\n      scenes: [\n")
            for k, line in enumerate(chunk):
                idx += 1
                stype = 'hook' if idx == 1 else ('recap' if idx == n else 'concept')
                sub = a.subtitle[idx - 1] if len(a.subtitle) >= idx else f"Beat {idx}"
                kw = a.keyword[idx - 1] if len(a.keyword) >= idx else ''
                body.append(scene_block(f's{idx}', stype, line, sub, kw))
            body.append("      ],\n    },\n")
        out = TEMPLATE_HEADER.format(slug=slug, title=title, tagline=a.tagline) + ''.join(body) + TEMPLATE_FOOTER
    else:
        # skeleton: 3 chapters, 6 scenes, each with a Hindi hint
        plan = [
            ('Part 1', ['hook', 'concept']),
            ('Part 2', ['steps', 'number']),
            ('Part 3', ['compare', 'recap']),
        ]
        body = []
        idx = 0
        for cname, types in plan[:max(1, min(5, a.parts))]:
            body.append(f"    {{\n      title: '{cname}',\n      scenes: [\n")
            for st in types:
                idx += 1
                say, sub, kw, extra = SKELETON[st]
                body.append(scene_block(f's{idx}', st, say.format(title=title),
                                        sub.format(title=title), kw.format(title=title), extra))
            body.append("      ],\n    },\n")
        out = TEMPLATE_HEADER.format(slug=slug, title=title, tagline=a.tagline) + ''.join(body) + TEMPLATE_FOOTER

    open(a.out, 'w', encoding='utf-8').write(out)
    print(f'likh diya: {a.out}')
    print(f'  slug  : {slug}')
    print(f'  title : {title}')
    print()
    print('Ab ye karo:')
    print('  1. src/content.ts kholo aur har `say` ko apne Hindi words se replace karo')
    print('     (subtitle / keyword ENGLISH me hi rahenge)')
    print('  2. python3 scripts/check_content.py     # galtiyan pakdo')
    print('  3. python3 scripts/build_voice.py       # voice banao')
    print('  4. npx remotion render src/index.ts Explainer out/video.mp4 --concurrency=2')
    return 0


if __name__ == '__main__':
    sys.exit(main())
