#!/usr/bin/env python3
"""Editor 3 defibit — reels no formato "explicativo animado" com a identidade Dani Sanverino.

Formato: painel animado em cima (kicker + título + visual), legenda palavra a palavra
com destaque dourado no meio, rosto da Dani num card arredondado embaixo. CTA final
com o rosto em tela cheia e uma caixa de comentário digitando a palavra-chave.

Fluxo (os dois GATES continuam valendo — nada de render completo sem aprovação):

  python editor3.py preparar  PROJETO/bruto.mp4      # CFR + corta pausas + transcreve
  python editor3.py rascunho  PROJETO                # gera edit/cenas.json para revisar  [GATE 1]
  python editor3.py render    PROJETO --ate 15       # piloto de 15s                      [GATE 2]
  python editor3.py render    PROJETO                # vídeo final
  python editor3.py conferir  PROJETO                # grade de frames para inspeção

Todas as saídas ficam em PROJETO/edit/. O bruto nunca é sobrescrito.
"""
import argparse
import json
import math
import re
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, str(Path(__file__).parent))
import estilo as E  # noqa: E402

FFMPEG = shutil.which("ffmpeg") or "ffmpeg"
FFPROBE = shutil.which("ffprobe") or "ffprobe"


# =====================================================================
# utilidades
# =====================================================================
def rodar(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"Falhou: {' '.join(map(str, cmd))}\n{r.stderr[-2000:]}")
    return r.stdout


def sonda(video):
    out = rodar([FFPROBE, "-v", "error", "-select_streams", "v:0", "-show_entries",
                 "stream=width,height:format=duration", "-of", "json", str(video)])
    d = json.loads(out)
    s = d["streams"][0]
    return int(s["width"]), int(s["height"]), float(d["format"]["duration"])


def audio_pcm(video, sr=16000):
    raw = subprocess.run([FFMPEG, "-v", "error", "-i", str(video), "-ac", "1", "-ar", str(sr),
                          "-f", "f32le", "-"], capture_output=True).stdout
    return np.frombuffer(raw, dtype=np.float32)


def suave(p):
    """ease-out cúbico, p em [0,1]."""
    p = min(max(p, 0.0), 1.0)
    return 1 - (1 - p) ** 3


def entra(tl, atraso=0.0, dur=0.45):
    return suave((tl - atraso) / dur)


def pasta_edit(projeto):
    p = Path(projeto)
    if p.is_file():
        p = p.parent
    (p / "edit").mkdir(parents=True, exist_ok=True)
    return p / "edit"


# =====================================================================
# FASE 0/1 — preparar: CFR, transcrição palavra a palavra, corte de pausas
# =====================================================================
def transcrever(video, modelo="small"):
    from faster_whisper import WhisperModel
    a = audio_pcm(video)
    m = WhisperModel(modelo, device="cpu", compute_type="int8")
    segs, _ = m.transcribe(a, language="pt", word_timestamps=True, vad_filter=True)
    palavras = []
    for s in segs:
        for w in s.words:
            t = w.word.strip()
            if t:
                palavras.append({"w": t, "s": round(w.start, 3), "e": round(w.end, 3)})
    return palavras


def intervalos_fala(palavras, dur, max_pausa=0.5, folga=0.12):
    """Trechos a manter: fala com folga; pausas maiores que max_pausa são encurtadas."""
    trechos = []
    for w in palavras:
        a, b = max(0.0, w["s"] - folga), min(dur, w["e"] + folga)
        if trechos and a - trechos[-1][1] <= max_pausa - 2 * folga:
            trechos[-1][1] = max(trechos[-1][1], b)
        else:
            trechos.append([a, b])
    return trechos


def cortar(video, trechos, saida):
    partes, rot = [], []
    for i, (a, b) in enumerate(trechos):
        f = 0.03
        partes.append(f"[0:v]trim={a:.3f}:{b:.3f},setpts=PTS-STARTPTS[v{i}];")
        partes.append(f"[0:a]atrim={a:.3f}:{b:.3f},asetpts=PTS-STARTPTS,"
                      f"afade=t=in:d={f},afade=t=out:st={max(0, b - a - f):.3f}:d={f}[a{i}];")
        rot.append(f"[v{i}][a{i}]")
    fc = "".join(partes) + "".join(rot) + f"concat=n={len(trechos)}:v=1:a=1[v][a]"
    script = Path(saida).with_suffix(".filtro.txt")
    script.write_text(fc, encoding="utf-8")
    rodar([FFMPEG, "-v", "error", "-y", "-i", str(video), "-filter_complex_script", str(script),
           "-map", "[v]", "-map", "[a]", "-r", str(E.FPS), "-c:v", "libx264", "-crf", "18",
           "-preset", "medium", "-c:a", "aac", "-b:a", "192k", str(saida)])
    script.unlink()


def remapear(palavras, trechos):
    out, base = [], 0.0
    for a, b in trechos:
        for w in palavras:
            if a <= w["s"] < b:
                out.append({"w": w["w"], "s": round(base + w["s"] - a, 3),
                            "e": round(base + min(w["e"], b) - a, 3)})
        base += b - a
    return out


