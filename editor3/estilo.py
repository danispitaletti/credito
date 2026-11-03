"""Identidade visual defibit (Dani Sanverino) e medidas do layout do editor 3.

Layout 1080x1920 (9:16), medido a partir do reels de referência:
  - topo (0-1000): painel animado — kicker dourado, título 2 linhas, visual
  - faixa de legenda centrada em y~996
  - card do rosto com cantos arredondados (y 1060-1827)
  - rodapé com a assinatura da marca
Na cena "cta" o rosto vai para tela cheia.
"""
import os
from pathlib import Path

from PIL import ImageFont

# ---------- tela ----------
W, H = 1080, 1920
FPS = 30

# ---------- paleta defibit ----------
FUNDO = (13, 13, 13)            # #0D0D0D
FUNDO_2 = (24, 22, 18)          # tom quente para gradiente
GRADE = (212, 175, 55, 14)      # linhas da grade (dourado bem fraco)
DOURADO = (212, 175, 55)        # #D4AF37
DOURADO_CLARO = (236, 205, 120)
BRANCO = (245, 242, 235)
CINZA = (150, 145, 135)
TEXTO_ESCURO = (13, 13, 13)

# ---------- layout ----------
MARGEM_X = 60
KICKER_Y = 118
TITULO_Y = 168
VISUAL_TOPO = 470               # área do visual de cada cena
VISUAL_BASE = 930
LEGENDA_Y = 996                 # centro da faixa de legenda (layout dividido)
LEGENDA_Y_CTA = 1500            # centro da legenda na cena de CTA
ROSTO_BOX = (45, 1060, 1035, 1827)   # x0, y0, x1, y1 do card do rosto
ROSTO_RAIO = 34
RODAPE_Y = 1868

ASSINATURA = "DANI SANVERINO · DEFIBIT"
LEMA = "LIBERDADE · PATRIMÔNIO · SOBERANIA"

# ---------- fontes ----------
# Ordem de busca: $EDITOR3_FONTES, ./fontes ao lado deste arquivo, pastas do sistema.
_PASTAS = [
    os.environ.get("EDITOR3_FONTES", ""),
    str(Path(__file__).parent / "fontes"),
    "/usr/share/fonts/opentype/inter",
    "/usr/share/fonts/truetype/inter",
    "/Library/Fonts",
    os.path.expanduser("~/Library/Fonts"),
    os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\Windows\Fonts"),
    r"C:\Windows\Fonts",
]

_PESOS = {
    # nome lógico: candidatos (primeiro que existir)
    "titulo": ["InterDisplay-Black.otf", "Inter-Black.otf", "Inter-Black.ttf",
               "InterDisplay-ExtraBold.otf", "ariblk.ttf", "arialbd.ttf"],
    "forte": ["InterDisplay-ExtraBold.otf", "Inter-ExtraBold.otf", "Inter-ExtraBold.ttf",
              "Inter-Bold.otf", "Inter-Bold.ttf", "arialbd.ttf"],
    "legenda": ["Inter-Bold.otf", "Inter-Bold.ttf", "InterDisplay-Bold.otf", "arialbd.ttf"],
    "semi": ["Inter-SemiBold.otf", "Inter-SemiBold.ttf", "Inter-Bold.otf", "arialbd.ttf"],
}

_cache = {}


def _achar(nome_logico):
    for arq in _PESOS[nome_logico]:
        for pasta in _PASTAS:
            if pasta and os.path.isfile(os.path.join(pasta, arq)):
                return os.path.join(pasta, arq)
    raise FileNotFoundError(
        f"Nenhuma fonte encontrada para '{nome_logico}'. Coloque Inter-Bold/ExtraBold/Black "
        f"(github.com/rsms/inter) na pasta editor3/fontes ou defina EDITOR3_FONTES.")


def fonte(nome_logico, tamanho):
    chave = (nome_logico, int(tamanho))
    if chave not in _cache:
        _cache[chave] = ImageFont.truetype(_achar(nome_logico), int(tamanho))
    return _cache[chave]
