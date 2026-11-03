"""Prévia 'Chile x Brasil / autocustódia' — sem pessoas. Mapa 3D (NASA Blue Marble, domínio público),
números animados, palavra gigante (Thiago), construção palavra a palavra, legenda cursiva + destaque terracota.
Uso: python3 render_chile.py <pasta_mapa> <pasta_fontes> <saida.mp4>
"""
import sys, math, subprocess, wave, random
import numpy as np
import shapefile
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

MD, FD, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
W, H, FPS, DUR = 1080, 1920, 30, 35.0
N = int(DUR * FPS)
TERRA, TERRA_L, CHAR, OW = (163, 72, 47), (205, 108, 80), (14, 14, 16), (242, 238, 232)
F_S, F_N, F_B = f'{FD}/f1.ttf', f'{FD}/f2.ttf', f'{FD}/f3.ttf'
_fc = {}
def font(p, s):
    if (p, s) not in _fc: _fc[(p, s)] = ImageFont.truetype(p, s)
    return _fc[(p, s)]
def ease(x): x = max(0.0, min(1.0, x)); return 1 - (1 - x) ** 3
def eio(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)
def lerp(a, b, p): return a + (b - a) * p

# ---------- plano do mapa ----------
LON0, LON1, LAT0, LAT1 = -100.0, -20.0, 40.0, -62.0
SC = 3  # upscale
src = Image.open(f'{MD}/earth-blue-marble.jpg').convert('RGB')
sw, sh = src.size
def lx(lon): return (lon + 180) / 360 * sw
def ly(lat): return (90 - lat) / 180 * sh
crop = src.crop((int(lx(LON0)), int(ly(LAT0)), int(lx(LON1)), int(ly(LAT1))))
PW, PH = crop.width * SC, crop.height * SC
plane = crop.resize((PW, PH), Image.LANCZOS)
# tratamento: escuro, sóbrio, levemente frio no mar e quente na terra
plane = ImageEnhance.Color(plane).enhance(0.55)
plane = ImageEnhance.Brightness(plane).enhance(0.62)
plane = ImageEnhance.Contrast(plane).enhance(1.15)
def px(lon, lat): return ((lon - LON0) / (LON1 - LON0) * PW, (LAT0 - lat) / (LAT0 - LAT1) * PH)

r = shapefile.Reader(f'{MD}/ne_50m_admin_0_countries')
fi_ = [x[0] for x in r.fields[1:]].index('ADMIN')
polys = {}
for k, rec in enumerate(r.records()):
    nm = rec[fi_]
    if nm in ('Chile', 'Brazil', 'Argentina', 'Peru', 'Bolivia', 'Paraguay', 'Uruguay', 'Colombia', 'Venezuela', 'Ecuador', 'Guyana', 'Suriname', 'France'):
        shp = r.shape(k); pts = shp.points; parts = list(shp.parts) + [len(pts)]
        polys[nm] = [[px(*pts[i]) for i in range(parts[j], parts[j + 1])] for j in range(len(parts) - 1)]
def mask_of(names):
    m = Image.new('L', (PW, PH), 0); d = ImageDraw.Draw(m)
    for nm in names:
        for ring in polys.get(nm, []):
            if len(ring) > 2: d.polygon(ring, fill=255)
    return m
borders = Image.new('RGBA', (PW, PH), (0, 0, 0, 0)); bd = ImageDraw.Draw(borders)
for nm, rings in polys.items():
    for ring in rings:
        if len(ring) > 2: bd.line(ring + [ring[0]], fill=(255, 255, 255, 70), width=3)
plane_b = plane.convert('RGBA'); plane_b.alpha_composite(borders); plane_b = plane_b.convert('RGB')
m_cl = mask_of(['Chile']); m_br = mask_of(['Brazil'])
def tint(base, mask, col, a):
    lay = Image.new('RGB', base.size, col)
    return Image.composite(lay, base, mask.point(lambda v: int(v * a)))