def cmd_preparar(args):
    bruto = Path(args.bruto)
    ed = pasta_edit(bruto)
    cfr = ed / "bruto_cfr.mp4"
    print("1/3 normalizando para 30fps constante...")
    rodar([FFMPEG, "-v", "error", "-y", "-i", str(bruto), "-vf", f"fps={E.FPS}", "-c:v", "libx264",
           "-crf", "18", "-preset", "medium", "-c:a", "aac", "-ar", "48000", "-b:a", "192k", str(cfr)])
    print(f"2/3 transcrevendo (whisper {args.modelo})...")
    palavras = transcrever(cfr, args.modelo)
    _, _, dur = sonda(cfr)
    final = ed / "video.mp4"
    if args.sem_cortes:
        shutil.copy(cfr, final)
    else:
        print("3/3 removendo pausas longas...")
        trechos = intervalos_fala(palavras, dur, args.max_pausa)
        cortar(cfr, trechos, final)
        palavras = remapear(palavras, trechos)
        _, _, nova = sonda(final)
        print(f"    {dur:.1f}s -> {nova:.1f}s ({len(trechos)} trechos)")
    (ed / "palavras.json").write_text(json.dumps(palavras, ensure_ascii=False, indent=1), "utf-8")
    texto = " ".join(w["w"] for w in palavras)
    (ed / "transcricao.txt").write_text(texto, "utf-8")
    print(f"\nPronto: {final}\nTranscrição: {ed / 'transcricao.txt'}\n"
          f"Corrija palavras erradas em {ed / 'palavras.json'} (ou use \"correcoes\" no cenas.json).\n"
          f"Tomadas repetidas: confira a transcrição — a regra é manter SEMPRE a última.")


# =====================================================================
# GATE 1 — rascunho de cenas a partir da transcrição
# =====================================================================
NUM = re.compile(r"\d+(?:[.,]\d+)?")


def frases(palavras):
    atual, todas = [], []
    for w in palavras:
        atual.append(w)
        if re.search(r"[.!?]$", w["w"]):
            todas.append(atual)
            atual = []
    if atual:
        todas.append(atual)
    # junta frases curtas (< 1.8s) com a seguinte
    juntas = []
    for f in todas:
        if juntas and (juntas[-1][-1]["e"] - juntas[-1][0]["s"]) < 1.8:
            juntas[-1] += f
        else:
            juntas.append(f)
    return juntas


def titulo_de(texto, n=6):
    pal = re.sub(r"[,;:]", "", texto).upper().split()[:n]
    meio = (len(pal) + 1) // 2
    return [" ".join(pal[:meio]), " ".join(pal[meio:])] if len(pal) > 3 else [" ".join(pal)]


def cmd_rascunho(args):
    ed = pasta_edit(args.projeto)
    palavras = json.loads((ed / "palavras.json").read_text("utf-8"))
    _, _, dur = sonda(ed / "video.mp4")
    fs = frases(palavras)
    cenas = []
    for i, f in enumerate(fs):
        texto = " ".join(w["w"] for w in f)
        ini = 0.0 if i == 0 else f[0]["s"]
        cena = {"inicio": round(ini, 2), "fim": None, "falado": texto,
                "kicker": "EDITE O KICKER", "titulo": titulo_de(texto)}
        m = NUM.search(texto)
        cta = re.search(r"coment\w*\s+[\"“]?([\wÀ-ú]+)", texto, re.I)
        if i == len(fs) - 1 and cta:
            cena.update(tipo="cta", kicker="RECEBA O PASSO A PASSO",
                        titulo=["COMENTA", cta.group(1).upper()], palavra=cta.group(1).upper())
        elif m:
            cena.update(tipo="numero", numero=m.group(0), rotulo="EDITE O RÓTULO")
        else:
            cena.update(tipo="titulo")
        cenas.append(cena)
    for a, b in zip(cenas, cenas[1:]):
        a["fim"] = b["inicio"]
    if cenas:
        cenas[-1]["fim"] = round(dur, 2)
    doc = {
        "video": "video.mp4",
        "foco_y": 0.42,
        "correcoes": {},
        "cenas": cenas,
    }
    destino = ed / "cenas.json"
    if destino.exists() and not args.sobrescrever:
        destino = ed / "cenas.rascunho.json"
    destino.write_text(json.dumps(doc, ensure_ascii=False, indent=2), "utf-8")
    print(f"Rascunho salvo em {destino}\n")
    print(f"{'#':>2}  {'início':>6}  {'fim':>6}  {'tipo':<10} falado")
    for i, c in enumerate(cenas):
        print(f"{i:>2}  {c['inicio']:>6.2f}  {c['fim']:>6.2f}  {c['tipo']:<10} {c['falado'][:70]}")
    print("\nGATE 1: revise títulos, kickers e tipos de cada cena e aprove antes do render.")


