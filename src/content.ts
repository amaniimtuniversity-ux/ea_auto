/**
 * ============================================================
 *  kathareel — content file (by raghv)
 *  Topic: RAG Explained
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
  slug: 'rag-demo',
  title: 'RAG Explained',
  tagline: 'The model needs your documents',
  chapters: [
    {
      title: 'Problem',
      scenes: [
        {
          id: 's1',
          type: 'hook',
          say: 'देखो भाई, एक language model अपनी याद से ही जवाब देता है। याद में ना हो, तो वो confident हो कर गलत भी बोल देता है।',
          subtitle: 'The model answers from memory',
          keyword: 'Wrong answer',
          bullets: ['No document', 'No source', 'Still confident'],
        },
        {
          id: 's2',
          type: 'concept',
          say: 'इसी gap को RAG भरता है। जवाब देने से पहले, उसको तुम्हारे document दिखा दिए जाते हैं।',
          subtitle: 'Show the source first',
          keyword: 'RAG',
          bullets: ['Retrieval', 'Then generation'],
        },
      ],
    },
    {
      title: 'Pipeline',
      scenes: [
        {
          id: 's3',
          type: 'steps',
          say: 'अब pipeline देखो। पहले document छोटे chunks में टूटे जाते हैं। हर chunk का एक number बनता है। सवाल आने पर सबसे करीबी chunks उठाए जाते हैं।',
          subtitle: 'Chunk → Embed → Retrieve',
          keyword: 'Pipeline',
          steps: [{label: 'CHUNK', note: 'split the docs'}, {label: 'EMBED', note: 'give each a number'}, {label: 'RETRIEVE', note: 'pick the closest'}],
        },
        {
          id: 's4',
          type: 'number',
          say: 'Model को पूरा document नहीं दिया जाता, सिर्फ तीन सबसे करीबी chunks दिए जाते हैं। इससे जवाब सस्ता भी रहता है, और check करना आसान भी।',
          subtitle: 'Only the closest chunks',
          keyword: 'Top 3',
          value: '3',
          unit: 'chunks',
          caption: 'closest matches go to the model',
        },
      ],
    },
    {
      title: 'Result',
      scenes: [
        {
          id: 's5',
          type: 'compare',
          say: 'फर्क साफ है। बिना RAG, जवाब सिर्फ याद से आता है। RAG के साथ, जवाब के साथ उसका source भी आता है। इसलिए study और research में ये ज़रूरी हो जाता है।',
          subtitle: 'Answer + source',
          keyword: 'Clear difference',
          left: {label: 'WITHOUT RAG', points: ['memory only', 'no proof']},
          right: {label: 'WITH RAG', points: ['your documents', 'source shown']},
        },
        {
          id: 's6',
          type: 'recap',
          say: 'बस इतना याद रखो। RAG का मतलब है, model को जवाब देने से पहले सही document दिखाओ। Chunk, embed, retrieve, फिर जवाब।',
          subtitle: 'Chunk, embed, retrieve',
          keyword: 'Remember',
          bullets: ['Chunk the documents', 'Embed to numbers', 'Retrieve, then answer'],
        },
      ],
    },
  ],
};

export const BUILT_BY = 'built by raghv';
