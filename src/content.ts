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
          say: 'Dekho bhai, ek language model apni yaad se hi jawab deta hai. Yaad me na ho, to wo confident ho kar galat bhi bol deta hai.',
          subtitle: 'The model answers from memory',
          bullets: ['No document', 'No source', 'Still confident'],
        },
        {
          id: 's2',
          type: 'concept',
          keyword: 'RAG',
          say: 'Isi gap ko RAG bharta hai. Jawab dene se pehle, usko tumhare document dikha diye jaate hain.',
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
          say: 'Ab pipeline dekho. Pehle document chhote chunks me toote jaate hain. Har chunk ka ek number banta hai. Sawaal aane par sabse kareebi chunks uthaye jaate hain.',
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
          say: 'Model ko poora document nahi diya jaata, sirf teen sabse kareebi chunks diye jaate hain. Isse jawab sasta bhi rehta hai, aur check karna aasan bhi.',
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
          say: 'Farq saaf hai. Bina RAG, jawab sirf yaad se aata hai. RAG ke saath, jawab ke saath uska source bhi aata hai. Isliye study aur research me ye zaroori ho jaata hai.',
          subtitle: 'Answer + source',
          left: {label: 'WITHOUT RAG', points: ['memory only', 'no proof']},
          right: {label: 'WITH RAG', points: ['your documents', 'source shown']},
        },
        {
          id: 's6',
          type: 'recap',
          keyword: 'Remember',
          say: 'Bas itna yaad rakho. RAG ka matlab hai, model ko jawab dene se pehle sahi document dikhao. Chunk, embed, retrieve, phir jawab.',
          subtitle: 'Chunk, embed, retrieve',
          bullets: ['Chunk the documents', 'Embed to numbers', 'Retrieve, then answer'],
        },
      ],
    },
  ],
};

export const BUILT_BY = 'built by raghv';
