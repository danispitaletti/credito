---
name: edicao-estilo-tay
description: 'EDIÇÃO ESTILO TAY — edita vídeo bruto da Dani Sanverino no estilo Tay Dantas (@tay.ldantas) adaptado à marca: ritmo rápido de cortes (mudança visual a cada 1–1,3 s, rajadas de 0,1–0,4 s em listas), seis táticas de cobertura com B-roll em moldura arredondada, prints de notícia, cartões de seção pretos com letra cursiva dourada #D4AF37, legendas brancas com UMA palavra dourada por tela, assinatura LIBERDADE·PATRIMÔNIO·SOBERANIA. Motor video-use + HyperFrames, com dois pontos de aprovação (EDL e piloto de 15 s). Use quando a Dani disser "estilo Tay", "edição Tay", "edita no estilo Tay Dantas", "edição rápida com B-roll", "corte rápido". A Dani tem TRÊS skills de edição (estilo Tay, estilo Thiago, estilo Escolinha): se ela pedir "edita esse vídeo" sem dizer o estilo, NÃO escolha sozinho — pergunte qual dos três usar.'
compatibility: 'Claude Code em Windows com ffmpeg no PATH, Node.js/npx, video-use instalado com ELEVENLABS_API_KEY configurada (ver references/instalacao.md)'
---

# Edição Estilo Tay — Pipeline Completo

Transforma um bruto de talking head no reels final, no padrão visual Dani Sanverino, sem edição manual.

**Antes de tudo:** se o video-use não estiver instalado/registrado neste computador (verificar `~/.claude/skills/video-use`), leia e execute `references/instalacao.md` primeiro.

## Arquitetura

- **Motor:** video-use (browser-use/video-use) — transcrição palavra a palavra via ElevenLabs Scribe, remoção de vícios de fala e pausas, fades de áudio de 30ms nos cortes, EDL, render e autoavaliação nos pontos de corte.
- **Camada de estilo (esta skill):** regras de cobertura Tay Dantas + identidade Dani Sanverino, que SOBRESCREVEM os padrões do video-use (ex.: as legendas default dele são 2 palavras maiúsculas — usar o padrão da Dani descrito abaixo).
- **Motion:** HyperFrames (o video-use já o chama via npx para overlays de animação).

## Fluxo

```
BRUTO → decupagem (video-use) → EDL estilizado [GATE 1] → montagem
      → legendas/motion (HyperFrames) → piloto 15s [GATE 2] → final + validação
```

Os dois GATES são obrigatórios: nunca renderizar o vídeo completo sem a Dani aprovar o EDL e o piloto.

## FASE 0 — Preparação

1. Trabalhar na pasta do projeto (padrão: subpastas de `C:\dani video hunter editora\`). Nunca sobrescrever o bruto; saídas ficam em `edit\` (padrão do video-use).
2. Se o bruto vier de celular, normalizar VFR antes de cortar:
   `ffmpeg -i bruto.mp4 -vsync cfr -r 30 -c:v libx264 -crf 18 -c:a aac bruto_cfr.mp4`
3. Ler o `roteiro*.md` do projeto, se existir, e o `project.md` do video-use de sessões anteriores.

## FASE 1 — Decupagem (video-use)

Deixar o video-use transcrever e propor os cortes de fala. Instruções específicas da Dani:
- Remover pausas > 0,5s, vícios ("é...", "né", "então" solto), falsos começos.
- **Tomadas repetidas: manter sempre a ÚLTIMA** (a Dani regrava a frase quando erra).
- Alinhar com o roteiro e sinalizar frases faltantes ou fora de ordem.

## FASE 2 — EDL estilizado (GATE 1)

Ler `references/estilo-tay-dantas.md` e enriquecer o EDL do video-use com a cobertura visual:
- Mudança visual com mediana de 1,0–1,3s; clímax/enumerações em 0,1–0,4s.
- Seis táticas de cobertura, nunca duas iguais em sequência.
- Sem B-roll adequado → punch-in 15–30%; nunca plano parado > 3s.
- CTA final: rosto na câmera, sem cobertura.
- B-roll: pasta `broll\` do projeto; faltando, buscar Pexels/Pixabay ou listar prompts de IA para a Dani gerar.

**Apresentar o EDL em tabela legível e AGUARDAR aprovação.**

## FASE 3 — Montagem

Executar o EDL aprovado (video-use + ffmpeg): cortes, B-roll, punch-ins, molduras arredondadas, cartões. Manter 1080×1920, 30fps CFR, `-crf 18`, áudio normalizado a -14 LUFS.

## FASE 4 — Legendas e motion (HyperFrames)

Sobrescrever o padrão de legenda do video-use pelo padrão Dani:
- 1–4 palavras por tela, sans-serif bold branca com contorno.
- Uma palavra de impacto por tela em fonte script itálica dourada `#D4AF37` (máx. 1).
- Cartões de seção: fundo #0D0D0D, texto script dourado, 1–1,5s.
- Assinatura "LIBERDADE · PATRIMÔNIO · SOBERANIA" na abertura ou CTA.
- Rodar `npx hyperframes lint` antes de qualquer render de composição.

## FASE 5 — Piloto (GATE 2)

Renderizar SÓ os primeiros 15s do vídeo final e apresentar o arquivo à Dani. Prosseguir apenas após aprovação; correções voltam à fase correspondente.

## FASE 6 — Final + validação

1. Render completo.
2. Deixar a autoavaliação do video-use rodar nos pontos de corte E extrair 1 frame a cada 2s (`ffmpeg -vf fps=0.5`) para inspeção visual: frames pretos, legendas cortadas, B-roll dessincronizado.
3. Conferir duração vs. planejada (±2s) e sincronia de áudio.
4. Entregar `edit\final.mp4` renomeado para `FINAL_<projeto>.mp4` e apresentar.

## Regras gerais

- Comunicar progresso por fase, em português, sem jargão desnecessário.
- Se existir `estilo.md` ou `TAY_DANTAS_REFERENCIA_COMPLETA.md` local, ele prevalece sobre o desta skill.
- Pedidos parciais ("só corta", "só legenda") executam apenas as fases correspondentes.
- Registrar decisões no `project.md` para a próxima sessão continuar de onde parou.

## Regras gerais da Dani (valem para os três estilos)

- **Duração máxima: 3 minutos.** Para encurtar, cortar repetições (quando ela fala a mesma coisa duas vezes), tropeços e trechos fora do tema; informar o que saiu.
- **Nunca cortar palavra** (início, meio ou fim) e manter a última palavra inteira, com o fade só depois dela.
- **Nada sobre o rosto:** nem legenda, card, B-roll, tarja, sombra ou caixa. Sem tarjas/degradês pretos sobre ela.
- Remover silêncios, respiros e ruídos sem deixar a fala artificial; voz a −14 LUFS.
- Headline (quando houver) só nos 10 s iniciais, no topo, com sombra preta, nunca sobre a cabeça/rosto.
- Área segura do Instagram: topo 200–250 px, base 350–400 px, laterais 60 px.
- Sem laranja, sem roxo, sem neon, sem emojis, sem bolinhas decorativas. (O dourado #D4AF37 deste estilo é amarelo-ouro, não laranja.)
- Quando citar marcas (Visa, Mastercard, J.P.Morgan…), usar logos oficiais que a Dani enviar.
- Entrega: 1080×1920, H.264 crf 18 + AAC, 30 fps, salvo em `C:\Users\Dani\Dropbox\fotos dani\videos\`.
