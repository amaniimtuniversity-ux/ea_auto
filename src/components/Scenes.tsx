import React from 'react';
import {AbsoluteFill, useCurrentFrame, useVideoConfig} from 'remotion';
import {COLORS, FONT, SAFE, SUBTITLE} from '../theme';
import {easeInOut, easeOut, pop, rise, stagger} from '../lib/anim';

/**
 * Scene visuals (by raghv). Six types, each one a single idea on screen.
 * Rule kept everywhere: on-screen words are English; Hindi lives in the voice.
 * Every scene gets its content from content.ts — nothing is hard-coded per topic.
 */

type Common = {keyword?: string; bullets?: string[]};

/** Content area: between the top chrome and the subtitle band, vertically centred. */
const Stage: React.FC<{children: React.ReactNode; style?: React.CSSProperties}> = ({children, style}) => (
  <AbsoluteFill
    style={{
      padding: `${SAFE.top + 26}px ${SAFE.right}px ${720 - SUBTITLE.top + 24}px ${SAFE.left}px`,
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'center',
      ...style,
    }}
  >
    {children}
  </AbsoluteFill>
);

const Keyword: React.FC<{text?: string; delay?: number; size?: number}> = ({text, delay = 6, size = 92}) => {
  const frame = useCurrentFrame();
  if (!text) return null;
  const a = easeOut(frame, delay, 18);
  return (
    <div
      style={{
        fontFamily: FONT.latin,
        fontSize: size,
        fontWeight: 800,
        letterSpacing: -2,
        color: COLORS.text,
        transform: `translateY(${rise(frame, delay, 22, 20)}px) scale(${pop(frame, delay, 18)})`,
        opacity: a,
        textShadow: '0 8px 40px rgba(0,0,0,.6)',
      }}
    >
      {text}
    </div>
  );
};

const BulletList: React.FC<{items?: string[]; start?: number; accentLast?: boolean}> = ({
  items = [],
  start = 24,
  accentLast = false,
}) => {
  const frame = useCurrentFrame();
  return (
    <div style={{display: 'flex', flexDirection: 'column', gap: 16, marginTop: 34}}>
      {items.map((b, i) => {
        const a = easeOut(frame, stagger(i, 10, start), 14);
        const isLast = accentLast && i === items.length - 1;
        return (
          <div
            key={b}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: 14,
              opacity: a,
              transform: `translateX(${(1 - a) * 26}px)`,
            }}
          >
            <div
              style={{
                width: 10,
                height: 10,
                borderRadius: 3,
                background: isLast ? COLORS.accent : COLORS.cool,
                flexShrink: 0,
              }}
            />
            <div
              style={{
                fontFamily: FONT.latin,
                fontSize: 30,
                fontWeight: 500,
                color: isLast ? COLORS.text : COLORS.textDim,
                letterSpacing: -0.2,
              }}
            >
              {b}
            </div>
          </div>
        );
      })}
    </div>
  );
};

/* ---------------------------------------------------------------- hook */
export const HookScene: React.FC<Common> = ({keyword, bullets}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const cardIn = easeOut(frame, 4, 20);

  return (
    <Stage>
      <div style={{display: 'flex', alignItems: 'center', gap: 48}}>
        <div style={{flex: 1, minWidth: 0}}>
          <Keyword text={keyword} delay={6} size={78} />
          <BulletList items={bullets} start={26} accentLast />
        </div>

        {/* chat card: the wrong answer, with no source */}
        <div
          style={{
            width: 400,
            flexShrink: 0,
            borderRadius: 22,
            border: `2px solid ${COLORS.panelEdge}`,
            background: COLORS.panel,
            padding: '22px 22px 20px',
            opacity: cardIn,
            transform: `translateY(${rise(frame, 4, 30, 22)}px)`,
            boxShadow: '0 22px 60px rgba(0,0,0,.5)',
          }}
        >
          <div style={{display: 'flex', gap: 9, marginBottom: 16}}>
            {['#FF5F57', '#FEBC2E', '#28C840'].map((c) => (
              <div key={c} style={{width: 10, height: 10, borderRadius: 99, background: c, opacity: 0.65}} />
            ))}
          </div>

          <div style={{fontFamily: FONT.mono, fontSize: 19, color: COLORS.textDim, lineHeight: 1.55}}>
            Q: <span style={{color: COLORS.text}}>leave policy?</span>
          </div>

          <div
            style={{
              marginTop: 12,
              fontFamily: FONT.mono,
              fontSize: 19,
              lineHeight: 1.55,
              color: COLORS.text,
              opacity: easeOut(frame, fps * 1.1, 16),
            }}
          >
            A: <span style={{color: COLORS.warn}}>"24 days"</span>
          </div>

          <div
            style={{
              marginTop: 14,
              alignSelf: 'flex-start',
              display: 'inline-flex',
              alignItems: 'center',
              gap: 8,
              border: `1.5px solid ${COLORS.warn}66`,
              borderRadius: 8,
              padding: '7px 11px',
              fontFamily: FONT.latin,
              fontSize: 15,
              letterSpacing: 1.6,
              color: COLORS.warn,
              opacity: easeOut(frame, fps * 1.5, 16),
            }}
          >
            NO SOURCE
          </div>
        </div>
      </div>
    </Stage>
  );
};

