import os
# Pasta base dos projetos (pode ser trocada pela variável de ambiente DANI_EDITORA)
BASE = os.environ.get('DANI_EDITORA', r'C:\dani video hunter editora')
import math, json, subprocess, sys
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30
SPEED = 1.2
CUT = json.load(open(os.path.join(BASE, 'v5', 'cut.json')))
SEGS = CUT['segs']; WORDS = CUT['words']
# mapa tempo novo -> tempo da fonte
_acc = []; a0 = 0.0
for a, b in SEGS:
    _acc.append((a0, a, b)); a0 += (b - a) / SPEED
TOTAL = a0
def src_t(T):
    for n0, a, b in reversed(_acc):
        if T >= n0: return min(b, a + (T - n0) * SPEED)
    return SEGS[0][0]

# ---------- básicos ----------
_fc = {}
def F(size, w=700):
    k = ('m', size, w)
    if k not in _fc:
        f = ImageFont.truetype(os.path.join(BASE, 'fonts', 'Montserrat.ttf'), size); f.set_variation_by_axes([w]); _fc[k] = f
    return _fc[k]
def OS(size, w=700):
    k = ('o', size, w)
    if k not in _fc:
        f = ImageFont.truetype(os.path.join(BASE, 'fonts', 'Oswald.ttf'), size); f.set_variation_by_axes([w]); _fc[k] = f
    return _fc[k]
def ease(x):
    x = max(0.0, min(1.0, x)); return 1 - (1 - x) ** 3
def ap(t, t0, d=0.3): return ease((t - t0) / d)

INK = (27, 28, 31); GR = (108, 112, 118); LGR = (170, 172, 176); WHITE = (255, 255, 255)
TEAL = (14, 124, 123); NAVY = (30, 58, 95); GREEN = (46, 125, 79); BLUE = (37, 99, 235); RED = (192, 57, 43)
GOLD = (206, 182, 140)

# ---------- 3D ----------
def project(w, h, cx, cy, ry=0.0, rx=0.0, scale=1.0, rz=0.0, f=1400.0):
    pts = []
    for x, y in [(-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2)]:
        x *= scale; y *= scale; z = 0.0
        x, y = x * math.cos(rz) - y * math.sin(rz), x * math.sin(rz) + y * math.cos(rz)
        x, z = x * math.cos(ry) + z * math.sin(ry), -x * math.sin(ry) + z * math.cos(ry)
        y, z = y * math.cos(rx) - z * math.sin(rx), y * math.sin(rx) + z * math.cos(rx)
        k = f / (f + z)
        pts.append((cx + x * k, cy + y * k))
    return pts

def paste_quad(canvas, im, quad, alpha=1.0):
    """canvas: PIL RGBA; im: PIL RGBA"""
    if alpha <= 0: return
    q = np.array(quad, np.float32)
    x0, y0 = np.floor(q.min(0)).astype(int); x1, y1 = np.ceil(q.max(0)).astype(int)
    X0, Y0 = max(0, x0), max(0, y0); X1, Y1 = min(canvas.width, x1), min(canvas.height, y1)
    if X1 <= X0 or Y1 <= Y0: return
    src = np.array([[0, 0], [im.width, 0], [im.width, im.height], [0, im.height]], np.float32)
    M = cv2.getPerspectiveTransform(src, q - np.array([X0, Y0], np.float32))
    warped = cv2.warpPerspective(np.asarray(im), M, (X1 - X0, Y1 - Y0), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0))
    wim = Image.fromarray(warped, 'RGBA')
    if alpha < 1: wim.putalpha(wim.getchannel('A').point(lambda v: int(v * alpha)))
    canvas.alpha_composite(wim, (X0, Y0))

def corner_mask(w, h, r):
    m = Image.new('L', (w, h), 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, w - 1, h - 1], r, fill=255); return m

# ---------- elementos de texto ----------
def txt_layer(s, font, col, pad=4):
    bb = ImageDraw.Draw(Image.new('RGBA', (1, 1))).textbbox((0, 0), s, font=font)
    lay = Image.new('RGBA', (bb[2] + pad * 2, bb[3] + pad * 2), (0, 0, 0, 0))
    ImageDraw.Draw(lay).text((pad, pad), s, font=font, fill=col + (255,)); return lay

