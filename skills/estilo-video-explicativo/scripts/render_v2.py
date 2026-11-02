"""Vídeo 'Bloqueio judicial / DeFi' — estilo explicativo versão 1 (desenhos 2D por código)."""
import math, random, subprocess, sys, os, json
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

BASE = sys.argv[1]
FONT = os.path.join(BASE, 'fonts/package/files/montserrat-latin-900-normal.woff')
FONT8 = os.path.join(BASE, 'fonts/package/files/montserrat-latin-800-normal.woff')
W, H, FPS = 1080, 1920, 30
SRC_W, SRC_H = 720, 1280
random.seed(7)

INK = (34, 25, 39); WHITE = (255, 251, 248); YEL = (229, 186, 48); MARK = (232, 174, 60)
RED = (230, 67, 50); KRAFT = (213, 189, 143); GREEN = (70, 170, 100); TEAL = (40, 170, 170)
SKIN = (176, 118, 78); NAVY = (45, 58, 92); GRAY = (150, 150, 155)

# ---------------- fala ----------------
SEGS = [
    (0.635, 1.473, "SEGUNDA-FEIRA"), (1.600, 2.368, "8H DA MANHÃ"), (2.489, 3.652, "VOCÊ PEGA O SEU CELULAR"),
    (4.020, 6.296, "ABRE A SUA CONTA BANCÁRIA E ENXERGA"), (6.441, 7.332, "BLOQUEIO JUDICIAL"),
    (7.887, 10.267, "VOCÊ NÃO PODE MAIS MOVIMENTAR O SEU DINHEIRO"), (10.526, 11.823, "EM NENHUMA CONTA CORRENTE"),
    (12.266, 13.548, "VOCÊ ESTÁ PASSANDO POR ISSO"), (14.287, 15.718, "OU JÁ PASSOU POR ISSO?"),
    (16.046, 16.643, "DE VER"), (16.906, 20.117, "TODO SEU DINHEIRO BLOQUEADO VOCÊ SEQUER CONSEGUIR TIRAR UM DINHEIRO"),
    (20.372, 21.664, "PARA CONTRATAR UM ADVOGADO"), (22.217, 23.024, "PARA TE DEFENDER"),
    (23.724, 25.320, "É ISSO QUE ACONTECE QUANDO VOCÊ DEIXA"), (25.494, 26.631, "TODO O SEU DINHEIRO"),
    (26.878, 28.634, "NUMA REDE BANCÁRIA LIGADA AO CPF"), (29.608, 32.608, "UMA ORDEM JUDICIAL, UMA CANETADA, BLOQUEIA TUDO"),
    (33.111, 33.383, "ENTÃO"), (33.525, 35.255, "VOCÊ PRECISA APRENDER"),
    (35.731, 38.720, "COMO MOVIMENTAR SEU DINHEIRO SEM USAR CONTA BANCÁRIA"), (39.021, 40.193, "VOCÊ PRECISA CONHECER"),
    (40.596, 42.413, "A REDE DE FINANÇAS DESCENTRALIZADAS"), (42.640, 44.246, "UMA REDE FINANCEIRA PARALELA"),
    (44.463, 45.689, "ONDE VOCÊ PODE MOVIMENTAR"), (45.997, 49.033, "REAIS, DÓLARES, BITCOIN, NÃO IMPORTA A MOEDA QUE VOCÊ ESCOLHER"),
    (49.292, 50.796, "ATRAVÉS DE CARTEIRAS DIGITAIS"), (51.324, 52.529, "SEM PRECISAR DE CPF"),
    (52.688, 53.858, "SEM PRECISAR DE CNPJ"), (54.378, 57.818, "E SE VOCÊ QUER SABER COMO ESSA REDE FUNCIONA, COMO VOCÊ PODE USAR"),
    (58.141, 60.309, "PARA SE PROTEGER E PROTEGER O SEU PATRIMÔNIO"), (60.720, 61.841, "CLICA EM SAIBA MAIS"),
    (62.281, 63.486, "E APLIQUE-SE PARA A MENTORIA"),
]
PAD = 0.08
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
    ('A', 0, 4), ('B', 5, 6), ('C', 7, 8), ('A', 9, 12), ('B', 13, 16), ('C', 17, 18),
    ('A', 19, 21), ('B', 22, 27), ('C', 28, 28), ('A', 29, 31),
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
# A (1080x960)
def sA_dia(t):
    im = BG_A.copy()
    paste_scaled(im, CAL_SEG, 330, 600, pop(t, WT(0, 0) - 0.1) * 0.9)
    sc = pop(t, WT(1, 0) - 0.05)
    if sc > 0:
        cl = CLOCK.copy(); d = ImageDraw.Draw(cl)
        k = clamp01((t - WT(1, 0)) / 0.6); hr = 8 * k; mn = 0
        ah = (hr % 12) / 12 * 2 * math.pi + 2 * math.pi * 3 * (1 - k)
        am = 2 * math.pi * 3 * (1 - k)
        d.line((170, 170, 170 + 70 * math.sin(ah), 170 - 70 * math.cos(ah)), fill=INK, width=14)
        d.line((170, 170, 170 + 110 * math.sin(am), 170 - 110 * math.cos(am)), fill=RED, width=9)
        d.ellipse((158, 158, 182, 182), fill=INK)
        paste_scaled(im, cl, 770, 580, sc * 0.9)
        paste_scaled(im, tag("8:00", INK, 46), 770, 780, pop(t, WT(1, 0) + 0.4))
    return im

