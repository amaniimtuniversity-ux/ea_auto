/**
 * ============================================================
 *  kathareel — content file (by raghv)
 *  Topic: Machine learning
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
  /** Screen layout — src/components/Scenes.tsx me har naam ka component hai. */
  layout?: string;
  /** Scene ka apna accent (video ke accent ko override karta hai). */
  accent?: string;
  /** Entry animation: fade | slide | pop | zoom | wipe */
  transition?: string;
  /** Definition / explanation card jo screen par popup ki tarah aata hai. */
  note?: string;
};

export type Chapter = {
  title: string;
  scenes: Scene[];
};

export type VideoContent = {
  slug: string;
  title: string;
  tagline: string;
  /** Poori video ka accent: orange | blue | green | violet | pink | amber | red | teal */
  accent?: string;
  /** Background: glow | grid | dots | plain | mesh */
  background?: string;
  chapters: Chapter[];
};

export const CONTENT: VideoContent = {
  slug: 'machine-learning',
  title: 'Machine learning',
  tagline: 'In Hindi, step by step',
  accent: 'blue',
  background: 'mesh',
  chapters: [
    {
      title: 'Part 1',
      scenes: [
        {
          id: 's1',
          type: 'hook',
          say: 'देखो भाई, Machine learning को एक line में समझो तो Model, Data और Training — यही तीन चीज़ें इसका दिल हैं।',
          subtitle: 'What is Machine learning',
          keyword: 'Machine learning',
          layout: 'bigword',
          transition: 'slide',
          bullets: ['Model', 'Data', 'Training'],
          note: 'Machine learning = Model, Data, Training working together.',
        },
        {
          id: 's2',
          type: 'concept',
          say: 'Machine learning में यह हिस्सा सबसे ज़्यादा काम का है। Machine learning के कई रूप हैं — जैसे Supervised, Unsupervised और Reinforcement।',
          subtitle: 'Types of Machine learning',
          keyword: 'TYPES',
          layout: 'cards',
          transition: 'pop',
          bullets: ['Supervised', 'Unsupervised', 'Reinforcement'],
          note: 'Machine learning splits into 3 kinds — pick by the job, not by hype.',
        },
      ],
    },
    {
      title: 'Part 2',
      scenes: [
        {
          id: 's3',
          type: 'concept',
          say: 'चलो, Machine learning को आसान भाषा में समझते हैं। ज़रूरी बात यह है कि Machine learning सिर्फ़ किताबी नहीं है। असली ज़िंदगी में इसे देखो तो बात तुरंत बैठ जाती है।',
          subtitle: 'Where Machine learning is used',
          keyword: 'IN PRACTICE',
          layout: 'bullets',
          transition: 'zoom',
          bullets: ['Spam filters', 'Product recommendations', 'Fraud detection'],
          note: 'Spam filters is the clearest example of Machine learning.',
        },
        {
          id: 's4',
          type: 'concept',
          say: 'अब Machine learning की मुख्य बात समझो। सच यह भी है कि Machine learning हर जगह सही नहीं बैठता।',
          subtitle: 'Limits of Machine learning',
          keyword: 'LIMITS',
          layout: 'two-col',
          transition: 'wipe',
          bullets: ['explicit if-else', 'breaks on new cases', 'human rewrites it'],
          note: 'Where Machine learning breaks — knowing this saves real pain.',
        },
      ],
    },
    {
      title: 'Part 3',
      scenes: [
        {
          id: 's5',
          type: 'recap',
          say: 'बस इतना याद रखो। Machine learning क्या है, यह कैसे काम करता है, और असली ज़िंदगी में कहाँ काम आता है —',
          subtitle: 'Recap',
          keyword: 'RECAP',
          layout: 'takeaways',
          transition: 'fade',
          bullets: ['Definition', 'How it works', 'Where it is used'],
          note: 'Three lines and Machine learning is yours.',
        },
      ],
    },
  ],
};

export const BUILT_BY = 'built by raghv';
