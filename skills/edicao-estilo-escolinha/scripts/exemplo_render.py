import os
# Pasta base dos projetos (pode ser trocada pela variável de ambiente DANI_EDITORA)
BASE = os.environ.get('DANI_EDITORA', r'C:\dani video hunter editora')
import sys
sys.path.insert(0, os.path.join(BASE, 'v5'))
from eng import *

PW, PH = 972, 570
SC = []
def scene(a, b, bg=None):
    def d(fn): SC.append((a, b, fn, bg)); return fn
    return d

# ---------------- cenas (tempo da fonte, coordenadas do painel) ----------------
@scene(60.3, 66.9, 'tax')
def b1(c, t):
    img3d(c, 'tax', 270, 300, 470, t, 60.3, 66.9)
    kicker(c, 'NÓS JÁ TEMOS A', 520, 55, NAVY, ap(t, 60.4))
    text(c, 'MAIOR CARGA', 520, 92, 62, INK, ap(t, 61.5))
    text(c, 'TRIBUTÁRIA', 520, 166, 62, INK, ap(t, 62.1))
    text(c, 'DO MUNDO.', 520, 240, 62, RED, ap(t, 63.0, .3), pop=True)
    chip(c, '+ IMPOSTO EM 2027', 715, 420, RED, ap(t, 65.0), size=40)
    coins_fall(c, t, 65.2, 560, 480)

@scene(66.9, 72.9, 'credit')
def b2(c, t):
    img3d(c, 'credit', 720, 300, 470, t, 66.9, 72.9)
    kicker(c, 'A PARTIR DE 2027', 46, 55, RED, ap(t, 66.95))
    text(c, 'IMPOSTO', 46, 92, 70, INK, ap(t, 67.0))
    text(c, 'DESCONTADO', 46, 172, 70, RED, ap(t, 67.5))
    text(c, 'DIRETO NA FONTE', 46, 252, 44, INK, ap(t, 68.2))
    bullet(c, 'do vendedor', 46, 350, t, 70.0, NAVY)
    bullet(c, 'do prestador de serviço', 46, 420, t, 71.7, TEAL)

@scene(72.9, 81.8, None)
def b3(c, t):
    kicker(c, 'ANTES MESMO DE CAIR NA SUA CONTA', 46, 40, INK, ap(t, 73.4))
    chip(c, 'PAGAMENTO', 486, 140, NAVY, ap(t, 73.6), size=50)
    arrow(c, (430, 190), (230, 300), RED, ap(t, 79.4, .4))
    arrow(c, (540, 190), (740, 300), LGR, ap(t, 75.6, .4), dashed=True)
    img3d(c, 'gov', 230, 400, 190, t, 79.6, 81.8)
    text(c, 'GOVERNO', 160, 505, 40, RED, ap(t, 80.4), w=700)
    text(c, 'PRIMEIRO', 168, 470 - 410, 1, RED, 0)
    img3d(c, 'p2p', 740, 400, 190, t, 75.6, 81.8)
    text(c, 'TRABALHADOR', 640, 505, 40, GR, ap(t, 76.2), w=700)
    if t >= 80.8:
        pill(c, 'o governo recebe primeiro', 290, 245, RED, WHITE, ap(t, 80.8), size=24)

@scene(81.8, 92.4, 'gov')
def b4(c, t):
    img3d(c, 'gov', 270, 300, 430, t, 81.8, 92.4)
    coins_fall(c, t, 88.2, 160, 60, ('usd', 'brl', 'btc'))
    kicker(c, 'VAI SER A MAIOR', 520, 55, NAVY, ap(t, 82.0))
    text(c, 'MÁQUINA DE', 520, 92, 66, INK, ap(t, 87.3))
    text(c, 'ARRECADAÇÃO', 520, 170, 66, NAVY, ap(t, 88.2))
    text(c, 'DO MUNDO.', 520, 260, 86, RED, ap(t, 90.0, .3), pop=True)