# =====================================================================
# desenho
# =====================================================================
def largura(draw, txt, f, tracking=0):
    return draw.textlength(txt, font=f) + tracking * max(0, len(txt) - 1)


def texto_tracking(draw, xy, txt, f, cor, tracking=0):
    x, y = xy
    if not tracking:
        draw.text((x, y), txt, font=f, fill=cor)
        return
    for ch in txt:
        draw.text((x, y), ch, font=f, fill=cor)
        x += draw.textlength(ch, font=f) + tracking


def com_alfa(cor, a):
    return tuple(cor[:3]) + (int(255 * max(0, min(1, a))),)


def fundo_base():
    """Fundo escuro com gradiente quente, brilho dourado e grade fina."""
    y = np.linspace(0, 1, E.H)[:, None]
    x = np.linspace(0, 1, E.W)[None, :]
    base = np.array(E.FUNDO, float)
    quente = np.array(E.FUNDO_2, float)
    mix = (0.55 * (1 - y) + 0.25 * x)[..., None]
    img = base * (1 - mix) + quente * mix
    # brilho dourado no canto superior direito
    d = np.sqrt((x - 0.85) ** 2 + ((y - 0.08) * 1.7) ** 2)
    glow = np.clip(1 - d / 0.55, 0, 1)[..., None] ** 2 * 0.10
    img = img * (1 - glow) + np.array(E.DOURADO, float) * glow
    im = Image.fromarray(img.clip(0, 255).astype(np.uint8)).convert("RGBA")
    grade = Image.new("RGBA", (E.W, E.H), (0, 0, 0, 0))
    g = ImageDraw.Draw(grade)
    for gx in range(0, E.W, 54):
        g.line([(gx, 0), (gx, E.H)], fill=E.GRADE, width=1)
    for gy in range(0, E.H, 54):
        g.line([(0, gy), (E.W, gy)], fill=E.GRADE, width=1)
    im.alpha_composite(grade)
    return im


def caixa_ouro(draw, box, raio=18, a=1.0, largura_borda=4, brilho=True):
    x0, y0, x1, y1 = box
    draw.rounded_rectangle(box, radius=raio, fill=com_alfa((20, 18, 14), 0.92 * a))
    draw.rounded_rectangle(box, radius=raio, outline=com_alfa(E.DOURADO, a), width=largura_borda)
    if brilho:
        draw.rounded_rectangle((x0 + 10, y0 + 10, x1 - 10, y1 - 10), radius=max(4, raio - 8),
                               outline=com_alfa(E.DOURADO, 0.18 * a), width=2)


def ajustar_fonte(draw, linhas, nome, maximo, largura_max, minimo=40):
    t = maximo
    while t > minimo and max(largura(draw, l, E.fonte(nome, t)) for l in linhas) > largura_max:
        t -= 2
    return E.fonte(nome, t), t