def put(c, lay, x, y, p, dx=0, scale=None):
    if p <= 0: return
    if scale is not None and abs(scale - 1) > 0.01:
        lay = lay.resize((max(1, int(lay.width * scale)), max(1, int(lay.height * scale))), Image.BICUBIC)
        x -= (lay.width - lay.width / scale) / 2; y -= (lay.height - lay.height / scale) / 2
        if p < 1: lay = lay.copy(); lay.putalpha(lay.getchannel('A').point(lambda v: int(v * min(1, p * 1.4))))
        c.alpha_composite(lay, (int(x), int(y))); return
    if p < 1:
        e = ease(p); cl = Image.new('RGBA', lay.size, (0, 0, 0, 0))
        cl.alpha_composite(lay, (0, int((1 - e) * lay.height * 0.85)))
        cl.putalpha(cl.getchannel('A').point(lambda v: int(v * min(1, p * 1.6)))); lay = cl
    c.alpha_composite(lay, (int(x + (1 - p) * dx), int(y)))

def text(c, s, x, y, size, col, p, font='os', w=700, pop=False, dx=0):
    f = OS(size, w) if font == 'os' else F(size, w)
    lay = txt_layer(s, f, col)
    put(c, lay, x, y, p, dx=dx, scale=(1 + 0.18 * (1 - p)) if pop else None)

def tracked(d, xy, s, font, fill, sp):
    x, y = xy
    for ch in s:
        d.text((x, y), ch, font=font, fill=fill); x += d.textlength(ch, font=font) + sp

