#!/usr/bin/env python3
"""
kathareel — brief se script banane wala engine (by raghv)

User ek chhota brief likhta hai, jaise:

    "machine learning: definition, types, supervised vs unsupervised, kya kaam aata hai"

`build(brief, minutes)` usse poora script bana deta hai — aur sabse zaroori:
content topic ka hota hai, generic nahi. Har video me wahi "first point /
second point" nahi aata, aur layout bhi topic ke hisaab se chunte hain.

3 layer:
  1. BRIEF PARSE  — topic, sections, labels, numbers alag karo
  2. LEXICON      — topic ka domain (ai / code / health / business / science / general)
                    se words, step verbs, compare labels, metric nikalo
  3. ARRANGE      — sections ko scene types me map karo, layout rotate karo,
                    aur Devanagari narration likho

Rule: screen par sab English, `say` Devanagari me (English tech words Latin me).
"""
import hashlib
import re

# ---------------------------------------------------------------------------
# 1. brief parsing
# ---------------------------------------------------------------------------
SECTION_WORDS = {
    'definition': 'definition', 'define': 'definition', 'matlab': 'definition',
    'meaning': 'definition', 'kya hai': 'definition', 'what is': 'definition',
    'intro': 'definition', 'basics': 'definition', 'history': 'definition',
    'types': 'types', 'type': 'types', 'kinds': 'types', 'kisme': 'types',
    'categories': 'types', 'classification': 'types', 'tools': 'types',
    'libraries': 'types', 'frameworks': 'types',
    'how it works': 'steps', 'how': 'steps', 'process': 'steps', 'steps': 'steps',
    'working': 'steps', 'pipeline': 'steps', 'kaise': 'steps',
    'algorithm': 'steps', 'flow': 'steps', 'method': 'steps', 'formula': 'steps',
    'example': 'example', 'examples': 'example', 'use case': 'example',
    'use cases': 'example', 'uses': 'example', 'applications': 'example',
    'real life': 'example', 'udaharan': 'example',
    'difference': 'compare', 'vs': 'compare', 'versus': 'compare',
    'comparison': 'compare', 'compare': 'compare', 'farq': 'compare',
    'fark': 'compare', 'diff': 'compare',
    'benefits': 'benefits', 'advantages': 'benefits', 'pros': 'benefits',
    'fayde': 'benefits', 'faayde': 'benefits', 'why': 'benefits',
    'importance': 'benefits', 'career': 'benefits', 'future': 'benefits',
    'scope': 'benefits',
    'limitations': 'limits', 'limits': 'limits', 'drawbacks': 'limits',
    'disadvantages': 'limits', 'cons': 'limits', 'nukaasan': 'limits',
    'problems': 'limits', 'challenges': 'limits',
}
VS = re.compile(r'\s+(?:vs\.?|versus)\s+', re.I)


def _clean(line):
    return re.sub(r'^[\s\-–—•*·▪◦\d.)>#]+', '', line).strip().rstrip('.')


