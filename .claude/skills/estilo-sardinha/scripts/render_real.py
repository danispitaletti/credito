"""Teste do estilo explicativo: tela dividida + b-roll 2D + apresentador em tela cheia."""
import math, random, subprocess, sys, os
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

BASE = sys.argv[1]            # pasta do teste
FONT = os.path.join(BASE, 'fonts/package/files/montserrat-latin-900-normal.woff')
FONT8 = os.path.join(BASE, 'fonts/package/files/montserrat-latin-800-normal.woff')
W, H, FPS = 1080, 1920, 30
SRC_W, SRC_H = 480, 854
random.seed(7)

INK = (34, 25, 39)
WHITE = (255, 251, 248)
YEL = (229, 186, 48)
MARK = (232, 174, 60)
RED = (230, 67, 50)
KRAFT = (213, 189, 143)
GREEN = (60, 160, 90)

# ---------------- tempos (fonte) ----------------
# trechos de fala detectados (início/fim no vídeo bruto) + palavras
SEGS = [
    (0.748, 2.244, "O IMPOSTO NO BRASIL"),
    (2.399, 4.365, "EM 2027"),
    (4.584, 8.394, "VAI DEIXAR DE SER UM BOLETO PARA VOCÊ PAGAR NO FINAL DO MÊS"),
    (8.885, 10.066, "E VAI PASSAR A SER"),
    (10.234, 11.540, "DÉBITO AUTOMÁTICO"),
    (11.903, 13.945, "DIRETO DA SUA CONTA"),
]
PAD = 0.08
WEIGHT = {"2027": 7}

cuts = []        # (src_ini, src_fim, out_ini)
words = []       # dicts: w, t0, t1, seg
out = 0.0
for i, (a, b, txt) in enumerate(SEGS):
    s0, s1 = a - PAD, b + PAD
    cuts.append((s0, s1, out))
    ws = txt.split()
    wt = [WEIGHT.get(w, len(w) + 2) for w in ws]
    tot = sum(wt); acc = a
    for w, k in zip(ws, wt):
        d = (b - a) * k / tot
        words.append(dict(w=w, t0=acc - s0 + out, t1=acc + d - s0 + out, seg=i))
        acc += d
    out += s1 - s0
TOTAL = out
seg_out = [(c[2], c[2] + c[1] - c[0]) for c in cuts]

def seg_t(i): return seg_out[i]
def word_t(seg, idx): return [w for w in words if w['seg'] == seg][idx]['t0']

# formatos: A=dividida, B=broll cheio, C=apresentador cheio
def fmt_at(t):
    if t < seg_t(2)[0]: return 'A'
    if t < seg_t(3)[0]: return 'B'
    if t < seg_t(5)[0]: return 'C'
    return 'A'

TR = 0.33   # duração das transições

# ---------------- utilidades ----------------
def font(sz, w900=True): return ImageFont.truetype(FONT if w900 else FONT8, sz)

def ease_out(x): x = min(max(x, 0), 1); return 1 - (1 - x) ** 3
def ease_back(x):
    x = min(max(x, 0), 1); c1 = 1.70158; c3 = c1 + 1
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2
def pop(t, t0, d=0.28): return 0 if t < t0 else ease_back((t - t0) / d)