class Painel:
    """Desenha a parte de cima (kicker, título e visual) de uma cena."""

    DINAMICOS = {"numero", "onda", "imagem"}

    def __init__(self, cena, projeto_dir, envelope, base_img):
        self.c = cena
        self.dir = projeto_dir
        self.env = envelope
        self.cache = None
        self.imgs = []
        for p in cena.get("imagens", []) or ([cena["imagem"]] if cena.get("imagem") else []):
            caminho = (projeto_dir / p) if not Path(p).is_absolute() else Path(p)
            self.imgs.append(Image.open(caminho).convert("RGB"))

    # ---- texto comum ----
    def cabecalho(self, d, tl, topo=None):
        c = self.c
        y = E.KICKER_Y if topo is None else topo
        if c.get("kicker"):
            a = entra(tl, 0.0, 0.35)
            texto_tracking(d, (E.MARGEM_X, y - 16 * (1 - a)), c["kicker"].upper(),
                           E.fonte("semi", 30), com_alfa(E.DOURADO, a), tracking=4)
        linhas = c.get("titulo") or []
        if isinstance(linhas, str):
            linhas = [linhas]
        if not linhas:
            return y + 50
        maxi = c.get("tamanho_titulo", 96 if c.get("tipo") != "cta" else 104)
        f, t = ajustar_fonte(d, linhas, "titulo", maxi, E.W - 2 * E.MARGEM_X)
        douradas = c.get("dourado", [len(linhas) - 1] if len(linhas) > 1 else [])
        ty = y + 50
        for i, l in enumerate(linhas):
            a = entra(tl, 0.08 + 0.12 * i, 0.4)
            cor = E.DOURADO if i in douradas else E.BRANCO
            tam = t
            if c.get("tipo") == "cta" and i in douradas:
                f2, tam = ajustar_fonte(d, [l], "titulo", int(t * 1.45), E.W - 2 * E.MARGEM_X)
            else:
                f2 = f
            d.text((E.MARGEM_X, ty + 30 * (1 - a)), l, font=f2, fill=com_alfa(cor, a))
            ty += int(tam * 1.06)
        return ty

    def nota(self, d, tl, y):
        txt = self.c.get("nota")
        if not txt:
            return
        a = entra(tl, 0.5, 0.4)
        f = E.fonte("forte", 40)
        linhas = quebrar(d, txt, f, E.W - 2 * E.MARGEM_X - 60)
        h = 30 + 50 * len(linhas)
        box = (E.MARGEM_X, y + 20 * (1 - a), E.W - E.MARGEM_X, y + h + 20 * (1 - a))
        d.rounded_rectangle(box, radius=18, fill=com_alfa(E.DOURADO, a))
        for i, l in enumerate(linhas):
            d.text((box[0] + 30, box[1] + 16 + 50 * i), l, font=f, fill=com_alfa(E.TEXTO_ESCURO, a))

    # ---- visuais por tipo ----
    def v_titulo(self, d, tl, layer):
        g = self.c.get("grande")
        if g:
            a = entra(tl, 0.25, 0.5)
            f, t = ajustar_fonte(d, [g], "titulo", 170, E.W - 2 * E.MARGEM_X)
            w = largura(d, g, f)
            x = (E.W - w) / 2
            y = (E.VISUAL_TOPO + E.VISUAL_BASE) / 2 - t * 0.75
            d.text((x, y + 30 * (1 - a)), g, font=f, fill=com_alfa(E.BRANCO, a))
            sub = entra(tl, 0.55, 0.5)
            d.rounded_rectangle((x, y + t * 1.25, x + w * sub, y + t * 1.25 + 12), radius=6,
                                fill=com_alfa(E.DOURADO, a))
        self.nota(d, tl, E.VISUAL_BASE - 130)

    def v_numero(self, d, tl, layer):
        c = self.c
        bruto = str(c.get("numero", "0"))
        alvo = float(bruto.replace(".", "").replace(",", ".")) if NUM.fullmatch(bruto) else None
        decimais = len(bruto.split(",")[1]) if "," in bruto else 0
        p = suave((tl - 0.2) / 0.9)
        if alvo is not None:
            val = alvo * p
            txt = f"{val:,.{decimais}f}".replace(",", "X").replace(".", ",").replace("X", ".")
        else:
            txt = bruto
        f = E.fonte("titulo", c.get("tamanho_numero", 230))
        a = entra(tl, 0.1, 0.3)
        y = E.VISUAL_TOPO + 10
        d.text((E.MARGEM_X - 6, y), txt + c.get("sufixo", ""), font=f, fill=com_alfa(E.DOURADO, a))
        wnum = largura(d, bruto + c.get("sufixo", ""), f)
        rot = c.get("rotulo", "")
        if rot:
            ar = entra(tl, 0.5, 0.4)
            fr = E.fonte("forte", 52)
            if E.MARGEM_X + wnum + 30 + largura(d, rot, fr) < E.W - E.MARGEM_X:
                d.text((E.MARGEM_X + wnum + 26, y + 150), rot, font=fr, fill=com_alfa(E.BRANCO, ar))
            else:
                d.text((E.MARGEM_X, y + 260), rot, font=fr, fill=com_alfa(E.BRANCO, ar))
        sub = c.get("sub")
        if sub:
            asb = entra(tl, 0.8, 0.4)
            d.text((E.MARGEM_X, y + 340), sub.upper(), font=E.fonte("semi", 40), fill=com_alfa(E.CINZA, asb))
        self.nota(d, tl, E.VISUAL_BASE - 130)

    def v_lista(self, d, tl, layer):
        itens = self.c.get("itens", [])
        f = E.fonte("forte", 46)
        gap = 22
        area = E.VISUAL_BASE - E.VISUAL_TOPO - 20
        h = min(104, (area - gap * (len(itens) - 1)) / max(1, len(itens)))
        f = E.fonte("forte", int(min(46, h * 0.45)))
        total = len(itens) * h + (len(itens) - 1) * gap
        y = (E.VISUAL_TOPO + E.VISUAL_BASE) / 2 - total / 2
        passo = self.c.get("intervalo", 0.35)
        for i, it in enumerate(itens):
            a = entra(tl, 0.3 + passo * i, 0.35)
            if a <= 0:
                continue
            x0 = E.MARGEM_X + 40 * (1 - a)
            box = (x0, y, E.W - E.MARGEM_X, y + h)
            d.rounded_rectangle(box, radius=18, fill=com_alfa((28, 25, 19), 0.95 * a),
                                outline=com_alfa(E.DOURADO, 0.35 * a), width=2)
            cx, cy = x0 + 56, y + h / 2
            d.ellipse((cx - 26, cy - 26, cx + 26, cy + 26), fill=com_alfa(E.DOURADO, a))
            d.line([(cx - 12, cy), (cx - 3, cy + 10), (cx + 13, cy - 10)],
                   fill=com_alfa(E.TEXTO_ESCURO, a), width=7, joint="curve")
            d.text((x0 + 106, cy - f.size * 0.6), it.upper(), font=f, fill=com_alfa(E.BRANCO, a))
            y += h + gap

    def v_comparacao(self, d, tl, layer):
        c = self.c
        cy = (E.VISUAL_TOPO + E.VISUAL_BASE) / 2
        a1 = entra(tl, 0.2, 0.4)
        box = (E.MARGEM_X, cy - 160, E.MARGEM_X + 330, cy + 160)
        caixa_ouro(d, box, raio=22, a=a1)
        fa = E.fonte("forte", 46)
        lin = quebrar(d, c.get("a", ""), fa, 280)
        for i, l in enumerate(lin):
            w = largura(d, l, fa)
            d.text(((box[0] + box[2]) / 2 - w / 2, cy - 30 * len(lin) + 60 * i), l, font=fa,
                   fill=com_alfa(E.BRANCO, a1))
        p = entra(tl, 0.55, 0.4)
        x0, x1 = box[2] + 40, box[2] + 40 + 150 * p
        if p > 0:
            d.line([(x0, cy), (x1, cy)], fill=com_alfa(E.BRANCO, p), width=8)
            d.polygon([(x1 + 4, cy), (x1 - 22, cy - 20), (x1 - 22, cy + 20)], fill=com_alfa(E.BRANCO, p))
        a2 = entra(tl, 0.85, 0.4)
        fb = E.fonte("titulo", 170)
        bx = box[2] + 230
        d.text((bx, cy - 150 + 30 * (1 - a2)), c.get("b", ""), font=fb, fill=com_alfa(E.DOURADO, a2))
        if c.get("rotulo_b"):
            d.text((bx + 6, cy + 50), c["rotulo_b"], font=E.fonte("forte", 50), fill=com_alfa(E.BRANCO, a2))

    def v_imagem(self, d, tl, layer):
        if not self.imgs:
            return
        troca = self.c.get("troca", 0.4)
        idx = min(int(tl / troca), len(self.imgs) - 1) if len(self.imgs) > 1 else 0
        if len(self.imgs) > 1 and self.c.get("repetir", True):
            idx = int(tl / troca) % len(self.imgs)
        im = self.imgs[idx]
        a = entra(tl, 0.1, 0.35)
        bw, bh = self.c.get("largura_card", 560), E.VISUAL_BASE - E.VISUAL_TOPO - 20
        cx = E.W / 2 if self.c.get("centro", True) else E.MARGEM_X + bw / 2
        x0, y0 = int(cx - bw / 2), int(E.VISUAL_TOPO - 20 + 30 * (1 - a))
        dur = max(0.1, self.c["fim"] - self.c["inicio"])
        z = 1.0 + 0.08 * (tl / dur)
        foto = cobrir(im, bw - 24, bh - 24, z)
        mask = Image.new("L", foto.size, 0)
        ImageDraw.Draw(mask).rounded_rectangle((0, 0, *foto.size), radius=14, fill=int(255 * a))
        caixa_ouro(d, (x0, y0, x0 + bw, y0 + bh), raio=22, a=a)
        layer.paste(foto.convert("RGBA"), (x0 + 12, y0 + 12), mask)

    def v_onda(self, d, tl, layer, t_global=0.0):
        c = self.c
        a = entra(tl, 0.1, 0.35)
        y = E.VISUAL_TOPO
        if c.get("rotulo"):
            d.text((E.MARGEM_X, y), c["rotulo"], font=E.fonte("titulo", 64), fill=com_alfa(E.BRANCO, a))
        cy = y + 210
        n, bw, gap = 64, 9, 5
        x = E.MARGEM_X
        env = self.env
        i0 = int(t_global * E.FPS)
        for k in range(n):
            j = i0 - (n - k) // 2
            v = env[j] if 0 <= j < len(env) else 0.0
            h = 10 + 150 * v * (0.6 + 0.4 * math.sin(k * 1.7) ** 2)
            d.rounded_rectangle((x, cy - h / 2, x + bw, cy + h / 2), radius=4, fill=com_alfa(E.DOURADO, a))
            x += bw + gap
        self.nota(d, tl, E.VISUAL_BASE - 130)

    def desenhar(self, tl, t_global):
        tipo = self.c.get("tipo", "titulo")
        estatico = tipo not in self.DINAMICOS and tl > 2.5
        if estatico and self.cache is not None:
            return self.cache
        layer = Image.new("RGBA", (E.W, E.VISUAL_BASE + 60), (0, 0, 0, 0))
        d = ImageDraw.Draw(layer)
        self.cabecalho(d, tl)
        if tipo == "onda":
            self.v_onda(d, tl, layer, t_global)
        else:
            getattr(self, f"v_{tipo}", self.v_titulo)(d, tl, layer)
        if estatico:
            self.cache = layer
        return layer


