---
name: edicao-estilo-escolinha
description: 'EDIÇÃO ESTILO ESCOLINHA — edita vídeo bruto da Dani Sanverino como uma aula visual: quadro/painel de slides flutuante em cima mostrando TUDO o que ela fala (imagens realistas 3D que entram girando com reflexo de luz, títulos que se revelam por máscara, listas com X vermelho riscando, checks verdes, setas, gráficos, moedas girando, rótulos apontando partes da imagem), painel que vira como página de livro a cada ideia, e ela num card arredondado embaixo com leve balanço 3D. Legenda palavra a palavra com palavras-chave coloridas, efeitos sonoros sutis, até 3 minutos. Inclui o motor de render em Python (scripts/). Use quando a Dani disser "estilo escolinha", "edição escolinha", "faz a versão com slides", "edita com o quadro", "vídeo aula", "estilo professora". A Dani tem TRÊS skills de edição (estilo Tay, estilo Thiago, estilo Escolinha): se ela pedir "edita esse vídeo" sem dizer o estilo, NÃO escolha sozinho — pergunte qual dos três usar.'
compatibility: 'Python 3.10+ com Pillow, numpy, opencv-python; ffmpeg no PATH; Whisper ou ElevenLabs Scribe para transcrição; fontes Montserrat e Oswald (variáveis)'
---

# Edição Estilo Escolinha

A Dani ensina e um quadro de slides ao lado mostra visualmente cada ideia que ela fala, como uma professora com o quadro. É o estilo para **explicar** um conceito com várias partes (split payment, autocustódia, carteira, rede descentralizada).

Diferença para os outros estilos:
- **Tay:** cortes rápidos com B-roll e cartões dourados (energia).
- **Thiago:** ela no centro com cenário e infográficos ao redor (impacto).
- **Escolinha (este):** painel de slides em cima, ela num card embaixo (ensino).

## Layout (1080×1920)

