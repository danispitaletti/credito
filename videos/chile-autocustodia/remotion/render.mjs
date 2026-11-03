import {bundle} from '@remotion/bundler';
import {renderMedia, renderStill, selectComposition} from '@remotion/renderer';
import path from 'path';
const mode = process.argv[2] || 'stills';
const browserExecutable = '/opt/pw-browsers/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell';
const chromiumOptions = {gl: 'swangle'};
const serveUrl = await bundle({entryPoint: path.resolve('src/index.ts'), publicDir: path.resolve('public')});
const composition = await selectComposition({serveUrl, id: 'Chile', browserExecutable, chromiumOptions});
if (mode === 'stills') {
  const frames = (process.argv[3] || '30,150,300,460,520,630,780,900,1000,1100,1200,1300').split(',').map(Number);
  for (const f of frames) {
    await renderStill({composition, serveUrl, frame: f, output: `stills/f${String(f).padStart(4,'0')}.png`, browserExecutable, chromiumOptions, timeoutInMilliseconds: 120000});
    console.log('still', f);
  }
} else {
  await renderMedia({composition, serveUrl, codec: 'h264', crf: 18, outputLocation: process.argv[5] || 'out/chile_v2_mudo.mp4', frameRange: process.argv[4] ? process.argv[4].split('-').map(Number) : undefined, browserExecutable, chromiumOptions, concurrency: Number(process.argv[3] || 4), timeoutInMilliseconds: 180000, muted: true,
    onProgress: ({progress}) => { if (Math.round(progress*100) % 5 === 0) process.stdout.write(`\r${Math.round(progress*100)}%`); }});
  console.log('\nok');
}