def parse_brief(brief):
    """Brief ko topic + sections me todo. Sections ka order user ka, hum nahi badalte."""
    text = (brief or '').strip()
    if not text:
        return {'topic': '', 'sections': [], 'labels': [], 'numbers': {},
                'definition': '', 'raw': ''}

    lines = [l for l in text.splitlines() if l.strip()]
    topic = ''
    m = re.search(r'^(?:topic|subject|about)\s*[:\-]\s*(.+)$', lines[0], re.I) if lines else None
    if m:
        topic = _clean(m.group(1))
    elif lines:
        m3 = re.match(r'^([^:.]{2,70}):', lines[0])
        topic = _clean(m3.group(1) if m3 else lines[0].split(',')[0])
    topic = re.sub(r'\s+(?:video|explainer|ke bare me.*)$', '', topic, flags=re.I).strip()
    if not topic:
        topic = 'Your Topic'

    sections, labels, numbers = [], [], {}
    # single-line brief: "photosynthesis: definition, uses" -> colon ke baad wala hissa
    rest = text
    if lines and topic.lower() in lines[0].lower():
        first = lines[0]
        tail = first.split(':', 1)[1] if ':' in first else ''
        rest = (tail + '\n' + '\n'.join(lines[1:])).strip()

    chunks = []
    for line in rest.splitlines():
        line = line.strip()
        if not line:
            continue
        if ':' in line and len(line.split(':')[0]) <= 40:
            head, tail = line.split(':', 1)
            chunks.append(head)
            chunks.extend(re.split(r'[,;•|]\s*', tail))
        else:
            chunks.extend(re.split(r'[,;•|]\s*', line))

    for raw in chunks:
        lab = _clean(raw)
        if not lab or len(lab) > 70:
            continue
        key = lab.lower()
        for num, unit in re.findall(r'(\d+(?:[\.,]\d+)?)\s*(%)?', lab):
            if unit == '%':
                numbers.setdefault('percent', num)
        kind = None
        for word, k in sorted(SECTION_WORDS.items(), key=lambda kv: -len(kv[0])):
            if word in key:
                kind = k
                break
        if VS.search(lab):
            kind = 'compare'
        labels.append(lab)
        sections.append({'kind': kind or 'point', 'label': lab})

    definition = ''
    mdef = re.search(r'(?:is|means|matlab)\s+([^\n.]{12,160})', text)
    if mdef:
        definition = mdef.group(1).strip()

    return {'topic': topic, 'sections': sections, 'labels': labels,
            'numbers': numbers, 'definition': definition, 'raw': text}