def quebrar(d, txt, f, wmax):
    linhas, atual = [], ""
    for p in txt.split():
        t = (atual + " " + p).strip()
        if largura(d, t, f) <= wmax or not atual:
            atual = t
        else:
            linhas.append(atual)
            atual = p
    if atual:
        linhas.append(atual)
    return linhas


def cobrir(im, w, h, zoom=1.0, foco_y=0.5):
    """Recorte central (sem distorcer) no aspecto w:h, com zoom (punch-in)."""
    sw, sh = im.size
    cw = sw / zoom
    ch = cw * h / w
    if ch > sh / zoom:
        ch = sh / zoom
        cw = ch * w / h
    cx = sw / 2
    cy = min(max(foco_y * sh, ch / 2), sh - ch / 2)
    box = (cx - cw / 2, cy - ch / 2, cx + cw / 2, cy + ch / 2)
    return im.resize((w, h), Image.BILINEAR, box=box)


# =====================================================================
# legendas
# =====================================================================
def blocos_legenda(palavras, correcoes, max_pal=4, wmax=900):
    d = ImageDraw.Draw(Image.new("RGB", (8, 8)))
    f = E.fonte("legenda", 54)
    blocos, atual = [], []

    def fecha():
        if atual:
            blocos.append(list(atual))
            atual.clear()

    for i, w in enumerate(palavras):
        txt = correcoes.get(w["w"], correcoes.get(w["w"].strip(".,!?;:"), None))
        if txt is not None and txt != w["w"]:
            pont = w["w"][len(w["w"].rstrip(".,!?;:")):]
            w = dict(w, w=txt + (pont if not txt.endswith(pont) else ""))
        if atual:
            prev = atual[-1]
            linha = " ".join(x["w"] for x in atual + [w])
            if (len(atual) >= max_pal or re.search(r"[.!?,;:]$", prev["w"])
                    or w["s"] - prev["e"] > 0.4 or largura(d, linha, f) > wmax):
                fecha()
        atual.append(w)
    fecha()
    out = []
    for i, b in enumerate(blocos):
        fim = blocos[i + 1][0]["s"] if i + 1 < len(blocos) else b[-1]["e"] + 0.4
        fim = min(fim, b[-1]["e"] + 0.6)
        out.append({"s": b[0]["s"], "e": fim, "pal": b})
    return out