def sA_cel(t):
    im = BG_A.copy()
    paste_scaled(im, VOCE, 300, 620, pop(t, T(2) - 0.15) * 0.8)
    tl = T(4) - 0.05
    sx = shake(t, tl)
    ph = PHONE_LOCK if t >= tl else PHONE_OK
    paste_scaled(im, ph, 720 + sx, 600, pop(t, WT(2, 4) - 0.1) * 0.78)
    if t >= tl:
        paste_scaled(im, PADLOCK, 900, 420, pop(t, tl + 0.1) * 0.6, rot=-12)
        sparkles(im, t, tl + 0.15, [(530, 280), (900, 640)], 0.6)
    return im

def sA_bloq(t):
    im = BG_A_DARK.copy()
    paste_scaled(im, MONEY, 540, 600, pop(t, T(9) - 0.1) * 1.3)
    d = ImageDraw.Draw(im)
    k = clamp01((t - WT(10, 2)) / 0.4)
    if k > 0:
        for y in (520, 640):
            xe = 200 + 680 * k
            for x in range(200, int(xe), 46):
                d.ellipse((x, y - 16, x + 50, y + 16), outline=(190, 190, 200), width=10)
        paste_scaled(im, PADLOCK, 540, 600, pop(t, WT(10, 2) + 0.3) * 0.8)
    paste_scaled(im, VOCE, 170, 610, pop(t, WT(10, 4)) * 0.8)
    paste_scaled(im, tag("R$ 0", RED, 46), 170, 330, pop(t, WT(10, 9)))
    return im

def sA_adv(t):
    im = BG_A_DARK.copy()
    paste_scaled(im, VOCE, 280, 590, 0.9)
    paste_scaled(im, tag("R$ 0", RED, 46), 280, 300, 1)
    paste_scaled(im, ADVOGADO, 790, 590, pop(t, WT(11, 3) - 0.1) * 0.9)
    paste_scaled(im, tag("R$ ???", INK, 46), 790, 300, pop(t, WT(11, 3) + 0.2))
    paste_scaled(im, XMARK, 790, 560, pop(t, T(12) + 0.2, 0.2) * 1.0)
    return im

