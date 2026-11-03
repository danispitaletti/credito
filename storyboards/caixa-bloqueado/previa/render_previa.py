"""Prévia em vídeo (animatic) do Reel 'Caixa bloqueado' — estilo Tay + Thiago, terracota.
Uso: python3 render_previa.py <pasta_assets> <pasta_fontes> <saida.mp4>
"""
import sys, math, subprocess, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

A, FD, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
W, H, FPS, DUR = 1080, 1920, 30, 20.0
N = int(DUR * FPS)
TERRA, TERRA_L, CHAR, OW = (163, 72, 47), (200, 102, 74), (14, 14, 16), (242, 238, 232)

F_S = f'{FD}/f1.ttf'; F_N = f'{FD}/f2.ttf'; F_B = f'{FD}/f3.ttf'
_fc = {}
def font(p, s):
    k = (p, s)
    if k not in _fc: _fc[k] = ImageFont.truetype(p, s)
    return _fc[k]

def ease(x): x = max(0.0, min(1.0, x)); return 1 - (1 - x) ** 3

# ---------- leitura de vídeo ----------
def read_clip(path, start, dur, w, h, extra=''):
    vf = f'scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},fps={FPS}' + (',' + extra if extra else '')
    n = int(round(dur * FPS)) + 2
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-ss', str(start), '-i', path, '-t', str(dur + 0.2), '-vf', vf,
                          '-frames:v', str(n), '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], capture_output=True).stdout
    arr = np.frombuffer(raw, np.uint8).reshape(-1, h, w, 3)
    return arr

def frame_at(arr, i):
    return Image.fromarray(arr[min(i, len(arr) - 1)])

def push(img, z, cy=0.4):
    """zoom lento centrado (cy = altura relativa do ponto fixo)"""
    if z <= 1.0001: return img
    w, h = img.size; nw, nh = int(w / z), int(h / z)
    x0 = (w - nw) // 2; y0 = int((h - nh) * cy)
    return img.crop((x0, y0, x0 + nw, y0 + nh)).resize((w, h), Image.BILINEAR)

# ---------- fundo escuro animado (Thiago/Tay: charcoal com luz) ----------
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
def dark_bg(t):
    cx = W * (0.5 + 0.15 * math.sin(t * 0.6)); cy = H * (0.42 + 0.05 * math.cos(t * 0.5))
    d = np.sqrt(((xx - cx) / W) ** 2 + ((yy - cy) / H) ** 2)
    g = np.clip(1 - d * 1.6, 0, 1) ** 2
    base = np.array(CHAR, np.float32)
    glow = np.array((60, 34, 26), np.float32)
    img = base[None, None, :] + g[..., None] * glow[None, None, :]
    return Image.fromarray(img.astype(np.uint8))

# ---------- sombra / cartão arredondado ----------
def rounded_mask(w, h, r):
    m = Image.new('L', (w, h), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), r, fill=255); return m

def paste_card(canvas, img, cx, cy, scale, alpha, r=40):
    w, h = int(img.width * scale), int(img.height * scale)
    if w < 4 or h < 4: return
    im = img.resize((w, h), Image.BILINEAR)
    m = rounded_mask(w, h, int(r * scale))
    if alpha < 1: m = m.point(lambda v: int(v * alpha))
    # sombra
    sh = Image.new('L', (w + 120, h + 120), 0); sh.paste(m, (60, 75))
    sh = sh.filter(ImageFilter.GaussianBlur(28)).point(lambda v: int(v * 0.75))
    canvas.paste(Image.new('RGB', sh.size, (0, 0, 0)), (int(cx - w / 2 - 60), int(cy - h / 2 - 60)), sh)
    canvas.paste(im, (int(cx - w / 2), int(cy - h / 2)), m)

# ---------- legenda estilo Tay ----------
STY = {'n': (F_N, 50, (255, 255, 255)), 's': (F_S, 104, (255, 255, 255)),
       't': (F_B, 58, TERRA_L), 'b': (F_B, 74, (255, 255, 255))}