@scene(92.4, 101.2, None)
def b5(c, t):
    kicker(c, 'NO BRASIL A GENTE JÁ PAGA', 46, 50, INK, ap(t, 92.5))
    text(c, 'POUCO IMPOSTO?', 46, 90, 66, LGR, ap(t, 94.2))
    q = ap(t, 95.6, .3)
    if q > 0:
        ln = Image.new('RGBA', (PW, PH), (0, 0, 0, 0)); ImageDraw.Draw(ln).line([46, 140, 46 + 470 * q, 140], fill=RED + (255,), width=9); c.alpha_composite(ln)
    text(c, 'O MAIOR', 46, 200, 66, INK, ap(t, 97.5))
    text(c, 'DO MUNDO', 46, 274, 66, RED, ap(t, 98.0))
    # gráfico subindo
    p = ap(t, 98.6, .6)
    if p > 0:
        g = Image.new('RGBA', (PW, PH), (0, 0, 0, 0)); d = ImageDraw.Draw(g)
        bars = [70, 110, 150, 205, 280]
        for i, h in enumerate(bars):
            hh = h * min(1, max(0, p * 1.6 - i * 0.15))
            x = 560 + i * 74
            d.rounded_rectangle([x, 500 - hh, x + 52, 500], 8, fill=(RED if i == 4 else NAVY) + (255,))
        d.line([(540, 502), (940, 502)], fill=GR + (255,), width=3)
        c.alpha_composite(g)
    text(c, 'E VAI AUMENTAR.', 46, 380, 58, RED, ap(t, 99.8, .3), pop=True)

@scene(101.2, 112.4, 'network')
def b6(c, t):
    img3d(c, 'network', 270, 300, 470, t, 101.2, 112.4)
    kicker(c, 'POR QUE VOCÊ AINDA NÃO', 520, 55, NAVY, ap(t, 102.3))
    text(c, 'APRENDEU', 520, 92, 66, INK, ap(t, 109.1))
    text(c, 'A USAR UMA', 520, 166, 50, INK, ap(t, 109.8))
    text(c, 'NOVA REDE', 520, 228, 66, TEAL, ap(t, 110.6))
    text(c, 'FINANCEIRA?', 520, 302, 66, TEAL, ap(t, 111.0))

@scene(112.4, 118.4, 'docs')
def b7(c, t):
    img3d(c, 'docs', 740, 320, 420, t, 112.4, 118.4)
    kicker(c, 'UMA REDE QUE NÃO PRECISA DE', 46, 55, RED, ap(t, 112.5))
    strike(c, 'Conta bancária', 46, 130, t, 112.6, 48)
    strike(c, 'Autorização', 46, 225, t, 115.9, 48)
    strike(c, 'Governo', 46, 320, t, 117.3, 48)

@scene(118.4, 132.4, 'items')
def b8(c, t):
    img3d(c, 'items', 720, 320, 450, t, 118.4, 132.4)
    kicker(c, 'AGORA VIROU UMA', 46, 55, NAVY, ap(t, 125.8))
    text(c, 'QUESTÃO DE', 46, 92, 64, INK, ap(t, 126.6))
    text(c, 'SOBREVI-', 46, 166, 74, RED, ap(t, 127.0, .3), pop=True)
    text(c, 'VÊNCIA.', 46, 250, 74, RED, ap(t, 127.2, .3), pop=True)
    text(c, 'todo brasileiro precisa entender', 50, 380, 26, GR, ap(t, 130.0), font='m', w=700)

@scene(132.4, 145.5, 'p2p')
def b9(c, t):
    img3d(c, 'p2p', 740, 300, 420, t, 132.4, 145.5)
    kicker(c, 'FINANÇAS DESCENTRALIZADAS', 46, 45, TEAL, ap(t, 132.8))
    text(c, 'Uma rede financeira que', 46, 85, 30, INK, ap(t, 137.8), font='m', w=800)
    text(c, 'não tem:', 46, 122, 30, INK, ap(t, 139.1), font='m', w=800)
    strike(c, 'Governo', 46, 185, t, 139.8, 44)
    strike(c, 'Estado', 46, 265, t, 141.0, 44)
    strike(c, 'Bloqueio', 46, 345, t, 142.8, 44)
    strike(c, 'Monitoramento', 46, 425, t, 143.8, 44)

@scene(145.5, 155.3, 'cctv')
def b10(c, t):
    img3d(c, 'cctv', 250, 300, 440, t, 145.5, 155.3)
    kicker(c, 'O GOVERNO SÓ CONSEGUE', 500, 55, RED, ap(t, 146.9))
    bullet(c, 'Manipular', 500, 110, t, 148.7, RED, 44)
    bullet(c, 'Monitorar', 500, 195, t, 150.4, RED, 44)
    bullet(c, 'Bloquear', 500, 280, t, 152.2, RED, 44)
    bullet(c, 'Pôr a mão no', 500, 365, t, 154.0, RED, 44)
    text(c, 'seu dinheiro', 546, 425, 44, INK, ap(t, 154.3), w=600)

