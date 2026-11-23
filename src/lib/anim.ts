/**
 * Small animation helpers (by raghv). Pure functions of the frame number, so a
 * render is deterministic and a frame can always be reproduced.
 */

export const clamp = (v: number, lo = 0, hi = 1) => Math.min(hi, Math.max(lo, v));

/** 0→1 ease-out over `len` frames, starts at `delay`. */
export const easeOut = (frame: number, delay = 0, len = 18) => {
  const t = clamp((frame - delay) / Math.max(1, len));
  return 1 - Math.pow(1 - t, 3);
};

/** 0→1 ease-in-out over `len` frames. */
export const easeInOut = (frame: number, delay = 0, len = 24) => {
  const t = clamp((frame - delay) / Math.max(1, len));
  return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
};

/** Fade in then hold; never fades out (use exit helpers for that). */
export const enter = (frame: number, delay = 0, len = 14) => clamp((frame - delay) / Math.max(1, len));

/** 1→0 fade-out over the last `len` frames of a scene. */
export const leave = (frame: number, sceneFrames: number, len = 12) =>
  clamp((sceneFrames - frame) / Math.max(1, len));

/** Slide-up offset in px (positive) that settles to 0. */
export const rise = (frame: number, delay = 0, distance = 26, len = 20) =>
  distance * (1 - easeOut(frame, delay, len));

/** Pop scale from 0.92 → 1. */
export const pop = (frame: number, delay = 0, len = 16) => 0.92 + 0.08 * easeOut(frame, delay, len);

/** Typewriter: how many characters of `text` are visible at this frame. */
export const typed = (frame: number, delay: number, charsPerFrame = 0.9, total = 0) => {
  const n = Math.floor(Math.max(0, frame - delay) * charsPerFrame);
  return total > 0 ? Math.min(total, n) : Math.max(0, n);
};

/** Stagger helper: delay for item i. */
export const stagger = (i: number, step = 8, start = 0) => start + i * step;
