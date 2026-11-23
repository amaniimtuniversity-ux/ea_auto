import React from 'react';
import {AbsoluteFill, Audio, Sequence, staticFile, useCurrentFrame} from 'remotion';
import {COLORS, FONT} from './theme';
import {BEATS, CHAPTERS, FPS, TOTAL_FRAMES} from './timeline';
import {CONTENT, BUILT_BY} from './content';
import {Fonts} from './lib/fonts';
import {Subtitles} from './components/Subtitle';
import {CutFlash, Grid, ProgressBar, Signature} from './components/Chrome';
import {EndCard, TitleCard} from './components/Cards';
import {
  CompareScene,
  ConceptScene,
  HookScene,
  NumberScene,
  RecapScene,
  StepsScene,
} from './components/Scenes';

/**
 * Main composition (by raghv).
 *
 * Structure per beat (one beat = one Hindi sentence group):
 *   beat.from .......... scene + caption fade in
 *   beat.from+1.1s ..... keyword appears under the caption
 *   beat.to ............ scene ends, short dip, next beat
 *
 * Everything on screen is English. The Hindi is only in the audio.
 */

const scenePropsFor = (id: string) => {
  for (const ch of CONTENT.chapters) {
    const s = ch.scenes.find((x) => x.id === id);
    if (s) return s;
  }
  return undefined;
};

const SceneBody: React.FC<{id: string}> = ({id}) => {
  const s = scenePropsFor(id);
  if (!s) return null;
  switch (s.type) {
    case 'hook':
      return <HookScene keyword={s.keyword} bullets={s.bullets} />;
    case 'concept':
      return <ConceptScene keyword={s.keyword} bullets={s.bullets} />;
    case 'steps':
      return <StepsScene keyword={s.keyword} steps={s.steps} />;
    case 'compare':
      return <CompareScene keyword={s.keyword} left={s.left} right={s.right} />;
    case 'number':
      return <NumberScene value={s.value} unit={s.unit} caption={s.caption} bullets={s.bullets} />;
    case 'recap':
      return <RecapScene keyword={s.keyword} bullets={s.bullets} />;
    default:
      return null;
  }
};

/** Small "PART n/3 · Chapter" label for the first ~1.2s of each chapter. */
const ChapterLabel: React.FC<{chapter: number}> = ({chapter}) => {
  const frame = useCurrentFrame();
  if (frame > 36) return null;
  const ch = CHAPTERS.find((c) => c.n === chapter);
  if (!ch) return null;
  const opacity = frame < 26 ? 1 : 1 - (frame - 26) / 10;
  return (
    <div
      style={{
        position: 'absolute',
        left: 72,
        top: 34,
        display: 'flex',
        alignItems: 'center',
        gap: 12,
        opacity,
      }}
    >
      <div
        style={{
          fontFamily: FONT.latin,
          fontSize: 13,
          letterSpacing: 2.5,
          color: COLORS.accent,
          border: `1.5px solid ${COLORS.accent}66`,
          borderRadius: 99,
          padding: '5px 11px',
        }}
      >
        PART {ch.n}/{CHAPTERS.length}
      </div>
      <div
        style={{
          fontFamily: FONT.latin,
          fontSize: 19,
          letterSpacing: 2.4,
          textTransform: 'uppercase',
          color: COLORS.textDim,
        }}
      >
        {ch.title}
      </div>
    </div>
  );
};

export const Explainer: React.FC = () => {
  const titleEnd = BEATS.length ? BEATS[0].from - 2 : 60;
  const endStart = TOTAL_FRAMES - 96;

  return (
    <AbsoluteFill style={{background: COLORS.bg}}>
      <Fonts />
      <Grid />

      {/* soft glow behind the content so the dark canvas is not flat */}
      <AbsoluteFill
        style={{
          background: `radial-gradient(900px 520px at 22% 18%, ${COLORS.accent}14, transparent 70%),
                       radial-gradient(760px 520px at 82% 78%, ${COLORS.cool}12, transparent 70%)`,
        }}
      />

      <Audio src={staticFile(`voice/${CONTENT.slug}.wav`)} />

      {/* opening card */}
      <Sequence from={0} durationInFrames={titleEnd}>
        <TitleCard
          title={CONTENT.title}
          tagline={CONTENT.tagline}
          meta={`${CHAPTERS.length} parts · ${Math.round(TOTAL_FRAMES / FPS)} sec · hinglish voice`}
        />
      </Sequence>

      {/* scenes */}
      {BEATS.map((b) => (
        <Sequence key={b.id} from={b.from - 1} durationInFrames={b.to - b.from + 2}>
          <AbsoluteFill>
            <SceneBody id={b.id} />
            <ChapterLabel chapter={b.chapter} />
            <Subtitles subtitle={b.subtitle} keyword={b.keyword} startFrame={0} endFrame={b.to - b.from + 2} />
          </AbsoluteFill>
        </Sequence>
      ))}

      {/* scene-change dips */}
      {BEATS.map((b) => (
        <Sequence key={`dip-${b.id}`} from={Math.max(0, b.from - 4)} durationInFrames={9}>
          <CutFlash atFrame={4} />
        </Sequence>
      ))}

      {/* end card */}
      <Sequence from={endStart} durationInFrames={TOTAL_FRAMES - endStart}>
        <EndCard builtBy={BUILT_BY} />
      </Sequence>

      <Signature />
      <ProgressBar />
    </AbsoluteFill>
  );
};
