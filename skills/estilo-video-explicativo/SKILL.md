---
name: estilo-video-explicativo
description: Padrão de edição de vídeo da Dani Sanverino no formato "explicativo animado" — vídeo vertical 9:16 que alterna TELA DIVIDIDA (animação 2D em cima, apresentador embaixo), B-ROLL ANIMADO EM TELA CHEIA e APRESENTADOR EM TELA CHEIA, com legenda dupla (título grande em cima + legenda em caixinha palavra por palavra). Use SEMPRE que a Dani disser "edita esse vídeo no meu estilo", "edita no estilo explicativo", "no estilo dos vídeos de referência", "tela dividida com animação", "faz igual aos modelos", "decupa/edita como o modelo 1/modelo 2", ou mandar um vídeo bruto falando para câmera pedindo edição. Funciona junto com a skill editar-video-dani (transcrição e cortes); esta skill define o VISUAL.
---

# Estilo "Explicativo Animado" — guia de edição

Fonte: decupagem de 2 vídeos de referência (85 s e 100 s), salvos no Dropbox em
`/Padrao de Edicao de Video/Modelo 1` e `/Modelo 2`. Os dois têm **o mesmo estilo**.
Quadros de referência na pasta `referencias/` desta skill — **olhe-os antes de editar**.

## 1. Formato técnico
- Vertical **1080×1920** (refs em 720×1280), **30 fps** (24 também serve).
- Áudio: só a **voz**, sem trilha de fundo contínua. Loudness final **−14 LUFS**.
- Duração alvo: **80–100 s**.
- Fala **sem respiros**: cortar todas as pausas > 0,15 s (jump cuts colados).
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
> 2. Cortar pausas (padding 0,08 s) e normalizar áudio (loudnorm −14 LUFS).
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

## 8. Passo a passo para editar um vídeo novo
1. Receber o vídeo bruto (Dani falando para câmera, vertical). Se possível, gravado com folga
   de enquadramento para permitir o punch-in.
2. Transcrever com tempos por palavra (pipeline da skill `editar-video-dani`) e cortar pausas.
3. Dividir o roteiro em blocos e marcar cada trecho como **A, B ou C** seguindo o ciclo do §2.
   Mostrar esse mapa para a Dani aprovar antes de gerar animações.
4. Para cada bloco B (e para a metade de cima dos blocos A), escrever o **prompt de animação**
   no estilo do §5 (usar a skill `image-prompt-generator` / gerar no Kairogen). Sempre citar:
   "2D flat paper-cutout animation, cardboard texture, kraft beige background, pastel city,
   character with sign 'VOCÊ', vertical 9:16, slow camera push-in".
5. Montar: layout A (animação 1080×960 em cima, rosto 1080×960 embaixo, borda rasgada no meio),
   B (animação 1080×1920), C (rosto 1080×1920 com zoom alternado).
6. Aplicar as duas camadas de legenda do §4 (título só com palavras-chave; caixinha karaokê).
7. Transições do §3. Normalizar áudio em −14 LUFS.
8. Exportar 1080×1920, H.264, 30 fps. Conferir: abre em A, fecha em A, C curto, nenhum plano parado > 4 s.

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