/* ------------------------------------------------------------- concept */
export const ConceptScene: React.FC<Common> = ({keyword, bullets}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const ring = easeInOut(frame, 14, 40);

  return (
    <Stage>
      <div style={{display: 'flex', alignItems: 'center', gap: 56}}>
        <div
          style={{
            position: 'relative',
            width: 300,
            height: 300,
            flexShrink: 0,
            borderRadius: 999,
            border: `2px solid ${COLORS.accent}`,
            background: `radial-gradient(circle at 50% 40%, ${COLORS.accent}22, transparent 68%)`,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            transform: `scale(${0.9 + 0.1 * ring})`,
            opacity: easeOut(frame, 10, 20),
          }}
        >
          <div
            style={{
              fontFamily: FONT.latin,
              fontSize: 74,
              fontWeight: 800,
              letterSpacing: -2,
              color: COLORS.text,
            }}
          >
            {keyword ?? 'RAG'}
          </div>
          {/* documents flying in, one per ~0.6s */}
          {[0, 1, 2].map((i) => {
            const t = easeOut(frame, 32 + i * fps * 0.5, 18);
            return (
              <div
                key={i}
                style={{
                  position: 'absolute',
                  right: -46 - i * 44,
                  top: 60 + i * 70,
                  width: 74,
                  height: 90,
                  borderRadius: 8,
                  border: `2px solid ${i === 1 ? COLORS.accent : COLORS.panelEdge}`,
                  background: COLORS.panel,
                  opacity: t,
                  transform: `translateX(${(1 - t) * 90}px) rotate(${(1 - t) * 14 - i * 5}deg)`,
                }}
              />
            );
          })}
        </div>
        <div>
          <div
            style={{
              fontFamily: FONT.latin,
              fontSize: 20,
              letterSpacing: 4,
              textTransform: 'uppercase',
              color: COLORS.accent,
              opacity: easeOut(frame, 8, 14),
              marginBottom: 16,
            }}
          >
            the idea
          </div>
          <BulletList items={bullets} start={20} accentLast />
        </div>
      </div>
    </Stage>
  );
};

