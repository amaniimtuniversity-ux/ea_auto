import React from 'react';
import {AbsoluteFill, staticFile} from 'remotion';
import {FONT} from '../theme';

/**
 * Loads the local font files once for the whole video (by raghv).
 * Files live in public/fonts, so rendering never touches the network.
 */
const FACES = [
  {family: 'NotoSansDevanagari', file: 'fonts/NotoSansDevanagari.ttf', weight: '100 900'},
  {family: 'Noto Sans', file: 'fonts/NotoSans.ttf', weight: '100 900'},
  {family: 'Inter', file: 'fonts/Inter.ttf', weight: '100 900'},
  {family: 'JetBrainsMono', file: 'fonts/JetBrainsMono.ttf', weight: '100 800'},
];

export const Fonts: React.FC = () => (
  <AbsoluteFill style={{pointerEvents: 'none'}}>
    <style>
      {FACES.map(
        (f) => `@font-face{font-family:'${f.family}';src:url('${staticFile(f.file)}') format('truetype');font-weight:${f.weight};font-display:block;}`
      ).join('\n')}
    </style>
  </AbsoluteFill>
);

export const fontStack = FONT;