@scene(155.3, 158.3, 'bank')
def b11(c, t):
    img3d(c, 'bank', 270, 300, 440, t, 155.3, 158.3)
    text(c, 'PORQUE', 520, 120, 60, INK, ap(t, 155.3))
    text(c, 'ELE ESTÁ', 520, 196, 60, INK, ap(t, 155.6))
    text(c, 'NO BANCO.', 520, 272, 76, RED, ap(t, 155.9, .3), pop=True)

@scene(158.3, 167.6, 'exploded')
def b12(c, t):
    s = 500; cx, cy = 680, 300
    img3d(c, 'exploded', cx, cy, s, t, 158.3, 167.6)
    kicker(c, 'APRENDA A USAR UMA REDE ONDE', 46, 40, INK, ap(t, 158.6))
    ox, oy = cx - s / 2, cy - s / 2
    leader(c, (ox + s * .30, oy + s * .22), (40, 120), 'O dinheiro', 'não fica no banco', RED, ap(t, 160.4, .5))
    leader(c, (ox + s * .26, oy + s * .52), (40, 250), 'Fica na', 'sua carteira', BLUE, ap(t, 162.3, .5))
    leader(c, (ox + s * .32, oy + s * .76), (40, 380), 'Autocustódia', 'só você acessa', GREEN, ap(t, 164.6, .5))

@scene(167.6, 178.8, 'coins')
def b13(c, t):
    s = 480; cx, cy = 700, 300
    img3d(c, 'coins', cx, cy, s, t, 167.6, 178.8)
    kicker(c, 'NÃO IMPORTA SE VOCÊ MOVIMENTA', 46, 40, INK, ap(t, 167.7))
    ox, oy = cx - s / 2, cy - s / 2
    leader(c, (ox + s * .80, oy + s * .36), (40, 110), 'Dólar', 'digital, estável', GREEN, ap(t, 168.3, .5))
    leader(c, (ox + s * .50, oy + s * .62), (40, 220), 'Real', 'digital', TEAL, ap(t, 168.9, .5))
    leader(c, (ox + s * .12, oy + s * .60), (40, 330), 'Bitcoin', 'amamos bitcoin', NAVY, ap(t, 169.4, .5))
    if t >= 173.8: pill(c, 'outras moedas, sem banco', 40, 470, TEAL, WHITE, ap(t, 173.8), size=26)

@scene(178.8, 195.6, 'vault')
def b14(c, t):
    img3d(c, 'vault', 760, 300, 380, t, 178.8, 195.6)
    kicker(c, 'O CIDADÃO TEM QUE ENTENDER', 46, 45, NAVY, ap(t, 180.3))
    text(c, 'É CRUCIAL', 46, 82, 64, RED, ap(t, 184.5, .3), pop=True)
    check(c, 'Movimentar o seu dinheiro', 46, 200, t, 187.2, GREEN, 34)
    check(c, 'Tirar o estado dele', 46, 285, t, 189.3, GREEN, 34)
    check(c, 'Tirar o governo dele', 46, 370, t, 191.9, GREEN, 34)

@scene(195.6, 201.8, 'dossier')
def b15(c, t):
    img3d(c, 'dossier', 740, 300, 420, t, 195.6, 201.8)
    kicker(c, 'PARAR DE', 46, 50, RED, ap(t, 195.6))
    strike(c, 'Usar só conta bancária', 46, 115, t, 195.8, 40)
    strike(c, 'Ser confiscado', 46, 200, t, 197.8, 40)
    strike(c, 'Ser bloqueado', 46, 285, t, 198.8, 40)
    strike(c, 'Correr risco', 46, 370, t, 199.7, 40)

@scene(201.8, 216.2, 'chess')
def b16(c, t):
    img3d(c, 'chess', 270, 300, 450, t, 201.8, 216.2)
    text(c, 'AUTOCUSTÓDIA', 520, 60, 66, TEAL, ap(t, 201.8, .3), pop=True)
    text(c, 'É UMA QUESTÃO', 520, 140, 48, INK, ap(t, 202.8))
    text(c, 'DE SOBREVIVÊNCIA.', 520, 200, 48, RED, ap(t, 203.3))
    text(c, 'num país que quer', 524, 300, 28, GR, ap(t, 206.0), font='m', w=700)
    text(c, 'tirar tudo do cidadão', 524, 340, 28, GR, ap(t, 207.3), font='m', w=700)

