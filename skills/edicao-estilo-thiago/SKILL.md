---
name: edicao-estilo-thiago
description: 'EDIÇÃO ESTILO THIAGO — edita vídeo bruto da Dani Sanverino no estilo do Reel "tempo da luz" do @tiagolemsosx (Thiago): "conteúdo 2.0", em que a edição DEMONSTRA ao vivo o que ela fala. A Dani fica no centro com o cenário trabalhado ao redor — palavra-chave gigante atrás/acima da cabeça com o fundo escurecido e desfocado (sem tarja), split com painel de infográfico em cima e ela num card arredondado embaixo (morph de layout, não corte seco), builds palavra a palavra, contadores animados, fundo trocado por cenário recriado, grade 2×2 de recap, objeto inserido na mão, CTA em interface de app, tema de cor por assunto. Use quando a Dani disser "estilo Thiago", "edição Thiago", "edita no estilo do Thiago", "conteúdo 2.0", "estilo tempo da luz". A Dani tem TRÊS skills de edição (estilo Tay, estilo Thiago, estilo Escolinha): se ela pedir "edita esse vídeo" sem dizer o estilo, NÃO escolha sozinho — pergunte qual dos três usar.'
---

# Edição Estilo Thiago

Estilo decupado do Reel "tempo da luz" do @tiagolemsosx (1:51). A ideia central: **a edição prova o que a pessoa fala enquanto ela fala**. Não é B-roll genérico: cada frase constrói um pedaço de um diagrama, metáfora ou cenário. É o estilo de **impacto e autoridade** — a Dani é o centro da tela, a edição acontece em volta dela.

Diferença para os outros estilos:
- **Tay:** cortes rápidos com B-roll e cartões dourados (energia).
- **Thiago (este):** ela no centro, cenário e infográficos construídos ao redor (impacto, sensação de "edição cara").
- **Escolinha:** quadro de slides em cima explicando tudo, ela num card embaixo (ensino).

Leia `references/decupagem-thiago.md` antes de planejar a edição.

## Fluxo

1. **Preparar:** normalizar VFR (`ffmpeg -i bruto.mp4 -vsync cfr -r 30 -c:v libx264 -crf 18 -c:a aac bruto_cfr.mp4`). Nunca sobrescrever o bruto.
2. **Transcrever com timestamps por palavra** (Whisper ou ElevenLabs Scribe).
3. **Cortar a fala:** manter cada palavra com margem de 0,08 s antes e 0,12 s depois; juntar trechos separados por ≤ 0,22 s. Pausas entre frases ficam em 0,2–0,4 s. Remover respiros, ruídos, tomadas repetidas (manter a ÚLTIMA) e repetições. Se passar de 3 min, cortar repetições e trechos fora do tema e informar.
4. **Roteiro visual (APROVAÇÃO 1):** dividir o vídeo em capítulos e, para cada frase, definir layout + o que é construído na tela + tema de cor. Apresentar em tabela (tempo | fala | layout | elemento | cor) e AGUARDAR a Dani aprovar. Listar as imagens/vídeos de IA necessários (prompts) e pedir aprovação das imagens antes de usar.
5. **Montar e animar** (Python PIL/numpy/OpenCV quadro a quadro, ou HyperFrames): layouts, morph entre layouts, builds por palavra, contadores, recortes de fundo (MediaPipe + guided filter, sem halo branco).
6. **Piloto de 15 s (APROVAÇÃO 2)** com os 10 s iniciais e o primeiro split. Só seguir após aprovação.
7. **Render final + revisão** (ver checklist) e entrega.

## Layouts (alternar conforme a fala)

1. **Tela cheia, cenário real** — ganchos, títulos, tese. Punch-in leve e lento, sem vai-e-vem.
2. **Split (layout dominante)** — painel escuro em cima (~38% da altura, cantos ~24 px) onde o infográfico se monta; ela num card arredondado embaixo (margem lateral ~30 px) até a base. Legenda dentro do card, na altura do peito.
3. **Título acima da cabeça** — frase-guia pequena branca + PALAVRA-CHAVE enorme na cor do tema, atrás/acima da cabeça. O FUNDO atrás dela escurece e desfoca; ela continua nítida. **Nunca tarja ou sombra sobre ela.**
4. **Fundo trocado** — ela recortada sobre um cenário recriado ligado ao tema (ex.: cofre, cidade financeira, rede de nós, espaço).
5. **Gráfico em tela cheia sem rosto** — só 3–4 s, no clímax de um dado; a legenda continua.
6. **Grade 2×2** — recap de exemplos/ideias em cards em volta da cabeça, com rótulo e ícone em cada um.
7. **Objeto na mão** — objeto inserido que acompanha o gesto (ex.: celular com carteira, moeda).
8. **Interface de app** — CTA: caixa de comentário em que se digita a palavra-chave, check, notificação de direct.

