/**
 * ============================================================
 *  kathareel — content file (by raghv)
 *  Topic: Photosynthesis
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
  slug: 'photosynthesis',
  title: 'Photosynthesis',
  tagline: 'In Hindi, step by step',
  chapters: [
    {
      title: 'Part 1',
      scenes: [
        {
          id: 's1',
          type: 'hook',
          say: 'देखो भाई, यहाँ एक आम situation है। Yahan likho ki viewer ko kya problem hoti hai, aur ye topic usse kaise solve karta hai.',
          subtitle: 'The problem',
          keyword: 'Problem',
          bullets: ['first point', 'second point', 'third point'],
        },
        {
          id: 's2',
          type: 'concept',
          say: 'अब मुख्य बात। Yahan likho ki Photosynthesis asal me hai kya — ek aasan example ke saath, bina jargon ke. यहाँ definition को अपने शब्दों में दोबारा बोलो। एक common गलतफहमी भी बताओ।',
          subtitle: 'Photosynthesis',
          keyword: 'Photosynthesis',
          bullets: ['first point', 'second point', 'third point'],
        },
        {
          id: 's3',
          type: 'steps',
          say: 'अब step by step चलो। Pehle ye hota hai, phir ye, phir ye — har step ek line me samjhao. हर step में बोलो कि input क्या जाता है।',
          subtitle: 'Step by step',
          keyword: 'How it works',
          steps: [{label: 'STEP ONE', note: 'what happens'}, {label: 'STEP TWO', note: 'what happens'}, {label: 'STEP THREE', note: 'what happens'}],
        },
        {
          id: 's4',
          type: 'number',
          say: 'Yahan ek number batao jo poori baat saaf kar de — kitna, kitne percent, kitne log. Number के बाद बोलो कि ये बड़ा है या छोटा।',
          subtitle: 'One number',
          keyword: 'By the numbers',
          value: '3',
          unit: 'items',
          caption: 'what the number means',
        },
        {
          id: 's5',
          type: 'compare',
          say: 'Farq saaf hai. Ek taraf ye hota hai, doosri taraf ye — dono ko saath rakho. दोनों तरफ़ का एक फ़ायदा बोलो। और एक नुकसान भी साफ़ शब्दों में।',
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
          say: 'अब मुख्य बात। Yahan likho ki Photosynthesis asal me hai kya — ek aasan example ke saath, bina jargon ke. यहाँ definition को अपने शब्दों में दोबारा बोलो। एक common गलतफहमी भी बताओ।',
          subtitle: 'Photosynthesis',
          keyword: 'Photosynthesis',
          bullets: ['first point', 'second point', 'third point'],
        },
        {
          id: 's7',
          type: 'steps',
          say: 'अब step by step चलो। Pehle ye hota hai, phir ye, phir ye — har step ek line me samjhao. हर step में बोलो कि input क्या जाता है।',
          subtitle: 'Step by step',
          keyword: 'How it works',
          steps: [{label: 'STEP ONE', note: 'what happens'}, {label: 'STEP TWO', note: 'what happens'}, {label: 'STEP THREE', note: 'what happens'}],
        },
        {
          id: 's8',
          type: 'concept',
          say: 'अब मुख्य बात। Yahan likho ki Photosynthesis asal me hai kya — ek aasan example ke saath, bina jargon ke. यहाँ definition को अपने शब्दों में दोबारा बोलो। एक common गलतफहमी भी बताओ।',
          subtitle: 'Photosynthesis',
          keyword: 'Photosynthesis',
          bullets: ['first point', 'second point', 'third point'],
        },
        {
          id: 's9',
          type: 'steps',
          say: 'अब step by step चलो। Pehle ye hota hai, phir ye, phir ye — har step ek line me samjhao. हर step में बोलो कि input क्या जाता है।',
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
          say: 'Yahan ek number batao jo poori baat saaf kar de — kitna, kitne percent, kitne log. Number के बाद बोलो कि ये बड़ा है या छोटा।',
          subtitle: 'One number',
          keyword: 'By the numbers',
          value: '3',
          unit: 'items',
          caption: 'what the number means',
        },
        {
          id: 's11',
          type: 'compare',
          say: 'Farq saaf hai. Ek taraf ye hota hai, doosri taraf ye — dono ko saath rakho. दोनों तरफ़ का एक फ़ायदा बोलो। और एक नुकसान भी साफ़ शब्दों में।',
          subtitle: 'The difference',
          keyword: 'Compare',
          left: {label: 'WITHOUT', points: ['point one', 'point two']},
          right: {label: 'WITH', points: ['point one', 'point two']},
        },
        {
          id: 's12',
          type: 'concept',
          say: 'अब मुख्य बात। Yahan likho ki Photosynthesis asal me hai kya — ek aasan example ke saath, bina jargon ke. यहाँ definition को अपने शब्दों में दोबारा बोलो। एक common गलतफहमी भी बताओ।',
          subtitle: 'Photosynthesis',
          keyword: 'Photosynthesis',
          bullets: ['first point', 'second point', 'third point'],
        },
        {
          id: 's13',
          type: 'steps',
          say: 'अब step by step चलो। Pehle ye hota hai, phir ye, phir ye — har step ek line me samjhao. हर step में बोलो कि input क्या जाता है।',
          subtitle: 'Step by step',
          keyword: 'How it works',
          steps: [{label: 'STEP ONE', note: 'what happens'}, {label: 'STEP TWO', note: 'what happens'}, {label: 'STEP THREE', note: 'what happens'}],
        },
      ],
    },
    {
      title: 'Part 4',
      scenes: [
        {
          id: 's14',
          type: 'concept',
          say: 'अब मुख्य बात। Yahan likho ki Photosynthesis asal me hai kya — ek aasan example ke saath, bina jargon ke. यहाँ definition को अपने शब्दों में दोबारा बोलो। एक common गलतफहमी भी बताओ।',
          subtitle: 'Photosynthesis',
          keyword: 'Photosynthesis',
          bullets: ['first point', 'second point', 'third point'],
        },
        {
          id: 's15',
          type: 'steps',
          say: 'अब step by step चलो। Pehle ye hota hai, phir ye, phir ye — har step ek line me samjhao. हर step में बोलो कि input क्या जाता है।',
          subtitle: 'Step by step',
          keyword: 'How it works',
          steps: [{label: 'STEP ONE', note: 'what happens'}, {label: 'STEP TWO', note: 'what happens'}, {label: 'STEP THREE', note: 'what happens'}],
        },
        {
          id: 's16',
          type: 'number',
          say: 'Yahan ek number batao jo poori baat saaf kar de — kitna, kitne percent, kitne log. Number के बाद बोलो कि ये बड़ा है या छोटा।',
          subtitle: 'One number',
          keyword: 'By the numbers',
          value: '3',
          unit: 'items',
          caption: 'what the number means',
        },
        {
          id: 's17',
          type: 'recap',
          say: 'Bas itna yaad rakho. Teen baatein, aur kaam khatam. तीन बातें एक-एक line में दोहराओ। और एक छोटा homework दे दो viewer को।',
          subtitle: 'Quick recap',
          keyword: 'Remember',
          bullets: ['first point', 'second point', 'third point'],
        },
      ],
    },
  ],
};

export const BUILT_BY = 'built by raghv';
