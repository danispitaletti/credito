# Instalação — video-use + HyperFrames (Windows)

Executar uma única vez neste computador. Pré-requisitos já presentes: ffmpeg v8.1.2 no PATH, Claude Code instalado. Verificar Node.js e Python:

```powershell
node --version   # precisa ser 18+; se não existir, instalar de https://nodejs.org (LTS)
python --version # 3.10+
```

## 1. video-use (motor de edição: cortes, legendas, autoavaliação)

Repositório oficial: https://github.com/browser-use/video-use

```powershell
git clone https://github.com/browser-use/video-use "C:\dani video hunter editora\ferramentas\video-use"
cd "C:\dani video hunter editora\ferramentas\video-use"
pip install -e . --break-system-packages
```

Registrar como skill do Claude Code (Windows não tem symlink fácil — copiar ou usar junction):

```powershell
New-Item -ItemType Junction -Path "$env:USERPROFILE\.claude\skills\video-use" -Target "C:\dani video hunter editora\ferramentas\video-use"
```

**API key da ElevenLabs (obrigatória):** o video-use transcreve com o Scribe da ElevenLabs (timestamps palavra a palavra). Criar conta em https://elevenlabs.io, pegar a key em Settings → API Keys, e:

```powershell
cd "C:\dani video hunter editora\ferramentas\video-use"
copy .env.example .env
# editar .env e colocar: ELEVENLABS_API_KEY=sua_key
```

O plano gratuito da ElevenLabs dá uma cota mensal de transcrição; vídeos curtos (reels) consomem pouco. Alternativa sem custo: whisper local (`pip install openai-whisper --break-system-packages`) — mas aí a decupagem é manual via ffmpeg, sem o motor do video-use.

## 2. HyperFrames (motion graphics e legendas animadas)

O video-use já chama o HyperFrames via `npx --yes hyperframes ...` quando precisa — não requer instalação global. Para ter os blocos e skills oficiais disponíveis:

```powershell
npx skills add heygen-com/hyperframes
```

Documentação: https://github.com/heygen-com/hyperframes

## 3. Estrutura de pastas por projeto

```
C:\dani video hunter editora\<nome-do-projeto>\
├── bruto.mp4     # gravação original (nunca sobrescrever)
├── roteiro.md    # roteiro do vídeo (se existir)
├── broll\        # clipes de cobertura (stock, IA, prints)
└── edit\         # o video-use gera tudo aqui, incluindo final.mp4
```

## 4. Teste do pipeline

Abrir o Claude Code NA PASTA do projeto (`cd` até ela) e pedir:

> "Edita o bruto dessa pasta usando a skill editar-video-dani"

Primeiro teste ideal: o projeto dos milionários saindo dos países (roteiro e decupagem já prontos).
