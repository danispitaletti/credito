"""Corta pausas e gera áudio LIMPO (GTCRN + DPDFNet + portão nos respiros) + vídeo cortado.
Uso: prepara_corte.py render.py PASTA_TRABALHO PASTA_MODELOS
Lê SEGS e PAD do render.py; usa PASTA/bruto.mp4; grava PASTA/cut.mp4 e PASTA/audio_cut.wav"""
import sys, os, subprocess, wave, numpy as np
render, W_, MD = sys.argv[1:4]
src = open(render).read()
ns = {}; exec(src[src.index('SEGS = ['):src.index('\nPAD = ')], ns); SEGS = ns['SEGS']
PAD = float(src[src.index('\nPAD = ') + 7:].split('\n')[0])
J = lambda *p: os.path.join(W_, *p)
run = lambda *c: subprocess.run(list(c), check=True, capture_output=True)
# 1) áudio limpo no tempo original
run('ffmpeg', '-v', 'error', '-y', '-i', J('bruto.mp4'), '-ac', '1', '-ar', '16000', J('raw16.wav'))
run('ffmpeg', '-v', 'error', '-y', '-i', J('bruto.mp4'), '-ac', '1', '-ar', '48000', J('raw48.wav'))
here = os.path.dirname(os.path.abspath(__file__))
run('python3', '-I', os.path.join(here, 'limpa_voz.py'), os.path.join(MD, 'gtcrn.onnx'), J('raw16.wav'), J('c1.wav'))
run('python3', '-I', os.path.join(here, 'limpa_voz2.py'), os.path.join(MD, 'dpdfnet4.onnx'), J('c1.wav'), J('c2.wav'))
run('ffmpeg', '-v', 'error', '-y', '-i', J('c2.wav'), '-i', J('raw48.wav'), '-filter_complex',
    '[0]aresample=48000:resampler=soxr,lowpass=f=7600[lo];[1]highpass=f=7600,volume=0.3[hi];[lo][hi]amix=inputs=2:normalize=0', J('limpo48.wav'))
w = wave.open(J('limpo48.wav')); sr = w.getframerate(); a = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
# 2) portão: só a fala passa; respiros ficam mudos (fades de 40 ms)
g = np.zeros_like(a); f = int(0.04 * sr)
for s, e, _ in SEGS:
    i0, i1 = int(max(s - 0.08, 0) * sr), int(min(e + 0.12, len(a) / sr) * sr)
    g[i0:i1] = 1
    g[max(i0 - f, 0):i0] = np.maximum(g[max(i0 - f, 0):i0], np.linspace(0, 1, i0 - max(i0 - f, 0)))
    g[i1:i1 + f] = np.maximum(g[i1:i1 + f], np.linspace(1, 0, len(g[i1:i1 + f])))
y = (a * g * 32767).astype(np.int16)
o = wave.open(J('limpo_gate.wav'), 'wb'); o.setnchannels(1); o.setsampwidth(2); o.setframerate(sr); o.writeframes(y.tobytes()); o.close()
# 3) cortes (mesma regra do render: PAD de cada lado, sem sobrepor)
v, au, lab, prev = [], [], '', 0
for i, (s, e, _) in enumerate(SEGS):
    s = max(s - PAD, 0); e = e + PAD
    if s < prev: s = prev
    prev = e
    v.append(f"[0:v]trim={s:.3f}:{e:.3f},setpts=PTS-STARTPTS[v{i}]")
    au.append(f"[1:a]atrim={s:.3f}:{e:.3f},asetpts=PTS-STARTPTS[a{i}]")
    lab += f"[v{i}][a{i}]"
open(J('fc.txt'), 'w').write(';'.join(v + au) + f";{lab}concat=n={len(SEGS)}:v=1:a=1[v][a]")
run('ffmpeg', '-v', 'error', '-y', '-i', J('bruto.mp4'), '-i', J('limpo_gate.wav'), '-filter_complex_script', J('fc.txt'),
    '-map', '[v]', '-map', '[a]', '-r', '30', '-c:v', 'libx264', '-crf', '14', '-preset', 'fast', '-c:a', 'pcm_s16le', J('cut_tmp.mkv'))
run('ffmpeg', '-v', 'error', '-y', '-i', J('cut_tmp.mkv'), '-an', '-c:v', 'copy', J('cut.mp4'))
run('ffmpeg', '-v', 'error', '-y', '-i', J('cut_tmp.mkv'), '-vn', '-af', 'acompressor=threshold=-20dB:ratio=3:attack=5:release=80,loudnorm=I=-14:TP=-1.5:LRA=7', '-ar', '48000', J('audio_cut.wav'))
print('ok', len(SEGS), 'trechos, PAD', PAD)