def desenhar_legenda(frame, bloco, t, cy):
    d = ImageDraw.Draw(frame)
    f = E.fonte("legenda", 54)
    esp = 18
    pal = bloco["pal"]
    ws = [largura(d, w["w"], f) for w in pal]
    total = sum(ws) + esp * (len(pal) - 1)
    padx, alt = 22, 84
    x0 = (E.W - total) / 2
    d.rounded_rectangle((x0 - padx, cy - alt / 2, x0 + total + padx, cy + alt / 2), radius=14,
                        fill=(13, 13, 13, 225))
    ativa = max([i for i, w in enumerate(pal) if w["s"] <= t + 0.02] or [0])
    x = x0
    for i, (w, lw) in enumerate(zip(pal, ws)):
        if i == ativa:
            d.rounded_rectangle((x - 8, cy - 33, x + lw + 8, cy + 33), radius=8, fill=E.DOURADO + (255,))
            d.text((x, cy - 32), w["w"], font=f, fill=E.TEXTO_ESCURO)
        else:
            d.text((x, cy - 32), w["w"], font=f, fill=E.BRANCO)
        x += lw + esp


# =====================================================================
# CTA
# =====================================================================
def caixa_comentario(frame, tl, palavra):
    d = ImageDraw.Draw(frame)
    a = entra(tl, 0.6, 0.35)
    if a <= 0:
        return
    x0, x1 = 66, E.W - 66
    y0 = 1060 + 40 * (1 - a)
    y1 = y0 + 236
    d.rounded_rectangle((x0, y0, x1, y1), radius=26, fill=(255, 255, 255, int(250 * a)))
    ft = E.fonte("forte", 32)
    d.text((x0 + 30, y0 + 26), "Comentários", font=ft, fill=(20, 20, 20, int(255 * a)))
    d.line([(x0 + 30, y0 + 84), (x1 - 30, y0 + 84)], fill=(225, 225, 225, int(255 * a)), width=2)
    cy = y0 + 140
    d.ellipse((x0 + 30, cy - 30, x0 + 90, cy + 30), fill=E.DOURADO + (int(255 * a),))
    d.text((x0 + 41, cy - 17), "DS", font=E.fonte("forte", 28), fill=(13, 13, 13, int(255 * a)))
    d.rounded_rectangle((x0 + 110, cy - 32, x1 - 160, cy + 32), radius=32,
                        outline=(210, 210, 210, int(255 * a)), width=2)
    n = int(max(0, (tl - 1.0) / 0.09))
    digitado = palavra[:n]
    if digitado:
        d.text((x0 + 136, cy - 20), digitado, font=E.fonte("forte", 34), fill=(13, 13, 13, int(255 * a)))
        cursor_x = x0 + 136 + largura(d, digitado, E.fonte("forte", 34)) + 4
    else:
        d.text((x0 + 136, cy - 18), "Adicione um comentário...", font=E.fonte("semi", 30),
               fill=(150, 150, 150, int(255 * a)))
        cursor_x = x0 + 132
    if int(tl * 2) % 2 == 0:
        d.line([(cursor_x, cy - 22), (cursor_x, cy + 22)], fill=(13, 13, 13, int(255 * a)), width=3)
    pub = (E.DOURADO if n >= len(palavra) else (190, 170, 110))
    d.text((x1 - 140, cy - 18), "Publicar", font=E.fonte("forte", 32), fill=pub + (int(255 * a),))
    d.text((x0 + 30, y0 + 190), "Comente a palavra · receba no Direct", font=E.fonte("semi", 28),
           fill=(110, 110, 110, int(255 * a)))