/* --------------------------------------------------------------- steps */
export const StepsScene: React.FC<Common & {steps?: {label: string; note?: string}[]}> = ({
  keyword,
  steps = [],
}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  // highlight advances every 1.6s so the pipeline is walked through, not shown at once
  const active = Math.min(steps.length - 1, Math.floor(Math.max(0, frame - 20) / (fps * 1.6)));

  return (
    <Stage>
      <div
        style={{
          fontFamily: FONT.latin,
          fontSize: 20,
          letterSpacing: 4,
          textTransform: 'uppercase',
          color: COLORS.textFaint,
          marginBottom: 18,
          opacity: easeOut(frame, 6, 14),
        }}
      >
        {keyword} — step by step
      </div>

      <div style={{display: 'flex', alignItems: 'center', gap: 0, marginTop: 24}}>
        {steps.map((s, i) => {
          const on = i === active;
          const seen = i < active;
          const a = easeOut(frame, stagger(i, 12, 14), 16);
          return (
            <React.Fragment key={s.label}>
              <div
                style={{
                  opacity: a,
                  transform: `translateY(${(1 - a) * 20}px)`,
                  flex: 1,
                  borderRadius: 20,
                  padding: '30px 20px 26px',
                  border: `2px solid ${on ? COLORS.accent : COLORS.panelEdge}`,
                  background: on ? `${COLORS.accent}14` : COLORS.panel,
                  boxShadow: on ? `0 0 60px ${COLORS.accent}33` : 'none',
                  textAlign: 'center',
                }}
              >
                <div
                  style={{
                    fontFamily: FONT.latin,
                    fontSize: 15,
                    fontWeight: 700,
                    letterSpacing: 2,
                    color: on ? COLORS.accent : seen ? COLORS.good : COLORS.textFaint,
                    marginBottom: 10,
                  }}
                >
                  STEP {i + 1}
                </div>
                <div
                  style={{
                    fontFamily: FONT.latin,
                    fontSize: 38,
                    fontWeight: 800,
                    letterSpacing: -0.8,
                    color: on ? COLORS.text : COLORS.textDim,
                  }}
                >
                  {s.label}
                </div>
                {s.note ? (
                  <div
                    style={{
                      fontFamily: FONT.latin,
                      fontSize: 20,
                      color: COLORS.textFaint,
                      marginTop: 10,
                    }}
                  >
                    {s.note}
                  </div>
                ) : null}
              </div>
              {i < steps.length - 1 ? (
                <div
                  style={{
                    width: 54,
                    textAlign: 'center',
                    fontFamily: FONT.latin,
                    fontSize: 34,
                    color: seen ? COLORS.cool : COLORS.textFaint,
                    opacity: easeOut(frame, stagger(i, 12, 22), 16),
                  }}
                >
                  →
                </div>
              ) : null}
            </React.Fragment>
          );
        })}
      </div>

      {/* a dot travelling along the pipeline, one loop per step */}
      <div style={{position: 'relative', height: 40, marginTop: 26}}>
        {steps.map((s, i) => {
          const period = fps * 1.6;
          const t = ((Math.max(0, frame - 20 - i * period) % period) / period);
          const on = i === active;
          if (!on) return null;
          return (
            <div
              key={s.label}
              style={{
                position: 'absolute',
                left: `${((i + 0.5) / steps.length) * 100}%`,
                top: 14,
                width: 12,
                height: 12,
                borderRadius: 99,
                background: COLORS.cool,
                boxShadow: `0 0 22px ${COLORS.cool}`,
                opacity: 0.5 + 0.5 * Math.sin(t * Math.PI),
                transform: 'translateX(-50%)',
              }}
            />
          );
        })}
      </div>
    </Stage>
  );
};

/* ------------------------------------------------------------- compare */
export const CompareScene: React.FC<
  Common & {left?: {label: string; points: string[]}; right?: {label: string; points: string[]}}
> = ({keyword, left, right}) => {
  const frame = useCurrentFrame();

  const Column: React.FC<{data?: {label: string; points: string[]}; bad?: boolean; delay: number}> = ({
    data,
    bad,
    delay,
  }) => {
    const a = easeOut(frame, delay, 20);
    if (!data) return null;
    const tint = bad ? COLORS.warn : COLORS.good;
    return (
      <div
        style={{
          flex: 1,
          borderRadius: 22,
          border: `2px solid ${tint}55`,
          background: bad ? '#1A1114' : '#0E1A15',
          padding: '28px 28px 30px',
          opacity: a,
          transform: `translateY(${(1 - a) * 24}px)`,
        }}
      >
        <div
          style={{
            fontFamily: FONT.latin,
            fontSize: 17,
            letterSpacing: 3,
            fontWeight: 700,
            color: tint,
            marginBottom: 22,
          }}
        >
          {data.label}
        </div>
        {data.points.map((p, i) => (
          <div
            key={p}
            style={{
              display: 'flex',
              gap: 12,
              alignItems: 'center',
              marginBottom: 16,
              opacity: easeOut(frame, delay + 12 + i * 9, 14),
            }}
          >
            <div style={{fontFamily: FONT.latin, fontSize: 22, color: tint, width: 20}}>{bad ? '✕' : '✓'}</div>
            <div style={{fontFamily: FONT.latin, fontSize: 28, color: COLORS.text, fontWeight: 500}}>{p}</div>
          </div>
        ))}
      </div>
    );
  };

  return (
    <Stage>
      <div
        style={{
          fontFamily: FONT.latin,
          fontSize: 20,
          letterSpacing: 4,
          textTransform: 'uppercase',
          color: COLORS.textFaint,
          marginBottom: 22,
          opacity: easeOut(frame, 6, 14),
        }}
      >
        {keyword}
      </div>
      <div style={{display: 'flex', gap: 30}}>
        <Column data={left} bad delay={12} />
        <Column data={right} delay={22} />
      </div>
    </Stage>
  );
};

