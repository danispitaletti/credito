import sys, json, wave, numpy as np, sherpa_onnx
M=sys.argv[1]; wav=sys.argv[2]
rec=sherpa_onnx.OfflineRecognizer.from_whisper(encoder=f"{M}/small-encoder.int8.onnx",decoder=f"{M}/small-decoder.int8.onnx",tokens=f"{M}/small-tokens.txt",language="pt",task="transcribe",num_threads=4)
w=wave.open(wav); a=np.frombuffer(w.readframes(w.getnframes()),dtype=np.int16).astype(np.float32)/32768; sr=w.getframerate()
s=rec.create_stream(); s.accept_waveform(sr,a); rec.decode_stream(s)
r=s.result; print(r.text)
print(json.dumps({"tokens":r.tokens,"timestamps":list(r.timestamps)},ensure_ascii=False))