def caption(canvas, lines, y, age):
    p = ease(age / 0.14); sc = 0.92 + 0.08 * p
    layer = Image.new('RGBA', (W, 560), (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
    yy0 = 20
    for txt, st in lines:
        fp, sz, col = STY[st]; f = font(fp, sz)
        bb = d.textbbox((0, 0), txt, font=f); tw, th = bb[2] - bb[0], bb[3] - bb[1]
        x = (W - tw) / 2 - bb[0]
        d.text((x, yy0 - bb[1]), txt, font=f, fill=col + (255,))
        yy0 += th + (6 if st != 's' else -2)
    sh = Image.new('RGBA', layer.size, (0, 0, 0, 0)); sh.putalpha(layer.split()[3].filter(ImageFilter.GaussianBlur(7)).point(lambda v: int(v * 0.7)))
    comp = Image.alpha_composite(sh, layer)
    if sc != 1:
        comp = comp.resize((int(W * sc), int(560 * sc)), Image.BILINEAR)
    a = comp.split()[3].point(lambda v: int(v * p))
    comp.putalpha(a)
    canvas.paste(comp, (int((W - comp.width) / 2), int(y - comp.height / 2 + 140)), comp)

def watermark(canvas):
    d = ImageDraw.Draw(canvas)
    f = font(F_N, 24); txt = 'PRÉVIA · rosto e B-rolls ilustrativos'
    bb = d.textbbox((0, 0), txt, font=f)
    d.text(((W - bb[2]) / 2, 215), txt, font=f, fill=(255, 255, 255))

# ---------- celular 3D ----------
def phone_ui(t_local):
    pw, ph = 470, 960
    im = Image.new('RGBA', (pw, ph), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, pw - 1, ph - 1), 70, fill=(18, 18, 20), outline=(58, 58, 62), width=6)
    d.rounded_rectangle((18, 18, pw - 19, ph - 19), 56, fill=(24, 25, 29))
    d.rounded_rectangle((pw / 2 - 60, 34, pw / 2 + 60, 64), 15, fill=(8, 8, 9))
    fN = font(F_N, 22); fB = font(F_B, 44); fS = font(F_N, 26)
    d.text((48, 120), 'SEGUNDA · 08:02', font=font(F_N, 20), fill=(150, 150, 155))
    d.text((48, 180), 'Conta Empresarial', font=fS, fill=OW)
    d.text((48, 222), 'R$ •••••', font=fB, fill=OW)
    for k, yb in enumerate((560, 610, 660)):
        d.rounded_rectangle((48, yb, pw - 48 - k * 60, yb + 20), 10, fill=(38, 39, 44))
    # notificação que entra
    p = ease((t_local - 0.7) / 0.35)
    if p > 0:
        y0 = 300 + (1 - p) * 40
        card = Image.new('RGBA', (pw - 80, 200), (0, 0, 0, 0)); cd = ImageDraw.Draw(card)
        cd.rounded_rectangle((0, 0, card.width - 1, 199), 26, fill=(60, 30, 24, 255), outline=TERRA_L + (255,), width=3)
        cd.text((26, 28), 'Conta em análise', font=font(F_B, 32), fill=(240, 150, 125))
        cd.text((26, 84), 'Movimentações', font=fN, fill=(225, 215, 210))
        cd.text((26, 116), 'temporariamente indisponíveis.', font=fN, fill=(225, 215, 210))
        a = card.split()[3].point(lambda v: int(v * p)); card.putalpha(a)
        im.alpha_composite(card, (40, int(y0)))
    return im

def perspective_coeffs(src, dst):
    m = []
    for (x, y), (u, v) in zip(dst, src):
        m.append([x, y, 1, 0, 0, 0, -u * x, -u * y]); m.append([0, 0, 0, x, y, 1, -v * x, -v * y])
    A_ = np.array(m, np.float64); B_ = np.array(src, np.float64).reshape(8)
    return np.linalg.solve(A_, B_).tolist()

def rotate_y(im, ang, scale):
    w, h = im.size; c = math.cos(ang); s = math.sin(ang)
    f = 1400.0
    pts = []
    for (x, y) in [(-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2)]:
        X = x * c; Z = x * s
        k = f / (f + Z)
        pts.append((X * k * scale, y * k * scale))
    minx = min(p[0] for p in pts); miny = min(p[1] for p in pts)
    dst = [(p[0] - minx, p[1] - miny) for p in pts]
    ow = int(max(p[0] for p in dst)) + 2; oh = int(max(p[1] for p in dst)) + 2
    co = perspective_coeffs([(0, 0), (w, 0), (w, h), (0, h)], dst)
    return im.transform((ow, oh), Image.PERSPECTIVE, co, Image.BICUBIC)

def light_sweep(im, t):
    w, h = im.size
    band = np.zeros((h, w), np.float32)
    pos = (t % 2.2) / 2.2 * (w + h) - h * 0.3
    xs = np.arange(w)[None, :] + np.arange(h)[:, None] * 0.45
    band = np.clip(1 - np.abs(xs - pos) / 60, 0, 1) * 0.18
    a = np.asarray(im.split()[3], np.float32) / 255
    over = Image.fromarray((band * a * 255).astype(np.uint8))
    white = Image.new('RGBA', im.size, (255, 255, 255, 0)); white.putalpha(over)
    return Image.alpha_composite(im, white)

# ---------- cartão de seção P&B ----------
def section_text(canvas, tl):
    lines = [('O PROBLEMA #1', F_N, 34, OW, 0.0), ('UM LUGAR SÓ', F_B, 104, TERRA_L, 0.15), ('o caixa inteiro', F_S, 96, (255, 255, 255), 0.3)]
    y = 1180
    for txt, fp, sz, col, dl in lines:
        f = font(fp, sz); p = ease((tl - dl) / 0.35)
        lay = Image.new('RGBA', (W, sz + 60), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
        bb = d.textbbox((0, 0), txt, font=f)
        d.text((80 - bb[0], 20 - bb[1] + (1 - p) * 40), txt, font=f, fill=col + (int(255 * p),))
        sh = Image.new('RGBA', lay.size, (0, 0, 0, 0)); sh.putalpha(lay.split()[3].filter(ImageFilter.GaussianBlur(6)).point(lambda v: int(v * .6)))
        canvas.paste(Image.alpha_composite(sh, lay), (0, int(y)), Image.alpha_composite(sh, lay))
        y += (bb[3] - bb[1]) + 34

# ---------- linha do tempo ----------
print('lendo vídeos...', flush=True)
DANI = f'{A}/dani.mp4'
warm = 'eq=saturation=1.06:gamma=1.02,colorbalance=rs=.03:gs=.01:bs=-.03'
clipA = read_clip(DANI, 1.0, 3.8, W, H, warm)
clipF = read_clip(DANI, 46.0, 1.8, W, H, 'hue=s=0,eq=contrast=1.15:brightness=-0.04')
clipG = read_clip(DANI, 52.0, 2.6, W, H, warm)
CW, CH_ = 900, 600
clipC = read_clip(f'{A}/b2.mp4', 0.5, 3.6, CW, CH_)
clipD = read_clip(f'{A}/b1.mp4', 2.0, 3.2, CW, CH_)
clipE = read_clip(f'{A}/b4.mp4', 3.0, 2.0, CW, CH_)

SEG = [('A', 0.0, 3.8), ('B', 3.8, 6.8), ('C', 6.8, 10.4), ('D', 10.4, 13.6), ('E', 13.6, 15.6), ('F', 15.6, 17.4), ('G', 17.4, 20.0)]
CAPS = [
    (0.0, 0.9, [('Imagina abrir', 'n')]),
    (0.9, 1.9, [('o aplicativo', 'n'), ('na segunda', 's')]),
    (1.9, 2.8, [('e descobrir que', 'n'), ('o caixa', 'b')]),
    (2.8, 3.8, [('da empresa', 't'), ('está bloqueado.', 'b')]),
    (3.8, 5.0, [('Ninguém avisou,', 'n')]),
    (5.0, 6.8, [('e a tela só diz', 'n'), ('em análise.', 's')]),
    (6.8, 8.6, [('pode ser um processo', 'n'), ('antigo,', 's')]),
    (8.6, 10.4, [('ou um erro', 'n'), ('do próprio banco.', 'b')]),
    (10.4, 12.0, [('o fornecedor vence', 'n'), ('na quarta,', 's')]),
    (12.0, 13.6, [('a folha', 'n'), ('na sexta,', 't')]),
    (13.6, 15.6, [('e o dinheiro fica', 'n'), ('parado.', 's')]),
    (17.4, 18.6, [('o problema é deixar', 'n'), ('o caixa inteiro', 't')]),
    (18.6, 20.0, [('num lugar', 'n'), ('só.', 'b')]),
]
CAP_Y = {'A': 1150, 'B': 1420, 'C': 1270, 'D': 1270, 'E': 1270, 'F': None, 'G': 1150}

ff = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                       '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p', OUT + '.video.mp4'], stdin=subprocess.PIPE)
for fi in range(N):
    t = fi / FPS
    seg = next(s for s in SEG if s[1] <= t < s[2]); name, s0, s1 = seg; tl = t - s0; li = int(round(tl * FPS))
    if name == 'A':
        c = push(frame_at(clipA, li), 1.0 + 0.06 * tl / 3.8)
    elif name == 'G':
        c = push(frame_at(clipG, li), 1.18 + 0.05 * tl / 2.6, 0.32)
    elif name == 'F':
        c = push(frame_at(clipF, li), 1.10 + 0.03 * tl, 0.3)
    elif name == 'B':
        c = dark_bg(t)
        ph = phone_ui(tl)
        ang = math.radians(32 * (1 - ease(tl / 0.6)) + 4 * math.sin(tl * 1.6))
        sc = (0.82 + 0.18 * ease(tl / 0.6) + 0.02 * tl) * 0.8
        img = light_sweep(rotate_y(ph, ang, sc), tl + 0.4)
        y = 800 + 10 * math.sin(tl * 2.0)
        c.paste(img, (int(W / 2 - img.width / 2), int(y - img.height / 2)), img)
    else:
        c = dark_bg(t)
        clip = {'C': clipC, 'D': clipD, 'E': clipE}[name]
        p = ease(tl / 0.28); sc = (0.88 + 0.12 * p) * (1 + 0.025 * tl)
        fr = frame_at(clip, li)
        if name == 'E': fr = push(fr, 1 + 0.08 * tl)
        paste_card(c, fr, W / 2, 700, sc, p)
    if name == 'F': section_text(c, tl)
    for a, b, lines in CAPS:
        if a <= t < b and CAP_Y[name]:
            caption(c, lines, CAP_Y[name], t - a)
    watermark(c)
    ff.stdin.write(c.convert('RGB').tobytes())
    if fi % 60 == 0: print(f'quadro {fi}/{N}', flush=True)
