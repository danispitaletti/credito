---
name: estilo-video-explicativo
description: Padrão de edição de vídeo da Dani Sanverino no formato "explicativo animado" — vídeo vertical 9:16 que alterna TELA DIVIDIDA (animação 2D em cima, apresentador embaixo), B-ROLL ANIMADO EM TELA CHEIA e APRESENTADOR EM TELA CHEIA, com legenda dupla (título grande em cima + legenda em caixinha palavra por palavra). Use SEMPRE que a Dani disser "edita esse vídeo no meu estilo", "edita no estilo explicativo", "no estilo dos vídeos de referência", "tela dividida com animação", "faz igual aos modelos", "decupa/edita como o modelo 1/modelo 2", ou mandar um vídeo bruto falando para câmera pedindo edição. Funciona junto com a skill editar-video-dani (transcrição e cortes); esta skill define o VISUAL.
---

# Estilo "Explicativo Animado" — guia de edição

Fonte: decupagem de 2 vídeos de referência (85 s e 100 s), salvos no Dropbox em
`/Padrao de Edicao de Video/Modelo 1` e `/Modelo 2`. Os dois têm **o mesmo estilo**.
Quadros de referência na pasta `referencias/` desta skill — **olhe-os antes de editar**.
Os arquivos `referencias/aprovado_*.jpg` são do vídeo da Dani APROVADO (versão 1): é exatamente esse o visual a repetir.

## 1. Formato técnico
- Vertical **1080×1920** (refs em 720×1280), **30 fps** (24 também serve).
- Áudio: só a **voz**, sem trilha de fundo contínua. Loudness final **−14 LUFS**.
- Duração: a que a fala da Dani tiver (o vídeo aprovado tinha 60 s).
- **Velocidade sempre 1.0.** Cortar só os silêncios, deixando **respiro natural**: padding de
  0,16 s antes e depois de cada trecho de fala (pausas curtas ficam inteiras, longas viram ~0,3 s).
  Cortes mais secos que isso deixaram o vídeo "acelerado" — a Dani reprovou.
- Marca d'água: avatar redondo + `@usuario` pequeno, branco, opacidade ~80 %,
  à esquerda logo abaixo da linha da divisão (y ≈ 57 % da altura).

## 2. Os 3 formatos de tela (o coração do estilo)

