import React from 'react';
import {AbsoluteFill, useCurrentFrame, useVideoConfig} from 'remotion';
import {COLORS, FONT, SUBTITLE} from '../theme';
import {easeOut} from '../lib/anim';

/**
 * Subtitle layer (by raghv).
 * On-screen text is ALWAYS English (board rule) — the Hindi is in the voice.
 * Two beats per scene: the caption first, then the keyword underneath in accent.
 */
export const Subtitles: React.FC<{subtitle: string; keyword?: string; startFrame: number; endFrame: number}> = ({
  subtitle,
  keyword,
  startFrame,
  endFrame,
}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const local = frame - startFrame;
  const showKeyword = keyword && local > fps * 1.1;

  const inA = easeOut(local, 2, 12);
  const outA = easeOut(endFrame - frame, 0, 10);
  const opacity = Math.min(inA, outA);

  return (
    <AbsoluteFill style={{pointerEvents: 'none'}}>
      <div
        style={{
          position: 'absolute',
          left: 0,
          right: 0,
          top: SUBTITLE.top,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          gap: 10,
          opacity,
        }}
      >
        <div
          style={{
            fontFamily: FONT.latin,
            fontSize: SUBTITLE.size,
            fontWeight: 700,
            letterSpacing: -0.2,
            color: COLORS.text,
            textAlign: 'center',
            maxWidth: SUBTITLE.maxWidth,
            lineHeight: SUBTITLE.lineHeight,
            textShadow: '0 2px 18px rgba(0,0,0,.85)',
          }}
        >
          {subtitle}
        </div>
        {showKeyword ? (
          <div
            style={{
              fontFamily: FONT.latin,
              fontSize: 22,
              fontWeight: 600,
              letterSpacing: 3,
              textTransform: 'uppercase',
              color: COLORS.accent,
              opacity: easeOut(local, fps * 1.1, 10),
            }}
          >
            {keyword}
          </div>
        ) : null}
      </div>
    </AbsoluteFill>
  );
};
