"""Procura latidos (AudioSet: Dog/Bark/Yip/Bow-wow/Howl) em janelas de 0,5 s. Uso: modelo_dir arquivo.wav"""
import sys, wave, numpy as np, sherpa_onnx
M, wav = sys.argv[1:3]
cfg = sherpa_onnx.AudioTaggingConfig(model=sherpa_onnx.AudioTaggingModelConfig(ced=f"{M}/model.int8.onnx", num_threads=4), labels=f"{M}/class_labels_indices.csv", top_k=40)
tg = sherpa_onnx.AudioTagging(cfg)
w = wave.open(wav); sr = w.getframerate(); a = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
DOG = {'Dog', 'Bark', 'Yip', 'Bow-wow', 'Howl', 'Growling', 'Whimper (dog)', 'Domestic animals, pets', 'Animal'}
win, hop = 1.0, 0.25
t = 0.0
while t + win <= len(a) / sr + 1e-6:
    x = a[int(t * sr):int((t + win) * sr)]
    st = tg.create_stream(); st.accept_waveform(sr, x)
    ev = tg.compute(st)
    dog = max([e.prob for e in ev if e.name in DOG] + [0])
    top = ', '.join(f"{e.name}:{e.prob:.2f}" for e in ev[:3])
    print(f"{t:5.2f}  cachorro={dog:.2f}  | {top}")
    t += hop
