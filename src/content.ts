/**
 * ============================================================
 *  kathareel — content file (by raghv)
 *  Ye ek hi file hai jise tum apne topic ke liye badalte ho.
 * ============================================================
 *
 * RULES
 *  - `say`      : jo bola jayega (Devanagari + English technical words). Voice isi se banti hai.
 *  - `subtitle` : screen par jo dikhega. ALWAYS ENGLISH ONLY (board rule).
 *                 Chhota rakho: ek line me 2-3 words per block.
 *  - `bullets`  : scene ke on-screen English points.
 *  - `keyword`  : scene ka hero word (bada, accent colour me).
 *
 * Scene types (visual ka type):
 *   'hook'      problem/opening, bada sawal
 *   'concept'   ek idea + uska short English tag
 *   'steps'     process/pipeline (3-5 steps, ek ek karke highlight)
 *   'compare'   do cheezein: left vs right
 *   'number'    ek bada number/stat
 *   'recap'     summary points
 */

export type SceneType = 'hook' | 'concept' | 'steps' | 'compare' | 'number' | 'recap';

export type Scene = {
  id: string;
  type: SceneType;
  /** Hindi sentence(s), Devanagari. English technical words bilkul theek hain. */
  say: string;
  /** English on-screen caption for this beat (1 short line). */
  subtitle: string;
  /** Big on-screen word/phrase. English only. */
  keyword?: string;
  bullets?: string[];
  /** steps */
  steps?: {label: string; note?: string}[];
  /** compare */
  left?: {label: string; points: string[]};
  right?: {label: string; points: string[]};
  /** number */
  value?: string;
  unit?: string;
  caption?: string;
};

export type Chapter = {
  title: string; // English, progress bar par dikhega
  scenes: Scene[];
};

export type VideoContent = {
  slug: string;
  title: string; // English, opening card
  tagline: string; // English, opening card (one line)
  chapters: Chapter[];
};

/* ------------------------------------------------------------------ */
/*  DEMO CONTENT — "RAG kya hai?" (isko apne topic se replace karo)     */
/* ------------------------------------------------------------------ */

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
          keyword: 'Wrong answer',
          say: 'देखो भाई, एक language model अपनी याद से ही जवाब देता है। याद में ना हो, तो वो confident हो कर गलत भी बोल देता है।',
          subtitle: 'The model answers from memory',
          bullets: ['No document', 'No source', 'Still confident'],
        },
        {
          id: 's2',
          type: 'concept',
          keyword: 'RAG',
          say: 'इसी gap को RAG भरता है। जवाब देने से पहले, उसको तुम्हारे document दिखा दिए जाते हैं।',
          subtitle: 'Show the source first',
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
          keyword: 'Pipeline',
          say: 'अब pipeline देखो। पहले document छोटे chunks में टूटे जाते हैं। हर chunk का एक number बनता है। सवाल आने पर सबसे करीबी chunks उठाए जाते हैं।',
          subtitle: 'Chunk → Embed → Retrieve',
          steps: [
            {label: 'CHUNK', note: 'split the docs'},
            {label: 'EMBED', note: 'give each a number'},
            {label: 'RETRIEVE', note: 'pick the closest'},
          ],
        },
        {
          id: 's4',
          type: 'number',
          keyword: 'Top 3',
          say: 'Model को पूरा document नहीं दिया जाता, सिर्फ तीन सबसे करीबी chunks दिए जाते हैं। इससे जवाब सस्ता भी रहता है, और check करना आसान भी।',
          subtitle: 'Only the closest chunks',
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
          keyword: 'Clear difference',
          say: 'फर्क साफ है। बिना RAG, जवाब सिर्फ याद से आता है। RAG के साथ, जवाब के साथ उसका source भी आता है। इसलिए study और research में ये ज़रूरी हो जाता है।',
          subtitle: 'Answer + source',
          left: {label: 'WITHOUT RAG', points: ['memory only', 'no proof']},
          right: {label: 'WITH RAG', points: ['your documents', 'source shown']},
        },
        {
          id: 's6',
          type: 'recap',
          keyword: 'Remember',
          say: 'बस इतना याद रखो। RAG का मतलब है, model को जवाब देने से पहले सही document दिखाओ। Chunk, embed, retrieve, फिर जवाब।',
          subtitle: 'Chunk, embed, retrieve',
          bullets: ['Chunk the documents', 'Embed to numbers', 'Retrieve, then answer'],
        },
      ],
    },
  ],
};

export const BUILT_BY = 'built by raghv';
