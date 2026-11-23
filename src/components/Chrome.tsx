import React from 'react';
import {AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig} from 'remotion';
import {COLORS, FONT, SAFE, VIDEO} from '../theme';
import {CHAPTERS, TOTAL_FRAMES} from '../timeline';
import {easeOut} from '../lib/anim';

/**
 * Persistent chrome (by raghv): progress bar with chapter segments at the bottom,
 * and a small "by raghv" mark top-right. All labels are English.
 */
export const ProgressBar: React.FC = () => {
  const frame = useCurrentFrame();
  const {durationInFrames} = useVideoConfig();
  const progress = Math.min(1, frame / Math.max(1, durationInFrames - 1));

  return (
    <div style={{position: 'absolute', left: 0, right: 0, bottom: 0, height: 46}}>
      <div style={{position: 'absolute', inset: 0, background: '#0F1219', opacity: 0.92}} />
      <div
        style={{
          position: 'absolute',
          left: 0,
          top: 0,
          bottom: 0,
          width: `${progress * 100}%`,
          background: `linear-gradient(90deg, ${COLORS.accent}00, ${COLORS.accent}55)`,
        }}
      />
      <div
        style={{
          position: 'absolute',
          left: 0,
          top: 0,
          height: 3,
          width: `${progress * 100}%`,
          background: COLORS.accent,
        }}
      />
      {CHAPTERS.map((c, i) => {
        const active = frame + 1 >= c.from && frame + 1 <= c.to;
        const done = frame + 1 > c.to;
        const total = TOTAL_FRAMES || 1;
        const left = ((c.from - 1) / total) * 100;
        const width = ((c.to - c.from + 1) / total) * 100;
        return (
          <div
            key={c.n}
            style={{
              position: 'absolute',
              left: `${left}%`,
              width: `${width}%`,
              top: 0,
              bottom: 0,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontFamily: FONT.latin,
              fontSize: 17,
              fontWeight: active ? 700 : 500,
              letterSpacing: 1.4,
              textTransform: 'uppercase',
              color: active ? COLORS.text : done ? COLORS.textFaint : COLORS.textFaint,
              opacity: active ? 1 : 0.62,
              borderLeft: i === 0 ? 'none' : `1px solid ${COLORS.line}`,
            }}
          >
            {c.title}
          </div>
        );
      })}
    </div>
  );
};

/** Small watermark so the video is identifiable without stealing attention. */
export const Signature: React.FC = () => {
  const frame = useCurrentFrame();
  const opacity = Math.min(easeOut(frame, 20, 20), 0.42);
  return (
    <div
      style={{
        position: 'absolute',
        top: SAFE.top - 46,
        right: SAFE.right,
        fontFamily: FONT.latin,
        fontSize: 15,
        letterSpacing: 2.4,
        textTransform: 'uppercase',
        color: COLORS.textFaint,
        opacity,
      }}
    >
      kathareel
    </div>
  );
};

/**
 * Scene transition dip: a very short dark flash at every scene change so the eye
 * registers a new beat (YouTube-style cut), without a hard jump.
 */
export const CutFlash: React.FC<{atFrame: number}> = ({atFrame}) => {
  const frame = useCurrentFrame();
  const d = frame - atFrame;
  if (d < 0 || d > 7) return null;
  const opacity = interpolate(d, [0, 3, 7], [0.55, 0.18, 0]);
  return <AbsoluteFill style={{background: '#000', opacity, pointerEvents: 'none'}} />;
};

/** Faint dot grid so empty areas never look dead. */
export const Grid: React.FC = () => (
  <AbsoluteFill
    style={{
      backgroundImage: `radial-gradient(${COLORS.panelEdge} 1px, transparent 1px)`,
      backgroundSize: '38px 38px',
      opacity: 0.35,
    }}
  />
);
