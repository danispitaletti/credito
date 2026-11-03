import React from 'react';
import {Composition} from 'remotion';
import {ChileVideo} from './Video';
export const RemotionRoot: React.FC = () => (
	<Composition id="Chile" component={ChileVideo} durationInFrames={1368} fps={30} width={1080} height={1920} />
);