def sA_semBanco(t):
    im = BG_A_MINT.copy()
    paste_scaled(im, BANCO, 540, 360, pop(t, T(19) - 0.1) * 0.75)
    paste_scaled(im, VOCE, 160, 610, pop(t, T(19)) * 0.8)
    paste_scaled(im, MONEY, 900, 680, pop(t, T(19) + 0.1) * 0.6)
    # dinheiro passando por baixo do banco
    for i in range(4):
        ti = WT(19, 1) + i * 0.3
        if t > ti:
            q = min((t - ti) / 0.9, 1)
            if q < 1: paste_scaled(im, COIN_R, 260 + 560 * q, 700 - 80 * math.sin(math.pi * q), 0.45, rot=q * 360)
    paste_scaled(im, XMARK, 540, 360, pop(t, WT(19, 5), 0.2) * 0.9)
    return im

def sA_defi(t):
    im = BG_A_DARK.copy(); d = ImageDraw.Draw(im)
    rng = random.Random(5)
    nodes = [(540, 470)] + [(540 + 330 * math.cos(a) * (0.75 + 0.25 * rng.random()), 470 + 250 * math.sin(a) * (0.75 + 0.25 * rng.random()))
                           for a in [i * 2 * math.pi / 9 for i in range(9)]]
    k = clamp01((t - T(20)) / 1.4)
    n = int(1 + 9 * k)
    for i in range(1, n):
        for j in (0, i % 9 + 1 if i % 9 + 1 < n else None):
            if j is None: continue
            d.line((*nodes[i], *nodes[j]), fill=(80, 220, 210), width=6)
    for i, (x, y) in enumerate(nodes[:n]):
        r = 26 if i else 0
        if r: d.ellipse((x - r, y - r, x + r, y + r), fill=(80, 220, 210), outline=WHITE, width=5)
    if t > T(20) - 0.35:
        c = tag("DeFi", TEAL, 70); paste_scaled(im, c, 540, 470, pop(t, T(20) - 0.35))
    if t > T(21):
        paste_scaled(im, tag("FINANÇAS DESCENTRALIZADAS", INK, 38), 540, 790, pop(t, WT(21, 3)))
    sparkles(im, t, WT(21, 4), [(180, 250), (900, 280), (930, 650)], 0.6)
    return im

def sA_escudo(t):
    im = BG_A_MINT.copy()
    paste_scaled(im, VOCE, 420, 610, 0.8 * pop(t, T(29) - 0.3))
    paste_scaled(im, MONEY, 700, 680, 0.6 * pop(t, T(29)))
    paste_scaled(im, SHIELD, 560, 470, pop(t, WT(29, 2)) * 1.05)
    paste_scaled(im, tag("PATRIMÔNIO", INK, 44), 560, 800, pop(t, WT(29, 7)))
    sparkles(im, t, WT(29, 3), [(250, 260), (880, 300), (900, 640)])
    return im

def sA_cta(t):
    im = BG_A.copy()
    tb = T(30) - 0.4
    press = 0.92 if WT(30, 2) < t < WT(30, 2) + 0.2 else 1.0
    paste_scaled(im, BTN, 540, 470, pop(t, tb) * press)
    k = ease_out((t - tb - 0.1) / 0.5)
    paste_scaled(im, HAND, 760 - 120 * k + 400 * (1 - k), 580 + 300 * (1 - k), 0.7 if t > tb else 0, rot=20)
    paste_scaled(im, tag("MENTORIA", RED, 56), 540, 790, pop(t, WT(31, 4)))
    sparkles(im, t, WT(31, 4) + 0.1, [(250, 760), (840, 720), (180, 420), (900, 400)])
    return im