## Movimento e transições

- **Morph de layout** é a transição principal: o quadro dela encolhe e desliza para o card (0,4–0,6 s, ease-out), em vez de corte seco.
- Cortes secos só entre takes, sempre mascarados por mudança de layout ou título no mesmo instante.
- **Builds por palavra:** nada aparece pronto. Números contam, linhas se desenham, barras crescem, ícones acendem um a um, palavras soltas flutuam e se organizam num diagrama (caos → ordem).
- **Contadores animados** recorrentes (valores, porcentagens, datas, cronômetro).
- Painéis 3D flutuantes e linhas de profundidade discretas; leve balanço.
- Algo novo entra na tela a cada ~1 s; o layout muda a cada 3–5 s.
- Sem giros chamativos, glitch, wipe ou aparência de PowerPoint.

## Tipografia e cor

- **Legenda neutra:** 1–3 palavras, branca, sans geométrica extra-bold (Montserrat ExtraBold / Plus Jakarta), sombra preta suave, sem caixa e **sem palavra colorida**. ~44–50 px em 1080. Nunca sobre olhos/boca.
- **A cor está nos títulos e gráficos**, não na legenda.
- Rótulos: caixa alta pequena com letras espaçadas ("● ANTES", "● HOJE").
- Números enormes, sempre maiores que qualquer texto em volta.
- Cards: fundo escuro translúcido, cantos ~20 px, borda de 1 px quase invisível.
- **Tema da casa:** charcoal #0E0E10, off-white #F2EEE8, cinza quente #8C8580 para rótulos; destaque terracota tijolo #A3482F (fechado, avermelhado — nunca laranja/pêssego).
- **Tema por assunto** (é o que dá a sensação de edição cara):
  - Bitcoin: preto + champagne/dourado frio (logo do Bitcoin, sem pintar a tela de laranja).
  - Dólar: verde-escuro sóbrio + off-white.
  - Bancos/governo: azul-marinho institucional, interface fria.
  - Privacidade/vigilância: preto + grafite, elementos que se apagam ou desfocam.
  - Reais/DePix: verde discreto só no ícone, base charcoal.
- Imagens realistas estilo render 3D (prédios clássicos de pedra, carteira digital real, cofre), nunca desenho infantil.

## Áudio

Voz limpa a −14 LUFS; música (se houver) ~10 dB abaixo da voz; whoosh sutil nas trocas de capítulo e som de impacto nos momentos fortes dos 10 s iniciais.

## Regras gerais da Dani (valem para os três estilos)

- **Duração máxima: 3 minutos.** Para encurtar, cortar repetições, tropeços e trechos fora do tema; informar o que saiu.
- **Nunca cortar palavra** e manter a última palavra inteira, com o fade só depois dela.
- **Nada sobre o rosto:** nem legenda, card, tarja, sombra, caixa de seleção ou retângulo.
- Headline (quando houver) só nos 10 s iniciais, no topo (~200–390 px), com sombra preta, nunca sobre a cabeça.
- Área segura do Instagram: topo 200–250 px, base 350–400 px, laterais 60 px.
- Sem laranja, sem roxo, sem neon, sem emojis, sem bolinhas decorativas.
- Quando citar marcas, usar logos oficiais que a Dani enviar.
- Entrega: 1080×1920, H.264 crf 18 + AAC, 30 fps, salvo em `C:\Users\Dani\Dropbox\fotos dani\videos\`.

## Checklist antes de entregar

Extrair 1 quadro a cada 2 s e conferir: palavra cortada; legenda errada, atrasada ou adiantada; texto/elemento sobre o rosto; elemento fora da área segura; transição seca; flash ou frame solto; tela preta; imagem congelada; áudio fora de sincronia; duração acima de 3 min. Corrigir antes de entregar.
