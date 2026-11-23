import React from 'react';
import {useCurrentFrame, useVideoConfig} from 'remotion';
import {COLORS, FONT} from '../theme';

/**
 * NoteCard — definition / explanation ka pop-up card (by raghv).
 *
 * User ki demand: "jo definition ya kuch or hai wo pop up ki tarah screen per
 * bhi aaye". Isliye roz sirf subtitle padhne ko nahi milta — scene ka `note`
 * ek card me aata hai, thoda der baad, aur halka slide karke chala jaata hai.
 *
 * Timing: scene ke ~18% par appear, ~60% tak rehta hai, phir out.
 * Position: upar-daayein, subtitle band ke upar — content se clash nahi.
 * Screen par text English rehta hai (project rule).
 */

const SAFE_BOTTOM = 354; // subtitle band (top: 556) se upar

export const NoteCard: React.FC<{
  note?: string;
  durationInFrames: number;
  /** wide = versus / table / two-col: content poora chauda hota hai, isliye upar-baayein */
  wide?: boolean;
}> = ({note, durationInFrames, wide}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  if (!note || !note.trim() || durationInFrames < fps * 1.5) return null;

  const appear = Math.round(Math.min(fps * 1.1, durationInFrames * 0.2));
  const leave = Math.round(Math.max(appear + fps * 1.2, durationInFrames * 0.6));
  if (frame < appear - 1 || frame > leave + 10) return null;

  const ease = (p: number) => 1 - Math.pow(1 - Math.max(0, Math.min(1, p)), 3);
  const inP = ease((frame - appear) / 10);
  const outP = ease((frame - leave) / 9);
  const opacity = Math.min(inP, 1 - outP);
  const dy = (1 - inP) * 16 - outP * 10;
  const long = note.length > 78;

  return (
    <div
      style={{
        position: 'absolute',
        ...(wide ? {left: 64, top: 96} : {right: 64, top: 118}),
        maxWidth: wide ? 380 : long ? 470 : 400,
        padding: '16px 20px 16px 18px',
        borderRadius: 14,
        background: 'rgba(23,27,37,.92)',
        border: '1px solid var(--accent-host-soft, var(--accent-soft, #FF6B2C66))',
        borderLeft: '3px solid var(--accent-host, var(--accent, #FF6B2C))',
        boxShadow: '0 18px 40px rgba(0,0,0,.55)',
        opacity,
        transform: `translateY(${dy}px)`,
        pointerEvents: 'none',
      }}
    >
      <div
        style={{
          fontFamily: FONT.latin,
          fontSize: 11,
          letterSpacing: 2.2,
          textTransform: 'uppercase',
          color: 'var(--accent-host, var(--accent, #FF6B2C))',
          marginBottom: 8,
        }}
      >
        Definition
      </div>
      <div
        style={{
          fontFamily: FONT.latin,
          fontSize: long ? 19 : 21,
          lineHeight: 1.42,
          color: COLORS.text,
          fontWeight: 500,
        }}
      >
        {note}
      </div>
    </div>
  );
};
