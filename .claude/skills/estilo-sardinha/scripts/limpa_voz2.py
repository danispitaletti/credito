"""Limpeza forte de ruído de fundo (latidos etc.) com DPDFNet (sherpa-onnx). Uso: dpdfnet.onnx entrada.wav saida.wav [atenuacao_db]"""
import sys, wave, numpy as np, sherpa_onnx
m, inp, out = sys.argv[1:4]; att = float(sys.argv[4]) if len(sys.argv) > 4 else 0.0
cfg = sherpa_onnx.OfflineSpeechDenoiserConfig(model=sherpa_onnx.OfflineSpeechDenoiserModelConfig(
    dpdfnet=sherpa_onnx.OfflineSpeechDenoiserDpdfNetModelConfig(model=m, attenuation_limit_db=att), num_threads=4))
dn = sherpa_onnx.OfflineSpeechDenoiser(cfg)
w = wave.open(inp); sr = w.getframerate(); a = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
r = dn(a, sr); y = np.clip(np.array(r.samples), -1, 1)
o = wave.open(out, 'wb'); o.setnchannels(1); o.setsampwidth(2); o.setframerate(r.sample_rate); o.writeframes((y * 32767).astype(np.int16).tobytes()); o.close()
print('ok', r.sample_rate, round(len(y) / r.sample_rate, 2), 'denoiser_sr', dn.sample_rate if hasattr(dn, 'sample_rate') else '?')
