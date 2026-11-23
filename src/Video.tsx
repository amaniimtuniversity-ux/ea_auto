import React from 'react';
import {AbsoluteFill, Audio, Sequence, staticFile, useCurrentFrame} from 'remotion';
import {COLORS, FONT} from './theme';
import {BEATS, CHAPTERS, FPS, TOTAL_FRAMES, type Beat} from './timeline';
import {CONTENT, BUILT_BY} from './content';
import {Fonts} from './lib/fonts';
import {Subtitles} from './components/Subtitle';
import {CutFlash, Grid, ProgressBar, Signature} from './components/Chrome';
import {Background, SceneEntrance} from './components/Backdrop';
import {NoteCard} from './components/NoteCard';
import {accentColor, withAlpha} from './theme';
import {EndCard, TitleCard} from './components/Cards';
import {
  BigWordScene,
  BulletsScene,
  CardsScene,
  ChecklistScene,
  CompareScene,
  ConceptScene,
  HookScene,
  NumberedScene,
  NumberScene,
  QuoteScene,
  RecapScene,
  StatScene,
  StepsScene,
  TableScene,
  TakeawaysScene,
  TimelineScene,
  TwoColScene,
  VersusScene,
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

/**
 * `layout` se screen chunte hain, `type` se sirf content ka matlab.
 * Isliye ek hi type ke do scenes alag dikh sakte hain — pattern repeat nahi hota.
 */
const LayoutBody: React.FC<{s: NonNullable<ReturnType<typeof scenePropsFor>>}> = ({s}) => {
  const p = {keyword: s.keyword, bullets: s.bullets, steps: s.steps,
             left: s.left, right: s.right, value: s.value, unit: s.unit, caption: s.caption};
  switch (s.layout) {
    case 'quote': return <QuoteScene {...p} />;
    case 'bigword': return <BigWordScene {...p} />;
    case 'bullets': return <BulletsScene {...p} />;
    case 'cards': return <CardsScene {...p} />;
    case 'two-col': return <TwoColScene {...p} />;
    case 'timeline': return <TimelineScene {...p} />;
    case 'numbered': return <NumberedScene {...p} />;
    case 'versus': return <VersusScene {...p} />;
    case 'table': return <TableScene {...p} />;
    case 'stat': return <StatScene {...p} />;
    case 'checklist': return <ChecklistScene {...p} />;
    case 'takeaways': return <TakeawaysScene {...p} />;
    default: break;
  }
  return null;   // fall through to type-based
};

/**
 * Scene ka apna accent ho to `--accent-host` set karke layout ko wrap karo,
 * warna video-level accent hi chalega.
 */
const WithAccent: React.FC<{accent?: string; children: React.ReactNode}> = ({accent, children}) =>
  accent ? (
    <AbsoluteFill
      style={{
        ['--accent-host' as string]: accentColor(accent),
        ['--accent-host-soft' as string]: withAlpha(accentColor(accent), 0.4),
      }}
    >
      {children}
    </AbsoluteFill>
  ) : (
    <>{children}</>
  );

/** Ye layouts poora chauda content rakhte hain — popup inke upar-baayein jaata hai. */
const WIDE_LAYOUTS = ['versus', 'table', 'two-col', 'timeline'];

const DEFAULT_LAYOUT_FOR: Record<string, string> = {
  hook: 'hook', concept: 'concept', steps: 'steps',
  compare: 'compare', number: 'number', recap: 'recap',
};

const sceneTransition = (id: string): string | undefined =>
  scenePropsFor(id)?.transition;

const SceneBody: React.FC<{id: string}> = ({id}) => {
  const s = scenePropsFor(id);
  if (!s) return null;
  // `layout` set hai aur type ke default se alag hai -> wo layout use karo
  const def = DEFAULT_LAYOUT_FOR[s.type];
  return <WithAccent accent={s.accent}>{inner(s, def)}</WithAccent>;
};

const inner = (s: ReturnType<typeof scenePropsFor>, def: string): React.ReactNode => {
  if (!s) return null;
  if (s.layout && s.layout !== def) {
    return <LayoutBody s={s} />;
  }
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
const ChapterLabel: React.FC<{chapter: number; accent?: string}> = ({chapter, accent}) => {
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
          color: accent ? accentColor(accent) : 'var(--accent, #FF6B2C)',
          border: `1.5px solid ${accent ? withAlpha(accentColor(accent), 0.4) : 'var(--accent-soft, #FF6B2C66)'}`,
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

/**
 * Ek scene. Transition ka timing scene ke andar hi count hota hai (apna
 * Sequence), warna pichhle scene ka glow/flash pehle hi dikh jata hai.
 * Subtitle band aur chapter label transition ke saath move karte hain.
 */
const SceneContent: React.FC<{b: Beat}> = ({b}) => {
  const p = scenePropsFor(b.id);
  const inner = Math.max(1, b.to - b.from + 1);
  return (
    <Sequence from={1} durationInFrames={inner}>
      <SceneEntrance kind={p?.transition} durationInFrames={inner}>
        <AbsoluteFill>
          <SceneBody id={b.id} />
          <ChapterLabel chapter={b.chapter} accent={p?.accent} />
          <NoteCard note={p?.note} durationInFrames={inner}
                    wide={WIDE_LAYOUTS.includes(p?.layout || '')} />
          <Subtitles subtitle={b.subtitle} keyword={b.keyword} startFrame={-1} endFrame={inner} />
        </AbsoluteFill>
      </SceneEntrance>
    </Sequence>
  );
};

export const Explainer: React.FC = () => {
  const titleEnd = BEATS.length ? BEATS[0].from - 2 : 60;
  const endStart = TOTAL_FRAMES - 96;

  return (
    <AbsoluteFill
      style={{
        background: COLORS.bg,
        ['--accent' as string]: accentColor(CONTENT.accent),
        ['--accent-soft' as string]: withAlpha(accentColor(CONTENT.accent), 0.4),
      }}
    >
      <Fonts />
      {/* default look: dotted grid. Baaki backgrounds Backdrop khud banata hai. */}
      {(!CONTENT.background || CONTENT.background === 'glow') && <Grid />}
      <Background style={CONTENT.background} accent={CONTENT.accent} />

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
          <SceneContent b={b} />
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
