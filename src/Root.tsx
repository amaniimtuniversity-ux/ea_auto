import React from 'react';
import {Composition} from 'remotion';
import {Explainer} from './Video';
import {TOTAL_FRAMES, FPS} from './timeline';
import {VIDEO} from './theme';

/** One composition: the finished explainer. */
export const Root: React.FC = () => (
  <Composition
    id="Explainer"
    component={Explainer}
    durationInFrames={TOTAL_FRAMES}
    fps={FPS}
    width={VIDEO.width}
    height={VIDEO.height}
  />
);