# B (1080x1920)
def sB_bancos(t):
    im = BG_B.copy()
    xs = [(220, 720), (540, 620), (860, 720)]
    trig = [WT(5, 4), WT(6, 1), WT(6, 2)]
    for (x, y), tt in zip(xs, trig):
        paste_scaled(im, BANCO, x, y, pop(t, T(5) - 0.2) * 0.72)
        paste_scaled(im, PADLOCK, x, y + 60, pop(t, tt) * 0.62)
    paste_scaled(im, VOCE, 300, 1250, pop(t, T(5) - 0.1) * 1.3)
    paste_scaled(im, MONEY, 760, 1430, pop(t, WT(5, 7) - 0.1) * 0.9)
    paste_scaled(im, PADLOCK, 760, 1400, pop(t, WT(5, 7) + 0.25) * 0.7)
    return im

def sB_cpf(t):
    im = BG_B.copy(); d = ImageDraw.Draw(im)
    paste_scaled(im, BANCO, 540, 640, pop(t, T(13) - 0.2) * 1.35)
    paste_scaled(im, MONEY, 540, 1030, pop(t, T(14) - 0.1) * 1.1)
    tc = WT(15, 5)
    k = clamp01((t - WT(15, 2)) / 0.5)
    if k > 0:
        for y in range(1150, int(1150 + 200 * k), 40):
            d.ellipse((520, y, 560, y + 50), outline=(110, 110, 120), width=9)
    paste_scaled(im, CARD_CPF, 540, 1480, pop(t, tc - 0.15) * 1.1)
    return im

def sB_ordem(t):
    im = BG_B.copy()
    paste_scaled(im, ORDEM, 540, 820, pop(t, T(16) - 0.1) * 1.4)
    tp = WT(16, 3)
    if t > tp - 0.1:
        k = clamp01((t - tp) / 0.7)
        x = 525 + 215 * k; y = 1060 + 14 * math.sin(k * 30)
        paste_scaled(im, PEN, x + 121, y - 148, 0.9)
        if k > 0:
            d = ImageDraw.Draw(im)
            pts = [(525 + 215 * q, 1060 + 14 * math.sin(q * 30)) for q in np.linspace(0, k, 30)]
            d.line(pts, fill=(30, 40, 120), width=7, joint='curve')
    ts = WT(16, 6)
    paste_scaled(im, STAMP_BLOQ, 540 + shake(t, ts, 10), 1450, pop(t, ts, 0.18) * 1.3, rot=-8)
    paste_scaled(im, PADLOCK, 860, 560, pop(t, ts + 0.2) * 0.8, rot=10)
    return im

def sB_paralela(t):
    im = BG_B_SKY.copy(); d = ImageDraw.Draw(im)
    # duas trilhas
    for x0, col, lab, tt in ((300, (150, 150, 155), "BANCOS", T(22)), (780, (60, 200, 190), "DeFi", WT(22, 3))):
        k = clamp01((t - tt) / 0.6)
        if k <= 0: continue
        d.rounded_rectangle((x0 - 110, 1800 - 1300 * k, x0 + 110, 1800), 20, fill=col, outline=INK, width=6)
        for y in range(int(1800 - 1300 * k) + 40, 1780, 140):
            d.rectangle((x0 - 10, y, x0 + 10, y + 70), fill=WHITE)
        paste_scaled(im, tag(lab, INK if lab == "BANCOS" else TEAL, 48), x0, 460, pop(t, tt + 0.2))
    if t > WT(23, 3):
        for i in range(3):
            q = ((t - WT(23, 3)) * 0.8 + i / 3) % 1
            paste_scaled(im, COIN_B if i == 0 else COIN_R, 780, 1750 - 1200 * q, 0.55)
    paste_scaled(im, XMARK, 300, 1050, 0)  # (sem X aqui)
    return im

