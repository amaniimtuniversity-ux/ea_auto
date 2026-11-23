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

/* =====================================================================
 * Extra layouts (by raghv) — content.ts ke `layout` field se chunte hain.
 * Sab ek hi Stage par rehte hain, isliye subtitle band aur chrome kabhi
 * nahi tootte. Text English, voice Hindi — wahi rule.
 * ===================================================================== */

/* ------------------------------------------------------------- quote */
export const QuoteScene: React.FC<Common> = ({keyword, bullets}) => {
  const frame = useCurrentFrame();
  const a = easeOut(frame, 6, 22);
  return (
    <Stage>
      <div style={{display: 'flex', gap: 28, alignItems: 'flex-start', opacity: a}}>
        <div
          style={{
            fontFamily: FONT.latin, fontSize: 150, lineHeight: 0.7, fontWeight: 800,
            color: COLORS.accent, opacity: 0.85, transform: `translateY(${rise(frame, 6, 26, 14)}px)`,
          }}
        >
          “
        </div>
        <div style={{flex: 1, minWidth: 0}}>
          <div
            style={{
              fontFamily: FONT.latin, fontSize: 60, fontWeight: 700, lineHeight: 1.28,
              letterSpacing: -1.2, color: COLORS.text,
            }}
          >
            {keyword}
          </div>
          <BulletList items={bullets} start={30} />
        </div>
      </div>
    </Stage>
  );
};

/* ------------------------------------------------------------ bigword */
export const BigWordScene: React.FC<Common> = ({keyword, bullets}) => {
  const frame = useCurrentFrame();
  const scale = 0.92 + 0.08 * pop(frame, 4, 26);
  return (
    <Stage style={{alignItems: 'center', textAlign: 'center'}}>
      <div
        style={{
          fontFamily: FONT.latin, fontSize: 132, fontWeight: 900, letterSpacing: -5,
          color: COLORS.text, transform: `scale(${scale})`, lineHeight: 1.02,
        }}
      >
        {keyword}
      </div>
      <div style={{display: 'flex', gap: 16, marginTop: 30, flexWrap: 'wrap', justifyContent: 'center'}}>
        {(bullets || []).slice(0, 3).map((b, i) => (
          <div
            key={b}
            style={{
              fontFamily: FONT.latin, fontSize: 22, color: COLORS.accent,
              border: `1.5px solid ${COLORS.accent}55`, borderRadius: 99,
              padding: '10px 20px', opacity: easeOut(frame, 24 + i * 8, 16),
            }}
          >
            {b}
          </div>
        ))}
      </div>
    </Stage>
  );
};

/* ------------------------------------------------------------ bullets */
export const BulletsScene: React.FC<Common> = ({keyword, bullets}) => {
  const frame = useCurrentFrame();
  return (
    <Stage>
      <div style={{fontFamily: FONT.latin, fontSize: 54, fontWeight: 800, letterSpacing: -1.4,
                   color: COLORS.text, marginBottom: 34}}>
        {keyword}
      </div>
      {(bullets || []).slice(0, 5).map((b, i) => (
        <div
          key={b}
          style={{
            display: 'flex', alignItems: 'flex-start', gap: 18, marginBottom: 18,
            opacity: easeOut(frame, 12 + i * 9, 18),
            transform: `translateX(${rise(frame, 12 + i * 9, 24, 26)}px)`,
          }}
        >
          <div style={{width: 12, height: 12, borderRadius: 4, background: COLORS.accent,
                       marginTop: 14, flexShrink: 0}} />
          <div style={{fontFamily: FONT.latin, fontSize: 32, lineHeight: 1.45, color: COLORS.textDim}}>
            {b}
          </div>
        </div>
      ))}
    </Stage>
  );
};

/* ------------------------------------------------------------- cards */
export const CardsScene: React.FC<Common> = ({keyword, bullets}) => {
  const frame = useCurrentFrame();
  const items = (bullets || []).slice(0, 4);
  return (
    <Stage>
      <div style={{fontFamily: FONT.latin, fontSize: 44, fontWeight: 800, color: COLORS.text,
                   marginBottom: 30, letterSpacing: -1}}>
        {keyword}
      </div>
      <div style={{display: 'flex', gap: 18, flexWrap: 'wrap'}}>
        {items.map((b, i) => (
          <div
            key={b}
            style={{
              flex: `1 1 ${items.length > 2 ? '42%' : '48%'}`, minWidth: 0,
              background: COLORS.panel, border: `1.5px solid ${COLORS.panelEdge}`,
              borderRadius: 18, padding: '22px 24px',
              opacity: easeOut(frame, 10 + i * 10, 20),
              transform: `translateY(${rise(frame, 10 + i * 10, 28, 20)}px)`,
            }}
          >
            <div style={{fontFamily: FONT.mono, fontSize: 15, color: COLORS.accent,
                         letterSpacing: 2, marginBottom: 10}}>
              {`0${i + 1}`}
            </div>
            <div style={{fontFamily: FONT.latin, fontSize: 25, lineHeight: 1.4, color: COLORS.text}}>
              {b}
            </div>
          </div>
        ))}
      </div>
    </Stage>
  );
};