# ---------------------------------------------------------------------------
# 2. lexicon
# ---------------------------------------------------------------------------
DOMAINS = {
    'ai': {
        'words': ['model', 'data', 'training', 'features', 'accuracy', 'dataset'],
        'step_verbs': ['Collect data', 'Clean the data', 'Pick a model', 'Train it', 'Evaluate'],
        'compare': ('Fixed rules', 'Learning from data'),
        'compare_points': (['explicit if-else', 'breaks on new cases', 'human rewrites it'],
                           ['finds patterns', 'improves with data', 'handles messy input']),
        'metric': ('Accuracy', '%', 'better than guessing'),
        'uses': ['Spam filters', 'Product recommendations', 'Fraud detection'],
        'triggers': ['machine learning', 'ml', 'ai', 'deep learning', 'neural', 'llm',
                     'rag', 'nlp', 'transformer', 'embedding', 'classifier', 'regression'],
        'types': ['Supervised', 'Unsupervised', 'Reinforcement'],
        'accent': 'blue',
        'bank': [
            {'kind': 'types', 'label': 'Supervised vs unsupervised', 'compare': ('Supervised', 'Unsupervised')},
            {'kind': 'steps', 'label': 'Training loop', 'steps': ['Feed data', 'Guess', 'Compare with truth', 'Adjust weights']},
            {'kind': 'example', 'label': 'Spam filter in real life', 'bullets': ['Email arrives', 'Model scores it', 'Spam folder']},
            {'kind': 'limits', 'label': 'Overfitting', 'bullets': ['memorises noise', 'fails on new data', 'needs more data']},
            {'kind': 'metric', 'label': 'Accuracy that matters', 'value': '90', 'unit': '%', 'caption': 'on unseen data'},
            {'kind': 'example', 'label': 'Why recommendations work', 'bullets': ['watch history', 'similar users', 'ranked list']},
            {'kind': 'benefits', 'label': 'Where it saves time', 'bullets': ['sorting', 'predicting', 'repeating']},
        ],
    },
    'code': {
        'words': ['repository', 'commit', 'branch', 'tests', 'build', 'deploy'],
        'step_verbs': ['Write the change', 'Test locally', 'Commit', 'Push', 'Deploy'],
        'compare': ('Without tests', 'With tests'),
        'compare_points': (['bugs ship silently', 'manual checking', 'scared refactors'],
                           ['fail fast', 'safe refactors', 'cheap rollback']),
        'metric': ('Build time', 'min', 'from commit to live'),
        'uses': ['Version control', 'CI pipelines', 'Health checks in prod'],
        'triggers': ['git', 'python', 'javascript', 'react', 'docker', 'api', 'code',
                     'programming', 'kubernetes', 'database', 'sql'],
        'types': ['Script', 'Library', 'Service'],
        'accent': 'violet',
        'bank': [
            {'kind': 'steps', 'label': 'Commit to deploy', 'steps': ['Write code', 'Run tests', 'Commit', 'Push', 'Deploy']},
            {'kind': 'compare', 'label': 'Monolith vs microservice', 'compare': ('Monolith', 'Microservice')},
            {'kind': 'example', 'label': 'Fix a bug safely', 'bullets': ['write a failing test', 'fix the code', 'test turns green']},
            {'kind': 'limits', 'label': 'When tests lie', 'bullets': ['flaky tests', 'bad assertions', 'no real data']},
            {'kind': 'metric', 'label': 'Build time', 'value': '4', 'unit': 'min', 'caption': 'commit to live'},
            {'kind': 'example', 'label': 'Review before merge', 'bullets': ['small diff', 'one reviewer', 'green checks']},
            {'kind': 'benefits', 'label': 'Why teams automate', 'bullets': ['fewer mistakes', 'faster ship', 'same steps']},
        ],
    },
    'health': {
        'words': ['body', 'nutrition', 'sleep', 'exercise', 'stress', 'immunity'],
        'step_verbs': ['Find the trigger', 'Change the habit', 'Track it', 'Adjust'],
        'compare': ('Old habit', 'New habit'),
        'compare_points': (['quick fix', 'energy crash', 'heavy load'],
                           ['steady energy', 'better sleep', 'easier to hold']),
        'metric': ('Improvement', '%', 'in eight weeks'),
        'uses': ['Daily energy', 'Better sleep', 'Recovery after exercise'],
        'triggers': ['health', 'body', 'diet', 'sleep', 'fitness', 'disease', 'brain',
                     'heart', 'nutrition', 'medicine', 'yoga'],
        'types': ['Prevention', 'Nutrition', 'Movement'],
        'accent': 'green',
        'bank': [
            {'kind': 'steps', 'label': 'Habit loop', 'steps': ['Trigger', 'Routine', 'Reward', 'Repeat']},
            {'kind': 'compare', 'label': 'Crash diet vs slow change', 'compare': ('Crash diet', 'Slow change')},
            {'kind': 'example', 'label': 'One day on a plate', 'bullets': ['protein first', 'fibre next', 'sugar last']},
            {'kind': 'limits', 'label': 'Why sleep matters more', 'bullets': ['hormones shift', 'hunger rises', 'focus drops']},
            {'kind': 'metric', 'label': 'Realistic change', 'value': '1', 'unit': '%', 'caption': 'per week, steady'},
            {'kind': 'example', 'label': 'Energy through the day', 'bullets': ['steady meals', 'short walk', 'real sleep']},
            {'kind': 'benefits', 'label': 'What improves first', 'bullets': ['sleep', 'focus', 'mood']},
        ],
    },
    'business': {
        'words': ['customer', 'revenue', 'market', 'pricing', 'channel', 'retention'],
        'step_verbs': ['Find the problem', 'Build the offer', 'Reach the buyer', 'Measure'],
        'compare': ('Costly way', 'Cheap way'),
        'compare_points': (['paid ads only', 'one channel', 'churn blindspot'],
                           ['own audience', 'repeat buyers', 'retention first']),
        'metric': ('Cost cut', '%', 'after the switch'),
        'uses': ['Pricing pages', 'Referral loops', 'Support that scales'],
        'triggers': ['business', 'startup', 'marketing', 'sales', 'finance', 'money',
                     'invest', 'product', 'growth', 'profit', 'ecommerce'],
        'types': ['Cost', 'Price', 'Value'],
        'accent': 'amber',
        'bank': [
            {'kind': 'steps', 'label': 'First ten customers', 'steps': ['Talk to 20', 'Pick one pain', 'Charge early']},
            {'kind': 'compare', 'label': 'Cheap reach vs paid ads', 'compare': ('Own audience', 'Paid ads')},
            {'kind': 'example', 'label': 'Pricing in practice', 'bullets': ['anchor high', 'show value', 'discount rarely']},
            {'kind': 'limits', 'label': 'Growth that kills', 'bullets': ['cheap traffic', 'no retention', 'cash crunch']},
            {'kind': 'metric', 'label': 'Retention beats reach', 'value': '30', 'unit': '%', 'caption': 'month two retention'},
            {'kind': 'example', 'label': 'A one-page offer', 'bullets': ['who it is for', 'what changes', 'what it costs']},
            {'kind': 'benefits', 'label': 'What compounding gives', 'bullets': ['trust', 'referrals', 'cheaper growth']},
        ],
    },
    'science': {
        'words': ['energy', 'force', 'molecule', 'reaction', 'field', 'particle'],
        'step_verbs': ['Observe it', 'Form a hypothesis', 'Test it', 'Conclude'],
        'compare': ('What it looks like', 'What actually happens'),
        'compare_points': (['surface detail', 'one observation', 'looks fixed'],
                           ['underlying cause', 'repeatable test', 'predicts new cases']),
        'metric': ('Speed', 'x', 'compared to before'),
        'uses': ['Food and cooking', 'Weather and climate', 'Medical tests'],
        'triggers': ['physics', 'chemistry', 'biology', 'photosynthesis', 'gravity',
                     'atom', 'energy', 'space', 'evolution', 'climate'],
        'types': ['Cause', 'Process', 'Effect'],
        'accent': 'teal',
        'bank': [
            {'kind': 'steps', 'label': 'Scientific method', 'steps': ['Observe', 'Hypothesis', 'Experiment', 'Conclude']},
            {'kind': 'compare', 'label': 'Theory vs law', 'compare': ('Theory', 'Law')},
            {'kind': 'example', 'label': 'Everyday example', 'bullets': ['cook food', 'boil water', 'feel the change']},
            {'kind': 'limits', 'label': 'Where the model breaks', 'bullets': ['edge cases', 'measurement error', 'scale']},
            {'kind': 'metric', 'label': 'Measured effect', 'value': '10', 'unit': 'x', 'caption': 'vs the baseline'},
            {'kind': 'example', 'label': 'Kitchen experiment', 'bullets': ['change one thing', 'note the result', 'repeat']},
            {'kind': 'benefits', 'label': 'Why the method wins', 'bullets': ['repeatable', 'falsifiable', 'honest']},
        ],
    },
    'general': {
        'words': ['idea', 'example', 'habit', 'goal', 'step', 'result'],
        'step_verbs': ['Start small', 'Do it daily', 'Measure it', 'Fix what breaks'],
        'compare': ('Common way', 'Better way'),
        'compare_points': (['one old method', 'no feedback', 'hard to repeat'],
                           ['one better method', 'weekly review', 'easy to repeat']),
        'metric': ('Progress', '%', 'after thirty days'),
        'uses': ['Daily routine', 'Study plans', 'Money habits'],
        'triggers': [],
        'types': ['Basics', 'Practice', 'Results'],
        'accent': 'orange',
        'bank': [
            {'kind': 'steps', 'label': 'A simple plan', 'steps': ['Start small', 'Do it daily', 'Track it', 'Adjust']},
            {'kind': 'compare', 'label': 'Common way vs better way', 'compare': ('Common way', 'Better way')},
            {'kind': 'example', 'label': 'In your own week', 'bullets': ['one clear goal', 'small daily step', 'weekly review']},
            {'kind': 'limits', 'label': 'Where it stops working', 'bullets': ['no feedback', 'too many goals', 'no rest']},
            {'kind': 'metric', 'label': 'What progress looks like', 'value': '1', 'unit': '%', 'caption': 'daily, compounding'},
            {'kind': 'example', 'label': 'Try it this week', 'bullets': ['pick one', 'timebox it', 'review']},
            {'kind': 'benefits', 'label': 'Why small wins stack', 'bullets': ['momentum', 'clarity', 'proof']},
        ],
    },
}