/* -------------------------------------------------------------- number */
export const NumberScene: React.FC<Common & {value?: string; unit?: string; caption?: string}> = ({
  value,
  unit,
  caption,
  bullets,
}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const target = Number(value);
  const done = easeOut(frame, 10, fps * 0.9);
  const shown = Number.isFinite(target) ? Math.round(target * done) : value;
  const ring = easeOut(frame, 16, fps * 1.2);

  return (
    <Stage>
      <div style={{display: 'flex', alignItems: 'center', gap: 64}}>
        <div style={{flex: 1}}>
          <div style={{display: 'flex', alignItems: 'baseline', gap: 18}}>
            <div
              style={{
                fontFamily: FONT.latin,
                fontSize: 190,
                fontWeight: 800,
                letterSpacing: -8,
                lineHeight: 0.95,
                color: COLORS.text,
                opacity: easeOut(frame, 8, 16),
              }}
            >
              {shown}
            </div>
            <div
              style={{
                fontFamily: FONT.latin,
                fontSize: 40,
                fontWeight: 600,
                color: COLORS.accent,
                opacity: easeOut(frame, 20, 16),
              }}
            >
              {unit}
            </div>
          </div>
          <div
            style={{
              marginTop: 18,
              height: 4,
              width: `${ring * 320}px`,
              background: COLORS.accent,
              borderRadius: 4,
              opacity: 0.85,
            }}
          />
          {caption ? (
            <div
              style={{
                marginTop: 24,
                fontFamily: FONT.latin,
                fontSize: 27,
                color: COLORS.textDim,
                opacity: easeOut(frame, 26, 16),
                maxWidth: 520,
              }}
            >
              {caption}
            </div>
          ) : null}
          <BulletList items={bullets} start={40} />
        </div>

        {/* three chunk cards, only three are kept */}
        <div style={{display: 'flex', flexDirection: 'column', gap: 14, width: 300}}>
          {['chunk 1', 'chunk 2', 'chunk 3', 'chunk 4'].map((c, i) => {
            const kept = i < 3;
            const a = easeOut(frame, stagger(i, 10, 24), 14);
            return (
              <div
                key={c}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  padding: '16px 18px',
                  borderRadius: 12,
                  border: `2px solid ${kept ? COLORS.cool : COLORS.panelEdge}`,
                  background: kept ? `${COLORS.cool}12` : 'transparent',
                  opacity: kept ? a : a * 0.4,
                }}
              >
                <div style={{fontFamily: FONT.mono, fontSize: 20, color: kept ? COLORS.text : COLORS.textFaint}}>
                  {c}
                </div>
                <div style={{fontFamily: FONT.latin, fontSize: 18, color: kept ? COLORS.good : COLORS.textFaint}}>
                  {kept ? 'kept' : 'dropped'}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </Stage>
  );
};

/* --------------------------------------------------------------- recap */
export const RecapScene: React.FC<Common> = ({keyword, bullets}) => {
  const frame = useCurrentFrame();
  return (
    <Stage>
      <Keyword text={keyword} delay={4} size={70} />
      <div style={{display: 'flex', gap: 22, marginTop: 40}}>
        {(bullets ?? []).map((b, i) => {
          const a = easeOut(frame, stagger(i, 14, 18), 18);
          return (
            <div
              key={b}
              style={{
                flex: 1,
                borderRadius: 18,
                border: `2px solid ${COLORS.panelEdge}`,
                background: COLORS.panel,
                padding: '26px 22px',
                opacity: a,
                transform: `translateY(${(1 - a) * 26}px)`,
              }}
            >
              <div
                style={{
                  fontFamily: FONT.latin,
                  fontSize: 15,
                  letterSpacing: 2,
                  color: COLORS.accent,
                  marginBottom: 12,
                }}
              >
                0{i + 1}
              </div>
              <div style={{fontFamily: FONT.latin, fontSize: 26, fontWeight: 600, color: COLORS.text}}>{b}</div>
            </div>
          );
        })}
      </div>
    </Stage>
  );
};
