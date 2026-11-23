import React from 'react';
import {AbsoluteFill, useCurrentFrame, useVideoConfig} from 'remotion';
import {COLORS, FONT, SAFE} from '../theme';
import {easeOut, pop, rise} from '../lib/anim';

/**
 * Opening title card + end card (by raghv). All on-screen text is English.
 */

export const TitleCard: React.FC<{title: string; tagline: string; meta: string}> = ({title, tagline, meta}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const out = easeOut(frame, fps * 2.4, 14); // fade away as the first scene starts

  return (
    <AbsoluteFill
      style={{
        alignItems: 'center',
        justifyContent: 'center',
        opacity: 1 - out,
        transform: `scale(${1 + out * 0.04})`,
      }}
    >
      <div
        style={{
          fontFamily: FONT.latin,
          fontSize: 19,
          letterSpacing: 6,
          textTransform: 'uppercase',
          color: 'var(--accent, #FF6B2C)',
          opacity: easeOut(frame, 6, 16),
          marginBottom: 26,
        }}
      >
        kathareel explains
      </div>

      <div
        style={{
          fontFamily: FONT.latin,
          fontSize: 108,
          fontWeight: 800,
          letterSpacing: -4,
          color: COLORS.text,
          opacity: easeOut(frame, 10, 18),
          transform: `translateY(${rise(frame, 10, 30, 22)}px) scale(${pop(frame, 10, 20)})`,
        }}
      >
        {title}
      </div>

      <div
        style={{
          marginTop: 26,
          height: 3,
          width: `${easeOut(frame, 20, 22) * 260}px`,
          background: 'var(--accent, #FF6B2C)',
          borderRadius: 3,
        }}
      />

      <div
        style={{
          marginTop: 26,
          fontFamily: FONT.latin,
          fontSize: 32,
          color: COLORS.textDim,
          opacity: easeOut(frame, 26, 18),
        }}
      >
        {tagline}
      </div>

      <div
        style={{
          marginTop: 18,
          fontFamily: FONT.latin,
          fontSize: 21,
          letterSpacing: 3,
          textTransform: 'uppercase',
          color: COLORS.textFaint,
          opacity: easeOut(frame, 34, 18),
        }}
      >
        {meta}
      </div>
    </AbsoluteFill>
  );
};

export const EndCard: React.FC<{builtBy: string}> = ({builtBy}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  return (
    <AbsoluteFill style={{alignItems: 'center', justifyContent: 'center'}}>
      <div
        style={{
          fontFamily: FONT.latin,
          fontSize: 46,
          fontWeight: 700,
          letterSpacing: -1,
          color: COLORS.text,
          opacity: easeOut(frame, 8, 20),
        }}
      >
        That's it.
      </div>
      <div
        style={{
          marginTop: 22,
          fontFamily: FONT.latin,
          fontSize: 24,
          letterSpacing: 3,
          textTransform: 'uppercase',
          color: 'var(--accent, #FF6B2C)',
          opacity: easeOut(frame, fps * 0.7, 20),
        }}
      >
        {builtBy}
      </div>
    </AbsoluteFill>
  );
};

/** Chapter bump: shows the chapter name for ~1s at each chapter start (YouTube style). */
export const ChapterBump: React.FC<{title: string; index: number; count: number}> = ({title, index, count}) => {
  const frame = useCurrentFrame();
  const a = easeOut(frame, 0, 10);
  return (
    <div
      style={{
        position: 'absolute',
        left: SAFE.left,
        top: SAFE.top - 34,
        display: 'flex',
        alignItems: 'center',
        gap: 14,
        opacity: a,
      }}
    >
      <div
        style={{
          fontFamily: FONT.latin,
          fontSize: 14,
          letterSpacing: 3,
          color: 'var(--accent, #FF6B2C)',
          border: `1.5px solid var(--accent-soft, #FF6B2C66)`,
          borderRadius: 99,
          padding: '6px 12px',
        }}
      >
        PART {index}/{count}
      </div>
      <div
        style={{
          fontFamily: FONT.latin,
          fontSize: 22,
          letterSpacing: 2,
          textTransform: 'uppercase',
          color: COLORS.textDim,
        }}
      >
        {title}
      </div>
    </div>
  );
};
