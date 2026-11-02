"""Vídeo 'Bloqueio judicial / DeFi' — estilo explicativo versão 1 (desenhos 2D por código)."""
import math, random, subprocess, sys, os, json
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

BASE = sys.argv[1]
FONT = os.path.join(BASE, 'fonts/package/files/montserrat-latin-900-normal.woff')
FONT8 = os.path.join(BASE, 'fonts/package/files/montserrat-latin-800-normal.woff')
W, H, FPS = 1080, 1920, 30
SRC_W, SRC_H = 480, 854
random.seed(7)

INK = (34, 25, 39); WHITE = (255, 251, 248); YEL = (229, 186, 48); MARK = (232, 174, 60)
RED = (230, 67, 50); KRAFT = (213, 189, 143); GREEN = (70, 170, 100); TEAL = (40, 170, 170)
SKIN = (176, 118, 78); NAVY = (45, 58, 92); GRAY = (150, 150, 155)

# ---------------- fala ----------------
SEGS = [
    (1.18, 2.42, "E COMO ISSO VAI FUNCIONAR?"), (2.94, 3.19, "BEM:"), (3.90, 5.75, "O SEU CLIENTE VAI TE FAZER UM PIX"),
    (5.99, 10.40, "POR EXEMPLO, UM PIX DE R$ 100 PARA PAGAR POR ALGUM PRODUTO OU POR ALGUM SERVIÇO"),
    (11.18, 15.75, "EM VEZ DE VOCÊ RECEBER OS 100 REAIS NA CONTA, VOCÊ VAI RECEBER 100 REAIS"),
    (16.14, 18.89, "JÁ DESCONTADO UM IMPOSTO"), (19.07, 24.29, "100 REAIS MENOS 27,5% DE IMPOSTO VOCÊ VAI RECEBER"),
    (24.42, 26.13, "R$ 72,50"), (26.33, 27.18, "OU SEJA,"), (27.44, 29.38, "O ESTADO RECEBE O IMPOSTO"),
    (29.62, 31.47, "ANTES DE VOCÊ RECEBER"), (32.00, 32.89, "DO SEU CLIENTE"),
    (34.06, 37.54, "E SE VOCÊ É UM EMPRESÁRIO QUE TRABALHA COM FLUXO DE CAIXA QUE NÃO"), (37.71, 38.10, "PODE"),
    (38.26, 40.00, "TER O IMPOSTO DESCONTADO"), (40.34, 41.62, "ANTES DO FINAL DO MÊS,"),
    (42.16, 43.85, "ISSO PODE ATRAPALHAR MUITO"), (44.15, 45.09, "SEUS NEGÓCIOS"),
    (46.36, 46.93, "MAS"), (47.19, 48.19, "ISSO TEM SOLUÇÃO"), (48.43, 50.95, "HOJE, COM A TECNOLOGIA, VOCÊ PODE APRENDER"),
    (51.16, 54.56, "A RECEBER O DINHEIRO DIRETO NA SUA CARTEIRA DIGITAL"), (54.87, 56.60, "SEM PRECISAR DE CONTA BANCÁRIA"),
    (56.92, 57.49, "E É ISSO"), (57.93, 59.06, "QUE EU ENSINO NA MENTORIA"),
    (59.57, 61.71, "ENTÃO, SE VOCÊ TEM UM NEGÓCIO E"), (61.92, 62.67, "QUER APRENDER"),
    (62.97, 65.30, "COMO MOVIMENTAR, RECEBER E PAGAR"), (65.52, 66.33, "O SEU DINHEIRO"),
    (66.52, 68.08, "SEM DEPENDER DE BANCOS,"), (68.53, 69.73, "CLIQUE AQUI EM SAIBA MAIS"),
    (69.88, 71.15, "E SE APLIQUE PARA A MENTORIA"),
]

PAD = 0.16
cuts, words = [], []
out = 0.0
for i, (a, b, txt) in enumerate(SEGS):
    s0 = max(a - PAD, 0); s1 = b + PAD
    if cuts and s0 < cuts[-1][1]: s0 = cuts[-1][1]
    cuts.append((s0, s1, out))
    ws = txt.split(); wt = [len(w.strip(',?')) + 2 for w in ws]; tot = sum(wt); acc = a
    for k, (w, q) in enumerate(zip(ws, wt)):
        d = (b - a) * q / tot
        words.append(dict(w=w, t0=acc - s0 + out, t1=acc + d - s0 + out, seg=i, k=k))
        acc += d
    out += s1 - s0
TOTAL = out
def T(i): return cuts[i][2]
def TE(i): return cuts[i][2] + cuts[i][1] - cuts[i][0]
def WT(i, k): return [w for w in words if w['seg'] == i][k]['t0']

# blocos: (formato, primeiro seg, último seg, cenas)
BLOCKS = [
    ('A', 0, 3), ('B', 4, 7), ('C', 8, 9), ('A', 10, 17), ('B', 18, 22), ('C', 23, 24), ('A', 25, 31),
]
BL = [dict(f=f, s=a, e=b, t0=T(a), t1=TE(b)) for f, a, b in BLOCKS]
def block_at(t):
    for i, b in enumerate(BL):
        if t < b['t1'] or i == len(BL) - 1: return i, b

TR = 0.33

# ---------------- utilidades ----------------
_fc = {}
def font(sz, w900=True):
    k = (sz, w900)
    if k not in _fc: _fc[k] = ImageFont.truetype(FONT if w900 else FONT8, sz)
    return _fc[k]
def ease_out(x): x = min(max(x, 0), 1); return 1 - (1 - x) ** 3
def ease_back(x):
    x = min(max(x, 0), 1); c1 = 1.70158; c3 = c1 + 1
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2
def pop(t, t0, d=0.28): return 0 if t < t0 else ease_back((t - t0) / d)
def clamp01(x): return min(max(x, 0), 1)

SS = 2
def sprite(w, h, fn, shadow=True):
    im = Image.new('RGBA', (w * SS, h * SS), (0, 0, 0, 0)); fn(ImageDraw.Draw(im), SS)
    im = im.resize((w, h), Image.LANCZOS)
    if not shadow: return im
    sh = Image.new('RGBA', (w + 30, h + 30), (0, 0, 0, 0))
    a = im.split()[3].point(lambda v: v * 0.35)
    blk = Image.new('RGBA', im.size, (40, 25, 15, 255)); blk.putalpha(a)
    sh.paste(blk, (12, 16), blk); sh = sh.filter(ImageFilter.GaussianBlur(6)); sh.alpha_composite(im, (0, 0))
    return sh