@scene(216.2, 223.6, 'spend')
def b17(c, t):
    img3d(c, 'spend', 740, 320, 420, t, 216.2, 223.6)
    text(c, 'ACORDA!', 46, 40, 90, RED, ap(t, 216.6, .3), pop=True)
    bullet(c, 'Você que tem empresa', 46, 170, t, 218.1, NAVY, 36)
    bullet(c, 'Que presta serviço', 46, 245, t, 220.4, TEAL, 36)
    bullet(c, 'Que tem uma loja', 46, 320, t, 222.2, GREEN, 36)
    bullet(c, 'Que movimenta dinheiro', 46, 395, t, 223.1, BLUE, 36)

@scene(223.6, 236.9, 'network')
def b18(c, t):
    img3d(c, 'network', 740, 300, 420, t, 223.6, 236.9)
    kicker(c, 'APRENDA A MOVIMENTAR UMA REDE', 46, 45, TEAL, ap(t, 224.7))
    text(c, 'Onde o seu dinheiro', 46, 90, 30, INK, ap(t, 229.6), font='m', w=800)
    text(c, 'não passa por:', 46, 128, 30, INK, ap(t, 230.1), font='m', w=800)
    strike(c, 'Banco', 46, 195, t, 231.3, 46)
    strike(c, 'Governo', 46, 280, t, 233.0, 46)
    strike(c, 'Estado', 46, 365, t, 233.7, 46)
    if t >= 236.1: pill(c, 'link na bio', 46, 470, NAVY, WHITE, ap(t, 236.1), size=28)

@scene(236.9, 249.3, 'vault')
def b19(c, t):
    img3d(c, 'vault', 760, 300, 380, t, 236.9, 249.3)
    text(c, 'AUTOCUSTÓDIA', 46, 45, 66, TEAL, ap(t, 237.8, .3), pop=True)
    text(c, 'O ÚNICO LUGAR ONDE O SEU', 46, 130, 34, INK, ap(t, 239.6))
    text(c, 'DINHEIRO ESTÁ SEGURO', 46, 176, 34, GREEN, ap(t, 241.6))
    check(c, 'Contra o estado', 46, 250, t, 243.6, GREEN, 34)
    check(c, 'Contra o governo', 46, 330, t, 244.7, GREEN, 34)
    check(c, 'Contra tudo', 46, 410, t, 248.6, GREEN, 34)

@scene(249.3, 257.3, 'exploded')
def b20(c, t):
    img3d(c, 'exploded', 720, 300, 460, t, 249.3, 257.3)
    kicker(c, 'AUTOCUSTÓDIA É VOCÊ', 46, 55, TEAL, ap(t, 249.3))
    text(c, 'BLINDANDO', 46, 92, 74, INK, ap(t, 251.7, .3), pop=True)
    text(c, 'O SEU DINHEIRO', 46, 182, 48, TEAL, ap(t, 252.7))
    text(c, 'Aprenda a se defender', 50, 300, 30, GR, ap(t, 255.6), font='m', w=800)

@scene(257.3, 999, None)
def b21(c, t):
    text(c, 'LINK NA BIO', 46, 40, 84, NAVY, ap(t, 257.3, .3), pop=True)
    p = ap(t, 262.2, .35)
    if p > 0:
        b = Image.new('RGBA', (560, 110), (0, 0, 0, 0)); d = ImageDraw.Draw(b)
        d.rounded_rectangle([0, 0, 559, 109], 55, fill=GREEN + (255,))
        d.text((280, 55), 'Aplique-se para a mentoria', font=F(32, 800), fill=WHITE + (255,), anchor='mm')
        pul = 1 + 0.03 * max(0, math.sin((t - 262.2) * 3))
        put(c, b, 46, 170, p, scale=(1 + 0.3 * (1 - p)) * pul)
    text(c, 'Afundar', 46, 330, 60, RED, ap(t, 268.9))
    text(c, 'ou', 300, 344, 40, GR, ap(t, 269.9), w=600)
    text(c, 'SE SALVAR.', 380, 330, 60, GREEN, ap(t, 271.2, .3), pop=True)

# ---------------- layout ----------------
BSTART = 60.3
import eng as _e
def fwd(S):
    for n0, a, b in _e._acc:
        if S <= b: return n0 + max(0, S - a) / SPEED
    return TOTAL