def sB_moedas(t):
    im = BG_B_SKY.copy()
    st0 = T(24) - 0.15
    trig = [(COIN_R, max(WT(24, 0) - 0.15, st0), 250, 700), (COIN_U, WT(24, 1), 540, 620), (COIN_B, WT(24, 2), 830, 700)]
    tw = T(25) + 0.1
    for c, tt, x, y in trig:
        if t < tw + 0.2:
            paste_scaled(im, c, x, y + 10 * math.sin((t - tt) * 4), pop(t, tt) * 1.2)
        else:
            q = clamp01((t - tw - 0.2) / 0.6)
            if q < 1: paste_scaled(im, c, x + (540 - x) * q, y + (1300 - y) * q, 1.2 * (1 - 0.6 * q))
    for (lab, tt, x) in (("REAIS", max(WT(24, 0) - 0.15, st0), 250), ("DÓLARES", WT(24, 1), 540), ("BITCOIN", WT(24, 2), 830)):
        if t < tw + 0.2: paste_scaled(im, tag(lab, INK, 34), x, 870 if x != 540 else 790, pop(t, tt + 0.1))
    paste_scaled(im, WALLET, 540, 1330, pop(t, tw) * 1.3)
    paste_scaled(im, tag("CARTEIRA DIGITAL", INK, 44), 540, 1600, pop(t, WT(25, 3)))
    return im

def sB_semcpf(t):
    im = BG_B_SKY.copy()
    paste_scaled(im, CARD_CPF, 540, 720, pop(t, T(26) - 0.4) * 1.3)
    paste_scaled(im, XMARK, 540, 720, pop(t, WT(26, 3), 0.2) * 1.2)
    paste_scaled(im, CARD_CNPJ, 540, 1300, pop(t, T(27) - 0.1) * 1.3)
    paste_scaled(im, XMARK, 540, 1300, pop(t, WT(27, 3), 0.2) * 1.2)
    return im

# cenas por bloco: lista de (início, função)
SCENES = {
    0: [(0, sA_dia), (T(2) - 0.1, sA_cel)],
    1: [(T(5), sB_bancos)],
    3: [(T(9), sA_bloq), (T(11) - 0.1, sA_adv)],
    4: [(T(13), sB_cpf), (T(16) - 0.15, sB_ordem)],
    6: [(T(19), sA_semBanco), (T(20) - 0.1, sA_defi)],
    7: [(T(22), sB_paralela), (T(24) - 0.15, sB_moedas), (T(26) - 0.15, sB_semcpf)],
    9: [(T(29), sA_escudo), (T(30) - 0.1, sA_cta)],
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
FACE = json.load(open(os.path.join(BASE, 'face.json')))
FT_ = np.array([f[0] for f in FACE]); FX_ = np.array([f[1] for f in FACE], float); FY_ = np.array([f[2] for f in FACE], float)
def out2src(t):
    for s0, s1, o in cuts:
        if t < o + (s1 - s0) + 1e-6: return s0 + (t - o)
    return cuts[-1][1]
def face_xy(st):
    m = (FT_ > st - 0.7) & (FT_ < st + 0.7)
    if not m.any(): return float(np.interp(st, FT_, FX_)), float(np.interp(st, FT_, FY_))
    return float(FX_[m].mean()), float(FY_[m].mean())

def presenter_split(fr, t):
    cx, cy = face_xy(out2src(t)); ch = 640
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
    return 1.0 if n % 2 == 0 else 1.32

# ---------------- legendas ----------------
YW = {"SEGUNDA-FEIRA", "8H", "CELULAR", "CONTA", "BANCÁRIA", "DINHEIRO", "ADVOGADO", "CPF", "CANETADA", "APRENDER",
      "FINANÇAS", "DESCENTRALIZADAS", "PARALELA", "REAIS,", "DÓLARES,", "BITCOIN,", "CARTEIRAS", "DIGITAIS", "PATRIMÔNIO",
      "SAIBA", "MAIS", "MENTORIA", "CONHECER", "REDE", "CNPJ", "DEFENDER", "PROTEGER"}
RW = {"BLOQUEIO", "JUDICIAL", "BLOQUEADO", "BLOQUEIA", "TUDO", "NENHUMA", "NÃO", "SEM", "JUDICIAL,"}
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
            c.paste(presenter_full(fr, t, 1.32), (0, 0)); c.paste(presenter_split(fr, t), (0, 960))
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