/* ----------------------------------------------------------- two-col */
export const TwoColScene: React.FC<Common> = ({keyword, bullets}) => {
  const frame = useCurrentFrame();
  const all = bullets || [];
  const half = Math.max(1, Math.ceil(all.length / 2));
  const col = (items: string[], side: number) => (
    <div style={{flex: 1, minWidth: 0}}>
      {items.map((b, i) => (
        <div key={b} style={{
          fontFamily: FONT.latin, fontSize: 27, lineHeight: 1.45, color: COLORS.textDim,
          padding: '12px 0 12px 20px', borderLeft: `3px solid ${side === 0 ? COLORS.accent : COLORS.cool}`,
          marginBottom: 8, opacity: easeOut(frame, 14 + (side * 6 + i) * 9, 18),
        }}>
          {b}
        </div>
      ))}
    </div>
  );
  return (
    <Stage>
      <div style={{fontFamily: FONT.latin, fontSize: 50, fontWeight: 800, color: COLORS.text,
                   marginBottom: 32, letterSpacing: -1.2}}>
        {keyword}
      </div>
      <div style={{display: 'flex', gap: 40}}>
        {col(all.slice(0, half), 0)}
        {all.length > 1 ? col(all.slice(half), 1) : <div style={{flex: 1}} />}
      </div>
    </Stage>
  );
};

/* --------------------------------------------------------- timeline */
export const TimelineScene: React.FC<Common & {steps?: {label: string; note?: string}[]}> = ({
  keyword, steps,
}) => {
  const frame = useCurrentFrame();
  const items = (steps || []).slice(0, 5);
  return (
    <Stage>
      <div style={{fontFamily: FONT.latin, fontSize: 24, fontWeight: 800, color: COLORS.textDim,
                   letterSpacing: 3, marginBottom: 34, textTransform: 'uppercase'}}>
        {keyword}
      </div>
      <div style={{position: 'relative', paddingLeft: 6}}>
        <div style={{position: 'absolute', left: 21, top: 10, bottom: 10, width: 2,
                     background: COLORS.panelEdge}} />
        {items.map((st, i) => (
          <div key={st.label} style={{
            display: 'flex', gap: 26, alignItems: 'flex-start', marginBottom: 24, position: 'relative',
            opacity: easeOut(frame, 12 + i * 12, 20),
            transform: `translateY(${rise(frame, 12 + i * 12, 26, 18)}px)`,
          }}>
            <div style={{
              width: 32, height: 32, borderRadius: 99, flexShrink: 0, zIndex: 1,
              background: COLORS.bg, border: `2.5px solid ${COLORS.accent}`,
              display: 'grid', placeItems: 'center',
              fontFamily: FONT.mono, fontSize: 15, color: COLORS.accent,
            }}>
              {i + 1}
            </div>
            <div>
              <div style={{fontFamily: FONT.latin, fontSize: 28, fontWeight: 700, color: COLORS.text}}>
                {st.label}
              </div>
              {st.note ? (
                <div style={{fontFamily: FONT.latin, fontSize: 21, color: COLORS.textDim, marginTop: 4}}>
                  {st.note}
                </div>
              ) : null}
            </div>
          </div>
        ))}
      </div>
    </Stage>
  );
};