| Formato | Como é | Quando usar | % do vídeo |
|---|---|---|---|
| **A. Tela dividida** | Metade de cima (0–50 %) = animação 2D; metade de baixo (50–100 %) = apresentador. Divisão com **borda de papel rasgado** branca/creme (#F6F2DF). | Abertura (gancho), explicações em que o rosto ajuda a convencer, fechamento/CTA | ~45 % |
| **B. B-roll em tela cheia** | Animação ocupa 100 % da tela; voz continua por baixo; **só o título de cima**, sem legenda de caixinha | Histórias, exemplos, números, "imagina que…" — blocos de 10 a 25 s | ~40 % |
| **C. Apresentador em tela cheia** | Só o rosto, enquadramento médio/fechado, legenda de caixinha embaixo | Frases de impacto, opinião, "pare de usar", pergunta forte — **curto, 2 a 5 s** | ~15 % |

### Ciclo que se repete (3 a 4 vezes por vídeo)
```
A (dividida, 8–14 s) → B (b-roll cheio, 10–25 s) → C (rosto cheio, 2–5 s) → A …
```
- Sempre **abre em A** (gancho com rosto + animação) e **fecha em A** (CTA).
- C é o "soco": aparece logo depois de um bloco de b-roll, para a frase-chave.

### Zoom no apresentador (dentro de A e C)
Alterna dois enquadramentos a cada 3–6 s, sempre num corte:
- **Fechado**: rosto ocupa ~60 % da largura (punch-in ~130 %).
- **Aberto**: busto + mesa + estante ao fundo (100 %).
Isso esconde os jump cuts e dá ritmo.

## 3. Transições (sempre rápidas, 0,3–0,5 s)
| De → Para | Movimento |
|---|---|
| A → B | O painel de animação **desce e cobre** o apresentador (a borda rasgada desliza até o fim da tela) |
| B → C | A animação **desliza para baixo e sai**, revelando o rosto em tela cheia |
| C → A | O vídeo do apresentador **encolhe/sobe** e a animação entra por cima com a borda rasgada |
| Cena → cena dentro do b-roll | **Whip/motion blur** (chicote) ou câmera que "voa" pela cidade 3D; nunca corte seco parado |

Easing: entrada rápida, final suave (ease-out). Leve motion blur no movimento.

## 4. Legendas — são DUAS camadas

### 4.1 Título de cima (texto-manchete)
- Posição: topo, y ≈ **4–8 %** em tela cheia; em A fica no meio da metade de cima (y ≈ 15–20 %).
- Fonte: sans-serif **Black/ExtraBold, CAIXA ALTA** (Montserrat Black, Poppins ExtraBold
  ou "The Bold Font"). Tamanho grande: ~60–80 px em 1080 de largura.
- Cor base **branco** (#F1ECE7) com **contorno escuro fino + sombra projetada** para baixo.
- Palavras-chave coloridas: **amarelo #E5BA30** (destaque positivo/neutro) e
  **vermelho #E64332** (perigo, dívida, "não", números ruins).
- Animação: **constrói a frase palavra por palavra** conforme a fala
  ("QUEM NÃO" → "QUEM NÃO TEM RESERVA"); quebra em 2 linhas; some com fade/blur
  quando a ideia muda. Números grandes em destaque ("84 MILHÕES", "R$ 27").

### 4.2 Legenda de caixinha (karaokê)
- **1 a 3 palavras** por vez, CAIXA ALTA, mesma fonte Black.
- Caixa **branca #FFFBF8**, cantos levemente arredondados, **borda escura fina**, leve sombra.
- Texto **preto/grafite #221927**.
- Palavra que está sendo dita: **marca-texto amarelo #E8AE3C** atrás da metade de baixo da palavra
  (ou texto vermelho #E64332 para palavras negativas); próxima palavra ainda não dita em **cinza claro**.
- Posição: em A, **centralizada exatamente na linha rasgada** (y ≈ 50 %);
  em C, **terço inferior** (y ≈ 86 %). **Em B não aparece.**
- Entrada: pop rápido (escala 90 → 100 %, 0,1 s).

## 5. B-roll animado (identidade visual)

> **DECISÃO DA DANI (teste aprovado em 02/11/2026): o padrão é a VERSÃO 1 — desenhos 2D
> "recorte de papel" feitos pelo próprio Claude com código** (`scripts/render_teste.py`).
> Não gerar imagens com IA por padrão. A versão realista com imagens 3D de IA
> (`scripts/render_real.py`) foi testada e **não** foi a preferida — só usar se ela pedir.
> Vantagens da versão 1: custo zero, sem depender de download de imagens, textos sem erro,
> cada objeto anima exatamente na palavra falada.
>
> Pipeline da versão 1 (o que funcionou no teste):
> 1. Transcrever: `scripts/transcreve.py` (Whisper small via sherpa-onnx; modelo baixado de
>    github.com/k2-fsa/sherpa-onnx/releases, asr-models/sherpa-onnx-whisper-small.tar.bz2).
>    Tempos por trecho com `silencedetect` (−32 dB, 0,12 s) e palavras distribuídas por tamanho.
> 2. Cortar pausas com **padding 0,16 s** de cada lado (pausas curtas ficam inteiras, longas viram
>    ~0,3 s) e normalizar áudio (loudnorm −14 LUFS). **Velocidade sempre 1.0.** Com 0,08 s a Dani
>    achou o vídeo "acelerado" — não usar menos que 0,16 s.
> 3. Rastrear o rosto (OpenCV haar cascade, opencv-python-headless < 5) para o recorte da meia tela.
> 4. Desenhar cada cena como sprites com contorno escuro + sombra (PIL, supersampling 2x),
>    fundo de papel kraft listrado com piso de madeira; objetos com etiqueta de texto;
>    pop com ease-back na palavra; push-in lento; whip entre cenas.
> 5. Fonte: Montserrat Black/ExtraBold via `npm pack @fontsource/montserrat` (arquivos .woff).
> 6. Compor quadro a quadro e exportar 1080×1920, 30 fps, H.264 CRF 18.
>
- Estilo **2D flat "recorte de papel"**: textura de papel/papelão, contorno escuro, sombras suaves,
  cenário em **perspectiva 3D leve** (cidade/rua vista de cima, câmera que se move).
- Paleta: bege kraft **#D5BD8F**, céu azul-acinzentado, tons pastel (rosa, verde-menta, azul),
  com **amarelo** e **vermelho** como cores de destaque.
- Personagem-protagonista com plaquinha **"VOCÊ"** no peito (o espectador vira personagem).
  Outros: "AMIGA", "COMERCIANTE", "GOVERNO"…
- Objetos com **etiquetas de texto** (cofrinho "RESERVA DE EMERGÊNCIA", celular "PIX CRÉDITO",
  boleto "FATURA DO CARTÃO") — cada conceito vira um objeto com nome.
- Dados viram gráfico ilustrado: pizza ("SALÁRIO" com fatia vermelha 25 %), barras com
  selo "RECORDE", multidão de bonecos com parte em vermelho ("4 EM 10").
- Micro-animações: elementos entram com **pop + brilhos (✦)**, X vermelho para "errado",
  ✓ verde para "certo", "?" ao lado do personagem em dúvida, câmera com **push-in lento** constante.
- Troca de cena dentro do b-roll a cada **2–4 s**.

## 6. Ritmo
- Algo muda na tela a cada **1–2 s** (palavra nova, objeto que entra, zoom, corte).
- Corte de enquadramento do apresentador a cada **3–6 s**.
- Nenhum plano parado > 4 s.

## 7. Estrutura de roteiro observada
1. **Gancho (0–3 s)** em A, frase que separa o público: "Quem não tem reserva de emergência…",
   "O imposto deixou de ser uma promessa…".
2. **Dado chocante** em B (número grande na tela).
3. **Explicação com exemplo do cotidiano** (amiga, feira, pastel) em B, intercalada com C.
4. **Virada/conselho** em C ("pare de usar", "invista no dia do salário").
5. **Solução prática + fechamento** em A.

## 8. Passo a passo para editar um vídeo novo (o que o Claude faz)

**Modelo pronto:** `scripts/render_v2.py` (vídeo "Bloqueio judicial / DeFi", APROVADO pela Dani).
Para um vídeo novo, copie esse arquivo e troque SÓ: a lista `SEGS`, a lista `BLOCKS`, as funções
de cena (`sA_*` para tela dividida 1080×960, `sB_*` para b-roll 1080×1920), o dicionário `SCENES`
e os conjuntos de palavras coloridas `YW` (amarelo) e `RW` (vermelho). Todo o resto — legendas,
transições, tela dividida, zoom, marca d'água — já está pronto e não deve ser mudado.

1. **Receber o vídeo** — a Dani anexa no chat (o Dropbox/Canva/Kairogen não baixam neste ambiente:
   a rede bloqueia). Se vier pelo WhatsApp a resolução cai; pedir o original quando possível.
2. **Preparar ferramentas** (sessão nova):
   - `pip install sherpa-onnx "opencv-python-headless<5"`
   - Whisper: `curl -L -o w.tar.bz2 https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/sherpa-onnx-whisper-small.tar.bz2 && tar xjf w.tar.bz2`
   - Fonte: `npm pack @fontsource/montserrat@5.0.19 && tar xzf fontsource-montserrat-*.tgz` (pasta `fonts/`)
3. **Transcrever**: `silencedetect=n=-32dB:d=0.12` → `scripts/transcreve_trechos.py` (um trecho por
   frase). Reler trechos estranhos com janela maior (`scripts/transcreve.py`). Corrigir erros óbvios
   pelo contexto (ex.: "queijo judicial" = "bloqueio judicial"). Mostrar a transcrição para a Dani.
4. **Rastrear o rosto** (haar cascade a cada 10 quadros → `face.json`) para o recorte da meia tela.
5. **Mapa A/B/C** seguindo o ciclo do §2: abre em A (gancho), B nas explicações/exemplos/números,
   C curto nas perguntas diretas e frases de impacto, fecha em A (CTA). Cada frase vira uma cena
   com objetos que representam o que ela diz, com etiqueta de texto, e cada objeto aparece
   (pop) exatamente na palavra falada.
6. **Cortar pausas** (padding 0,16 s) e normalizar o áudio (`highpass=80, acompressor, loudnorm I=-14`).
7. **Prévia**: `python3 render.py PASTA t1 t2 ...` gera quadros soltos. Montar uma folha e conferir:
   título não cobre os desenhos (máx. 4 palavras por título, objetos com centro em y≈600 no painel A),
   nenhum quadro vazio na troca de cena (pop dos objetos da cena nova começa ~0,3 s ANTES do início dela).
8. **Render final** (~3 min por minuto de vídeo) → conferir folha de quadros a cada 0,7 s → enviar.

Fluxo com a Dani: ela grava o texto inteiro de uma vez falando para a câmera (busto, celular
vertical, câmera parada, luz de frente) → manda aqui → Claude mostra a TRANSCRIÇÃO e o
STORYBOARD → ela aprova/ajusta → Claude renderiza e entrega → ajustes.

- **Storyboard antes do render** (aprovado pela Dani): `python3 scripts/storyboard.py render.py PASTA "Título" saida.jpg`
  gera uma folha com 1 quadro por cena, o formato (cores: azul = tela dividida, verde = b-roll,
  laranja = rosto) e a fala. Enviar com uma tabela "nº | formato | fala | o que aparece".
- **Vídeo grande (> ~30 MB)** não anexa no chat: pedir para ela mandar para si mesma no WhatsApp
  (sem HD), salvar e anexar. Fica 480p–720p, aceitável.
- **CTA da mentoria (padrão):** sempre que o vídeo falar da mentoria, a cena final mostra o botão
  "SAIBA MAIS" + o cartão: **MENTORIA / para empresários com patrimônio estabelecido / +100k INVESTIDOS**
  ("100k" — sem "reais" nem "dólares"). Segurar a imagem final por **2 s** (áudio com silêncio)
  para dar tempo de ler. Ver `CARD_MENT` e `sA_cta` em `scripts/render_v3.py`.
- Modelo mais recente: `scripts/render_v3.py` (vídeo "Imposto no PIX", fonte 480×854).
  Vídeos de fonte pequena: zoom do rosto em tela cheia 1.18 (em vez de 1.32).
- **Limpar ruído de fundo (latido de cachorro etc.)** — a Dani grava em casa e há cachorro:
  1. Detectar: `scripts/acha_latido.py` (modelo CED audio-tagging, GitHub k2-fsa/sherpa-onnx
     releases `audio-tagging-models/sherpa-onnx-ced-mini-audio-tagging-2024-04-19.tar.bz2`).
  2. Limpar: `scripts/limpa_voz.py` (modelo GTCRN, releases `speech-enhancement-models/gtcrn_simple.onnx`)
     sobre o áudio 16 kHz; depois juntar: GTCRN reamostrado (lowpass 7,6 kHz) + original
     highpass 7,6 kHz × 0,5, e loudnorm −14. Conferir de novo com o detector (deve ficar ~0)
     e retranscrever para garantir que a voz não foi afetada.
- **Enquadramento do rosto FIXO por bloco** (`face_block` em `render_v3.py`): usar a mediana da
  posição do rosto no bloco inteiro e manter o recorte parado, como câmera no tripé. NÃO seguir o
  rosto quadro a quadro — isso fez o vídeo "tremer" e a Dani reprovou.
- Toda cena nova deve ter algum objeto visível já no 1º quadro (pop começando ~0,3 s antes) —
  nunca deixar painel vazio enquanto a fala acontece.

## 9. Checklist final
- [ ] Abre com gancho em tela dividida
- [ ] Pelo menos 3 ciclos A → B → C
- [ ] Título de cima com amarelo/vermelho só nas palavras-chave
- [ ] Legenda de caixinha 1–3 palavras com marca-texto amarelo, ausente no b-roll cheio
- [ ] Borda de papel rasgado na divisão
- [ ] Personagem "VOCÊ" aparece no b-roll
- [ ] Sem pausas, sem trilha, −14 LUFS
- [ ] Fecha com conselho/CTA em tela dividida

## Observação de marca
A referência usa amarelo + vermelho sobre bege. Se a Dani pedir a versão **defibit**, troque
o amarelo do marca-texto pelo **dourado da marca** e mantenha todo o resto do estilo.