TB = fwd(BSTART)
PX, PY = 54, 230; PS = 1.0
# card A (fase da conversa) e card B (fase escolinha)
CA = dict(y0=0, y1=1920, scale=0.78, top=400)
CB = dict(y0=330, y1=1890, scale=0.695, top=PY + PH + 24)

HEADLINE = [[('A MAIOR CARGA TRIBUTÁRIA', 0)], [('DO MUNDO VAI ', 0), ('AUMENTAR.', RED)], [('PROTEJA O SEU ', 0), ('DINHEIRO.', TEAL)]]
def make_head():
    f = F(46, 800); lay = Image.new('RGBA', (W, 200), (0, 0, 0, 0)); d = ImageDraw.Draw(lay); y = 4
    for ln in HEADLINE:
        tw = sum(d.textlength(s, font=f) + (16 if h else 0) for s, h in ln); x = (W - tw) / 2
        for s, h in ln:
            wd = d.textlength(s, font=f)
            if h:
                d.rounded_rectangle([x - 2, y - 4, x + wd + 14, y + 58], 12, fill=h + (255,)); d.text((x + 6, y), s, font=f, fill=WHITE + (255,)); x += wd + 16
            else:
                d.text((x, y), s, font=f, fill=(246, 241, 232, 255)); x += wd
        y += 64
    sh = Image.new('RGBA', lay.size, (0, 0, 0, 255)); sh.putalpha(lay.getchannel('A').filter(ImageFilter.GaussianBlur(9)).point(lambda v: int(v * .9)))
    out = Image.new('RGBA', lay.size, (0, 0, 0, 0)); out.alpha_composite(sh); out.alpha_composite(lay); return out
HEAD = make_head()

# segmentos de frase para motion control (push-in / pull-out alternado)
TRS = json.load(open(os.path.join(BASE, 'v5', 'tr.json')))
SENT = [(s['s'], s['e']) for s in TRS]
def cam_zoom(S):
    for i, (a, b) in enumerate(SENT):
        if a - 0.6 <= S <= b + 0.6:
            k = max(0, min(1, (S - a) / max(1, b - a)))
            return 1.0 + (0.06 * k if i % 2 == 0 else 0.06 * (1 - k))
    return 1.0

HPS, HPY = 0.82, 410
def hv(T): return 1 - ap(T, 10.0, 0.7)
def pan_geom(T):
    h = hv(T); sc = 1 + (HPS - 1) * h
    top = PY + (HPY - PY) * h
    return top + PH * sc / 2, sc, top + PH * sc
def card_geom(T):
    h = hv(T); _, _, pbot = pan_geom(T)
    g = dict(y0=CB['y0'], y1=CB['y1'])
    g['top'] = pbot + 24
    g['scale'] = min(CB['scale'], (1900 - g['top']) / (CB['y1'] - CB['y0']))
    return g, 1.0

def card_img(frame, T, S, g):
    z = cam_zoom(S)
    ch = (g['y1'] - g['y0']); cw = 1080
    sw, sh = cw / z, ch / z
    fx, fy = 540, 760
    x0 = fx - sw / 2; y0 = g['y0'] + (fy - g['y0']) * (1 - 1 / z)
    x0 = max(0, min(1080 - sw, x0)); y0 = max(0, min(1920 - sh, y0))
    CW, CH = int(1080 * g['scale']), int(ch * g['scale'])
    im = frame.crop((int(x0), int(y0), int(x0 + sw), int(y0 + sh))).resize((CW, CH), Image.BILINEAR).convert('RGBA')
    im.putalpha(corner_mask(CW, CH, 36))
    ImageDraw.Draw(im).rounded_rectangle([1, 1, CW - 2, CH - 2], 36, outline=GOLD + (170,), width=3)
    return im

yy = np.linspace(0, 1, H)[:, None]; xx = np.linspace(-1, 1, W)[None, :]
SHADE = (0.40 - 0.18 * xx ** 2 - 0.10 * np.clip((0.25 - yy) / 0.25, 0, 1) - 0.12 * np.clip((yy - 0.8) / 0.2, 0, 1))[..., None]
def bg_from(frame):
    sm = frame.resize((90, 160), Image.BILINEAR).filter(ImageFilter.GaussianBlur(3)).resize((W, H), Image.BICUBIC)
    a = np.asarray(sm).astype(np.float32) * SHADE * np.array([1.0, 0.94, 0.86]) + np.array([10, 6, 2])
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert('RGBA')

