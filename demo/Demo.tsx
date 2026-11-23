import React from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {Stage} from '../Main';
import {SENTENCES, TOTAL_FRAMES} from '../common/timeline';
import {Box, CText, Pill, TechText, PURPLE, PURPLE_LIGHT, ORANGE, GREY, WHITE, GLOW_PURPLE_S, fadeIn, slideUp} from '../ui';
import type {ShotDef, BgSpec} from '../common';
import {SHOTS_OVERLAY, SHOTS_OVERLAY_TOP, BG_OVERLAY} from '../overlay';

const S = (id: string) => SENTENCES.find((s) => s.id === id)!;

// ---- Shot 1: model answers from memory only (English board) ----
const Shot1: React.FC = () => {
  const f = useCurrentFrame();
  const a = S('S01');
  return (
    <AbsoluteFill>
      <Box x={440} y={230} w={400} h={230} fill="#000" stroke={WHITE} sw={3} r={10} opacity={fadeIn(f, 18)}>
        <CText cx={200} cy={100} size={54} weight={900} color={WHITE} letterSpacing={2}>LLM</CText>
        <CText cx={200} cy={160} size={26} weight={600} color={GREY}>memory only</CText>
      </Box>
      <Pill x={960} y={318} w={210} h={54} fill={ORANGE} sw={0} text="NO SOURCES" fontSize={26} weight={800}
        opacity={fadeIn(f - 20, 14)} style={{filter: 'drop-shadow(0 0 18px rgba(240,95,65,.55))'}} />
      <TechText cx={640} cy={545} text="Where did that answer come from?" fontSize={34}
        opacity={fadeIn(f - 40, 16)} />
      <CText cx={640} cy={600} size={30} weight={700} color={PURPLE_LIGHT} opacity={fadeIn(f - 55, 16)}>
        {a.text.slice(0, 42)}
      </CText>
    </AbsoluteFill>
  );
};

// ---- Shot 2: RAG fixes the gap by showing documents ----
const Shot2: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill>
      <Pill x={520} y={200} w={240} h={72} fill={PURPLE} sw={2.5} text="RAG" fontSize={44} weight={900}
        textDy={-2} opacity={fadeIn(f, 14)} glow={GLOW_PURPLE_S} />
      <TechText cx={640} cy={292} text="retrieval-augmented generation" fontSize={26} opacity={fadeIn(f - 12, 14)} />
      {[0, 1, 2].map((i) => (
        <Box key={i} x={350 + i * 210} y={360 + slideUp(f - 24 - i * 8)} w={170} h={110} fill="#000" stroke={i === 1 ? PURPLE_LIGHT : WHITE} sw={2.5} r={6}
          opacity={fadeIn(f - 24 - i * 8, 16)}>
          <CText cx={85} cy={40} size={24} weight={700} color={WHITE}>doc {i + 1}</CText>
          <CText cx={85} cy={74} size={19} weight={500} color={GREY}>source</CText>
        </Box>
      ))}
      <CText cx={640} cy={540} size={30} weight={700} color={WHITE} opacity={fadeIn(f - 60, 16)}>
        Show the source before the answer
      </CText>
    </AbsoluteFill>
  );
};

// ---- Shot 3: chunk -> embed -> retrieve pipeline ----
const Shot3: React.FC = () => {
  const f = useCurrentFrame();
  const steps = ['CHUNK', 'EMBED', 'RETRIEVE'];
  const on = Math.min(2, Math.floor(Math.max(0, f - 10) / 34));
  return (
    <AbsoluteFill>
      {steps.map((t, i) => (
        <React.Fragment key={t}>
          <Pill x={190 + i * 330} y={300} w={250} h={84} fill={i === on ? PURPLE : '#000'} sw={2.5} text={t} fontSize={30} weight={800}
            textDy={-2} opacity={fadeIn(f - 8 - i * 10, 16)} glow={i === on ? GLOW_PURPLE_S : undefined} />
          {i < 2 ? (
            <CText cx={190 + i * 330 + 290} cy={344} size={40} weight={900} color={i === on ? PURPLE_LIGHT : GREY}
              opacity={fadeIn(f - 8 - i * 10, 16)}>→</CText>
          ) : null}
        </React.Fragment>
      ))}
      <CText cx={640} cy={460} size={28} weight={600} color={GREY} opacity={fadeIn(f - 70, 16)}>
        every chunk gets a number
      </CText>
    </AbsoluteFill>
  );
};

const SHOTS: ShotDef[] = [
  {id: 'D1', from: S('S01').from - 8, to: S('S02').to + 2, Comp: Shot1},
  {id: 'D2', from: S('S03').from - 8, to: S('S03').to + 2, Comp: Shot2},
  {id: 'D3', from: S('S04').from - 8, to: S('S05').to + 2, Comp: Shot3},
];
const BG: BgSpec[] = [...BG_OVERLAY];

export const Demo: React.FC = () => (
  <Stage shots={[...SHOTS_OVERLAY, ...SHOTS, ...SHOTS_OVERLAY_TOP]} bg={BG} audio />
);
export const DEMO_FRAMES = TOTAL_FRAMES;
