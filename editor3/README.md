# Editor 3 defibit

Gera reels no formato **explicativo animado** com a identidade Dani Sanverino (@dani.defibit):

- **topo:** painel animado: kicker dourado, título em 2 linhas (a 2ª em dourado) e um visual por cena
- **meio:** legenda palavra a palavra, 1 a 4 palavras por tela, com a palavra falada destacada em dourado
- **base:** rosto da Dani num card de cantos arredondados, com punch-in alternado entre as cenas
- **CTA:** rosto em tela cheia, "COMENTA <PALAVRA>" e uma caixa de comentário digitando a palavra-chave, com o lema LIBERDADE · PATRIMÔNIO · SOBERANIA

Saída: 1080×1920, 30 fps, H.264 CRF 18, áudio normalizado a -14 LUFS.

## Instalação

```bash
pip install -r editor3/requirements.txt   # precisa de ffmpeg/ffprobe no PATH
```

Fontes: usa Inter (Bold, ExtraBold e Black). Se não estiverem instaladas, baixe em
github.com/rsms/inter e coloque os arquivos em `editor3/fontes/` (ou aponte `EDITOR3_FONTES`).

## Fluxo (com os 2 gates)

```bash
python editor3/editor3.py preparar  PROJETO/bruto.mp4    # 30fps CFR + transcrição + corta pausas > 0,5s
python editor3/editor3.py rascunho  PROJETO              # cria PROJETO/edit/cenas.json   -> GATE 1 (aprovar)
python editor3/editor3.py render    PROJETO --ate 15     # PROJETO/edit/piloto.mp4        -> GATE 2 (aprovar)
python editor3/editor3.py render    PROJETO              # PROJETO/edit/final.mp4
python editor3/editor3.py conferir  PROJETO              # grade 1 frame/2s, frames pretos, LUFS
```

O bruto nunca é sobrescrito. Tomadas repetidas: confira `edit/transcricao.txt`; a regra é manter sempre a última.

## cenas.json

```json
{
  "video": "video.mp4",
  "foco_y": 0.42,
  "correcoes": {"cloud": "Claude", "defi": "DeFi"},
  "cenas": [ { "inicio": 0, "tipo": "numero", "kicker": "...", "titulo": ["LINHA 1", "LINHA 2"], ... } ]
}
```

- `foco_y`: altura do rosto no bruto (0 = topo, 1 = base), usada nos recortes
- `correcoes`: corrige palavras que o whisper errou, direto nas legendas
- cada cena vai de `inicio` até o `inicio` da cena seguinte (ou até `fim`, se informado)

Campos comuns: `kicker`, `titulo` (lista de linhas), `dourado` (índices das linhas douradas;
o padrão é a última), `nota` (caixa dourada com texto escuro) e `zoom` (força o punch-in).

| tipo | para quê | campos |
|---|---|---|
| `titulo` | abertura de bloco, palavra/marca em destaque | `grande` (texto enorme com sublinhado animado) |
| `numero` | dado ou estatística (contagem animada) | `numero` ("24,9"), `sufixo`, `rotulo`, `sub` |
| `lista` | passos/itens com check (entram um a um) | `itens`, `intervalo` |
| `comparacao` | A → B | `a`, `b`, `rotulo_b` |
| `imagem` | print, foto ou burst de imagens | `imagem` ou `imagens` + `troca` (s), `largura_card` |
| `onda` | áudio/voz, forma de onda real da fala | `rotulo`, `nota` |
| `cta` | chamada final com rosto em tela cheia | `palavra` (digitada na caixa de comentário) |

Exemplo completo: `editor3/exemplo/cenas.exemplo.json`.