# painel
PMASK = corner_mask(PW, PH, 34)
def draw_scene(sc, S):
    bgc = bgcol(sc[3]) if sc[3] and sc[3] not in DARK else (250, 248, 244)
    pan = Image.new('RGBA', (PW, PH), bgc + (255,))
    sc[2](pan, S)
    pan.putalpha(Image.fromarray(np.minimum(np.asarray(pan.getchannel('A')), np.asarray(PMASK))))
    ImageDraw.Draw(pan).rounded_rectangle([2, 2, PW - 3, PH - 3], 32, outline=GOLD + (170,), width=3)
    return pan

def panel(canvas, T, S, kin):
    if kin <= 0: return
    cur = prev = None
    for i, sc in enumerate(SC):
        if sc[0] <= S < sc[1]: cur = sc; prev = SC[i - 1] if i > 0 else None
    if cur is None: cur = SC[0]
    cx = PX + PW / 2; cy, PSC, _ = pan_geom(T)
    hry = 0.035 * math.sin(T * 0.55) + (1 - ap(T, 0, 0.6)) * -1.0; hrx = 0.025 * math.sin(T * 0.42 + 1.0)
    # sombra
    sh = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ImageDraw.Draw(sh).rounded_rectangle([cx - PW * PSC / 2 + 8, cy - PH * PSC / 2 + 18, cx + PW * PSC / 2 - 8, cy + PH * PSC / 2 + 22], 34, fill=(0, 0, 0, 160))
    canvas.alpha_composite(sh.filter(ImageFilter.GaussianBlur(20)))
    k = (S - cur[0]) / (0.42 * SPEED)
    if prev is not None and k < 1 and kin >= 1:
        e = ease(k)
        if e < 0.5:
            paste_quad(canvas, draw_scene(prev, S), project(PW, PH, cx, cy, hry + 1.45 * (e / 0.5) ** 1.6, hrx, PSC * (1 - 0.06 * e / 0.5)))
        else:
            paste_quad(canvas, draw_scene(cur, S), project(PW, PH, cx, cy, hry - 1.45 * (1 - (e - 0.5) / 0.5) ** 1.6, hrx, PSC * (0.94 + 0.06 * (e - 0.5) / 0.5)))
        return
    paste_quad(canvas, draw_scene(cur, S), project(PW, PH, cx, cy, hry, hrx, PSC * (0.9 + 0.1 * ap(T, 0, 0.6))), min(1, ap(T, 0, 0.4) * 1.5 + 0.01))

# legendas
KEY = {'imposto': RED, 'impostos': RED, 'governo': RED, 'estado': RED, 'banco': NAVY, 'bancária': NAVY, 'bloqueio': RED, 'bloqueado': RED,
       'confiscado': RED, 'monitoramento': RED, 'autocustódia': TEAL, 'custódia': TEAL, 'auto': TEAL, 'bitcoin': BLUE, 'dólar': GREEN, 'real': GREEN,
       'carteira': BLUE, 'sobrevivência': RED, 'descentralizadas': TEAL, 'rede': TEAL, 'financeira': TEAL, 'mentoria': GREEN, 'salvar': GREEN,
       'blindando': TEAL, 'dinheiro': GREEN, 'mundo': RED, 'arrecadação': RED, 'acorda': RED, 'bio': BLUE}
CH = []
cur = []
for a, b, w in WORDS:
    if a < 1.0: continue
    cur.append((a, b, w))
    txt = ' '.join(x[2] for x in cur)
    if len(cur) >= 3 or len(txt) >= 17 or w.endswith(('.', ',', '?', '!')):
        CH.append(cur); cur = []
if cur: CH.append(cur)
CAPS = []
for i, ch in enumerate(CH):
    s0 = ch[0][0]; e0 = ch[-1][1] + 0.25
    if i + 1 < len(CH): e0 = min(max(e0, ch[-1][1]), CH[i + 1][0][0])
    CAPS.append((s0, e0, ch))