def glow_edge(base, mask, col):
    e = mask.filter(ImageFilter.FIND_EDGES).filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.GaussianBlur(6))
    return Image.composite(Image.new('RGB', base.size, col), base, e.point(lambda v: min(255, v * 3)))
P0 = plane_b
P1 = glow_edge(tint(P0, m_cl, TERRA, 0.38), m_cl, TERRA)                       # Chile em terracota
P2 = tint(P1, m_br, (40, 40, 44), 0.55)                                          # Brasil apagado
print('plano', PW, PH, flush=True)

# ---------- câmera 3D (homografia) ----------
def cam_coeffs(lon, lat, wdeg, k):
    cx, cy = px(lon, lat)
    wb = wdeg / (LON1 - LON0) * PW / 2          # meia-largura na base
    wt = wb * k                                  # meia-largura no topo (mais longe)
    hn = wb * 1.05; hf = wb * 2.4 * (0.75 + 0.25 * k)
    srcq = [(cx - wt, cy - hf), (cx + wt, cy - hf), (cx + wb, cy + hn), (cx - wb, cy + hn)]
    dst = [(0, 0), (W, 0), (W, H), (0, H)]
    m = []
    for (x, y), (u, v) in zip(dst, srcq):
        m.append([x, y, 1, 0, 0, 0, -u * x, -u * y]); m.append([0, 0, 0, x, y, 1, -v * x, -v * y])
    c = np.linalg.solve(np.array(m, float), np.array(srcq, float).reshape(8))
    return c.tolist()
def project(coeffs, lon, lat):
    a, b, c, d, e, f, g, h = coeffs
    Hm = np.array([[a, b, c], [d, e, f], [g, h, 1.0]]); Hi = np.linalg.inv(Hm)
    u, v = px(lon, lat); q = Hi @ np.array([u, v, 1.0]); return q[0] / q[2], q[1] / q[2]
sky = np.zeros((H, W), np.float32)
for y in range(H): sky[y, :] = max(0.0, 1 - y / (H * 0.30)) ** 1.6
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
vig = np.clip(((xx - W / 2) / W) ** 2 * 1.4 + ((yy - H * 0.55) / H) ** 2 * 1.2, 0, 1)
shade = np.clip(1 - 0.85 * sky - 0.55 * vig, 0, 1)[..., None]
CHAR_A = np.array(CHAR, np.float32)
def render_map(P, lon, lat, wdeg, k):
    co = cam_coeffs(lon, lat, wdeg, k)
    img = P.transform((W, H), Image.PERSPECTIVE, co, Image.BILINEAR, fillcolor=CHAR)
    a = np.asarray(img, np.float32)
    a = a * shade + CHAR_A * (1 - shade)
    return Image.fromarray(a.astype(np.uint8)), co