def pick_domain(topic, brief=''):
    t = f'{topic} {brief}'.lower()
    best, best_hits = 'general', 0
    for name, d in DOMAINS.items():
        hits = sum(1 for w in d['triggers'] if w in t)
        if hits > best_hits:
            best, best_hits = name, hits
    return best


def _h(s, n=6):
    return int(hashlib.sha1(s.encode()).hexdigest()[:8], 16) % n


# ---------------------------------------------------------------------------
# 3. arrange
# ---------------------------------------------------------------------------
# (type, layout) — sirf wahi jodi jo scripts/check_content.py valid maanta hai.
# definition -> hook type, kyunki bigword/quote hook ke layouts hain (opening scene).
LAYOUTS_BY_KIND = {
    'definition': ['bigword', 'quote', 'hook'],
    'point': ['cards', 'bullets', 'two-col'],
    'types': ['cards', 'two-col', 'bullets'],
    'steps': ['timeline', 'steps', 'numbered'],
    'compare': ['versus', 'table', 'compare'],
    'example': ['cards', 'bullets', 'two-col'],
    'benefits': ['checklist', 'takeaways', 'recap'],
    'limits': ['bullets', 'cards', 'two-col'],
    'metric': ['stat', 'number'],
    'recap': ['takeaways', 'checklist', 'recap'],
}
TYPE_BY_KIND = {
    'definition': 'hook', 'point': 'concept', 'types': 'concept',
    'steps': 'steps', 'compare': 'compare', 'example': 'concept',
    'benefits': 'recap', 'limits': 'concept', 'metric': 'number', 'recap': 'recap',
}