_cc = {}
def cap_layer(i):
    if i in _cc: return _cc[i]
    if len(_cc) > 20: _cc.clear()
    ch = CAPS[i][2]; f = F(50, 800); d0 = ImageDraw.Draw(Image.new('RGBA', (1, 1)))
    words = [w for _, _, w in ch]; sp = d0.textlength(' ', font=f)
    tw = sum(d0.textlength(w, font=f) for w in words) + sp * (len(words) - 1)
    lay = Image.new('RGBA', (int(tw) + 30, 80), (0, 0, 0, 0)); d = ImageDraw.Draw(lay); x = 15
    for w in words:
        key = w.lower().strip('.,?!…')
        col = KEY.get(key)
        if col:
            d.text((x, 10), w, font=f, fill=WHITE + (255,), stroke_width=6, stroke_fill=col + (255,))
        else:
            d.text((x, 10), w, font=f, fill=WHITE + (255,), stroke_width=6, stroke_fill=(10, 10, 12, 255))
        x += d0.textlength(w, font=f) + sp
    _cc[i] = lay; return lay

def captions(canvas, S, cy):
    for i, (a, b, ch) in enumerate(CAPS):
        if a <= S < b:
            lay = cap_layer(i); p = ap(S, a, .15)
            sc = 1 + 0.12 * (1 - p)
            l2 = lay.resize((int(lay.width * sc), int(lay.height * sc)), Image.BICUBIC) if sc > 1.005 else lay
            if l2.width > 1040: l2 = l2.resize((1040, int(l2.height * 1040 / l2.width)), Image.BICUBIC)
            canvas.alpha_composite(l2, (int((W - l2.width) / 2), int(cy - l2.height / 2)))
            return

def frame(fr, T):
    S = src_t(T)
    canvas = bg_from(fr)
    g, kin = card_geom(T)
    im = card_img(fr, T, S, g)
    sh = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([(W - im.width) / 2 + 8, g['top'] + 18, (W + im.width) / 2 - 8, g['top'] + im.height + 24], 36, fill=(0, 0, 0, 170))
    canvas.alpha_composite(sh.filter(ImageFilter.GaussianBlur(20)))
    ry = 0.025 * math.sin(T * 0.37 + 2.0); rx = 0.015 * math.sin(T * 0.29)
    paste_quad(canvas, im, project(im.width, im.height, W / 2, g['top'] + im.height / 2, ry, rx, 1.0 + 0.01 * math.sin(T * 0.21)))
    panel(canvas, T, S, kin)
    if T < 10.6:
        p = 1 - ap(T, 10.0, 0.5)
        h = HEAD if p >= 1 else HEAD.copy()
        if p < 1: h.putalpha(h.getchannel('A').point(lambda v: int(v * p)))
        if T < 0.6:
            q = ap(T, 0.0, 0.6); h = h.resize((int(W * (1 + 0.15 * (1 - q))), int(200 * (1 + 0.15 * (1 - q)))), Image.BICUBIC)
            h.putalpha(h.getchannel('A').point(lambda v: int(v * q)))
        canvas.alpha_composite(h, (int((W - h.width) / 2), int(196 - (h.height - 200) / 2)))
    cap_src = 1205
    cy = g['top'] + (cap_src - g['y0']) * g['scale']
    captions(canvas, S, cy)
    return canvas

def render(T0, T1, out):
    n = int(round((T1 - T0) * FPS))
    dec = subprocess.Popen(['ffmpeg', '-v', 'error', '-ss', f'{T0:.4f}', '-i', os.path.join(BASE, 'v5', 'base.mov'), '-frames:v', str(n), '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
    enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                            '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
    for i in range(n):
        raw = dec.stdout.read(W * H * 3)
        if len(raw) < W * H * 3: break
        fr = Image.frombuffer('RGB', (W, H), raw)
        enc.stdin.write(frame(fr, T0 + i / FPS).convert('RGB').tobytes())
        if i % 150 == 0: print(out, i, n, flush=True)
    enc.stdin.close(); enc.wait(); dec.wait()

def grab(T):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-ss', str(T), '-i', os.path.join(BASE, 'v5', 'base.mov'), '-frames:v', '1', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], capture_output=True).stdout
    return Image.frombuffer('RGB', (W, H), raw)

if __name__ == '__main__':
    if sys.argv[1] == 'still':
        for ts in sys.argv[2:]:
            T = float(ts); frame(grab(T), T).convert('RGB').save(os.path.join(BASE, 'v5', f's_{ts}.png'))
    elif sys.argv[1] == 'info':
        print('TOTAL', TOTAL, 'TB', TB)
    else:
        render(float(sys.argv[1]), float(sys.argv[2]), sys.argv[3])