# ---------- textos ----------
def text_layer(txt, fp, size, col, track=0):
    f = font(fp, size); d0 = ImageDraw.Draw(Image.new('L', (1, 1)))
    if track:
        ws = [d0.textlength(ch, font=f) + track for ch in txt]; tw = int(sum(ws)) + 10
    else:
        bb = d0.textbbox((0, 0), txt, font=f); tw = bb[2] - bb[0] + 20
    asc, desc = f.getmetrics(); th = asc + desc + 20
    lay = Image.new('RGBA', (tw, th), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    if track:
        x = 5
        for ch, wv in zip(txt, ws): d.text((x, 10), ch, font=f, fill=col + (255,)); x += wv
    else:
        bb = d.textbbox((0, 0), txt, font=f); d.text((10 - bb[0], 10), txt, font=f, fill=col + (255,))
    return lay
def with_shadow(lay, blur=8, a=0.75):
    s = Image.new('RGBA', lay.size, (0, 0, 0, 0)); s.putalpha(lay.split()[3].filter(ImageFilter.GaussianBlur(blur)).point(lambda v: int(v * a)))
    return Image.alpha_composite(s, lay)
def put(canvas, lay, cx, cy, p=1.0, dy=30, scale=1.0, anchor='c'):
    if p <= 0: return
    if scale != 1.0: lay = lay.resize((max(1, int(lay.width * scale)), max(1, int(lay.height * scale))), Image.BILINEAR)
    lay = lay.copy(); lay.putalpha(lay.split()[3].point(lambda v: int(v * min(1, p))))
    x = cx - lay.width / 2 if anchor == 'c' else cx
    canvas.paste(lay, (int(x), int(cy - lay.height / 2 + (1 - ease(p)) * dy)), lay)

def caption(canvas, script_txt, key_txt, y, age, dur):
    """legenda: fala em cursiva branca + palavra-chave em terracota; entra palavra a palavra"""
    words = script_txt.split()
    n_show = max(1, int(len(words) * min(1, age / (dur * 0.55))) + 1)
    full = words; d0 = ImageDraw.Draw(Image.new('L', (1, 1))); f = font(F_S, 80)
    lines = [full]
    if d0.textlength(' '.join(full), font=f) > 900:
        best = min(range(1, len(full)), key=lambda i: abs(d0.textlength(' '.join(full[:i]), font=f) - d0.textlength(' '.join(full[i:]), font=f)))
        lines = [full[:best], full[best:]]
    shown = n_show; yy_ = y - (len(lines) - 1) * 44
    for ln in lines:
        part = ln[:max(0, shown)]; shown -= len(ln)
        if part:
            l1 = with_shadow(text_layer(' '.join(part), F_S, 80, (255, 255, 255)), 8, 0.9)
            put(canvas, l1, W / 2, yy_, p=age / 0.15, dy=10)
        yy_ += 88
    y = yy_ - 88
    if key_txt:
        pk = (age - dur * 0.45) / 0.18
        if pk > 0:
            l2 = with_shadow(text_layer(key_txt, F_B, 64, TERRA_L, track=3), 8, 0.85)
            put(canvas, l2, W / 2, y + 92, p=pk, dy=18, scale=0.9 + 0.1 * ease(pk))

def label(canvas, txt, cx, cy, p, col=OW):
    put(canvas, with_shadow(text_layer(txt, F_N, 30, col, track=6), 6, 0.7), cx, cy, p, dy=12)

def glass(canvas, x0, y0, x1, y1, p):
    if p <= 0: return
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    a = int(190 * min(1, p))
    d.rounded_rectangle((x0, y0, x1, y1), 34, fill=(16, 16, 19, a), outline=(255, 255, 255, int(40 * min(1, p))), width=2)
    canvas.paste(lay, (0, 0), lay)

def marker(canvas, x, y, p, col, txt):
    if p <= 0: return
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    r0 = 14 * ease(p)
    for k in range(3):
        rr = r0 + 26 * ((p * 1.5 + k / 3) % 1)
        d.ellipse((x - rr, y - rr, x + rr, y + rr), outline=col + (int(160 * (1 - ((p * 1.5 + k / 3) % 1))),), width=3)
    d.ellipse((x - r0, y - r0, x + r0, y + r0), fill=col + (255,))
    canvas.paste(lay, (0, 0), lay)
    label(canvas, txt, x, y - 58, p)

# ---------- rede (final) ----------
random.seed(4)
land = mask_of(['Chile', 'Brazil', 'Argentina', 'Peru', 'Bolivia', 'Paraguay', 'Uruguay', 'Colombia', 'Venezuela', 'Ecuador', 'Guyana', 'Suriname'])
la = np.asarray(land)
NODES = []
while len(NODES) < 70:
    u, v = random.uniform(0, PW - 1), random.uniform(0, PH - 1)
    if la[int(v), int(u)] > 0:
        lon = LON0 + u / PW * (LON1 - LON0); lat = LAT0 - v / PH * (LAT0 - LAT1); NODES.append((lon, lat, random.random()))
EDGES = []
for i, a in enumerate(NODES):
    ds = sorted(((math.hypot(a[0] - b[0], a[1] - b[1]), j) for j, b in enumerate(NODES) if j != i))[:3]
    for dd, j in ds:
        if i < j: EDGES.append((i, j))
def network(canvas, co, p, t):
    if p <= 0: return
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    pts = [project(co, lon, lat) for lon, lat, _ in NODES]
    for i, j in EDGES:
        q = (p * 1.6 - NODES[i][2] * 0.6)
        if q <= 0: continue
        q = min(1, q); (x0, y0), (x1, y1) = pts[i], pts[j]
        d.line((x0, y0, lerp(x0, x1, q), lerp(y0, y1, q)), fill=TERRA_L + (150,), width=3)
    for (x, y), (_, _, s) in zip(pts, NODES):
        q = min(1, max(0, p * 1.6 - s * 0.6))
        if q <= 0: continue
        rr = 5 + 3 * math.sin(t * 3 + s * 9)
        d.ellipse((x - rr, y - rr, x + rr, y + rr), fill=(255, 205, 185, int(255 * q)))
    g = lay.filter(ImageFilter.GaussianBlur(10))
    canvas.paste(g, (0, 0), g); canvas.paste(lay, (0, 0), lay)

# ---------- câmera: chaves (t, lon, lat, largura_graus, inclinação) ----------
CAM = [(0.0, -60, -18, 74, 1.25), (4.2, -71.5, -33, 26, 1.7), (10.0, -71.0, -36, 21, 1.8), (17.0, -70.5, -30, 24, 1.7),
       (20.0, -57, -20, 50, 1.45), (23.0, -56, -21, 46, 1.4), (28.0, -60, -22, 70, 1.3), (35.0, -60, -24, 84, 1.2)]
def cam(t):
    for a, b in zip(CAM, CAM[1:]):
        if a[0] <= t <= b[0]:
            p = eio((t - a[0]) / (b[0] - a[0])); return [lerp(a[i], b[i], p) for i in range(1, 5)]
    return CAM[-1][1:]

CAPS = [  # (início, fim, fala em cursiva, palavra-chave, y)
    (0.0, 2.6, 'Em menos de um ano de governo,', None, 1480),
    (2.6, 5.5, 'o Chile aprovou uma das maiores', 'REFORMAS TRIBUTÁRIAS', 1480),
    (5.5, 10.0, 'o imposto das empresas vai cair', 'ATÉ 2029', 1480),
    (10.0, 13.5, 'quem compra imóvel novo fica', 'ISENTO DE IVA', 1480),
    (13.5, 17.5, 'grandes investimentos ganham regras', 'CONGELADAS', 1480),
    (17.5, 20.3, 'o Chile é o 17º país', 'MAIS LIVRE DO MUNDO', 780),
    (20.3, 23.0, 'e o Brasil?', '134º', 780),
    (23.0, 25.6, 'você não escolhe as regras do seu país,', None, 1200),
    (25.6, 28.0, 'mas pode escolher onde guarda', 'O SEU PATRIMÔNIO', 1200),
    (28.0, 31.0, 'com autocustódia em cripto,', None, 1450),
]

ff = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                       '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p', OUT + '.video.mp4'], stdin=subprocess.PIPE)
for fi in range(N):
    t = fi / FPS
    lon, lat, wd, k = cam(t)
    hl = eio((t - 1.8) / 1.6)
    if t < 19.0:
        base, co = render_map(P0 if hl <= 0 else P1, lon, lat, wd, k)
        if 0 < hl < 1:
            b0, _ = render_map(P0, lon, lat, wd, k); base = Image.blend(b0, base, hl)
    else:
        pb = eio((t - 19.0) / 1.5)
        base, co = render_map(P2, lon, lat, wd, k)
        if pb < 1:
            b1, _ = render_map(P1, lon, lat, wd, k); base = Image.blend(b1, base, pb)
    c = base
    # bloco "escolha": mapa escurece e desfoca, palavra gigante atrás
    if 23.0 <= t < 28.6:
        p = eio((t - 23.0) / 0.6) * (1 - eio((t - 28.0) / 0.6))
        blur = c.filter(ImageFilter.GaussianBlur(14)); blur = ImageEnhance.Brightness(blur).enhance(0.45)
        c = Image.blend(c, blur, p)
        g1 = with_shadow(text_layer('VOCÊ', F_N, 54, OW, track=14), 10, 0.6)
        g2 = with_shadow(text_layer('ESCOLHE', F_B, 210, TERRA_L), 18, 0.6)
        put(c, g1, W / 2, 640, p=(t - 23.2) / 0.3); put(c, g2, W / 2, 800, p=(t - 23.4) / 0.35, dy=50, scale=1 + 0.03 * (t - 23.4))
        if t >= 25.6:
            g3 = with_shadow(text_layer('ONDE GUARDA', F_N, 46, OW, track=10), 10, 0.6); put(c, g3, W / 2, 960, p=(t - 25.7) / 0.3)
    # rede + chave + autocustódia
    if t >= 27.8:
        pn = eio((t - 27.8) / 3.0)
        network(c, co, pn, t)
    if 28.6 <= t < 31.2:
        p = (t - 28.8) / 0.35
        put(c, with_shadow(text_layer('A CHAVE', F_N, 64, OW, track=12), 12, 0.7), W / 2, 560, p)
        put(c, with_shadow(text_layer('É SUA', F_B, 200, TERRA_L), 18, 0.7), W / 2, 720, (t - 29.1) / 0.35, dy=50, scale=1 + 0.02 * (t - 29))
    if t >= 31.0:
        p = (t - 31.0) / 0.4
        put(c, with_shadow(text_layer('AUTOCUSTÓDIA', F_B, 100, OW), 16, 0.75), W / 2, 760, p, dy=40, scale=1 + 0.012 * (t - 31))
        put(c, with_shadow(text_layer('é segurança', F_S, 120, (255, 255, 255)), 10, 0.8), W / 2, 930, (t - 31.6) / 0.4)
        put(c, with_shadow(text_layer('E PROTEÇÃO', F_B, 92, TERRA_L, track=4), 12, 0.8), W / 2, 1060, (t - 32.3) / 0.4, dy=30)
    # números e cartões
    if 5.5 <= t < 10.2:
        p = (t - 5.6) / 0.4; q = eio((t - 7.0) / 1.6)
        glass(c, 150, 330, 930, 820, p)
        label(c, 'IMPOSTO DAS EMPRESAS', W / 2, 400, p)
        val = round(lerp(27, 23, q))
        col = OW if q < 1 else TERRA_L
        put(c, with_shadow(text_layer(f'{val}%', F_B, 250, col), 14, 0.6), W / 2, 590, p, dy=30)
        put(c, with_shadow(text_layer('até 2029', F_S, 90, OW), 8, 0.7), W / 2, 750, (t - 8.4) / 0.4)
    if 10.0 <= t < 13.7:
        p = (t - 10.1) / 0.35
        glass(c, 150, 360, 930, 800, p)
        label(c, 'IMÓVEL NOVO', W / 2, 430, p)
        put(c, with_shadow(text_layer('IVA', F_B, 210, OW), 14, 0.6), W / 2, 590, p, dy=30)
        ps = eio((t - 11.2) / 0.3)
        if ps > 0:
            lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
            d.line((330, 600, lerp(330, 750, ps), 600), fill=TERRA_L + (255,), width=14); c.paste(lay, (0, 0), lay)
        put(c, with_shadow(text_layer('isento', F_S, 100, TERRA_L), 8, 0.7), W / 2, 730, (t - 11.6) / 0.4)
    if 13.5 <= t < 17.7:
        p = (t - 13.6) / 0.35; q = eio((t - 14.0) / 1.6)
        glass(c, 150, 330, 930, 820, p)
        label(c, 'GRANDES INVESTIMENTOS', W / 2, 400, p)
        put(c, with_shadow(text_layer(f'{round(lerp(0, 20, q))}', F_B, 260, TERRA_L if q >= 1 else OW), 14, 0.6), W / 2, 590, p, dy=30)
        put(c, with_shadow(text_layer('ANOS DE REGRAS CONGELADAS', F_N, 34, OW, track=5), 8, 0.7), W / 2, 760, (t - 15.4) / 0.3)
    if 17.5 <= t < 23.0:
        x, y = project(co, -70.6, -33.4); marker(c, x, y, (t - 17.6) / 0.6, TERRA_L, 'CHILE')
        pc = (t - 17.8) / 0.4
        glass(c, 90, 300, 520, 640, pc)
        label(c, 'RANKING', 305, 360, pc)
        put(c, with_shadow(text_layer(f'{round(lerp(184, 17, eio((t - 18.0) / 1.4)))}º', F_B, 170, TERRA_L), 12, 0.6), 305, 500, pc)
        label(c, 'CHILE', 305, 600, pc)
        if t >= 20.3:
            x2, y2 = project(co, -47.9, -15.8); marker(c, x2, y2, (t - 20.3) / 0.6, (150, 150, 155), 'BRASIL')
            pb = (t - 20.5) / 0.4
            glass(c, 560, 300, 990, 640, pb)
            label(c, 'RANKING', 775, 360, pb)
            put(c, with_shadow(text_layer(f'{round(lerp(1, 134, eio((t - 20.7) / 1.3)))}º', F_B, 170, (170, 170, 175)), 12, 0.6), 775, 500, pb)
            label(c, 'BRASIL', 775, 600, pb)
    if t < 5.6:
        label(c, 'AMÉRICA DO SUL · 2026', W / 2, 330, t / 0.5)
    # legendas
    for a, b, s, kk, y in CAPS:
        if a <= t < b: caption(c, s, kk, y, t - a, b - a)
    # fade final
    if t > 34.2:
        c = Image.blend(c, Image.new('RGB', (W, H), CHAR), eio((t - 34.2) / 0.8))
    d = ImageDraw.Draw(c); d.text((W / 2, 225), 'PRÉVIA · sem narração', font=font(F_N, 24), fill=(200, 200, 200), anchor='mm')
    ff.stdin.write(c.tobytes())
    if fi % 90 == 0: print(f'quadro {fi}/{N}', flush=True)