- **Painel** ~972×570 px em x=54, topo em y≈230 (cantos 34 px, borda dourada fina #CEB68C translúcida, sombra suave embaixo). Fundo do painel: off-white #FAF8F4 ou a cor de fundo da imagem do slide; pode ser escuro se ela pedir.
- **Card dela** embaixo do painel (~24 px de distância), recortado do topo da cabeça até a cintura, cantos 36 px, borda dourada, sombra, balanço 3D leve (rotação ±0,025 rad) e motion control: push-in/pull-out lento alternado por frase (até 6%), sem vai-e-vem.
- **Fundo:** o próprio vídeo desfocado e escurecido em tom quente. Se ela pedir, biblioteca de estantes de madeira ocupando a tela toda (recorte MediaPipe + guided filter, sem halo branco).
- **Headline:** só nos 10 s iniciais, no topo (~196–390 px), Montserrat ExtraBold off-white com sombra preta, palavras de destaque em selo colorido. Nesses 10 s o painel fica menor (escala ~0,82, topo em y=410) e o card desce/encolhe; aos 10 s tudo sobe suavemente (0,7 s) para a posição normal.
- Se o vídeo não tiver espaço, a cena começa direto no painel; não deixar a tela parada só com ela.

## Slides (uma ideia falada = um slide)

Cada slide tem uma imagem realista estilo render 3D (de um lado) + texto (do outro), e TUDO entra sincronizado com a palavra falada:
- **Kicker** pequeno em caixa alta espaçada (Montserrat 21/800) com barrinha colorida.
- **Títulos** em Oswald 50–90 px, revelados de baixo para cima por máscara; palavra de impacto com "pop" (escala 1,18→1) + som de impacto.
- **Riscados:** ícone X vermelho + texto + linha vermelha atravessando ("sem banco, sem governo, sem bloqueio").
- **Checks:** ícone ✓ verde + texto ("movimentar o seu dinheiro").
- **Bullets** coloridos, **chips** (rótulo em pílula), **setas** (contínuas ou tracejadas), **gráfico de barras** crescendo, **moedas** (R$, $, ₿) girando e caindo, **rótulos com linha** apontando partes da imagem (anatomia da carteira, moedas).
- **Imagens 3D:** entram girando em perspectiva (rotação Y ~0,75 rad → 0, escala 0,86 → 1), reflexo de luz passando na diagonal, leve flutuação e sombra elíptica embaixo.
- **Troca de slide:** o painel vira como página de livro (rotação Y até ~1,45 rad e volta, 0,42 s), com whoosh.
- Nenhum slide fica vazio por muitos segundos: se a fala demora a chegar ao título, adiantar um kicker ligado ao que ela está dizendo.
- Imagens novas: gerar realistas (Canva/IA), estilo render 3D com fundo claro, sem laranja; **pedir aprovação da Dani antes de usar**. Banco/governo em pedra clássica; carteira digital real; cofre; câmera de vigilância; documentos; rede de celulares; moedas.

## Legendas

- Palavra por palavra, blocos de até 3 palavras (ou ≤17 caracteres, quebrando em pontuação), Montserrat 50/800 branca com contorno de 6 px, entrada com leve pop (0,15 s).
- **Palavra-chave com contorno colorido:** imposto/governo/estado/bloqueio/sobrevivência em vermelho #C0392B; rede/autocustódia/descentralizadas em teal #0E7C7B; banco em azul-marinho #1E3A5F; dinheiro/dólar/real/mentoria em verde #2E7D4F; bitcoin/carteira em azul #2563EB.
- Posição: entre o queixo e o peito dentro do card. Se ela tiver caixa de texto gravada no vídeo, não cobrir.

## Fluxo técnico (o que funcionou)

1. **Transcrever** com timestamps por palavra → `tr.json` (lista de frases com `s`, `e`, `w`=[[início, fim, palavra]]).
2. **Lista de cortes** (`cut.json`): cada palavra com margem 0,08 s antes / 0,12 s depois; juntar trechos com intervalo ≤ 0,22 s; excluir trechos removidos (repetições/tropeços) sem que a margem invada a palavra removida; +0,15 s no fim.
3. **Base** com ffmpeg: `select`/`aselect` com a lista, `setpts=(N/30)/1.2/TB` e `atempo=1.2` (velocidade 1,2×), áudio `highpass=f=70,afftdn=nf=-26,loudnorm=I=-14:TP=-1.5:LRA=11`. Usar `-preset ultrafast -crf 14` em segundo plano (demora vários minutos). Se usar `-ss`, somar o deslocamento com `setpts=PTS+X/TB` e `asetpts=PTS+X/TB` antes do select.
4. **Cenas** programadas no tempo ORIGINAL da fala; o motor converte (função `src_t`).
5. **Render** quadro a quadro com `scripts/motor_3d.py` + um arquivo de cenas no formato de `scripts/exemplo_render.py` (decorador `@scene(início, fim, imagem)`), em pedaços de ~24 s rodando em segundo plano; ~0,5 s por quadro.
6. **SFX** com `scripts/sfx.py` (whoosh nas trocas, tique nos itens, impacto nos pops), mix com a voz a −14 LUFS e `afade` curto só depois da última palavra.
7. **Concatenar** os pedaços com `-c copy` e mixar o áudio (`-c:v copy`), `+faststart`.

Os scripts usam a pasta base `C:\dani video hunter editora\` (variável `BASE` no topo de cada script). Dentro dela ficam `v5\` (cut.json, tr.json, base.mov), `fonts\` (Montserrat.ttf, Oswald.ttf) e `img\` (imagens dos slides). Para outro projeto, defina a variável de ambiente `DANI_EDITORA` com a pasta do projeto.

## Regras gerais da Dani (valem para os três estilos)

- **Duração máxima: 3 minutos.** Para encurtar, cortar repetições (falou a mesma coisa duas vezes), tropeços e trechos fora do tema; informar o que saiu.
- **Nunca cortar palavra** e manter a última palavra inteira, com o fade só depois dela.
- **Nada sobre o rosto:** nem legenda, card, tarja, sombra, caixa ou retângulo. Sem degradês pretos sobre ela.
- Área segura do Instagram: topo 200–250 px, base 350–400 px, laterais 60 px.
- Cores variadas (teal, azul-marinho, verde, vermelho, azul); **sem laranja, sem roxo**, sem neon, sem emojis, sem bolinhas decorativas.
- Quando citar marcas, usar logos oficiais que a Dani enviar.
- Conteúdo político sobre eleições/pessoas: só legenda, sem slides reforçando; avisar sobre risco jurídico de acusações a pessoas nomeadas.
- Entrega: 1080×1920, H.264 crf 18 + AAC 256k, 30 fps, salvo em `C:\Users\Dani\Dropbox\fotos dani\videos\`.

## Checklist antes de entregar

Renderizar 4–6 quadros de teste antes do render completo e mostrar. No final, extrair quadros ao longo do vídeo e conferir: palavra cortada; legenda errada/fora de sincronia; slide fora de sincronia com a fala; texto sobre o rosto; elemento fora da área segura; slide vazio por muito tempo; flash, tela preta ou frame congelado; áudio e vídeo com a mesma duração; duração ≤ 3 min. Corrigir antes de entregar.