# keyword: scene kind ke hisaab se bada word (har scene par topic dohraana lazy lagta hai)
KEYWORD_BY_KIND = {
    'definition': None, 'point': None, 'types': 'TYPES', 'steps': 'HOW IT WORKS',
    'compare': 'VS', 'example': 'IN PRACTICE', 'benefits': 'WHY IT MATTERS',
    'limits': 'LIMITS', 'metric': 'BY THE NUMBERS', 'recap': 'RECAP',
}
TRANSITIONS = ['fade', 'slide', 'pop', 'zoom', 'wipe']


def _hi(items):
    items = [i for i in items if i]
    if not items:
        return ''
    if len(items) == 1:
        return items[0]
    return ', '.join(items[:-1]) + ' और ' + items[-1]


def narrate(topic, kind, things, order, definition=''):
    """Devanagari narration, topic-specific. Har kind ka apna angle."""
    t = _hi(things[:3])
    openers = [
        f'अब {topic} की मुख्य बात समझो।',
        f'यहाँ एक बात ध्यान से सुनो, {topic} को लेकर।',
        f'{topic} में यह हिस्सा सबसे ज़्यादा काम का है।',
        f'चलो, {topic} को आसान भाषा में समझते हैं।',
    ]
    o = openers[order % len(openers)]

    if kind == 'definition':
        return (f'देखो भाई, {topic} को एक line में समझो तो {t} — यही तीन चीज़ें इसका दिल हैं। '
                f'इसका मतलब यह नहीं कि इसे रटना है, बल्कि इसे एक उदाहरण से जोड़कर देखो, '
                f'तभी बात बैठती है और लंबे समय तक याद रहती है।')
    if kind == 'types':
        return (f'{o} {topic} के कई रूप हैं — जैसे {t}। हर रूप का काम अलग है, '
                f'इसलिए पहले पहचानो कि तुम्हें कौन सा चाहिए।')
    if kind == 'steps':
        return (f'{o} काम {t} — इसी क्रम में होता है। हर step में देखो कि अंदर क्या जाता है '
                f'और बाहर क्या आता है, तभी पूरा {topic} समझ आता है।')
    if kind == 'compare':
        a = things[0] if things else 'पहला तरीका'
        b = things[1] if len(things) > 1 else 'दूसरा तरीका'
        return (f'{o} एक तरफ़ {a} है, दूसरी तरफ़ {b}। फ़र्क सिर्फ़ speed का नहीं है, '
                f'सोचने का भी है — और यही फ़र्क ज़्यादातर लोग miss करते हैं।')
    if kind == 'example':
        return (f'{o} ज़रूरी बात यह है कि {topic} सिर्फ़ किताबी नहीं है। '
                f'असली ज़िंदगी में इसे देखो तो बात तुरंत बैठ जाती है।')
    if kind == 'benefits':
        return (f'{o} इसका फ़ायदा सीधा है — {t}। इसलिए {topic} सीखना सिर्फ़ theory नहीं, '
                f'एक practical फ़ायदा है।')
    if kind == 'limits':
        return (f'{o} सच यह भी है कि {topic} हर जगह सही नहीं बैठता। {t} जैसी limitation आती है, '
                f'और यही जानना सबसे ज़रूरी है।')
    if kind == 'metric':
        return (f'{o} एक number पकड़ लो — {t}। number से पता चलता है कि बात कितनी काम की है। '
                f'जब भी सुनो कि यह तेज़ है या बेहतर है, पूछो कि कितना और किस चीज़ पर — '
                f'यही आदत तुम्हें बाकी लोगों से आगे रखती है।')
    if kind == 'recap':
        return ('बस इतना याद रखो। ' + topic + ' क्या है, यह कैसे काम करता है, और असली ज़िंदगी में '
                'कहाँ काम आता है — तीन बातें पकड़ लो, तो आगे जो भी पढ़ोगे वह जल्दी समझ आएगा। '
                'बाकी सब ब्यौरा है, उसे बाद में देख लेना।')
    return (f'{o} {t} पर ध्यान दो, तो पूरा {topic} आसान लगने लगता है।')