# =====================================================================
# render
# =====================================================================
def envelope_audio(video):
    a = audio_pcm(video, 16000)
    passo = 16000 // E.FPS
    n = len(a) // passo
    rms = np.sqrt((a[: n * passo].reshape(n, passo) ** 2).mean(axis=1))
    rms = rms / (np.percentile(rms, 98) + 1e-6)
    return np.clip(rms, 0, 1)


def cmd_render(args):
    ed = pasta_edit(args.projeto)
    proj_dir = ed.parent
    doc = json.loads((ed / args.cenas).read_text("utf-8"))
    video = ed / doc.get("video", "video.mp4")
    palavras = json.loads((ed / "palavras.json").read_text("utf-8"))
    sw, sh, dur = sonda(video)
    if args.ate:
        dur = min(dur, args.ate)
    cenas = sorted(doc["cenas"], key=lambda c: c["inicio"])
    for a, b in zip(cenas, cenas[1:]):
        a.setdefault("fim", b["inicio"])
        if a["fim"] is None:
            a["fim"] = b["inicio"]
    if cenas and cenas[-1].get("fim") is None:
        cenas[-1]["fim"] = dur
    foco_y = doc.get("foco_y", 0.42)
    legendas = blocos_legenda(palavras, doc.get("correcoes", {}))
    env = envelope_audio(video)
    base = fundo_base()
    rodape = Image.new("RGBA", (E.W, E.H), (0, 0, 0, 0))
    texto_tracking(ImageDraw.Draw(rodape), (E.MARGEM_X, E.RODAPE_Y), E.ASSINATURA,
                   E.fonte("semi", 26), E.CINZA + (255,), tracking=3)
    base.alpha_composite(rodape)
    bx0, by0, bx1, by1 = E.ROSTO_BOX
    bw, bh = bx1 - bx0, by1 - by0
    mask_rosto = Image.new("L", (bw, bh), 0)
    ImageDraw.Draw(mask_rosto).rounded_rectangle((0, 0, bw, bh), radius=E.ROSTO_RAIO, fill=255)
    sombra = Image.new("RGBA", (E.W, E.H), (0, 0, 0, 0))
    ImageDraw.Draw(sombra).rounded_rectangle((bx0 + 4, by0 + 12, bx1 + 4, by1 + 16), radius=E.ROSTO_RAIO,
                                             fill=(0, 0, 0, 150))
    base.alpha_composite(sombra.filter(ImageFilter.GaussianBlur(18)))
    topo_cta = Image.new("RGBA", (E.W, E.H), (0, 0, 0, 0))
    grad = np.zeros((E.H, E.W, 4), np.uint8)
    yy = np.arange(E.H)[:, None]
    grad[..., 3] = np.clip(235 * (1 - yy / 760), 0, 235).astype(np.uint8)
    grad[..., :3] = E.FUNDO
    topo_cta = Image.fromarray(grad, "RGBA")
    base_cta = np.zeros((E.H, E.W, 4), np.uint8)
    base_cta[..., 3] = np.clip(200 * (yy - 1650) / 270, 0, 200).astype(np.uint8)
    topo_cta.alpha_composite(Image.fromarray(base_cta, "RGBA"))
    lema = Image.new("RGBA", (E.W, E.H), (0, 0, 0, 0))
    dl = ImageDraw.Draw(lema)
    fl = E.fonte("semi", 26)
    texto_tracking(dl, ((E.W - largura(dl, E.LEMA, fl, 3)) / 2, E.RODAPE_Y), E.LEMA, fl,
                   E.DOURADO + (230,), tracking=3)
    topo_cta.alpha_composite(lema)

    paineis = [Painel(c, proj_dir, env, base) for c in cenas]
    saida = ed / (args.saida or ("piloto.mp4" if args.ate else "final.mp4"))
    dec = subprocess.Popen([FFMPEG, "-v", "error", "-i", str(video), "-t", f"{dur:.3f}", "-r", str(E.FPS),
                            "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    enc = subprocess.Popen([FFMPEG, "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
                            "-s", f"{E.W}x{E.H}", "-r", str(E.FPS), "-i", "-", "-i", str(video),
                            "-map", "0:v", "-map", "1:a", "-t", f"{dur:.3f}",
                            "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-c:v", "libx264", "-crf", "18",
                            "-preset", "medium", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
                            "-ar", "48000", "-movflags", "+faststart", str(saida)], stdin=subprocess.PIPE)
    nbytes = sw * sh * 3
    total = int(dur * E.FPS)
    ci = 0
    li = 0
    for n in range(total):
        buf = dec.stdout.read(nbytes)
        if len(buf) < nbytes:
            break
        t = n / E.FPS
        src = Image.frombuffer("RGB", (sw, sh), buf, "raw", "RGB", 0, 1)
        while ci + 1 < len(cenas) and t >= cenas[ci + 1]["inicio"]:
            ci += 1
        cena, painel = cenas[ci], paineis[ci]
        tl = t - cena["inicio"]
        cdur = max(0.1, cena["fim"] - cena["inicio"])
        # punch-in alternado por cena + leve deriva (nunca plano parado)
        z0 = cena.get("zoom", 1.0 if ci % 2 == 0 else 1.12)
        zoom = z0 + 0.04 * min(1, tl / cdur)
        if cena.get("tipo") == "cta":
            frame = cobrir(src, E.W, E.H, zoom, foco_y).convert("RGBA")
            frame.alpha_composite(topo_cta)
            camada = Image.new("RGBA", (E.W, E.H), (0, 0, 0, 0))
            painel.cabecalho(ImageDraw.Draw(camada), tl)
            frame.alpha_composite(camada)
            caixa_comentario(frame, tl, cena.get("palavra", ""))
            cy_leg = E.LEGENDA_Y_CTA
        else:
            frame = base.copy()
            frame.alpha_composite(painel.desenhar(tl, t))
            rosto = cobrir(src, bw, bh, zoom, foco_y)
            frame.paste(rosto, (bx0, by0), mask_rosto)
            cy_leg = E.LEGENDA_Y
        while li + 1 < len(legendas) and t >= legendas[li + 1]["s"]:
            li += 1
        if legendas and legendas[li]["s"] <= t < legendas[li]["e"]:
            desenhar_legenda(frame, legendas[li], t, cy_leg)
        enc.stdin.write(frame.convert("RGB").tobytes())
        if n % (E.FPS * 5) == 0:
            print(f"  {t:5.1f}s / {dur:.1f}s", flush=True)
    enc.stdin.close()
    enc.wait()
    dec.stdout.close()
    dec.wait()
    print(f"\nVídeo salvo em {saida}")
    if args.ate:
        print("GATE 2: mostre o piloto para a Dani e só renderize o final após aprovação.")


