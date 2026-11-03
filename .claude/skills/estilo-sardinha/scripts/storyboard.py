"""Gera storyboard: um quadro por cena (A/B) e um por bloco C, com formato e fala. Uso: render.py PASTA titulo saida.jpg"""
import sys, subprocess, glob, os, importlib.util
from PIL import Image, ImageDraw, ImageFont
render, base, titulo, saida = sys.argv[1:5]
sys.argv = ['x', base]
spec = importlib.util.spec_from_file_location('r', render); R = importlib.util.module_from_spec(spec); spec.loader.exec_module(R)
pts = []
for bi, b in enumerate(R.BL):
    if b['f'] == 'C': pts.append((b['t0'] + b['t1']) / 2); continue
    sc = R.SCENES[bi]
    for i, (st, fn) in enumerate(sc):
        end = sc[i + 1][0] if i + 1 < len(sc) else b['t1']
        pts.append(max(st + 0.4, end - 0.35))
pts = [round(round(p * R.FPS) / R.FPS, 3) for p in pts]
for f in glob.glob(os.path.join(base, 'prev_*.jpg')): os.remove(f)
subprocess.run(['python3', '-I', render, base] + [str(p) for p in pts], capture_output=True)
def seg_text(t):
    for i in range(len(R.SEGS)):
        if R.T(i) <= t + 0.3 and t < R.TE(i) + 0.5: last = i
    return R.SEGS[last][2].capitalize()
F = os.path.join(base, 'fonts/package/files/montserrat-latin-900-normal.woff'); F8 = F.replace('900', '800')
nomes = {"A": "TELA DIVIDIDA", "B": "B-ROLL TELA CHEIA", "C": "VOCÊ EM TELA CHEIA"}
cores = {'A': (43, 79, 160), 'B': (40, 140, 90), 'C': (200, 80, 50)}
tw, th, cap, cols = 300, 533, 120, 7
rows = (len(pts) + cols - 1) // cols
S = Image.new('RGB', (cols * (tw + 16) + 16, 110 + rows * (th + cap + 16)), (245, 240, 230)); d = ImageDraw.Draw(S)
d.text((20, 30), "STORYBOARD — " + titulo, font=ImageFont.truetype(F, 46), fill=(34, 25, 39))
for i, t in enumerate(pts):
    fp = os.path.join(base, f'prev_{t:05.2f}.jpg')
    if not os.path.exists(fp): continue
    x = 16 + (i % cols) * (tw + 16); y = 110 + (i // cols) * (th + cap + 16)
    S.paste(Image.open(fp).resize((tw, th)), (x, y))
    fmt = R.block_at(t)[1]['f']
    d.rounded_rectangle((x, y + th + 6, x + tw, y + th + 40), 8, fill=cores[fmt])
    d.text((x + tw / 2, y + th + 23), f"{i + 1}. {nomes[fmt]}", font=ImageFont.truetype(F, 20), fill='white', anchor='mm')
    fo = ImageFont.truetype(F8, 17); words = ('"' + seg_text(t) + '"').split(); lines = []; cur = ''
    for w in words:
        if fo.getlength(cur + ' ' + w) > tw - 6 and cur: lines.append(cur); cur = w
        else: cur = (cur + ' ' + w).strip()
    lines.append(cur)
    for k, l in enumerate(lines[:4]): d.text((x + 3, y + th + 48 + k * 21), l, font=fo, fill=(34, 25, 39))
S.save(saida, quality=90); print('ok', len(pts))
