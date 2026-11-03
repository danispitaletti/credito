"""Transcreve cada trecho de fala (entre silêncios) com Whisper small. Uso: modelo wav silencios.txt saida.json"""
import sys, json, wave, re, numpy as np, sherpa_onnx
M, wav, sil, out = sys.argv[1:5]
rec = sherpa_onnx.OfflineRecognizer.from_whisper(encoder=f"{M}/small-encoder.int8.onnx", decoder=f"{M}/small-decoder.int8.onnx", tokens=f"{M}/small-tokens.txt", language="pt", task="transcribe", num_threads=4)
w = wave.open(wav); sr = w.getframerate(); a = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
dur = len(a) / sr
starts, ends = [], []
for ln in open(sil):
    m = re.findall(r'silence_(start|end): ([\d.]+)', ln)
    for k, v in m: (starts if k == 'start' else ends).append(float(v))
# trechos de fala = do fim de um silêncio ao início do próximo
segs = []; cur = 0.0
sil_pairs = sorted(zip(starts, ends + [dur] * (len(starts) - len(ends))))
for s0, s1 in sil_pairs:
    if s0 - cur > 0.15: segs.append((cur, s0))
    cur = s1
if dur - cur > 0.15: segs.append((cur, dur))
res = []
for s0, s1 in segs:
    x = a[int(max(s0 - 0.05, 0) * sr):int(min(s1 + 0.05, dur) * sr)]
    st = rec.create_stream(); st.accept_waveform(sr, x); rec.decode_stream(st)
    txt = st.result.text.strip()
    res.append(dict(a=round(s0, 3), b=round(s1, 3), txt=txt)); print(f"{s0:6.2f}-{s1:6.2f} {txt}", flush=True)
json.dump(res, open(out, 'w'), ensure_ascii=False, indent=1)