def kicker(c, s, x, y, col, p):
    lay = Image.new('RGBA', (900, 40), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.rounded_rectangle([0, 10, 8, 30], 3, fill=col + (255,)); tracked(d, (18, 8), s, F(21, 800), col + (255,), 4)
    put(c, lay, x, y, p)

def pill(c, s, x, y, bg, fg, p, size=28):
    f = F(size, 800); tw = ImageDraw.Draw(Image.new('RGBA', (1, 1))).textlength(s, font=f)
    lay = Image.new('RGBA', (int(tw) + 44, size + 28), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.rounded_rectangle([0, 0, lay.width - 1, lay.height - 1], (size + 28) // 2, fill=bg + (255,))
    d.text((22, 12), s, font=f, fill=fg + (255,)); put(c, lay, x, y, p)

def icon(kind, col, size=46):
    ic = Image.new('RGBA', (size, size), (0, 0, 0, 0)); d = ImageDraw.Draw(ic)
    d.ellipse([0, 0, size - 1, size - 1], fill=col + (255,))
    if kind == 'x':
        d.line([14, 14, 31, 31], fill=WHITE + (255,), width=5); d.line([31, 14, 14, 31], fill=WHITE + (255,), width=5)
    elif kind == 'v':
        d.line([(12, 24), (20, 32), (34, 15)], fill=WHITE + (255,), width=5, joint='curve')
    return ic

def strike(c, s, x, y, t, t0, size=44):
    p = ap(t, t0, .25)
    if p <= 0: return
    lay = txt_layer(s, OS(size, 600), INK)
    put(c, icon('x', RED), x, y + size * 0.28, p, scale=1 + 0.4 * (1 - p))
    put(c, lay, x + 62, y, p, dx=-16)
    q = ap(t, t0 + 0.28, .28)
    if q > 0:
        ln = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(ln).line([x + 60, y + lay.height * 0.55, x + 60 + lay.width * q, y + lay.height * 0.55], fill=RED + (255,), width=5)
        c.alpha_composite(ln)

def check(c, s, x, y, t, t0, col=GREEN, size=40):
    p = ap(t, t0, .25)
    if p <= 0: return
    put(c, icon('v', col), x, y + size * 0.25, p, scale=1 + 0.4 * (1 - p))
    text(c, s, x + 62, y, size, INK, p, w=600, dx=-16)

def bullet(c, s, x, y, t, t0, col, size=40):
    p = ap(t, t0, .25)
    if p <= 0: return
    put(c, icon('o', col, 30), x, y + size * 0.42, p, scale=1 + 0.5 * (1 - p))
    text(c, s, x + 46, y, size, INK, p, w=600, dx=-16)

def chip(c, s, cx, cy, bg, p, size=50):
    if p <= 0: return
    f = OS(size, 700); tw = ImageDraw.Draw(Image.new('RGBA', (1, 1))).textlength(s, font=f)
    lay = Image.new('RGBA', (int(tw) + 60, size + 44), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.rounded_rectangle([0, 0, lay.width - 1, lay.height - 1], 22, fill=bg + (255,))
    d.text((lay.width / 2, lay.height / 2), s, font=f, fill=WHITE + (255,), anchor='mm')
    put(c, lay, cx - lay.width / 2, cy - lay.height / 2, p, scale=1 + 0.25 * (1 - p))

def arrow(c, p0, p1, col, p, width=5, dashed=False):
    if p <= 0: return
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    x = p0[0] + (p1[0] - p0[0]) * p; y = p0[1] + (p1[1] - p0[1]) * p
    if dashed:
        n = 14
        for i in range(n):
            if i % 2: continue
            a = i / n; b = min(p, (i + 1) / n)
            if a > p: break
            d.line([(p0[0] + (p1[0] - p0[0]) * a, p0[1] + (p1[1] - p0[1]) * a), (p0[0] + (p1[0] - p0[0]) * b, p0[1] + (p1[1] - p0[1]) * b)], fill=col + (255,), width=width)
    else:
        d.line([p0, (x, y)], fill=col + (255,), width=width)
    if p > 0.85:
        ang = math.atan2(p1[1] - p0[1], p1[0] - p0[0])
        for s_ in (-0.5, 0.5):
            d.line([(x, y), (x - 22 * math.cos(ang + s_), y - 22 * math.sin(ang + s_))], fill=col + (255,), width=width)
    c.alpha_composite(lay)

def leader(c, pt, lab, title, sub, col, p, side='l'):
    if p <= 0: return
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    lx, ly = lab; q = min(1, p * 1.7)
    ex = lx + (14 if side == 'l' else -14)
    d.line([pt, (pt[0] + (ex - pt[0]) * q, pt[1] + (ly + 22 - pt[1]) * q)], fill=col + (230,), width=3)
    r = 8 * min(1, p * 3); d.ellipse([pt[0] - r, pt[1] - r, pt[0] + r, pt[1] + r], fill=WHITE + (255,), outline=col + (255,), width=3)
    c.alpha_composite(lay)
    if p > 0.45:
        pp = (p - 0.45) / 0.55; f1 = F(34, 800); f2 = F(22, 600)
        d0 = ImageDraw.Draw(Image.new('RGBA', (1, 1)))
        tw = max(d0.textlength(title, font=f1), d0.textlength(sub, font=f2) if sub else 0)
        tl = Image.new('RGBA', (int(tw) + 10, 90), (0, 0, 0, 0)); td = ImageDraw.Draw(tl)
        td.text((0, 0), title, font=f1, fill=col + (255,))
        if sub: td.text((0, 46), sub, font=f2, fill=GR + (255,))
        put(c, tl, lx + 20 if side == 'l' else lx - 20 - tl.width, ly, pp, dx=(-14 if side == 'l' else 14))

# ---------- imagens realistas em 3D ----------
IMG = {n: Image.open(os.path.join(BASE, 'img', f'{n}.png')).convert('RGB') for n in
       ['cctv', 'chess', 'coins', 'credit', 'docs', 'dossier', 'exploded', 'items', 'network', 'p2p', 'spend', 'tax', 'bank', 'gov', 'vault']}
_isz = {}
def img_sized(n, s):
    if (n, s) not in _isz:
        if len(_isz) > 60: _isz.clear()
        _isz[(n, s)] = IMG[n].resize((s, s), Image.LANCZOS)
    return _isz[(n, s)]
def bgcol(n):
    a = np.asarray(IMG[n]); c = np.concatenate([a[:30, :30].reshape(-1, 3), a[:30, -30:].reshape(-1, 3), a[-30:, :30].reshape(-1, 3), a[-30:, -30:].reshape(-1, 3)])
    return tuple(int(v) for v in np.median(c, 0))
DARK = {'bank', 'gov', 'vault'}

def img3d(c, n, cx, cy, size, t, t0, t1=None):
    p = ap(t, t0, .6)
    if p <= 0: return
    ph = (sum(map(ord, n)) % 100) / 16.0
    t1 = t1 or t0 + 6
    s = int(size * (1 + 0.04 * max(0, min(1, (t - t0) / max(0.1, t1 - t0)))))
    im = img_sized(n, s).convert('RGBA')
    m = Image.new('L', (s, s), 0)
    if n in DARK: ImageDraw.Draw(m).rounded_rectangle([0, 0, s - 1, s - 1], s * .07, fill=255)
    else: ImageDraw.Draw(m).rounded_rectangle([s * .04, s * .04, s * .96, s * .96], s * .1, fill=255); m = m.filter(ImageFilter.GaussianBlur(s * .03))
    im.putalpha(m)
    q = (t - t0 - 0.35) / 0.9
    if 0 <= q <= 1:
        st = Image.new('RGBA', (s, s), (0, 0, 0, 0)); sd = ImageDraw.Draw(st); x = -s * 0.4 + q * s * 1.8
        sd.polygon([(x, 0), (x + s * .12, 0), (x - s * .18, s), (x - s * .30, s)], fill=(255, 255, 255, 70))
        st = st.filter(ImageFilter.GaussianBlur(s * .02))
        st.putalpha(Image.fromarray(np.minimum(np.asarray(st.getchannel('A')), np.asarray(im.getchannel('A')))))
        im.alpha_composite(st)
    e = ease(p); sgn = 1 if (sum(map(ord, n)) % 2) else -1
    ry = 0.75 * (1 - e) * sgn + 0.07 * math.sin(t * 0.8 + ph)
    rx = 0.25 * (1 - e) + 0.05 * math.sin(t * 0.6 + ph * 1.3)
    rz = 0.02 * math.sin(t * 0.5 + ph); bob = 7 * math.sin(t * 1.25 + ph)
    sc = 0.86 + 0.14 * e; ly = cy + bob + (1 - e) * 40
    sh = Image.new('RGBA', (W, H), (0, 0, 0, 0)); w2 = s * 0.36 * sc
    ImageDraw.Draw(sh).ellipse([cx - w2, ly + s * 0.40 * sc - bob, cx + w2, ly + s * 0.40 * sc + 22 - bob], fill=(40, 30, 20, int(60 * e)))
    c.alpha_composite(sh.filter(ImageFilter.GaussianBlur(14)))
    paste_quad(c, im, project(s, s, cx, ly, ry, rx, sc, rz), min(1, p * 1.5))

def coin(c, kind, x, y, size, spin, alpha=1.0):
    col = {'btc': (196, 198, 204), 'usd': (46, 160, 110), 'brl': (60, 150, 190)}[kind]
    sym = {'btc': '₿', 'usd': '$', 'brl': 'R$'}[kind]
    w = max(4, int(size * abs(math.cos(spin))))
    im = Image.new('RGBA', (size, size), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.ellipse([0, 0, size - 1, size - 1], fill=tuple(int(v * 0.75) for v in col) + (255,))
    d.ellipse([size * .06, size * .06, size * .94, size * .94], fill=col + (255,))
    d.ellipse([size * .14, size * .14, size * .86, size * .86], outline=(255, 255, 255, 120), width=max(1, size // 30))
    d.text((size / 2, size / 2), sym, font=F(int(size * (0.34 if sym == 'R$' else 0.5)), 900), fill=WHITE + (255,), anchor='mm')
    hl = Image.new('RGBA', (size, size), (0, 0, 0, 0)); ImageDraw.Draw(hl).ellipse([size * .18, size * .1, size * .55, size * .4], fill=(255, 255, 255, 70))
    im.alpha_composite(hl.filter(ImageFilter.GaussianBlur(size * .05)))
    im = im.resize((w, size), Image.BICUBIC)
    if alpha < 1: im.putalpha(im.getchannel('A').point(lambda v: int(v * alpha)))
    c.alpha_composite(im, (int(x - w / 2), int(y - size / 2)))

def coins_fall(c, t, t0, x0, y0, kinds=('brl', 'usd', 'btc')):
    if t < t0: return
    for i, k in enumerate(kinds):
        q = ((t - t0 - i * 0.35) % 1.6) / 1.6
        coin(c, k, x0 + 80 * i, y0 + q * 160, 58, t * 3 + i, max(0, 1 - q) * min(1, (t - t0) * 3))