# =====================================================================
# validação
# =====================================================================
def cmd_conferir(args):
    ed = pasta_edit(args.projeto)
    v = ed / args.arquivo
    w, h, dur = sonda(v)
    n = max(1, int(dur / 2))
    cols = 6
    linhas = math.ceil(n / cols)
    grade = ed / "conferencia.png"
    rodar([FFMPEG, "-v", "error", "-y", "-i", str(v), "-vf",
           f"fps=0.5,scale=270:-1,tile={cols}x{linhas}", "-frames:v", "1", str(grade)])
    r = subprocess.run([FFMPEG, "-i", str(v), "-vf", "blackdetect=d=0.2:pix_th=0.05", "-an", "-f", "null", "-"],
                       capture_output=True, text=True)
    pretos = [l for l in r.stderr.splitlines() if "black_start" in l]
    r = subprocess.run([FFMPEG, "-i", str(v), "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True)
    lufs = re.findall(r"I:\s+(-?[\d.]+) LUFS", r.stderr)
    print(f"Arquivo: {v}\nResolução: {w}x{h}  Duração: {dur:.2f}s  Loudness: {lufs[-1] if lufs else '?'} LUFS")
    print(f"Trechos pretos: {len(pretos)}" + ("".join("\n  " + p for p in pretos)))
    print(f"Grade (1 frame a cada 2s): {grade}")


def main():
    ap = argparse.ArgumentParser(description="Editor 3 defibit — reels explicativo animado")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("preparar", help="CFR + transcrição + corte de pausas")
    p.add_argument("bruto")
    p.add_argument("--modelo", default="small", help="tamanho do whisper (tiny/base/small/medium)")
    p.add_argument("--max-pausa", type=float, default=0.5)
    p.add_argument("--sem-cortes", action="store_true")
    p.set_defaults(f=cmd_preparar)
    p = sub.add_parser("rascunho", help="gera edit/cenas.json a partir da transcrição")
    p.add_argument("projeto")
    p.add_argument("--sobrescrever", action="store_true")
    p.set_defaults(f=cmd_rascunho)
    p = sub.add_parser("render", help="renderiza piloto (--ate 15) ou final")
    p.add_argument("projeto")
    p.add_argument("--ate", type=float, help="renderiza só os primeiros N segundos")
    p.add_argument("--cenas", default="cenas.json")
    p.add_argument("--saida")
    p.set_defaults(f=cmd_render)
    p = sub.add_parser("conferir", help="grade de frames + checagens")
    p.add_argument("projeto")
    p.add_argument("--arquivo", default="final.mp4")
    p.set_defaults(f=cmd_conferir)
    a = ap.parse_args()
    a.f(a)


if __name__ == "__main__":
    main()
