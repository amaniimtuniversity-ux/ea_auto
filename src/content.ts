/**
 * ============================================================
 *  kathareel — content file (by raghv)
 *  Topic: Machine Learning
 * ============================================================
 *
 *  `say`      = jo bola jayega -> HINDI, DEVANAGARI me (English tech words Latin me chalenge)
 *  `subtitle` = screen par line -> ENGLISH ONLY, chhota
 *  `keyword`  = bada word       -> ENGLISH ONLY
 *
 *  Ye file web UI se generate hui hai (web/server.py).
 */

export type SceneType = 'hook' | 'concept' | 'steps' | 'compare' | 'number' | 'recap';

export type Scene = {
  id: string;
  type: SceneType;
  say: string;
  subtitle: string;
  keyword?: string;
  bullets?: string[];
  steps?: {label: string; note?: string}[];
  left?: {label: string; points: string[]};
  right?: {label: string; points: string[]};
  value?: string;
  unit?: string;
  caption?: string;
};

export type Chapter = {
  title: string;
  scenes: Scene[];
};

export type VideoContent = {
  slug: string;
  title: string;
  tagline: string;
  chapters: Chapter[];
};

export const CONTENT: VideoContent = {
  slug: 'machine-learning',
  title: 'Machine Learning',
  tagline: 'In Hindi, step by step',
  chapters: [
    {
      title: 'Part 1',
      scenes: [
        {
          id: 's1',
          type: 'hook',
          say: 'देखो भाई, यहाँ एक आम situation है। ज़्यादातर लोग इस problem से रोज़ गुज़रते हैं, और उन्हें पता भी नहीं होता कि इसका solution इतना आसान है।',
          subtitle: 'The problem',
          keyword: 'Problem',
          bullets: ['first point', 'second point', 'third point'],
        },
        {
          id: 's2',
          type: 'concept',
          say: 'अब मुख्य बात समझो। Machine Learning का मतलब है कि काम को छोटे-छोटे हिस्सों में बाँट देना, और हर हिस्से को एक-एक करके सॉल्व करना। एक आसान उदाहरण से बात पक्की हो जाती है।',
          subtitle: 'Machine Learning',
          keyword: 'Machine Learning',
          bullets: ['first point', 'second point', 'third point'],
        },
        {
          id: 's3',
          type: 'steps',
          say: 'अब step by step चलो। पहले डेटा इकट्ठा होता है, फिर उसे साफ़ किया जाता है, और आख़िर में model उससे सीखता है।',
          subtitle: 'Step by step',
          keyword: 'How it works',
          steps: [{label: 'STEP ONE', note: 'what happens'}, {label: 'STEP TWO', note: 'what happens'}, {label: 'STEP THREE', note: 'what happens'}],
        },
        {
          id: 's4',
          type: 'number',
          say: 'अब एक number देखो जो पूरी बात साफ़ कर देगा। नब्बे फ़ीसदी से ज़्यादा लोग यही गलती करते हैं, और वजह बहुत छोटी है।',
          subtitle: 'One number',
          keyword: 'By the numbers',
          value: '3',
          unit: 'items',
          caption: 'what the number means',
        },
        {
          id: 's5',
          type: 'compare',
          say: 'फ़र्क साफ़ है। एक तरफ़ पुराना तरीका है जो धीमा है, दूसरी तरफ़ नया तरीका जो तेज़ है — दोनों को साथ रखकर देखो।',
          subtitle: 'The difference',
          keyword: 'Compare',
          left: {label: 'WITHOUT', points: ['point one', 'point two']},
          right: {label: 'WITH', points: ['point one', 'point two']},
        },
      ],
    },
    {
      title: 'Part 2',
      scenes: [
        {
          id: 's6',
          type: 'concept',
          say: 'अब मुख्य बात समझो। Machine Learning का मतलब है कि काम को छोटे-छोटे हिस्सों में बाँट देना, और हर हिस्से को एक-एक करके सॉल्व करना। एक आसान उदाहरण से बात पक्की हो जाती है।',
          subtitle: 'Machine Learning',
          keyword: 'Machine Learning',
          bullets: ['first point', 'second point', 'third point'],
        },
        {
          id: 's7',
          type: 'steps',
          say: 'अब step by step चलो। पहले डेटा इकट्ठा होता है, फिर उसे साफ़ किया जाता है, और आख़िर में model उससे सीखता है।',
          subtitle: 'Step by step',
          keyword: 'How it works',
          steps: [{label: 'STEP ONE', note: 'what happens'}, {label: 'STEP TWO', note: 'what happens'}, {label: 'STEP THREE', note: 'what happens'}],
        },
        {
          id: 's8',
          type: 'concept',
          say: 'अब मुख्य बात समझो। Machine Learning का मतलब है कि काम को छोटे-छोटे हिस्सों में बाँट देना, और हर हिस्से को एक-एक करके सॉल्व करना। एक आसान उदाहरण से बात पक्की हो जाती है।',
          subtitle: 'Machine Learning',
          keyword: 'Machine Learning',
          bullets: ['first point', 'second point', 'third point'],
        },
        {
          id: 's9',
          type: 'steps',
          say: 'अब step by step चलो। पहले डेटा इकट्ठा होता है, फिर उसे साफ़ किया जाता है, और आख़िर में model उससे सीखता है।',
          subtitle: 'Step by step',
          keyword: 'How it works',
          steps: [{label: 'STEP ONE', note: 'what happens'}, {label: 'STEP TWO', note: 'what happens'}, {label: 'STEP THREE', note: 'what happens'}],
        },
      ],
    },
    {
      title: 'Part 3',
      scenes: [
        {
          id: 's10',
          type: 'number',
          say: 'अब एक number देखो जो पूरी बात साफ़ कर देगा। नब्बे फ़ीसदी से ज़्यादा लोग यही गलती करते हैं, और वजह बहुत छोटी है।',
          subtitle: 'One number',
          keyword: 'By the numbers',
          value: '3',
          unit: 'items',
          caption: 'what the number means',
        },
        {
          id: 's11',
          type: 'compare',
          say: 'फ़र्क साफ़ है। एक तरफ़ पुराना तरीका है जो धीमा है, दूसरी तरफ़ नया तरीका जो तेज़ है — दोनों को साथ रखकर देखो।',
          subtitle: 'The difference',
          keyword: 'Compare',
          left: {label: 'WITHOUT', points: ['point one', 'point two']},
          right: {label: 'WITH', points: ['point one', 'point two']},
        },
        {
          id: 's12',
          type: 'concept',
          say: 'अब मुख्य बात समझो। Machine Learning का मतलब है कि काम को छोटे-छोटे हिस्सों में बाँट देना, और हर हिस्से को एक-एक करके सॉल्व करना। एक आसान उदाहरण से बात पक्की हो जाती है।',
          subtitle: 'Machine Learning',
          keyword: 'Machine Learning',
          bullets: ['first point', 'second point', 'third point'],
        },
        {
          id: 's13',
          type: 'recap',
          say: 'बस इतना याद रखो। समस्या क्या थी, हल कैसे निकला, और आगे क्या करना है। तीन बातें, और काम ख़त्म। तीन बातें एक-एक line में दोहरा लो, तो सब पक्का हो जाता है।',
          subtitle: 'Quick recap',
          keyword: 'Remember',
          bullets: ['first point', 'second point', 'third point'],
        },
      ],
    },
  ],
};

export const BUILT_BY = 'built by raghv';