ff.stdin.close(); ff.wait()

# ---------- som ----------
SR = 48000; out = np.zeros(int(DUR * SR) + SR); rng = np.random.default_rng(5)
def whoosh(d=0.45, g=0.22):
    n = int(d * SR); x = rng.standard_normal(n); tt = np.linspace(0, 1, n)
    y = np.convolve(x, np.ones(10) / 10, 'same') - np.convolve(x, np.ones(120) / 120, 'same'); return y * np.sin(np.pi * tt) ** 2 * g
def tick(f=1500, g=0.09):
    n = int(0.05 * SR); tt = np.arange(n) / SR; return np.sin(2 * np.pi * f * tt) * np.exp(-tt * 80) * g
def boom(g=0.35):
    n = int(0.6 * SR); tt = np.arange(n) / SR; return np.sin(2 * np.pi * 55 * tt * (1 - tt * 0.5)) * np.exp(-tt * 6) * g
def add(T, s):
    i = int(T * SR); out[i:i + len(s)] += s[:max(0, len(out) - i)]
# drone grave contínuo
tt = np.arange(len(out)) / SR; out += (np.sin(2 * np.pi * 55 * tt) * 0.025 + np.sin(2 * np.pi * 82.5 * tt) * 0.015) * np.clip(tt / 2, 0, 1) * np.clip((DUR - tt) / 1.0, 0, 1)
for T in (0.1, 5.5, 10.0, 13.5, 17.5, 20.3, 23.0, 28.0): add(T, whoosh())
for T0, T1 in ((7.0, 8.6), (14.0, 15.6), (18.0, 19.4), (20.7, 22.0)):
    for T in np.arange(T0, T1, 0.12): add(T, tick())
for T in (11.2, 23.4, 29.1, 31.0): add(T, boom())
out = np.clip(out, -1, 1)
with wave.open(OUT + '.wav', 'wb') as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((out * 32767).astype(np.int16).tobytes())
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', OUT + '.video.mp4', '-i', OUT + '.wav', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', OUT])
print('ok', OUT)