/* --------------------------------------------------------- numbered */
export const NumberedScene: React.FC<Common & {steps?: {label: string; note?: string}[]}> = ({
  keyword, steps,
}) => {
  const frame = useCurrentFrame();
  const items = (steps || []).slice(0, 4);
  return (
    <Stage>
      <div style={{fontFamily: FONT.latin, fontSize: 40, fontWeight: 800, color: COLORS.text,
                   marginBottom: 28, letterSpacing: -1}}>
        {keyword}
      </div>
      <div style={{display: 'flex', gap: 16}}>
        {items.map((st, i) => (
          <div key={st.label} style={{
            flex: 1, minWidth: 0, background: COLORS.panel, borderRadius: 18,
            border: `1.5px solid ${COLORS.panelEdge}`, padding: '24px 20px',
            opacity: easeOut(frame, 10 + i * 11, 20),
            transform: `translateY(${rise(frame, 10 + i * 11, 30, 24)}px)`,
          }}>
            <div style={{fontFamily: FONT.latin, fontSize: 60, fontWeight: 900,
                         color: COLORS.accent, lineHeight: 1, marginBottom: 14}}>
              {i + 1}
            </div>
            <div style={{fontFamily: FONT.latin, fontSize: 24, fontWeight: 700, color: COLORS.text}}>
              {st.label}
            </div>
            {st.note ? (
              <div style={{fontFamily: FONT.latin, fontSize: 18, color: COLORS.textDim, marginTop: 8}}>
                {st.note}
              </div>
            ) : null}
          </div>
        ))}
      </div>
    </Stage>
  );
};

/* ----------------------------------------------------------- versus */
export const VersusScene: React.FC<
  Common & {left?: {label: string; points: string[]} | null; right?: {label: string; points: string[]} | null}
> = ({keyword, left, right}) => {
  const frame = useCurrentFrame();
  const side = (data: typeof left, toward: number, color: string, delay: number) =>
    data ? (
      <div style={{
        flex: 1, minWidth: 0, background: COLORS.panel, borderRadius: 20,
        border: `2px solid ${color}44`, padding: '26px 28px',
        opacity: easeOut(frame, delay, 22),
        transform: `translateX(${toward * (1 - pop(frame, delay, 26)) * 40}px)`,
      }}>
        <div style={{fontFamily: FONT.latin, fontSize: 27, fontWeight: 800, color, marginBottom: 16}}>
          {data.label}
        </div>
        {data.points.slice(0, 4).map((p) => (
          <div key={p} style={{fontFamily: FONT.latin, fontSize: 22, color: COLORS.textDim,
                               lineHeight: 1.5, marginBottom: 8}}>
            {p}
          </div>
        ))}
      </div>
    ) : null;
  return (
    <Stage>
      {keyword ? (
        <div style={{fontFamily: FONT.latin, fontSize: 38, fontWeight: 800, color: COLORS.text,
                     marginBottom: 26, letterSpacing: -1}}>
          {keyword}
        </div>
      ) : null}
      <div style={{display: 'flex', alignItems: 'center', gap: 22}}>
        {side(left, -1, COLORS.warn, 10)}
        <div style={{
          fontFamily: FONT.latin, fontSize: 26, fontWeight: 900, color: COLORS.textDim,
          letterSpacing: 3, opacity: easeOut(frame, 24, 18), flexShrink: 0,
        }}>
          VS
        </div>
        {side(right, 1, COLORS.good, 18)}
      </div>
    </Stage>
  );
};

/* ------------------------------------------------------------ table */
export const TableScene: React.FC<
  Common & {keyword?: string; left?: {label: string; points: string[]} | null; right?: {label: string; points: string[]} | null}
> = ({keyword, left, right}) => {
  const frame = useCurrentFrame();
  const rows = Math.max(left?.points.length || 0, right?.points.length || 0);
  const cell = (txt: string | undefined, i: number, color: string) => (
    <div key={i} style={{
      fontFamily: FONT.latin, fontSize: 22, color: COLORS.textDim, lineHeight: 1.4,
      padding: '13px 4px', borderTop: i ? `1px solid ${COLORS.panelEdge}` : 'none',
      opacity: txt ? easeOut(frame, 16 + i * 8, 16) : 0,
    }}>
      {txt || '—'}
    </div>
  );
  return (
    <Stage>
      {keyword ? (
        <div style={{fontFamily: FONT.latin, fontSize: 38, fontWeight: 800, color: COLORS.text,
                     marginBottom: 26, letterSpacing: -1}}>
          {keyword}
        </div>
      ) : null}
      <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0 48px'}}>
        <div style={{fontFamily: FONT.latin, fontSize: 24, fontWeight: 800, color: COLORS.warn,
                     paddingBottom: 10, borderBottom: `2px solid ${COLORS.warn}66`}}>
          {left?.label || 'A'}
        </div>
        <div style={{fontFamily: FONT.latin, fontSize: 24, fontWeight: 800, color: COLORS.good,
                     paddingBottom: 10, borderBottom: `2px solid ${COLORS.good}66`}}>
          {right?.label || 'B'}
        </div>
        {Array.from({length: rows}, (_, i) => (
          <React.Fragment key={i}>
            {cell(left?.points[i], i, COLORS.warn)}
            {cell(right?.points[i], i, COLORS.good)}
          </React.Fragment>
        ))}
      </div>
    </Stage>
  );
};