ff.stdin.close(); ff.wait()

# ---------- efeitos sonoros discretos ----------
SR = 48000; out = np.zeros(int(DUR * SR) + SR)
rng = np.random.default_rng(3)
def whoosh(d=0.32):
    n = int(d * SR); x = rng.standard_normal(n); tt = np.linspace(0, 1, n)
    y = np.convolve(x, np.ones(10) / 10, 'same') - np.convolve(x, np.ones(90) / 90, 'same')
    return y * np.sin(np.pi * tt) ** 2 * 0.22
def tick():
    n = int(0.05 * SR); tt = np.arange(n) / SR
    return np.sin(2 * np.pi * 1500 * tt) * np.exp(-tt * 80) * 0.10
def add(T, s):
    i = int(T * SR); out[i:i + len(s)] += s[:max(0, len(out) - i)]
for s in SEG[1:]: add(max(0, s[1] - 0.12), whoosh())
for a, b, lines in CAPS:
    if any(st in ('t', 's', 'b') for _, st in lines): add(a + 0.05, tick())
out = np.clip(out, -1, 1)
with wave.open(OUT + '.wav', 'wb') as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((out * 32767).astype(np.int16).tobytes())
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', OUT + '.video.mp4', '-i', OUT + '.wav', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k',
                '-shortest', '-movflags', '+faststart', OUT])
print('ok', OUT)
