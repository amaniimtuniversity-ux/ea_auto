import React from 'react';
import {AbsoluteFill, useCurrentFrame, useVideoConfig} from 'remotion';
import {COLORS, accentColor, withAlpha} from '../theme';

/**
 * Background styles + scene transitions (by raghv).
 *
 * `content.ts` ka `background` field yahan aata hai:
 *   glow  — do soft radial glows (default, sabase soft)
 *   grid  — technical grid lines
 *   dots  — dotted grid
 *   plain — sirf flat dark canvas
 *   mesh  — gradient mesh (do accent blobs, dhime dhime move karte hain)
 *
 * Transition scene ke andar lagta hai (frame 0 se), taaki cut hard na lage.
 */

const Dots: React.FC = () => (
  <AbsoluteFill
    style={{
      backgroundImage: `radial-gradient(${COLORS.panelEdge} 1.5px, transparent 1.5px)`,
      backgroundSize: '34px 34px',
      opacity: 0.5,
    }}
  />
);

const Lines: React.FC = () => (
  <AbsoluteFill
    style={{
      backgroundImage: `linear-gradient(${COLORS.line} 1px, transparent 1px),
                        linear-gradient(90deg, ${COLORS.line} 1px, transparent 1px)`,
      backgroundSize: '64px 64px',
      opacity: 0.55,
    }}
  />
);

const Mesh: React.FC<{accent: string; frame: number}> = ({accent, frame}) => {
  const t = frame / 150;
  const x1 = 22 + Math.sin(t) * 6;
  const y1 = 18 + Math.cos(t * 0.8) * 5;
  const x2 = 82 + Math.cos(t * 0.7) * 6;
  const y2 = 78 + Math.sin(t * 0.9) * 5;
  return (
    <AbsoluteFill
      style={{
        background: `radial-gradient(760px 520px at ${x1}% ${y1}%, ${withAlpha(accent, 0.16)}, transparent 68%),
                     radial-gradient(680px 480px at ${x2}% ${y2}%, ${withAlpha(COLORS.cool, 0.12)}, transparent 68%)`,
      }}
    />
  );
};

export const Background: React.FC<{style?: string; accent?: string}> = ({style, accent}) => {
  const frame = useCurrentFrame();
  const color = accentColor(accent);

  if (style === 'plain') return null;
  if (style === 'grid') {
    return (
      <>
        <Lines />
        <Mesh accent={color} frame={frame} />
      </>
    );
  }
  if (style === 'dots') {
    return (
      <>
        <Dots />
        <Mesh accent={color} frame={frame} />
      </>
    );
  }
  if (style === 'mesh') return <Mesh accent={color} frame={frame} />;

  // glow (default)
  return (
    <AbsoluteFill
      style={{
        background: `radial-gradient(900px 520px at 22% 18%, ${withAlpha(color, 0.09)}, transparent 70%),
                     radial-gradient(760px 520px at 82% 78%, ${withAlpha(COLORS.cool, 0.07)}, transparent 70%)`,
      }}
    />
  );
};

/* ------------------------------------------------------------ transitions */

export type TransitionName = 'fade' | 'slide' | 'pop' | 'zoom' | 'wipe';

/**
 * Transition ka poora style — ek hi jagah, taaki scene aur overlay dono
 * bilkul same maths use karein (warna transition "dikhta" nahi hai).
 * p = progress 0..1 (eased).
 */
export const transitionStyle = (kind: string | undefined, p: number): React.CSSProperties => {
  const e = 1 - Math.pow(1 - Math.max(0, Math.min(1, p)), 3);
  const OUT: React.CSSProperties = {
    opacity: e,
    transformOrigin: 'center center',
    willChange: 'opacity, transform',
  };
  switch (kind) {
    case 'slide':
      OUT.transform = `translateY(${(1 - e) * 56}px)`;
      break;
    case 'pop':
      OUT.transform = `scale(${0.93 + 0.07 * e})`;
      break;
    case 'zoom':
      OUT.transform = `scale(${1.14 - 0.14 * e})`;
      OUT.opacity = Math.min(1, e * 1.6);
      break;
    case 'wipe':
      OUT.clipPath = `inset(0 ${100 - e * 100}% 0 0)`;
      OUT.opacity = Math.min(1, e * 1.5);
      break;
    default:
      break; // fade
  }
  return OUT;
};

/** @deprecated — purana API, transitionStyle() use karo. */
export const transitionProgress = (frame: number, len: number): number =>
  len <= 1 ? 1 : Math.min(1, frame / len);

/**
 * Non-fade transitions ka ek chhota "ghoomta hua" wrapper:
 * background aur subtitle ko chhodd kar sirf content ko animate karta hai.
 */
export const SceneEntrance: React.FC<{
  kind?: string;
  durationInFrames: number;
  children: React.ReactNode;
}> = ({kind, durationInFrames, children}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const len = Math.min(Math.round(fps * 0.5), Math.max(2, Math.round(durationInFrames * 0.4)));
  return (
    <AbsoluteFill style={transitionStyle(kind, frame / Math.max(1, len))}>{children}</AbsoluteFill>
  );
};