/* -------------------------------------------------------------- stat */
export const StatScene: React.FC<Common & {value?: string; unit?: string; caption?: string}> = ({
  value, unit, caption, bullets,
}) => {
  const frame = useCurrentFrame();
  return (
    <Stage style={{alignItems: 'flex-start'}}>
      <div style={{display: 'flex', alignItems: 'baseline', gap: 18,
                   transform: `scale(${0.94 + 0.06 * pop(frame, 4, 24)})`, transformOrigin: 'left bottom'}}>
        <div style={{fontFamily: FONT.latin, fontSize: 150, fontWeight: 900, lineHeight: 0.95,
                     letterSpacing: -6, color: COLORS.accent}}>
          {value}
        </div>
        <div style={{fontFamily: FONT.latin, fontSize: 40, fontWeight: 700, color: COLORS.textDim}}>
          {unit}
        </div>
      </div>
      {/* highlight bar */}
      <div style={{
        height: 6, borderRadius: 99, background: `linear-gradient(90deg, ${COLORS.accent}, ${COLORS.cool})`,
        width: `${Math.min(100, 30 + (bullets?.length || 0) * 15)}%`, margin: '18px 0 22px',
        opacity: easeOut(frame, 18, 20),
      }} />
      <div style={{fontFamily: FONT.latin, fontSize: 28, color: COLORS.text, lineHeight: 1.45}}>
        {caption}
      </div>
      <BulletList items={bullets} start={34} />
    </Stage>
  );
};

/* -------------------------------------------------------- checklist */
export const ChecklistScene: React.FC<Common> = ({keyword, bullets}) => {
  const frame = useCurrentFrame();
  const items = (bullets || []).slice(0, 5);
  return (
    <Stage>
      <div style={{fontFamily: FONT.latin, fontSize: 42, fontWeight: 800, color: COLORS.text,
                   marginBottom: 28, letterSpacing: -0.8}}>
        {keyword}
      </div>
      {items.map((b, i) => (
        <div key={b} style={{
          display: 'flex', alignItems: 'center', gap: 18, marginBottom: 14,
          opacity: easeOut(frame, 12 + i * 10, 18),
        }}>
          <svg width="28" height="28" viewBox="0 0 24 24" style={{flexShrink: 0}}>
            <circle cx="12" cy="12" r="11" fill="none" stroke={COLORS.good} strokeWidth="2" />
            <path d="M7 12.4l3.3 3.3L17 8.8" fill="none" stroke={COLORS.good} strokeWidth="2.6"
                  strokeLinecap="round" strokeLinejoin="round"
                  strokeDasharray="18" strokeDashoffset={18 * (1 - pop(frame, 18 + i * 10, 16))} />
          </svg>
          <div style={{fontFamily: FONT.latin, fontSize: 29, color: COLORS.text, lineHeight: 1.4}}>
            {b}
          </div>
        </div>
      ))}
    </Stage>
  );
};

/* -------------------------------------------------------- takeaways */
export const TakeawaysScene: React.FC<Common> = ({keyword, bullets}) => {
  const frame = useCurrentFrame();
  const items = (bullets || []).slice(0, 3);
  return (
    <Stage style={{alignItems: 'center', textAlign: 'center'}}>
      <div style={{fontFamily: FONT.latin, fontSize: 26, fontWeight: 700, letterSpacing: 4,
                   textTransform: 'uppercase', color: COLORS.cool, marginBottom: 16}}>
        {keyword}
      </div>
      <div style={{display: 'flex', gap: 18, marginTop: 10}}>
        {items.map((b, i) => (
          <div key={b} style={{
            width: 250, background: COLORS.panel, borderRadius: 20,
            border: `1.5px solid ${i === items.length - 1 ? COLORS.accent : COLORS.panelEdge}`,
            padding: '24px 20px',
            opacity: easeOut(frame, 14 + i * 12, 20),
            transform: `translateY(${rise(frame, 14 + i * 12, 30, 26)}px)`,
          }}>
            <div style={{fontFamily: FONT.mono, fontSize: 14, color: COLORS.cool,
                         letterSpacing: 2, marginBottom: 12}}>
              {`0${i + 1}`}
            </div>
            <div style={{fontFamily: FONT.latin, fontSize: 23, lineHeight: 1.4, color: COLORS.text}}>
              {b}
            </div>
          </div>
        ))}
      </div>
    </Stage>
  );
};