def _fit(say, max_words=34):
    """Validator limit 34 words.

    Sentence units `।` par todo, aur agar phir bhi lamba ho to aakhri *clause*
    (— , aur , पर) hatao. Sirf words kaatne se `बस इतना याद रखो।` jaisa
    aadha-adhoora narration bach jaata tha.
    """
    if len(say.split()) <= max_words:
        return say.strip()

    sents = [x.strip() for x in re.split(r'(?<=।)\s*|(?<=—)\s*(?=[^—]{25,})', say) if x.strip()]
    out = say
    while len(out.split()) > max_words and len(sents) > 1:
        sents.pop()
        out = ' '.join(sents).strip()
    if len(out.split()) > max_words:          # ek hi lamba vaakya
        w = out.split()[:max_words]
        out = ' '.join(w).rstrip(',—-') + '।'
    return out


def _default_sections(topic):
    return [
        {'kind': 'definition', 'label': f'What is {topic}'},
        {'kind': 'types', 'label': f'Types of {topic}'},
        {'kind': 'steps', 'label': f'How {topic} works'},
        {'kind': 'example', 'label': f'Where {topic} is used'},
        {'kind': 'benefits', 'label': f'Why {topic} matters'},
        {'kind': 'recap', 'label': 'Recap'},
    ]