SS = 2  # supersampling dos sprites
def sprite(w, h, fn):
    im = Image.new('RGBA', (w * SS, h * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(im); fn(d, SS)
    im = im.resize((w, h), Image.LANCZOS)
    # sombra suave
    sh = Image.new('RGBA', (w + 30, h + 30), (0, 0, 0, 0))
    a = im.split()[3].point(lambda v: v * 0.35)
    blk = Image.new('RGBA', im.size, (40, 25, 15, 255)); blk.putalpha(a)
    sh.paste(blk, (12, 16), blk); sh = sh.filter(ImageFilter.GaussianBlur(6))
    sh.alpha_composite(im, (0, 0))
    return sh

def ctext(d, xy, s, txt, sz, fill, w900=True):
    f = font(int(sz * s), w900); x, y = xy
    bb = d.textbbox((0, 0), txt, font=f)
    d.text((x * s - (bb[2] - bb[0]) / 2 - bb[0], y * s - (bb[3] - bb[1]) / 2 - bb[1]), txt, font=f, fill=fill)

def rrect(d, s, box, r, fill, ol=INK, w=5):
    x0, y0, x1, y1 = box
    d.rounded_rectangle((x0 * s, y0 * s, x1 * s, y1 * s), r * s, fill=fill, outline=ol, width=int(w * s))

def paste_scaled(dst, spr, cx, cy, sc, rot=0):
    if sc <= 0.01: return
    w, h = spr.size
    im = spr.resize((max(1, int(w * sc)), max(1, int(h * sc))), Image.BILINEAR)
    if rot: im = im.rotate(rot, Image.BICUBIC, expand=True)
    dst.alpha_composite(im, (int(cx - im.width / 2), int(cy - im.height / 2)))

# ---------------- fundos ----------------
def paper_bg(w, h, base, stripes=True, floor=None):
    arr = np.zeros((h, w, 3), np.float32) + np.array(base, np.float32)
    if stripes:
        for x in range(0, w, 54):
            arr[:, x:x + 27] *= 0.975
    noise = np.random.default_rng(3).normal(0, 6, (h, w, 1))
    arr += noise
    if floor:
        fy = int(h * floor)
        arr[fy:] = np.array((168, 118, 78), np.float32) + noise[fy:] * 1.2
        for y in range(fy, h, 38): arr[y:y + 3] *= 0.85
        arr[fy:fy + 8] *= 0.7
    # vinheta
    yy, xx = np.mgrid[0:h, 0:w]
    v = 1 - 0.18 * (((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2)
    arr *= v[..., None]
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).convert('RGBA')

BG_A = paper_bg(W, 960, KRAFT, True, floor=0.80)
BG_B = paper_bg(W, H, KRAFT, True, floor=0.78)
BG_A2 = paper_bg(W, 960, (196, 214, 205), True, floor=0.80)   # verde-menta p/ cena do celular

# ---------------- sprites ----------------
def draw_bag(d, s):
    d.ellipse((40 * s, 120 * s, 360 * s, 420 * s), fill=(201, 164, 106), outline=INK, width=6 * s)
    d.polygon([(140 * s, 135 * s), (260 * s, 135 * s), (290 * s, 60 * s), (110 * s, 60 * s)], fill=(190, 150, 95), outline=INK)
    d.line((110 * s, 60 * s, 290 * s, 60 * s), fill=INK, width=6 * s)
    rrect(d, s, (120, 120, 280, 150), 10, (150, 70, 50))
    ctext(d, (200, 250), s, "R$", 110, (120, 85, 40))
    rrect(d, s, (70, 330, 330, 400), 12, WHITE)
    ctext(d, (200, 366), s, "IMPOSTO", 44, RED)
BAG = sprite(400, 440, draw_bag)

def draw_flag(d, s):
    d.rectangle((20 * s, 10 * s, 30 * s, 330 * s), fill=(120, 90, 60), outline=INK, width=3 * s)
    rrect(d, s, (30, 20, 330, 220), 6, (46, 157, 79))
    d.polygon([(180 * s, 40 * s), (310 * s, 120 * s), (180 * s, 200 * s), (50 * s, 120 * s)], fill=(242, 194, 48), outline=INK, width=4 * s)
    d.ellipse((135 * s, 75 * s, 225 * s, 165 * s), fill=(43, 79, 160), outline=INK, width=4 * s)
    d.arc((128 * s, 98 * s, 232 * s, 170 * s), 200, 340, fill=WHITE, width=7 * s)
    rrect(d, s, (60, 245, 300, 305), 10, WHITE)
    ctext(d, (180, 276), s, "BRASIL", 40, INK)
FLAG = sprite(350, 340, draw_flag)

def make_cal(top_txt, big, red_circle=False):
    def f(d, s):
        rrect(d, s, (20, 40, 380, 400), 18, WHITE)
        d.rounded_rectangle((20 * s, 40 * s, 380 * s, 140 * s), 18 * s, fill=RED, outline=INK, width=5 * s)
        d.rectangle((25 * s, 110 * s, 375 * s, 140 * s), fill=RED)
        d.line((20 * s, 140 * s, 380 * s, 140 * s), fill=INK, width=5 * s)
        for x in (110, 290):
            rrect(d, s, (x - 12, 15, x + 12, 70), 10, (200, 200, 200))
        ctext(d, (200, 92), s, top_txt, 46, WHITE)
        if big:
            ctext(d, (200, 270), s, big, 110, INK)
        else:
            for r in range(4):
                for c in range(7):
                    x0, y0 = 45 + c * 47, 160 + r * 55
                    d.rectangle((x0 * s, y0 * s, (x0 + 36) * s, (y0 + 40) * s), fill=(230, 225, 215))
            if red_circle:
                d.ellipse((310 * s, 310 * s, 380 * s, 380 * s), outline=RED, width=8 * s)
    return sprite(400, 420, f)
CAL_YEARS = {y: make_cal("ANO", str(y)) for y in (2025, 2026, 2027)}
CAL_FIM = make_cal("FIM DO MÊS", None, True)

def draw_person(d, s):
    sk, shirt, pants = (176, 118, 78), (233, 182, 59), (45, 58, 92)
    # pernas
    rrect(d, s, (95, 420, 135, 560), 10, pants); rrect(d, s, (145, 420, 185, 560), 10, pants)
    rrect(d, s, (80, 545, 140, 575), 10, INK); rrect(d, s, (140, 545, 200, 575), 10, INK)
    # braços
    rrect(d, s, (40, 250, 85, 420), 20, shirt); rrect(d, s, (195, 250, 240, 420), 20, shirt)
    d.ellipse((42 * s, 400 * s, 84 * s, 442 * s), fill=sk, outline=INK, width=5 * s)
    d.ellipse((196 * s, 400 * s, 238 * s, 442 * s), fill=sk, outline=INK, width=5 * s)
    # tronco
    rrect(d, s, (75, 230, 205, 440), 30, shirt)
    rrect(d, s, (88, 300, 192, 350), 6, (25, 22, 28), ol=(25, 22, 28))
    ctext(d, (140, 325), s, "VOCÊ", 30, WHITE)
    # cabeça
    d.ellipse((75 * s, 70 * s, 205 * s, 215 * s), fill=sk, outline=INK, width=5 * s)
    d.chord((70 * s, 60 * s, 210 * s, 170 * s), 180, 360, fill=(30, 22, 20), outline=INK, width=5 * s)
    d.ellipse((108 * s, 145 * s, 120 * s, 160 * s), fill=INK); d.ellipse((160 * s, 145 * s, 172 * s, 160 * s), fill=INK)
    d.arc((118 * s, 165 * s, 162 * s, 195 * s), 20, 160, fill=INK, width=4 * s)
PERSON = sprite(280, 600, draw_person)

def draw_boleto(d, s):
    rrect(d, s, (10, 10, 330, 430), 8, WHITE)
    rrect(d, s, (10, 10, 330, 80), 8, (225, 225, 220))
    ctext(d, (170, 46), s, "BOLETO", 42, INK)
    for i, y in enumerate((110, 145, 180)):
        d.rectangle((40 * s, y * s, (300 - i * 50) * s, (y + 14) * s), fill=(200, 196, 190))
    for x in range(40, 300, 9):
        d.rectangle((x * s, 330 * s, (x + random.choice((3, 5, 7))) * s, 400 * s), fill=INK)
    # carimbo
    d.rounded_rectangle((60 * s, 215 * s, 285 * s, 295 * s), 8 * s, outline=RED, width=7 * s)
    ctext(d, (172, 255), s, "IMPOSTO", 44, RED)
BOLETO = sprite(340, 440, draw_boleto)

def draw_x(d, s):
    for a, b in (((30, 30), (270, 270)), ((270, 30), (30, 270))):
        d.line((a[0] * s, a[1] * s, b[0] * s, b[1] * s), fill=INK, width=62 * s)
        d.line((a[0] * s, a[1] * s, b[0] * s, b[1] * s), fill=RED, width=46 * s)
XMARK = sprite(300, 300, draw_x)

def draw_phone(d, s):
    rrect(d, s, (10, 10, 330, 610), 40, (40, 40, 48))
    rrect(d, s, (30, 60, 310, 560), 16, WHITE, w=3)
    rrect(d, s, (130, 26, 210, 40), 7, (90, 90, 100), w=0)
    ctext(d, (170, 110), s, "SUA CONTA", 34, INK)
    d.line((60 * s, 140 * s, 280 * s, 140 * s), fill=(220, 215, 205), width=3 * s)
    ctext(d, (170, 175), s, "SALDO", 24, (130, 125, 120), False)
    rrect(d, s, (55, 420, 285, 520), 16, (120, 200, 140))
    ctext(d, (170, 452), s, "DÉBITO", 32, INK)
    ctext(d, (170, 490), s, "AUTOMÁTICO", 26, INK)
PHONE = sprite(340, 620, draw_phone)

def draw_receita(d, s):
    d.polygon([(20 * s, 130 * s), (200 * s, 30 * s), (380 * s, 130 * s)], fill=(236, 230, 214), outline=INK, width=5 * s)
    rrect(d, s, (30, 130, 370, 175), 4, (236, 230, 214))
    for x in (60, 140, 220, 300):
        rrect(d, s, (x, 175, x + 40, 360), 4, (245, 240, 228))
    rrect(d, s, (20, 360, 380, 400), 4, (210, 200, 180))
    rrect(d, s, (90, 120, 310, 165), 6, (43, 79, 160))
    ctext(d, (200, 143), s, "RECEITA", 34, WHITE)
RECEITA = sprite(400, 410, draw_receita)

def draw_coin(d, s):
    d.ellipse((5 * s, 5 * s, 95 * s, 95 * s), fill=(242, 194, 48), outline=INK, width=5 * s)
    ctext(d, (50, 52), s, "R$", 34, (150, 100, 20))
COIN = sprite(100, 100, draw_coin)

def draw_spark(d, s):
    c = 40
    d.polygon([(c * s, 0), (46 * s, 34 * s), (80 * s, c * s), (46 * s, 46 * s), (c * s, 80 * s), (34 * s, 46 * s), (0, c * s), (34 * s, 34 * s)], fill=(255, 240, 180), outline=INK, width=3 * s)
SPARK = sprite(80, 80, draw_spark)

# borda de papel rasgado (faixa)
def torn_strip(w):
    h = 46; im = Image.new('RGBA', (w * 2, h * 2), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    rng = random.Random(11)
    top = [(x * 2, (16 + rng.uniform(-9, 9)) * 2) for x in range(0, w + 12, 12)]
    bot = [(x * 2, (30 + rng.uniform(-9, 9)) * 2) for x in range(0, w + 12, 9)]
    d.polygon(top + bot[::-1], fill=(246, 242, 223))
    return im.resize((w, h), Image.LANCZOS)
TORN = torn_strip(W)

# ---------------- cenas (imagens realistas) ----------------
T_S2 = seg_t(1)[0]
T_B = seg_t(2)[0]
T_C = seg_t(3)[0]
T_A2 = seg_t(5)[0]

def load_scene(name):
    im = Image.open(os.path.join(BASE, 'real', name)).convert('RGB')
    im = im.resize((W, H), Image.LANCZOS).filter(ImageFilter.UnsharpMask(2, 80, 2))
    return im.convert('RGBA')
IMG_IMPOSTO = load_scene('imposto.jpg')
IMG_CAL = load_scene('calendario.jpg')
IMG_BOLETO = load_scene('boleto.jpg')
IMG_CEL = load_scene('celular.jpg')

def window(img, cy, zoom=1.0, cx=W / 2, h=960):
    """recorta uma janela W x h centrada em (cx, cy) com zoom"""
    ww, hh = W / zoom, h / zoom
    x0 = min(max(cx - ww / 2, 0), W - ww); y0 = min(max(cy - hh / 2, 0), H - hh)
    return img.crop((int(x0), int(y0), int(x0 + ww), int(y0 + hh))).resize((W, h), Image.BILINEAR)

FTAG = font(40)
def tag(txt, col=INK):
    w = int(FTAG.getlength(txt)) + 44; h = 70
    im = Image.new('RGBA', (w + 12, h + 12), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((6, 8, w + 6, h + 8), 10, fill=(30, 20, 20, 110))
    d.rounded_rectangle((0, 0, w, h), 10, fill=WHITE, outline=INK, width=4)
    d.text((w / 2, h / 2), txt, font=FTAG, fill=col, anchor='mm')
    return im
TAG_IMPOSTO = tag("IMPOSTO", RED); TAG_BRASIL = tag("BRASIL")
TAG_BOLETO = tag("BOLETO"); TAG_FIM = tag("FIM DO MÊS", RED)
TAG_CONTA = tag("SUA CONTA"); TAG_RECEITA = tag("RECEITA")

def scene_a1(t):
    """'O imposto no Brasil': começa no saco de dinheiro, sobe para a bandeira em BRASIL"""
    tb = word_t(0, 3)
    p = ease_out((t - (tb - 0.25)) / 0.6) if t > tb - 0.25 else 0
    cy = 1180 + (560 - 1180) * p
    im = window(IMG_IMPOSTO, cy, 1.0 + 0.04 * t)
    oy = cy - 480
    paste_scaled(im, TAG_IMPOSTO, 540, 1130 - oy, pop(t, word_t(0, 1) - 0.05))
    paste_scaled(im, TAG_BRASIL, 520, 560 - oy, pop(t, tb))
    return im

YEAR_F = font(150)
def scene_a2(t):
    """'Em 2027': calendário com o ano virando"""
    t0 = word_t(1, 1)
    yr = 2025 if t < t0 else (2026 if t < t0 + 0.25 else 2027)
    im = window(IMG_CAL, 980, 1.0 + 0.03 * (t - T_S2))
    d = ImageDraw.Draw(im)
    sc = 1.0 + (0.15 * (1 - ease_out((t - (t0 + 0.5)) / 0.3)) if t > t0 + 0.5 else 0)
    f = font(int(150 * sc)); col = RED if yr == 2027 else INK
    d.text((560, 470), str(yr), font=f, fill=col, anchor='mm')
    d.text((560, 330), "ANO", font=font(48), fill=(120, 110, 100), anchor='mm')
    if yr == 2027:
        for i, (x, y) in enumerate(((220, 330), (900, 360), (880, 640))):
            paste_scaled(im, SPARK, x, y, pop(t, t0 + 0.3 + i * 0.08) * 0.8)
    return im

def scene_b(t):
    """'vai deixar de ser um boleto para você pagar no final do mês' (tela cheia)"""
    im = window(IMG_BOLETO, H / 2, 1.0 + 0.06 * min(max((t - T_B) / 4, 0), 1), h=H)
    tb = word_t(2, 5)
    paste_scaled(im, TAG_BOLETO, 520, 1240, pop(t, tb - 0.1))
    tf = word_t(2, 10)
    if t > tf:
        d = ImageDraw.Draw(im); r = 120 * pop(t, tf)
        d.ellipse((930 - r, 760 - r, 930 + r, 760 + r), outline=RED, width=12)
    paste_scaled(im, TAG_FIM, 860, 960, pop(t, tf + 0.05))
    tx = seg_t(2)[1] - 0.55
    paste_scaled(im, XMARK, 575, 1040, pop(t, tx, 0.2) * 1.4)
    return im

def scene_a3(t):
    """'direto da sua conta': celular com o dinheiro voando para o governo"""
    im = window(IMG_CEL, 760, 1.0 + 0.05 * min(max((t - T_A2) / 2.5, 0), 1))
    paste_scaled(im, TAG_RECEITA, 800, 330, pop(t, T_A2 + 0.1))
    paste_scaled(im, TAG_CONTA, 330, 700, pop(t, T_A2 - 0.2))
    p = ease_out((t - (T_A2 + 0.2)) / 1.4) if t > T_A2 + 0.2 else 0
    val = int(round(1000 - 270 * p))
    lay = tag(f"R$ {val:,}".replace(',', '.'), RED if p > 0.05 else INK)
    paste_scaled(im, lay, 330, 800, pop(t, T_A2 - 0.1))
    return im

def push_in(im, t, t0, amt=0.05, dur=4.0):
    k = 1 + amt * min(max((t - t0) / dur, 0), 1)
    w, h = im.size
    big = im.resize((int(w * k), int(h * k)), Image.BILINEAR)
    return big.crop(((big.width - w) // 2, (big.height - h) // 2, (big.width - w) // 2 + w, (big.height - h) // 2 + h))

def whip(a, b, p):
    """transição chicote horizontal de a para b, p 0..1"""
    w, h = a.size; x = int(-w * ease_out(p))
    canvas = Image.new('RGBA', (w, h)); canvas.alpha_composite(a, (x, 0)); canvas.alpha_composite(b, (x + w, 0))
    return canvas.filter(ImageFilter.BoxBlur(int(14 * math.sin(math.pi * p)))) if 0 < p < 1 else canvas

def top_panel(t):
    if t < T_S2 - 0.12:
        return push_in(scene_a1(t), t, 0)
    if t < T_S2 + 0.13:
        p = (t - (T_S2 - 0.12)) / 0.25
        return whip(push_in(scene_a1(t), t, 0), scene_a2(t), p)
    if t < T_B:
        return push_in(scene_a2(t), t, T_S2, 0.04, 2)
    return push_in(scene_a3(t), t, T_A2, 0.05, 2.5)

# ---------------- apresentador ----------------
FACE = [(0.0, 346), (0.5, 348), (1.0, 363), (1.5, 405), (2.0, 443), (2.5, 447), (3.0, 474), (3.5, 472), (4.0, 453),
        (5.0, 450), (5.5, 460), (6.0, 422), (6.5, 427), (7.0, 436), (7.5, 434), (8.0, 422), (8.5, 413), (9.0, 390),
        (9.5, 398), (10.0, 399), (10.5, 427), (11.0, 396), (11.5, 368), (12.0, 383), (12.5, 387), (13.1, 383),
        (13.6, 400), (14.1, 403), (14.6, 398)]
def out2src(t):
    for s0, s1, o in cuts:
        if t < o + (s1 - s0) + 1e-6: return s0 + (t - o)
    return cuts[-1][1]
def face_cy(src_t):
    ts = np.array([f[0] for f in FACE]); ys = np.array([f[1] for f in FACE], float)
    # suavização: média de janela de 1,2 s
    m = (ts > src_t - 0.6) & (ts < src_t + 0.6)
    return float(ys[m].mean()) if m.any() else float(np.interp(src_t, ts, ys))

def presenter_split(frame, t):
    cy = face_cy(out2src(t)); ch = 427
    top = int(min(max(cy - 0.42 * ch, 0), SRC_H - ch))
    return frame.crop((0, top, SRC_W, top + ch)).resize((W, 960), Image.LANCZOS)

def presenter_full(frame, t, zoom):
    im = frame.resize((W, int(SRC_H * W / SRC_W)), Image.LANCZOS)
    if zoom > 1:
        cy = face_cy(out2src(t)) * W / SRC_W
        big = im.resize((int(im.width * zoom), int(im.height * zoom)), Image.LANCZOS)
        cx = big.width // 2; cyb = int(cy * zoom)
        top = int(min(max(cyb - 0.40 * H, 0), big.height - H))
        im = big.crop((cx - W // 2, top, cx + W // 2, top + H))
    else:
        im = im.crop((0, 0, W, H)) if im.height >= H else im.resize((W, H))
    return im

# ---------------- legendas ----------------
TITLES = [  # (seg, palavras inicial-final, cores)
    dict(seg=0, idx=range(0, 4), col={"IMPOSTO": YEL}),
    dict(seg=1, idx=range(0, 2), col={"2027": YEL}),
    dict(seg=2, idx=range(0, 6), col={"BOLETO": YEL}),
    dict(seg=2, idx=range(6, 13), col={"FINAL": YEL, "DO": YEL, "MÊS": YEL}),
    dict(seg=5, idx=range(0, 4), col={"SUA": RED, "CONTA": RED}),
]
for T in TITLES:
    ws = [w for w in words if w['seg'] == T['seg']]
    T['words'] = [ws[i] for i in T['idx']]
    T['t0'] = T['words'][0]['t0'] - 0.05
nxt = [T['t0'] for T in TITLES[1:]] + [TOTAL + 1]
for T, n in zip(TITLES, nxt):
    T['t1'] = min(n, seg_t(T['seg'])[1] + 0.15)
TITLES[3]['t1'] = T_C  # some na transição

FT = font(78)
def draw_title(canvas, t, ytop):
    for T in TITLES:
        if not (T['t0'] <= t < T['t1']): continue
        vis = [w for w in T['words'] if w['t0'] <= t + 0.02]
        if not vis: return
        # quebra de linha
        lines, cur = [], []
        for w in vis:
            test = ' '.join(x['w'] for x in cur + [w])
            if FT.getlength(test) > 900 and cur: lines.append(cur); cur = [w]
            else: cur.append(w)
        lines.append(cur)
        y = ytop
        for ln in lines:
            txt = ' '.join(x['w'] for x in ln); lw = FT.getlength(txt); x = (W - lw) / 2
            for w in ln:
                ww = w['w']; col = T['col'].get(ww, (246, 241, 233))
                age = t - w['t0']; sc = 0.75 + 0.25 * ease_back(age / 0.15)
                layer = Image.new('RGBA', (int(FT.getlength(ww)) + 40, 120), (0, 0, 0, 0))
                d = ImageDraw.Draw(layer)
                d.text((20, 18 + 8), ww, font=FT, fill=(30, 20, 20, 150), stroke_width=6, stroke_fill=(30, 20, 20, 150))
                d.text((20, 18), ww, font=FT, fill=col, stroke_width=6, stroke_fill=(38, 26, 30))
                if sc < 0.999:
                    layer = layer.resize((int(layer.width * sc), int(layer.height * sc)), Image.BILINEAR)
                cx = x + FT.getlength(ww) / 2
                canvas.alpha_composite(layer, (int(cx - layer.width / 2), int(y + 60 - layer.height / 2)))
                x += FT.getlength(ww + ' ')
            y += 92
        return

# caixinha: grupos de 1-3 palavras
CHUNK_SEGS = [0, 1, 3, 4, 5]
chunks = []
for sg in CHUNK_SEGS:
    ws = [w for w in words if w['seg'] == sg]; cur = []
    for w in ws:
        if cur and (len(' '.join(x['w'] for x in cur + [w])) > 13 or len(cur) == 3):
            chunks.append(cur); cur = []
        cur.append(w)
    chunks.append(cur)
RED_WORDS = {"AUTOMÁTICO", "CONTA"}
FC = font(46)
def draw_caption(canvas, t, cy):
    ch = None
    for c in chunks:
        if c[0]['t0'] - 0.03 <= t < c[-1]['t1'] + 0.1: ch = c
    if not ch: return
    txt = ' '.join(w['w'] for w in ch)
    tw = FC.getlength(txt); pad_x, bh = 22, 70
    bw = tw + pad_x * 2
    sc = 0.9 + 0.1 * ease_out((t - ch[0]['t0'] + 0.03) / 0.1)
    layer = Image.new('RGBA', (int(bw) + 20, bh + 20), (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
    d.rounded_rectangle((14, 14, bw + 6, bh + 6), 10, fill=(30, 20, 20, 90))
    d.rounded_rectangle((8, 8, bw, bh), 10, fill=WHITE, outline=INK, width=4)
    x = 8 + pad_x
    for w in ch:
        ww = w['w']; lw = FC.getlength(ww)
        active = w['t0'] <= t < w['t1'] + 0.12 or (w is ch[-1] and t >= w['t0'])
        said = w['t0'] <= t
        if active and ww not in RED_WORDS:
            d.rectangle((x - 4, 8 + bh * 0.48, x + lw + 4, bh - 6), fill=MARK)
        col = (RED if ww in RED_WORDS else INK) if said else (175, 170, 168)
        d.text((x, 8 + (bh - 8) / 2), ww, font=FC, fill=col, anchor='lm')
        x += FC.getlength(ww + ' ')
    if sc < 0.999: layer = layer.resize((int(layer.width * sc), int(layer.height * sc)), Image.BILINEAR)
    canvas.alpha_composite(layer, (int(W / 2 - layer.width / 2), int(cy - layer.height / 2)))

# marca d'água
FW = font(26, False)
def watermark(canvas, y):
    d = ImageDraw.Draw(canvas)
    d.ellipse((60, y, 104, y + 44), fill=(255, 255, 255, 60), outline=(255, 255, 255, 210), width=3)
    ctx = Image.new('RGBA', (400, 50), (0, 0, 0, 0)); dd = ImageDraw.Draw(ctx)
    dd.text((0, 25), "@dani.defibit", font=FW, fill=(255, 255, 255, 215), anchor='lm')
    canvas.alpha_composite(ctx, (118, y - 3))

# ---------------- composição ----------------
def compose(frame, t):
    f = fmt_at(t)
    canvas = Image.new('RGBA', (W, H), (0, 0, 0, 255))
    if f == 'A' and t < T_B:
        pres = presenter_split(frame, t); canvas.paste(pres, (0, 960))
        top = top_panel(t); canvas.alpha_composite(top, (0, 0))
        canvas.alpha_composite(TORN, (0, 960 - 23)); watermark(canvas, 1000)
        draw_title(canvas, t, 110); draw_caption(canvas, t, 960)
        # transição A->B: animação desce cobrindo o apresentador
        if t > T_B - TR:
            p = ease_out((t - (T_B - TR)) / TR)
            b = scene_b(t); hcut = int(960 + 960 * p)
            canvas.alpha_composite(b.crop((0, 0, W, hcut)), (0, 0))
            canvas.alpha_composite(TORN, (0, hcut - 23))
            draw_title(canvas, t, 110)
    elif f == 'B':
        b = push_in(scene_b(t), t, T_B, 0.05, 4)
        if t > T_C - TR:   # B->C: animação desliza para baixo e sai
            p = ease_out((t - (T_C - TR)) / TR)
            canvas.paste(presenter_full(frame, t, 1.0), (0, 0))
            off = int(H * p); canvas.alpha_composite(b.crop((0, 0, W, H - off)), (0, off))
            canvas.alpha_composite(TORN, (0, max(off - 23, 0)))
        else:
            canvas.alpha_composite(b)
        draw_title(canvas, t, 110)
    elif f == 'C':
        zoom = 1.0 if t < seg_t(4)[0] else 1.32      # corte de enquadramento em "DÉBITO"
        canvas.paste(presenter_full(frame, t, zoom), (0, 0))
        draw_caption(canvas, t, int(H * 0.86))
    else:  # A final: animação entra por cima
        canvas.paste(presenter_full(frame, t, 1.32), (0, 0))
        pres = presenter_split(frame, t); canvas.paste(pres, (0, 960))
        p = ease_out((t - T_A2 + 0.12) / TR)
        top = top_panel(t); y = int(-960 * (1 - p))
        canvas.alpha_composite(top.crop((0, -y, W, 960)) if y < 0 else top, (0, 0))
        canvas.alpha_composite(TORN, (0, 960 + y - 23)); watermark(canvas, 1000)
        draw_title(canvas, t, 110); draw_caption(canvas, t, 960)
    return canvas.convert('RGB')

if __name__ == '__main__':
    cutv = os.path.join(BASE, 'cut.mp4')
    n = int(TOTAL * FPS)
    only = [float(x) for x in sys.argv[2:]]   # modo prévia: tempos específicos
    rd = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', cutv, '-vf', f'fps={FPS},scale={SRC_W}:{SRC_H}', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
    wr = None if only else subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                                             '-i', os.path.join(BASE, 'audio_cut.wav'), '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p',
                                             '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', os.path.join(BASE, 'teste_realista.mp4')], stdin=subprocess.PIPE)
    fsz = SRC_W * SRC_H * 3
    for i in range(n):
        buf = rd.stdout.read(fsz)
        if len(buf) < fsz: break
        t = i / FPS
        if only:
            if any(abs(t - x) < 0.5 / FPS for x in only):
                compose(Image.frombytes('RGB', (SRC_W, SRC_H), buf), t).save(os.path.join(BASE, f'prev_{t:05.2f}.jpg'), quality=85)
            continue
        wr.stdin.write(compose(Image.frombytes('RGB', (SRC_W, SRC_H), buf), t).tobytes())
    if wr: wr.stdin.close(); wr.wait()
    print('ok', TOTAL)
