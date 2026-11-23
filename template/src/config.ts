/**
 * Video-level config (the main file to edit per topic; the other is script/narration.txt).
 * Sentence ids (S01...) come from scripts/tts_build.py generated timeline.ts;
 * chapter count and titles come from narration.txt `# CHAPTER n Title` lines.
 *
 * BOARD RULE (by raghv): Everything written on the board / screen in the video
 * (title, chapter cards, HUD, progress bar, subtitles, labels) is ENGLISH ONLY.
 * Do not put Chinese / Devanagari / Hindi text on screen. Subtitles, titles, HUD,
 * chapters and labels are English; the voiceover may be Hinglish (see `lang`).
 */
export type HudEntry = {fromS: string; toS: string; text: string; tech?: string; fromOffset?: number; toOffset?: number; w?: number};
export type RailSpec = {steps: string[]; switchS: string[]; fromS: string; toS: string};
export const VIDEO = {
  slug: 'demo', // assets folder public/assets/<slug>/ (voiceover audio.wav written by tts_build.py)
  /**
   * Video language / voice:
   *   'en' = English narration + English board (default).
   *   'hi' = HINGLISH: narration is Hindi written in Latin script ("matlab kya hai"),
   *          the voiceover uses a Hindi voice (edge-tts hi-IN-MadhurNeural), and the
   *          BOARD STILL STAYS ENGLISH - `lang: 'hi'` only switches the voice and the
   *          script-heuristic, typography stays on the English metrics.
   *   'zh' = Chinese narration; not used by this skill's default board rule.
   * BOARD RULE (by raghv): everything written on screen is English only.
   */
  lang: 'en' as 'zh' | 'en' | 'hi',
  /**
   * Backdrop: 'dots' dot-field wave (default, `common/DotFieldBg.tsx`) | 'stars' star field + fog gradient.
   */
  bg: 'dots' as 'stars' | 'dots',
  /**
   * Title (English only on the board).
   * big: main word / abbreviation in Audiowide, rest: leave '' for English-only board,
   * en: full name or subtitle, tagline: one-line hook in English.
   */
  title: {big: 'TOPIC', rest: '', en: 'Full Name of the Topic', tagline: 'One line hook in English'},
  /** End credit card (fade to black + ~2s after last subtitle, aboveBar; set to null if not needed).
   *  Example: {kicker: 'BASED ON', title: '<paper / book / report title>', byline: '<author - source - year>', note: 'all visuals drawn in code'} */
  credit: null as {kicker: string; title: string; byline: string; note: string} | null,
  /** End credit line (on by default): below the credit card if present, otherwise centered alone. Set to '' to drop. */
  builtBy: 'built by raghv',
  /** Chapter English subtitles (order matches narration CHAPTER 1..n; chapter cards show from chapter 2; leave '' to not render).
   *  Write English keywords or step sequence for this chapter (`Build - Run - Trace`). */
  chapterTech: ['Chapter One', 'Chapter Two'],
  /** Top HUD capsule (current section name): by sentence id range; auto no-gap between neighbours; auto fade across chapter cards.
   *  text is a navigation label in ENGLISH ONLY: a noun phrase saying what this section covers (`Knowledge Base`, `Hybrid Search`).
   *  tech is the small English subtitle under the capsule (grey 22px, `TechSub`): only real English terms that must be shown. */
  hud: [
    {fromS: 'S01', toS: 'S01', text: 'Section One'},
    {fromS: 'S02', toS: 'S02', text: 'Section Two', tech: 'Optional English'},
  ] as HudEntry[],
  /** Pipeline rail (optional, only for chapters with a real step order; max one per chapter, max five steps): y118-162.
   *  Example: {steps: ['Step One', 'Step Two', 'Step Three'], switchS: ['S12', 'S14', 'S16'], fromS: 'S12', toS: 'S18'} */
  rails: [] as RailSpec[],
  /** Title frames (LEAD+CHAPTER_GAP from tts_build, usually 85) and end fade to black */
  endingFade: 30,
};