def build(brief, minutes=3, title=None, tagline=None, topic=None):
    parsed = parse_brief(brief)
    topic = (topic or parsed['topic'] or 'Your Topic').strip()
    topic = topic[:1].upper() + topic[1:] if topic.islower() else topic
    # "How to save money" -> video ka topic "saving money" nahi, par "What is How to..."
    # bhaddi lagta hai — isliye aise topics ke liye subtitle alag rakhte hain
    # display name: "How to save money" -> "Saving money" (warna "How How to save money works")
    disp = topic
    m_how = re.match(r'^how\s+to\s+(.+)$', topic, re.I)
    if m_how:
        verb = m_how.group(1)
        disp = verb[:1].upper() + verb[1:]
    else:
        disp = re.sub(r'^(why|what is|when to|should i)\s+', '', topic, flags=re.I)
        disp = disp[:1].upper() + disp[1:] if disp else topic
    domain = pick_domain(topic, parsed['raw'])
    d = DOMAINS[domain]
    # narration aur screen notes me display naam chalta hai ("How to save money" nahi)
    topic = disp

    slug = re.sub(r'[^a-z0-9-]+', '-', topic.lower()).strip('-') or 'video'
    title = (title or topic).strip()
    tagline = tagline or 'In Hindi, step by step'

    target_s = max(30.0, minutes * 60)
    beats = max(4, min(30, round(target_s / 14.0)))
    parts = max(2, min(6, round(beats / 4)))

    sections = list(parsed['sections']) or _default_sections(topic)
    if not any(s['kind'] == 'definition' for s in sections):
        sections.insert(0, {'kind': 'definition', 'label': f'What is {disp}'})
    if not any(s['kind'] == 'recap' for s in sections):
        sections.append({'kind': 'recap', 'label': 'Recap'})

    # Brief me sections diye hain -> sirf wahi banao. User ne "sirf definition"
    # likha to 9 scene ka padding nahi chahiye (yahi user ki demand thi).
    explicit = bool(parsed['sections'])
    pool = sections
    used_kinds = {x['kind'] for x in sections}
    bank = [] if explicit else sorted(
        d.get('bank') or [], key=lambda b: 1 if b['kind'] in used_kinds else 0)
    bi = 0
    while len(pool) < beats and bi < len(bank):
        b = dict(bank[bi])
        # bank item ke paas apna content hai — kind usi se, warna render galat layout me chala jayega
        if b.get('compare'):
            b['kind'] = 'compare'
        elif b.get('steps'):
            b['kind'] = 'steps'
        elif b.get('value'):
            b['kind'] = 'metric'
        pool.insert(len(pool) - 1, b)
        bi += 1
    # bank bhi khatam -> generic point (sirf jab user ne bahut lamba video maanga ho
    # aur brief me sections nahi diye)
    while len(pool) < beats and not explicit:
        n = len(pool)
        pool.insert(len(pool) - 1, {'kind': 'point',
                                    'label': f'{topic} — point {n}', 'bullets': d['words'][:3]})
    pool = pool[:beats]

    chapters, made, used = [], 0, []
    per_part = [max(1, len(pool) // parts + (1 if i < len(pool) % parts else 0)) for i in range(parts)]

    for p, n_in in enumerate(per_part):
        ch = {'title': f'Part {p + 1}', 'scenes': []}
        for s in pool[made:made + n_in]:
            made += 1
            kind = s['kind']
            ty = TYPE_BY_KIND.get(kind, 'concept')
            choices = LAYOUTS_BY_KIND.get(kind, ['cards'])
            # layout rotate: pichhle 2 scene ka layout dohrao mat
            layout = choices[made % len(choices)]
            for c in choices:
                if c not in used[-2:]:
                    layout = c
                    break
            used.append(layout)

            # Screen par padhne layak label: "definition" akela bhadda lagta hai,
            # isliye topic ke saath jodte hain. "What is X" redundant ho to hata do.
            label = s['label'].strip()
            low = label.lower()
            if low in ('definition', 'matlab', 'meaning', 'what is', 'kya hai'):
                label = f'What is {disp}'
            elif low in ('types', 'type', 'kinds'):
                label = f'Types of {disp}'
            elif low in ('steps', 'how it works', 'how', 'process'):
                label = f'How {disp} works'
            elif low in ('uses', 'use', 'examples', 'applications', 'use cases'):
                label = f'Where {disp} is used'
            elif low in ('limitations', 'limits', 'drawbacks', 'cons'):
                label = f'Limits of {disp}'
            elif low in ('benefits', 'advantages', 'pros', 'why'):
                label = f'Why {disp} matters'
            elif low.startswith('what is '):
                label = label
            sc = {
                'id': f's{made}', 'type': ty, 'say': '',
                'subtitle': label[:46],
                'keyword': (topic[:22] if kind == 'definition' else
                            KEYWORD_BY_KIND.get(kind) or
                            re.sub(r'^(what is|how|why|types of)\s+', '', s['label'], flags=re.I)[:22]),
                'layout': layout, 'accent': '',
                'transition': TRANSITIONS[(made + _h(topic)) % len(TRANSITIONS)],
                'bullets': [], 'steps': [], 'left': None, 'right': None,
                'value': '', 'unit': '', 'caption': '', 'note': '',
            }

            words3 = [w.title() for w in d['words'][:3]]

            # bank se aaya section: uska apna content seedha use karo
            if s.get('steps'):
                sc['steps'] = [{'label': v.upper()} for v in s['steps'][:5]]
                sc['note'] = f"{s['label']} — step by step."
                sc['say'] = narrate(topic, 'steps', s['steps'][:3], made)
            elif s.get('compare'):
                lab, lab2 = s['compare']
                pl, pr = d.get('compare_points', (['slower', 'manual', 'fixed rules'],
                                                 ['faster', 'automatic', 'learns from data']))
                sc['left'] = {'label': lab, 'points': list(pl)}
                sc['right'] = {'label': lab2, 'points': list(pr)}
                sc['note'] = f'{lab} vs {lab2} — the difference that matters for {topic}.'
                sc['say'] = narrate(topic, 'compare', [lab, lab2], made)
            elif s.get('value'):
                sc['value'] = s['value']
                sc['unit'] = s.get('unit', '')
                sc['caption'] = s.get('caption', '')
                sc['note'] = f"{s['label']} — the number that matters."
                sc['say'] = narrate(topic, 'metric', [f"{s['value']} {s.get('unit', '')}".strip()], made)
            elif s.get('bullets') and not explicit:
                sc['bullets'] = s['bullets'][:3]
                sc['note'] = (f"{sc['bullets'][0]} is the clearest example of {topic}."
                              if kind == 'example' else f"{s['label']} — in one line.")
                sc['say'] = narrate(topic, kind, sc['bullets'], made)
            elif kind == 'types':
                tl = d.get('types') or d['words'][:3]
                sc['bullets'] = tl[:3]
                sc['note'] = f'{topic} splits into {len(tl[:3])} kinds — pick by the job, not by hype.'
                sc['say'] = narrate(topic, kind, sc['bullets'], made)
            elif kind == 'steps':
                sc['steps'] = [{'label': v.upper()} for v in d['step_verbs'][:4]]
                sc['note'] = f'Each step of {topic} hands something to the next.'
                sc['say'] = narrate(topic, kind, d['step_verbs'][:3], made)
            elif kind == 'compare':
                lab, lab2 = d['compare']
                pl, pr = d.get('compare_points', (['slower', 'manual', 'fixed rules'],
                                                 ['faster', 'automatic', 'learns from data']))
                sc['left'] = {'label': lab, 'points': list(pl)}
                sc['right'] = {'label': lab2, 'points': list(pr)}
                sc['note'] = f'The real difference in {topic} is what you hand over to the machine.'
                sc['say'] = narrate(topic, kind, [lab, lab2], made)
            elif kind == 'metric':
                val, unit, cap = d['metric']
                num = parsed['numbers'].get('percent') or '90'
                sc['value'], sc['unit'], sc['caption'] = num, unit, cap
                sc['note'] = f'That number is why {topic} keeps coming up.'
                sc['say'] = narrate(topic, kind, [f'{num} {unit}'], made)
            elif kind == 'definition':
                if parsed['definition']:
                    sc['note'] = parsed['definition'][:130]
                else:
                    sc['note'] = f"{topic} = {', '.join(words3[:3])} working together."
                sc['bullets'] = words3
                sc['say'] = narrate(topic, kind, sc['bullets'], made, parsed['definition'])
            elif kind == 'benefits':
                uses = d.get('uses') or words3
                sc['bullets'] = [f'{u}: less manual work' for u in uses[:3]]
                sc['note'] = f'Why people actually care about {topic}.'
                sc['say'] = narrate(topic, kind, words3, made)
            elif kind == 'limits':
                pl = d.get('compare_points', (['slower', 'manual', 'fixed rules'], []))[0]
                sc['bullets'] = list(pl[:3])
                sc['note'] = f'Where {topic} breaks — knowing this saves real pain.'
                sc['say'] = narrate(topic, kind, sc['bullets'], made)
            elif kind == 'recap':
                sc['bullets'] = ['Definition', 'How it works', 'Where it is used']
                sc['note'] = f'Three lines and {topic} is yours.'
                sc['say'] = narrate(topic, 'recap', [], made)
            else:  # point / example
                uses = d.get('uses') or words3
                sc['bullets'] = list(uses[:3])
                sc['note'] = (f"{uses[0]} is the clearest example of {topic}."
                              if kind == 'example' else f"{s['label']} — in one line.")
                sc['say'] = narrate(topic, kind, sc['bullets'], made)

            sc['say'] = _fit(sc['say'])
            ch['scenes'].append(sc)
        if ch['scenes']:
            chapters.append(ch)

    return {
        'slug': slug, 'title': title, 'tagline': tagline,
        'accent': d['accent'],
        'background': ['glow', 'grid', 'dots', 'mesh'][_h(topic, 4)],
        'chapters': chapters,
    }


if __name__ == '__main__':
    import json
    import sys
    b = ' '.join(sys.argv[1:]) or 'machine learning: definition, types, how it works, uses'
    print(json.dumps(build(b, 3), indent=1, ensure_ascii=False))
