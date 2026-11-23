/**
 * kathareel — theme tokens (by raghv)
 *
 * Look: dark charcoal canvas, big Devanagari + Latin type, one accent colour per role.
 * Everything is a plain constant so scenes never invent their own colours.
 */

export const COLORS = {
  bg: '#0B0D12',
  bgSoft: '#12151D',
  panel: '#171B25',
  panelEdge: '#2A3040',
  text: '#F4F6FB',
  textDim: '#A7AFBF',
  textFaint: '#6C7484',
  accent: '#FF6B2C', // orange — the "hero" of the current beat
  accentSoft: '#FFB38A',
  cool: '#3BC9F5', // blue — data / flow
  good: '#5BE58B',
  warn: '#FF4D5E',
  line: '#39405280',
} as const;

/** Fonts are loaded by <Fonts/> from public/fonts (local files, no network at render time). */
export const FONT = {
  /** Devanagari + Latin body: Noto Sans covers both scripts in one family. */
  sans: "'Noto Sans', 'NotoSansDevanagari', sans-serif",
  /** Devanagari-first display font for big Hindi words. */
  deva: "'NotoSansDevanagari', 'Noto Sans', sans-serif",
  /** Tight modern Latin for English keywords, numbers, code. */
  latin: "'Inter', 'Noto Sans', sans-serif",
  mono: "'JetBrainsMono', monospace",
} as const;

/** Video geometry. */
export const VIDEO = {
  width: 1280,
  height: 720,
  fps: 30,
} as const;

/** Safe areas: keep content out of the subtitle band and the progress bar. */
export const SAFE = {
  top: 96,
  bottom: 200, // subtitles live below this
  left: 72,
  right: 72,
} as const;

/** Subtitle band (2 lines max, centred). */
export const SUBTITLE = {
  top: 556,
  size: 40,
  lineHeight: 1.28,
  maxWidth: 1120,
} as const;