def ctext(d, xy, s, txt, sz, fill, w900=True):
    d.text((xy[0] * s, xy[1] * s), txt, font=font(int(sz * s), w900), fill=fill, anchor='mm')
def rrect(d, s, box, r, fill, ol=INK, w=5):
    x0, y0, x1, y1 = box
    d.rounded_rectangle((x0 * s, y0 * s, x1 * s, y1 * s), r * s, fill=fill, outline=ol, width=int(w * s))
def ell(d, s, box, fill, ol=INK, w=5):
    d.ellipse(tuple(v * s for v in box), fill=fill, outline=ol, width=int(w * s))
def paste_scaled(dst, spr, cx, cy, sc, rot=0):
    if sc <= 0.01: return
    w, h = spr.size
    im = spr.resize((max(1, int(w * sc)), max(1, int(h * sc))), Image.BILINEAR)
    if rot: im = im.rotate(rot, Image.BICUBIC, expand=True)
    dst.alpha_composite(im, (int(cx - im.width / 2), int(cy - im.height / 2)))

def paper_bg(w, h, base, floor=0.8, floor_col=(168, 118, 78)):
    rng = np.random.default_rng(3)
    arr = np.zeros((h, w, 3), np.float32) + np.array(base, np.float32)
    for x in range(0, w, 54): arr[:, x:x + 27] *= 0.975
    noise = rng.normal(0, 6, (h, w, 1)); arr += noise
    if floor:
        fy = int(h * floor); arr[fy:] = np.array(floor_col, np.float32) + noise[fy:] * 1.2
        for y in range(fy, h, 38): arr[y:y + 3] *= 0.85
        arr[fy:fy + 8] *= 0.7
    yy, xx = np.mgrid[0:h, 0:w]
    arr *= (1 - 0.18 * (((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2))[..., None]
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).convert('RGBA')

BG_A = paper_bg(W, 960, KRAFT, 0.80)
BG_A_MINT = paper_bg(W, 960, (196, 214, 205), 0.80)
BG_A_DARK = paper_bg(W, 960, (60, 70, 92), 0.80, (40, 46, 60))
BG_B = paper_bg(W, H, KRAFT, 0.78)
BG_B_SKY = paper_bg(W, H, (190, 205, 215), 0.70, (200, 190, 170))
BG_B_DARK = paper_bg(W, H, (55, 64, 86), 0.78, (38, 44, 58))

# ---------------- sprites ----------------
def person(shirt=(233, 182, 59), label="VOCÊ", suit=False, arm_up=False):
    def f(d, s):
        pants = (40, 40, 50) if suit else NAVY
        rrect(d, s, (95, 420, 135, 560), 10, pants); rrect(d, s, (145, 420, 185, 560), 10, pants)
        rrect(d, s, (80, 545, 140, 575), 10, INK); rrect(d, s, (140, 545, 200, 575), 10, INK)
        rrect(d, s, (40, 250, 85, 420), 20, shirt)
        if arm_up:
            rrect(d, s, (195, 120, 240, 290), 20, shirt); ell(d, s, (196, 95, 238, 137), SKIN)
        else:
            rrect(d, s, (195, 250, 240, 420), 20, shirt); ell(d, s, (196, 400, 238, 442), SKIN)
        ell(d, s, (42, 400, 84, 442), SKIN)
        rrect(d, s, (75, 230, 205, 440), 30, shirt)
        if suit:
            d.polygon([(125 * s, 232 * s), (155 * s, 232 * s), (140 * s, 300 * s)], fill=WHITE)
            d.polygon([(134 * s, 240 * s), (146 * s, 240 * s), (150 * s, 290 * s), (140 * s, 305 * s), (130 * s, 290 * s)], fill=RED)
        w = 30 if len(label) < 6 else 22
        rrect(d, s, (82, 315, 198, 362), 6, (25, 22, 28), ol=(25, 22, 28))
        ctext(d, (140, 339), s, label, w, WHITE)
        ell(d, s, (75, 70, 205, 215), SKIN)
        d.chord((70 * s, 60 * s, 210 * s, 170 * s), 180, 360, fill=(30, 22, 20), outline=INK, width=5 * s)
        ell(d, s, (108, 145, 120, 160), INK, w=0); ell(d, s, (160, 145, 172, 160), INK, w=0)
        d.arc((118 * s, 168 * s, 162 * s, 195 * s), 20, 160, fill=INK, width=4 * s)
    return sprite(280, 600, f)
VOCE = person(); VOCE_UP = person(arm_up=True)
ADVOGADO = person(shirt=(50, 60, 90), label="ADVOGADO", suit=True)

def phone(title, line, col_screen=WHITE, col_txt=INK, lock=False):
    def f(d, s):
        rrect(d, s, (10, 10, 330, 610), 40, (40, 40, 48))
        rrect(d, s, (30, 60, 310, 560), 16, col_screen, w=3)
        rrect(d, s, (130, 26, 210, 40), 7, (90, 90, 100), w=0)
        ctext(d, (170, 115), s, title, 34, col_txt)
        d.line((60 * s, 145 * s, 280 * s, 145 * s), fill=col_txt, width=3 * s)
        if lock:
            d.arc((115 * s, 200 * s, 225 * s, 320 * s), 180, 360, fill=WHITE, width=18 * s)
            rrect(d, s, (95, 260, 245, 380), 14, (250, 210, 80))
            ell(d, s, (157, 295, 183, 321), INK, w=0); d.rectangle((165 * s, 315 * s, 175 * s, 345 * s), fill=INK)
            ctext(d, (170, 440), s, "BLOQUEIO", 38, WHITE); ctext(d, (170, 485), s, "JUDICIAL", 38, WHITE)
        else:
            ctext(d, (170, 200), s, "SALDO", 24, (130, 125, 120), False)
            ctext(d, (170, 260), s, line, 50, col_txt)
            for i, y in enumerate((340, 395, 450)):
                rrect(d, s, (60, y, 280, y + 36), 8, (235, 230, 222), w=0)
    return sprite(340, 620, f)
PHONE_OK = phone("SUA CONTA", "R$ 5.000")
PHONE_BLANK = phone("SUA CONTA", "")
PHONE_LOCK = phone("SUA CONTA", "", col_screen=RED, col_txt=WHITE, lock=True)

def padlock(sz=1.0):
    def f(d, s):
        d.arc((60 * s, 10 * s, 200 * s, 160 * s), 180, 360, fill=INK, width=40 * s)
        d.arc((60 * s, 10 * s, 200 * s, 160 * s), 180, 360, fill=(170, 170, 178), width=26 * s)
        rrect(d, s, (30, 85, 230, 250), 22, (242, 194, 48))
        ell(d, s, (113, 135, 147, 169), INK, w=0); d.rectangle((122 * s, 160 * s, 138 * s, 205 * s), fill=INK)
    return sprite(260, 270, f)
PADLOCK = padlock()

def calendar_day(top, big):
    def f(d, s):
        rrect(d, s, (20, 40, 380, 400), 18, WHITE)
        d.rounded_rectangle((20 * s, 40 * s, 380 * s, 140 * s), 18 * s, fill=RED, outline=INK, width=5 * s)
        d.rectangle((25 * s, 110 * s, 375 * s, 140 * s), fill=RED); d.line((20 * s, 140 * s, 380 * s, 140 * s), fill=INK, width=5 * s)
        for x in (110, 290): rrect(d, s, (x - 12, 15, x + 12, 70), 10, (200, 200, 200))
        ctext(d, (200, 92), s, top, 44, WHITE); ctext(d, (200, 270), s, big, 120, INK)
    return sprite(400, 420, f)
CAL_SEG = calendar_day("NOVEMBRO", "SEG")

def clock_face():
    def f(d, s):
        ell(d, s, (10, 10, 330, 330), WHITE, w=10)
        for i in range(12):
            a = i / 12 * 2 * math.pi; r0, r1 = (120, 145) if i % 3 else (105, 145)
            d.line(((170 + r0 * math.sin(a)) * s, (170 - r0 * math.cos(a)) * s, (170 + r1 * math.sin(a)) * s, (170 - r1 * math.cos(a)) * s), fill=INK, width=8 * s)
    return sprite(340, 340, f, shadow=True)
CLOCK = clock_face()

def bank(label="BANCO", col=(236, 230, 214)):
    def f(d, s):
        d.polygon([(20 * s, 130 * s), (200 * s, 30 * s), (380 * s, 130 * s)], fill=col, outline=INK, width=5 * s)
        rrect(d, s, (30, 130, 370, 175), 4, col)
        for x in (60, 140, 220, 300): rrect(d, s, (x, 175, x + 40, 360), 4, (245, 240, 228))
        rrect(d, s, (20, 360, 380, 400), 4, (210, 200, 180))
        rrect(d, s, (90, 120, 310, 165), 6, (43, 79, 160)); ctext(d, (200, 143), s, label, 32, WHITE)
    return sprite(400, 410, f)
BANCO = bank()

def money_stack():
    def f(d, s):
        for i in range(5):
            y = 200 - i * 34
            rrect(d, s, (20, y, 330, y + 70), 8, (120, 190, 130))
            ell(d, s, (145, y + 12, 205, y + 58), (90, 160, 100), w=3)
        ctext(d, (175, 101), s, "R$", 34, (40, 90, 50))
    return sprite(350, 290, f)
MONEY = money_stack()

def coin(txt, col, tcol):
    def f(d, s):
        ell(d, s, (5, 5, 195, 195), col, w=7); ell(d, s, (25, 25, 175, 175), None, ol=tuple(int(c * 0.8) for c in col), w=5)
        ctext(d, (100, 102), s, txt, 52 if len(txt) < 3 else 44, tcol)
    return sprite(200, 200, f)
COIN_R = coin("R$", (120, 200, 130), (30, 80, 40))
COIN_U = coin("US$", (150, 210, 160), (20, 70, 40))
COIN_B = coin("BTC", (247, 147, 26), WHITE)

def doc(title, lines=4, seal=True):
    def f(d, s):
        rrect(d, s, (10, 10, 360, 470), 8, WHITE)
        ctext(d, (185, 60), s, title.split('\n')[0], 34, INK)
        if '\n' in title: ctext(d, (185, 100), s, title.split('\n')[1], 34, INK)
        for i in range(lines): d.rectangle((40 * s, (150 + i * 45) * s, (330 - (i % 2) * 60) * s, (164 + i * 45) * s), fill=(200, 196, 190))
        if seal: ell(d, s, (40, 360, 120, 440), (200, 60, 50), w=4)
        d.line((170 * s, 420 * s, 330 * s, 420 * s), fill=INK, width=3 * s)
    return sprite(370, 480, f)
ORDEM = doc("ORDEM\nJUDICIAL")

def pen():
    def f(d, s):
        d.polygon([(20 * s, 380 * s), (40 * s, 330 * s), (60 * s, 350 * s)], fill=INK)
        d.polygon([(40 * s, 330 * s), (60 * s, 350 * s), (260 * s, 30 * s), (240 * s, 10 * s)], fill=(30, 30, 40), outline=INK)
        d.polygon([(205 * s, 70 * s), (225 * s, 90 * s), (260 * s, 30 * s), (240 * s, 10 * s)], fill=(200, 170, 60))
    return sprite(280, 400, f)
PEN = pen()

def stamp(txt, col=RED):
    fw = font(64)
    w = int(fw.getlength(txt)) + 60
    def f(d, s):
        d.rounded_rectangle((10 * s, 10 * s, (w - 10) * s, 120 * s), 12 * s, outline=col, width=10 * s)
        ctext(d, (w / 2, 66), s, txt, 64, col)
    return sprite(w, 130, f, shadow=False)
STAMP_BLOQ = stamp("BLOQUEADO")

def idcard(txt, sub):
    def f(d, s):
        rrect(d, s, (10, 10, 390, 250), 18, (225, 235, 245))
        rrect(d, s, (10, 10, 390, 70), 18, (43, 79, 160)); d.rectangle((15 * s, 50 * s, 385 * s, 70 * s), fill=(43, 79, 160))
        ctext(d, (200, 42), s, sub, 26, WHITE)
        ell(d, s, (40, 95, 140, 210), (200, 205, 215), w=4); ell(d, s, (70, 110, 110, 150), SKIN, w=3)
        ctext(d, (270, 140), s, txt, 64, INK)
        d.rectangle((170 * s, 190 * s, 360 * s, 202 * s), fill=(170, 175, 185))
    return sprite(400, 260, f)
CARD_CPF = idcard("CPF", "PESSOA FÍSICA"); CARD_CNPJ = idcard("CNPJ", "EMPRESA")

def wallet():
    def f(d, s):
        rrect(d, s, (20, 60, 400, 330), 30, (120, 80, 50))
        rrect(d, s, (20, 40, 380, 110), 24, (150, 100, 65))
        rrect(d, s, (290, 150, 420, 240), 20, (100, 65, 40)); ell(d, s, (330, 180, 360, 210), (242, 194, 48), w=3)
        ctext(d, (160, 210), s, "₿", 1, INK)
    return sprite(440, 350, f)
WALLET = wallet()

def shield():
    def f(d, s):
        pts = [(200, 20), (370, 80), (350, 280), (200, 420), (50, 280), (30, 80)]
        d.polygon([(x * s, y * s) for x, y in pts], fill=(60, 120, 200), outline=INK, width=8 * s)
        pts2 = [(200, 60), (330, 105), (315, 265), (200, 375), (85, 265), (70, 105)]
        d.polygon([(x * s, y * s) for x, y in pts2], fill=(90, 160, 230))
        d.line((130 * s, 220 * s, 185 * s, 280 * s, 285 * s, 160 * s), fill=WHITE, width=30 * s, joint='curve')
    return sprite(400, 440, f)
SHIELD = shield()

def button(txt):
    fw = font(64); w = int(fw.getlength(txt)) + 120
    def f(d, s):
        rrect(d, s, (10, 18, w - 10, 158), 70, (170, 50, 40), w=0)
        rrect(d, s, (10, 10, w - 10, 140), 70, RED, w=6)
        ctext(d, (w / 2, 76), s, txt, 64, WHITE)
    return sprite(w, 170, f)
BTN = button("SAIBA MAIS")

def hand():
    def f(d, s):
        rrect(d, s, (60, 10, 110, 170), 25, WHITE, w=6)
        rrect(d, s, (40, 120, 200, 290), 40, WHITE, w=6)
        for x in (110, 145): rrect(d, s, (x, 100, x + 45, 190), 22, WHITE, w=6)
    return sprite(220, 300, f)
HAND = hand()

def draw_x(d, s):
    for a, b in (((30, 30), (270, 270)), ((270, 30), (30, 270))):
        d.line((a[0] * s, a[1] * s, b[0] * s, b[1] * s), fill=INK, width=62 * s)
        d.line((a[0] * s, a[1] * s, b[0] * s, b[1] * s), fill=RED, width=46 * s)
XMARK = sprite(300, 300, draw_x)
def draw_spark(d, s):
    c = 40
    d.polygon([(c * s, 0), (46 * s, 34 * s), (80 * s, c * s), (46 * s, 46 * s), (c * s, 80 * s), (34 * s, 46 * s), (0, c * s), (34 * s, 34 * s)], fill=(255, 240, 180), outline=INK, width=3 * s)
SPARK = sprite(80, 80, draw_spark)

FTAG = font(40)
def tag(txt, col=INK, sz=40):
    f = font(sz); w = int(f.getlength(txt)) + 44; h = int(sz * 1.75)
    im = Image.new('RGBA', (w + 12, h + 12), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((6, 8, w + 6, h + 8), 10, fill=(30, 20, 20, 110))
    d.rounded_rectangle((0, 0, w, h), 10, fill=WHITE, outline=INK, width=4)
    d.text((w / 2, h / 2), txt, font=f, fill=col, anchor='mm')
    return im

def torn_strip(w):
    h = 46; im = Image.new('RGBA', (w * 2, h * 2), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    rng = random.Random(11)
    top = [(x * 2, (16 + rng.uniform(-9, 9)) * 2) for x in range(0, w + 12, 12)]
    bot = [(x * 2, (30 + rng.uniform(-9, 9)) * 2) for x in range(0, w + 12, 9)]
    d.polygon(top + bot[::-1], fill=(246, 242, 223))
    return im.resize((w, h), Image.LANCZOS)
TORN = torn_strip(W)

def sparkles(im, t, t0, pts, sc=0.8):
    for i, (x, y) in enumerate(pts):
        k = pop(t, t0 + i * 0.07)
        if k > 0: paste_scaled(im, SPARK, x, y, k * sc * (0.85 + 0.15 * math.sin((t - t0) * 6 + i)))

def shake(t, t0, amp=14, dur=0.4):
    if t < t0 or t > t0 + dur: return 0
    return amp * math.sin((t - t0) * 60) * (1 - (t - t0) / dur)


# ---------------- cenas ----------------
CLIENTE = person(shirt=(110, 190, 140), label="CLIENTE")
EMPRESARIO = person(shirt=(50, 60, 90), label="EMPRESÁRIO", suit=True)
RECEITA = bank("RECEITA")

def qmark():
    def f(d, s):
        ell(d, s, (10, 10, 290, 290), (242, 194, 48), w=8)
        ctext(d, (150, 160), s, "?", 210, INK)
    return sprite(300, 300, f)
QMARK = qmark()

def gear(col):
    def f(d, s):
        for i in range(8):
            a = i / 8 * 2 * math.pi
            x, y = 110 + 85 * math.cos(a), 110 + 85 * math.sin(a)
            ell(d, s, (x - 22, y - 22, x + 22, y + 22), col, w=5)
        ell(d, s, (30, 30, 190, 190), col, w=6); ell(d, s, (85, 85, 135, 135), (230, 225, 215), w=5)
    return sprite(220, 220, f)
GEAR1 = gear((150, 160, 175)); GEAR2 = gear((120, 130, 150))

def box_prod():
    def f(d, s):
        d.polygon([(30 * s, 110 * s), (150 * s, 60 * s), (270 * s, 110 * s), (150 * s, 160 * s)], fill=(214, 168, 110), outline=INK, width=5 * s)
        d.polygon([(30 * s, 110 * s), (150 * s, 160 * s), (150 * s, 300 * s), (30 * s, 250 * s)], fill=(190, 140, 90), outline=INK, width=5 * s)
        d.polygon([(270 * s, 110 * s), (150 * s, 160 * s), (150 * s, 300 * s), (270 * s, 250 * s)], fill=(170, 120, 75), outline=INK, width=5 * s)
        d.line((90 * s, 85 * s, 210 * s, 135 * s), fill=(240, 220, 180), width=10 * s)
    return sprite(300, 320, f)
PRODUTO = box_prod()

def wrench():
    def f(d, s):
        d.line((70 * s, 230 * s, 200 * s, 100 * s), fill=INK, width=52 * s)
        d.line((70 * s, 230 * s, 200 * s, 100 * s), fill=(170, 175, 185), width=38 * s)
        ell(d, s, (170, 30, 270, 130), (170, 175, 185), w=6); ell(d, s, (205, 45, 255, 95), (196, 214, 205), w=0)
    return sprite(300, 280, f)
SERVICO = wrench()

def notif(txt, col=(60, 170, 100)):
    fw = font(54); w = int(fw.getlength(txt)) + 150
    def f(d, s):
        rrect(d, s, (10, 10, w - 10, 130), 30, WHITE)
        ell(d, s, (30, 30, 110, 110), col, w=4); ctext(d, (70, 72), s, "PIX", 22, WHITE)
        ctext(d, (w / 2 + 50, 72), s, txt, 54, col)
    return sprite(w, 140, f)
NOTIF_100 = notif("+ R$ 100")
NOTIF_7250 = notif("+ R$ 72,50", (60, 140, 90))

def bulb():
    def f(d, s):
        ell(d, s, (40, 20, 300, 280), (255, 220, 90), w=8)
        rrect(d, s, (110, 270, 230, 330), 10, (170, 170, 178)); rrect(d, s, (120, 330, 220, 370), 10, (140, 140, 150))
        d.arc((120 * s, 120 * s, 220 * s, 220 * s), 200, 340, fill=(250, 160, 40), width=10 * s)
    return sprite(340, 380, f)
BULB = bulb()

def store(label):
    def f(d, s):
        rrect(d, s, (30, 140, 470, 420), 6, (236, 230, 214))
        for i in range(6):
            col = RED if i % 2 == 0 else WHITE
            d.polygon([((20 + i * 77) * s, 60 * s), ((97 + i * 77) * s, 60 * s), ((97 + i * 77) * s, 150 * s), ((20 + i * 77) * s, 150 * s)], fill=col, outline=INK)
        d.line((20 * s, 60 * s, 482 * s, 60 * s), fill=INK, width=6 * s)
        rrect(d, s, (60, 220, 200, 420), 4, (120, 90, 60)); rrect(d, s, (250, 220, 430, 330), 4, (180, 215, 235))
        rrect(d, s, (110, 160, 390, 210), 8, (43, 79, 160)); ctext(d, (250, 186), s, label, 30, WHITE)
    return sprite(500, 440, f)
LOJA = store("SEU NEGÓCIO")

CAL_FIM = calendar_day("FIM DO", "MÊS")

def arrow_down():
    def f(d, s):
        d.polygon([(60 * s, 20 * s), (140 * s, 20 * s), (140 * s, 180 * s), (190 * s, 180 * s), (100 * s, 290 * s), (10 * s, 180 * s), (60 * s, 180 * s)], fill=RED, outline=INK, width=6 * s)
    return sprite(200, 300, f)
ARROW_DOWN = arrow_down()

def chart(im, t, t0, x0, y0, w, h, drop_t=None, label="FLUXO DE CAIXA"):
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((x0, y0, x0 + w, y0 + h), 16, fill=WHITE, outline=INK, width=5)
    d.text((x0 + w / 2, y0 + 40), label, font=font(34), fill=INK, anchor='mm')
    k = clamp01((t - t0) / 0.9)
    pts = []
    for i in range(9):
        q = i / 8
        if q > k: break
        yv = 0.55 - 0.35 * q + 0.08 * math.sin(i * 1.7)
        if drop_t and t > drop_t and q > 0.6:
            yv += 0.55 * clamp01((t - drop_t) / 0.4) * (q - 0.6) / 0.4
        pts.append((x0 + 40 + (w - 80) * q, y0 + 80 + (h - 120) * min(yv, 0.98)))
    if len(pts) > 1:
        col = RED if drop_t and t > drop_t else GREEN
        d.line(pts, fill=col, width=12, joint='curve')

def sA_comofunciona(t):
    im = BG_A.copy()
    a = (t - 0) * 90
    paste_scaled(im, GEAR1, 330, 540, pop(t, WT(0, 2)) * 1.1, rot=a)
    paste_scaled(im, GEAR2, 520, 650, pop(t, WT(0, 3)) * 0.85, rot=-a * 1.2)
    paste_scaled(im, QMARK, 790, 560, pop(t, WT(0, 4) - 0.1) * 1.0)
    return im

def sA_pix(t):
    im = BG_A_MINT.copy()
    paste_scaled(im, CLIENTE, 180, 620, pop(t, T(2) - 0.3) * 0.75)
    paste_scaled(im, VOCE, 900, 620, pop(t, T(2) - 0.2) * 0.75)
    tp = WT(2, 6)
    if t > tp:
        q = ((t - tp) / 1.1) % 1
        paste_scaled(im, tag("PIX", TEAL, 40), 300 + 480 * q, 470 - 90 * math.sin(math.pi * q), 1)
    paste_scaled(im, tag("PIX R$ 100", INK, 50), 540, 300, pop(t, WT(3, 5)))
    paste_scaled(im, PRODUTO, 430, 640, pop(t, WT(3, 10)) * 0.6)
    paste_scaled(im, SERVICO, 650, 640, pop(t, WT(3, 14)) * 0.6)
    return im

def sB_conta(t):
    im = BG_B.copy()
    sc = pop(t, T(4) - 0.3)
    paste_scaled(im, PHONE_BLANK, 540, 1020, sc * 1.5)
    tn = WT(4, 5); ti = WT(5, 3)
    if sc > 0.95:
        d = ImageDraw.Draw(im)
        val = 'R$ 0,00' if t < tn + 0.2 else ('R$ 100,00' if t < ti + 0.3 else 'R$ 72,50')
        d.text((525, 1000), val, font=font(74), fill=RED if t >= ti + 0.3 else INK, anchor='mm')
        if tn + 0.2 <= t < ti + 0.3 and t > ti: d.line((360, 1000, 690, 1000), fill=RED, width=10)
    paste_scaled(im, NOTIF_100, 540, 440, pop(t, tn))
    ti = WT(5, 3)
    if t > ti:
        paste_scaled(im, tag("− IMPOSTO", RED, 54), 540 + shake(t, ti, 10), 1600, pop(t, ti))
    return im

def sB_calc(t):
    im = BG_B.copy(); d = ImageDraw.Draw(im)
    cx, cy, r = 540, 900, 330
    sc = pop(t, T(6) - 0.3)
    if sc > 0:
        rr = r * sc
        d.ellipse((cx - rr - 8, cy - rr - 8, cx + rr + 8, cy + rr + 8), fill=INK)
        d.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), fill=(120, 200, 130))
        tm = WT(6, 2)
        if t > tm:
            k = clamp01((t - tm) / 0.6); ang = 360 * 0.275 * k; off = 40 * clamp01((t - tm - 0.6) / 0.3)
            ox, oy = off * math.cos(math.radians(-90 + ang / 2)), off * math.sin(math.radians(-90 + ang / 2))
            d.pieslice((cx - rr + ox, cy - rr + oy, cx + rr + ox, cy + rr + oy), -90, -90 + ang, fill=RED, outline=INK, width=8)
        d.text((cx - 60, cy + 60), "R$ 100", font=font(64), fill=(30, 80, 40), anchor='mm')
        if t > WT(6, 3):
            paste_scaled(im, tag("27,5% IMPOSTO", RED, 44), 800, 470, pop(t, WT(6, 3)))
    t7 = T(7) - 0.1
    if t > t7:
        paste_scaled(im, tag("VOCÊ RECEBE  R$ 72,50", (30, 120, 60), 56), 540, 1440, pop(t, t7))
        sparkles(im, t, t7 + 0.2, [(180, 1330), (900, 1330), (860, 1560)])
    return im

def sA_fila(t):
    im = BG_A.copy()
    paste_scaled(im, RECEITA, 300, 600, pop(t, T(10) - 0.3) * 0.75)
    paste_scaled(im, tag("1º", RED, 60), 300, 840, pop(t, WT(10, 0)))
    paste_scaled(im, VOCE, 780, 620, pop(t, T(10) - 0.2) * 0.75)
    paste_scaled(im, tag("2º", INK, 60), 780, 860, pop(t, WT(10, 3)))
    paste_scaled(im, CLIENTE, 980, 640, pop(t, T(11)) * 0.6)
    return im

def sA_empresario(t):
    im = BG_A.copy()
    paste_scaled(im, EMPRESARIO, 210, 610, pop(t, T(12) - 0.3) * 0.8)
    chart(im, t, WT(12, 8), 400, 345, 600, 390, drop_t=WT(14, 3))
    paste_scaled(im, CAL_FIM, 960, 820, pop(t, T(15)) * 0.4)
    if t > WT(14, 3): paste_scaled(im, tag("− IMPOSTO", RED, 40), 660, 820, pop(t, WT(14, 3)))
    return im

def sA_atrapalha(t):
    im = BG_A.copy()
    paste_scaled(im, LOJA, 400 + shake(t, WT(16, 2), 12), 580, pop(t, T(16) - 0.3) * 0.95)
    paste_scaled(im, ARROW_DOWN, 830, 560, pop(t, WT(16, 2)) * 1.0)
    paste_scaled(im, tag("NEGÓCIOS", RED, 44), 400, 820, pop(t, T(17)))
    return im

def sB_solucao(t):
    im = BG_B_SKY.copy()
    sc = pop(t, T(19) - 0.1)
    paste_scaled(im, BULB, 540, 900, sc * 1.6)
    if t > T(19):
        d = ImageDraw.Draw(im); k = clamp01((t - T(19)) / 0.4)
        for i in range(10):
            a = i / 10 * 2 * math.pi
            d.line((540 + 340 * math.cos(a), 840 + 340 * math.sin(a), 540 + (340 + 90 * k) * math.cos(a), 840 + (340 + 90 * k) * math.sin(a)), fill=(250, 200, 60), width=14)
    paste_scaled(im, tag("SOLUÇÃO", (30, 120, 60), 64), 540, 1450, pop(t, WT(19, 2)))
    sparkles(im, t, WT(19, 2), [(200, 600), (880, 620), (870, 1250), (210, 1220)])
    return im

def sB_carteira(t):
    im = BG_B_SKY.copy()
    paste_scaled(im, PHONE_OK, 260, 760, pop(t, T(20) - 0.3) * 0.9)
    paste_scaled(im, WALLET, 760, 1180, pop(t, WT(21, 5)) * 1.3)
    paste_scaled(im, tag("CARTEIRA DIGITAL", INK, 44), 760, 1430, pop(t, WT(21, 7)))
    if t > WT(21, 2):
        for i in range(5):
            ti = WT(21, 2) + i * 0.35
            if t > ti:
                q = min((t - ti) / 0.9, 1)
                if q < 1: paste_scaled(im, COIN_R if i % 2 else COIN_B, 330 + 430 * q, 760 + 380 * q - 200 * math.sin(math.pi * q), 0.5, rot=q * 360)
    paste_scaled(im, BANCO, 540, 1650, pop(t, T(22) - 0.1) * 0.55)
    paste_scaled(im, XMARK, 540, 1650, pop(t, WT(22, 3), 0.2) * 0.7)
    return im

def sA_negocio(t):
    im = BG_A_MINT.copy()
    paste_scaled(im, LOJA, 600, 580, pop(t, WT(25, 5)) * 0.9)
    paste_scaled(im, VOCE, 190, 620, pop(t, T(25) - 0.3) * 0.75)
    paste_scaled(im, BULB, 190, 280, pop(t, T(26)) * 0.4)
    return im

def sA_fluxo(t):
    im = BG_A_MINT.copy()
    paste_scaled(im, WALLET, 540, 660, pop(t, T(27) - 0.3) * 0.75)
    for lab, k, x, y in (("MOVIMENTAR", 1, 210, 420), ("RECEBER", 2, 540, 380), ("PAGAR", 4, 870, 420)):
        paste_scaled(im, tag(lab, (30, 120, 60), 40), x, y, pop(t, WT(27, k)))
    if t > T(28):
        for i in range(3):
            a = (t - T(28)) * 2.5 + i * 2.1
            paste_scaled(im, COIN_R if i != 1 else COIN_B, 540 + 330 * math.cos(a), 680 + 120 * math.sin(a), 0.45)
    paste_scaled(im, BANCO, 920, 700, pop(t, T(29) - 0.1) * 0.4)
    paste_scaled(im, XMARK, 920, 700, pop(t, WT(29, 3), 0.2) * 0.5)
    return im

def sA_cta(t):
    im = BG_A.copy()
    tb = T(30) - 0.4
    press = 0.92 if WT(30, 4) < t < WT(30, 4) + 0.2 else 1.0
    paste_scaled(im, BTN, 540, 470, pop(t, tb) * press)
    k = ease_out((t - tb - 0.1) / 0.5)
    paste_scaled(im, HAND, 760 - 120 * k + 400 * (1 - k), 580 + 300 * (1 - k), 0.7 if t > tb else 0, rot=20)
    paste_scaled(im, tag("MENTORIA", RED, 56), 540, 790, pop(t, WT(31, 5)))
    sparkles(im, t, WT(31, 5) + 0.1, [(250, 760), (840, 720), (180, 420), (900, 400)])
    return im

SCENES = {
    0: [(0, sA_comofunciona), (T(2) - 0.1, sA_pix)],
    1: [(T(4), sB_conta), (T(6) - 0.15, sB_calc)],
    3: [(T(10), sA_fila), (T(12) - 0.1, sA_empresario), (T(16) - 0.1, sA_atrapalha)],
    4: [(T(18), sB_solucao), (T(20) - 0.15, sB_carteira)],
    6: [(T(25), sA_negocio), (T(27) - 0.1, sA_fluxo), (T(30) - 0.1, sA_cta)],
}


def push_in(im, k):
    if k <= 1.0005: return im
    w, h = im.size; big = im.resize((int(w * k), int(h * k)), Image.BILINEAR)
    x0, y0 = (big.width - w) // 2, (big.height - h) // 2
    return big.crop((x0, y0, x0 + w, y0 + h))

def whip(a, b, p):
    w, h = a.size; x = int(-w * ease_out(p))
    c = Image.new('RGBA', (w, h)); c.alpha_composite(a, (x, 0)); c.alpha_composite(b, (x + w, 0))
    r = int(14 * math.sin(math.pi * p))
    return c.filter(ImageFilter.BoxBlur(r)) if r > 0 else c

def scene_img(bi, t):
    lst = SCENES[bi]; idx = 0
    for i, (st, fn) in enumerate(lst):
        if t >= st - 0.125: idx = i
    st, fn = lst[idx]
    cur = push_in(fn(t), 1 + 0.05 * clamp01((t - st) / 4))
    if idx > 0 and t < st + 0.125:
        pst, pfn = lst[idx - 1]
        prev = push_in(pfn(t), 1 + 0.05 * clamp01((t - pst) / 4))
        return whip(prev, cur, (t - (st - 0.125)) / 0.25)
    return cur

# ---------------- apresentador ----------------
FACE = [f for f in json.load(open(os.path.join(BASE, 'face.json'))) if f[3] >= 180]
FT_ = np.array([f[0] for f in FACE]); FX_ = np.array([f[1] for f in FACE], float); FY_ = np.array([f[2] for f in FACE], float)
def out2src(t):
    for s0, s1, o in cuts:
        if t < o + (s1 - s0) + 1e-6: return s0 + (t - o)
    return cuts[-1][1]
def face_xy(st):
    m = (FT_ > st - 0.7) & (FT_ < st + 0.7)
    if not m.any(): return float(np.interp(st, FT_, FX_)), float(np.interp(st, FT_, FY_))
    return float(np.median(FX_[m])), float(np.median(FY_[m]))

def presenter_split(fr, t):
    cx, cy = face_xy(out2src(t)); ch = int(SRC_W * 960 / W)
    top = int(min(max(cy - 0.42 * ch, 0), SRC_H - ch))
    return fr.crop((0, top, SRC_W, top + ch)).resize((W, 960), Image.LANCZOS)

def presenter_full(fr, t, zoom=1.0):
    if zoom <= 1.0: return fr.resize((W, H), Image.LANCZOS)
    cx, cy = face_xy(out2src(t)); ww, hh = SRC_W / zoom, SRC_H / zoom
    x0 = min(max(cx - ww / 2, 0), SRC_W - ww); y0 = min(max(cy - 0.40 * hh, 0), SRC_H - hh)
    return fr.crop((int(x0), int(y0), int(x0 + ww), int(y0 + hh))).resize((W, H), Image.LANCZOS)

# zoom do bloco C: alterna a cada segmento
def c_zoom(t, b):
    segi = max(i for i in range(b['s'], b['e'] + 1) if T(i) <= t + 1e-6) if t >= T(b['s']) else b['s']
    n = segi - b['s']
    if b['s'] == b['e']:   # um só segmento: corta na metade
        n = 0 if t < (T(b['s']) + TE(b['s'])) / 2 else 1
    return 1.0 if n % 2 == 0 else 1.18

# ---------------- legendas ----------------
YW = {"PIX", "R$", "100", "PRODUTO", "SERVIÇO", "CONTA,", "ESTADO", "EMPRESÁRIO", "FLUXO", "CAIXA", "SOLUÇÃO", "TECNOLOGIA,",
      "CARTEIRA", "DIGITAL", "MENTORIA", "NEGÓCIO", "MOVIMENTAR,", "RECEBER", "PAGAR", "DINHEIRO", "SAIBA", "MAIS", "72,50", "FUNCIONAR?"}
RW = {"IMPOSTO", "27,5%", "MENOS", "DESCONTADO", "ATRAPALHAR", "ANTES", "SEM", "NÃO"}
def wcol(w):
    if w in RW: return RED
    if w in YW: return YEL
    return (246, 241, 233)

# títulos: por segmento (em blocos A/B), em grupos de até 5 palavras; segmentos curtos se juntam
TITLES = []
for b in BL:
    if b['f'] == 'C': continue
    cur = []
    for si in range(b['s'], b['e'] + 1):
        ws = [w for w in words if w['seg'] == si]
        chunks = [ws[i:i + 4] for i in range(0, len(ws), 4)]
        if len(chunks) > 1 and len(chunks[-1]) <= 2: last = chunks.pop(); chunks[-1] = chunks[-1] + last
        for ch in chunks:
            if cur and len(cur) + len(ch) <= 4 and ch[0]['seg'] != cur[-1]['seg'] and si - cur[-1]['seg'] == 1 and len(cur) <= 2:
                cur += ch
            else:
                if cur: TITLES.append(cur)
                cur = list(ch)
    if cur: TITLES.append(cur)
TT = []
for i, ws in enumerate(TITLES):
    t0 = ws[0]['t0'] - 0.05
    nxt = TITLES[i + 1][0]['t0'] - 0.05 if i + 1 < len(TITLES) else TOTAL + 1
    b = block_at(ws[0]['t0'])[1]
    TT.append(dict(ws=ws, t0=t0, t1=min(nxt, b['t1'] + 0.05)))

FT = font(78)
def draw_title(canvas, t, ytop):
    for T_ in TT:
        if not (T_['t0'] <= t < T_['t1']): continue
        vis = [w for w in T_['ws'] if w['t0'] <= t + 0.02]
        if not vis: return
        lines, cur = [], []
        for w in vis:
            if cur and FT.getlength(' '.join(x['w'] for x in cur + [w])) > 940: lines.append(cur); cur = [w]
            else: cur.append(w)
        lines.append(cur)
        y = ytop
        for ln in lines:
            lw = FT.getlength(' '.join(x['w'] for x in ln)); x = (W - lw) / 2
            for w in ln:
                ww = w['w']; sc = 0.75 + 0.25 * ease_back((t - w['t0']) / 0.15)
                layer = Image.new('RGBA', (int(FT.getlength(ww)) + 40, 120), (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
                d.text((20, 26), ww, font=FT, fill=(30, 20, 20, 150), stroke_width=6, stroke_fill=(30, 20, 20, 150))
                d.text((20, 18), ww, font=FT, fill=wcol(ww), stroke_width=6, stroke_fill=(38, 26, 30))
                if sc < 0.999: layer = layer.resize((int(layer.width * sc), int(layer.height * sc)), Image.BILINEAR)
                cx = x + FT.getlength(ww) / 2
                canvas.alpha_composite(layer, (int(cx - layer.width / 2), int(y + 60 - layer.height / 2)))
                x += FT.getlength(ww + ' ')
            y += 92
        return

chunks = []
for b in BL:
    if b['f'] == 'B': continue
    for si in range(b['s'], b['e'] + 1):
        cur = []
        for w in [w for w in words if w['seg'] == si]:
            if cur and (len(' '.join(x['w'] for x in cur + [w])) > 14 or len(cur) == 3): chunks.append(cur); cur = []
            cur.append(w)
        chunks.append(cur)
FC = font(46)
def draw_caption(canvas, t, cy):
    ch = None
    for c in chunks:
        if c[0]['t0'] - 0.03 <= t < c[-1]['t1'] + 0.1: ch = c
    if not ch: return
    txt = ' '.join(w['w'] for w in ch); tw = FC.getlength(txt); pad, bh = 22, 70; bw = tw + pad * 2
    sc = 0.9 + 0.1 * ease_out((t - ch[0]['t0'] + 0.03) / 0.1)
    layer = Image.new('RGBA', (int(bw) + 20, bh + 20), (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
    d.rounded_rectangle((14, 14, bw + 6, bh + 6), 10, fill=(30, 20, 20, 90))
    d.rounded_rectangle((8, 8, bw, bh), 10, fill=WHITE, outline=INK, width=4)
    x = 8 + pad
    for w in ch:
        ww = w['w']; lw = FC.getlength(ww)
        active = w['t0'] <= t < w['t1'] + 0.12 or (w is ch[-1] and t >= w['t0'])
        red = ww in RW
        if active and not red: d.rectangle((x - 4, 8 + bh * 0.48, x + lw + 4, bh - 6), fill=MARK)
        col = (RED if red else INK) if w['t0'] <= t else (175, 170, 168)
        d.text((x, 8 + (bh - 8) / 2), ww, font=FC, fill=col, anchor='lm')
        x += FC.getlength(ww + ' ')
    if sc < 0.999: layer = layer.resize((int(layer.width * sc), int(layer.height * sc)), Image.BILINEAR)
    canvas.alpha_composite(layer, (int(W / 2 - layer.width / 2), int(cy - layer.height / 2)))

FW = font(26, False)
def watermark(canvas, y):
    d = ImageDraw.Draw(canvas)
    d.ellipse((60, y, 104, y + 44), fill=(255, 255, 255, 60), outline=(255, 255, 255, 210), width=3)
    l = Image.new('RGBA', (400, 50), (0, 0, 0, 0)); ImageDraw.Draw(l).text((0, 25), "@dani.defibit", font=FW, fill=(255, 255, 255, 215), anchor='lm')
    canvas.alpha_composite(l, (118, y - 3))

# ---------------- composição ----------------
def render(f, bi, fr, t, canvas=None):
    c = canvas or Image.new('RGBA', (W, H), (0, 0, 0, 255))
    if f == 'A':
        c.paste(presenter_split(fr, t), (0, 960)); c.alpha_composite(scene_img(bi, t), (0, 0))
        c.alpha_composite(TORN, (0, 937)); watermark(c, 1000)
    elif f == 'B':
        c.alpha_composite(scene_img(bi, t))
    else:
        c.paste(presenter_full(fr, t, c_zoom(t, BL[bi])), (0, 0))
    return c

def overlays(c, f, t):
    if f in 'AB': draw_title(c, t, 110)
    if f == 'A': draw_caption(c, t, 960)
    if f == 'C': draw_caption(c, t, int(H * 0.86))

def compose(fr, t):
    bi, b = block_at(t); f = b['f']; tt = t - b['t0']
    if bi == 0 or tt >= TR:
        c = render(f, bi, fr, t); overlays(c, f, t); return c.convert('RGB')
    pf = BL[bi - 1]['f']; p = ease_out(tt / TR)
    c = Image.new('RGBA', (W, H), (0, 0, 0, 255))
    if f == 'B':
        img = scene_img(bi, t)
        if pf == 'A':     # animação desce cobrindo o apresentador
            c.paste(presenter_split(fr, t), (0, 960)); hc = int(960 + 960 * p)
            c.alpha_composite(img.crop((0, 0, W, hc))); c.alpha_composite(TORN, (0, hc - 23))
        else:             # C -> B: entra por cima
            c.paste(presenter_full(fr, t, c_zoom(t - TR, BL[bi - 1])), (0, 0)); off = int(-H * (1 - p))
            c.alpha_composite(img.crop((0, -off, W, H)), (0, 0)); c.alpha_composite(TORN, (0, max(H + off - 23, 0)))
    elif f == 'C':
        c.paste(presenter_full(fr, t, c_zoom(t, b)), (0, 0))
        if pf == 'B':     # b-roll desce e sai
            img = scene_img(bi - 1, t); off = int(H * p)
            c.alpha_composite(img.crop((0, 0, W, H - off)), (0, off)); c.alpha_composite(TORN, (0, max(off - 23, 0)))
        else:             # A -> C: painel sobe e sai
            img = scene_img(bi - 1, t); off = int(960 * p)
            c.alpha_composite(img.crop((0, off, W, 960)), (0, 0)); c.alpha_composite(TORN, (0, 960 - off - 23))
    else:  # f == 'A'
        if pf == 'C':     # painel entra por cima sobre o rosto
            c.paste(presenter_full(fr, t, 1.18), (0, 0)); c.paste(presenter_split(fr, t), (0, 960))
            img = scene_img(bi, t); y = int(-960 * (1 - p))
            c.alpha_composite(img.crop((0, -y, W, 960)), (0, 0)); c.alpha_composite(TORN, (0, 960 + y - 23))
        else:             # B -> A: b-roll sobe e sai revelando a tela dividida
            render('A', bi, fr, t, c); img = scene_img(bi - 1, t); off = int(-H * p)
            c.alpha_composite(img.crop((0, -off, W, H)), (0, 0)); c.alpha_composite(TORN, (0, H + off - 23))
    overlays(c, f, t)
    return c.convert('RGB')

if __name__ == '__main__':
    n = int(TOTAL * FPS); only = [float(x) for x in sys.argv[2:]]
    rd = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', os.path.join(BASE, 'cut.mp4'), '-vf', f'fps={FPS},scale={SRC_W}:{SRC_H}', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
    wr = None if only else subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
        '-i', os.path.join(BASE, 'audio_cut.wav'), '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p',
        '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', os.path.join(BASE, 'video_final.mp4')], stdin=subprocess.PIPE)
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
        if i % 300 == 0: print('quadro', i, '/', n, flush=True)
    if wr: wr.stdin.close(); wr.wait()
    print('ok', round(TOTAL, 2))
