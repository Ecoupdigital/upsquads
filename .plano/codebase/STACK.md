# Stack de Tecnologia

**Data da Analise:** 2026-04-01

## Linguagens

**Principal:**
- JavaScript (Node.js) — CLI installer (`bin/install.js`), squad management (`lib/squad-tools.cjs`), Instagram publisher (`skills/instagram-publisher/scripts/publish.js`)
- Python 3 — Scripts de geracao de imagem para carrosseis (`skills/carrossel-twitter/scripts/generate_slide.py`, `skills/carrossel-estilo-noticia/scripts/generate_slide.py`)

**Secundaria:**
- Markdown (.md) — Definicoes de agentes (259 arquivos .md em `squads/`), skills, tasks, workflows, commands
- YAML — Configuracao de squads (`squads/*/config/config.yaml`), registry (`squads/registry.yaml`), workflows (`squads/*/workflows/*.yaml`), model tiers (`config.yaml`)
- HTML/CSS — Templates de slides renderizados via Playwright (`skills/carrossel-twitter/scripts/compose_html.py` gera HTML)

## Runtime

**Ambiente:**
- Node.js >= 16.7.0 (definido em `package.json` campo `engines`)

**Gerenciador de Pacotes:**
- npm (inferido pelo `package.json`)
- Lockfile: ausente (projeto nao tem `package-lock.json` — zero dependencias npm)

**Observacao:** O projeto tem ZERO dependencias npm. Nao ha campo `dependencies` ou `devDependencies` no `package.json`. Todo codigo usa apenas modulos built-in do Node.js (`fs`, `path`, `readline`, `os`).

## Frameworks

**Core:**
- Nenhum framework. O projeto e uma colecao de scripts Node.js/Python puros + arquivos Markdown que se integram ao ecossistema Claude Code.

**Testes:**
- Nao detectado. Sem framework de testes configurado.

**Build/Dev:**
- Nao detectado. Sem bundler, transpiler ou build step. Codigo e executado diretamente.

## Dependencias Chave

**Zero dependencias npm declaradas.**

**Dependencias de runtime externas (nao gerenciadas pelo projeto):**

Criticas:
- **Claude Code** — Ambiente de execucao principal. Agentes (.md) e commands sao consumidos pelo Claude Code CLI. Ferramentas usadas: `Read`, `Write`, `Bash`, `Glob`, `Grep`, `WebFetch`, `WebSearch`, `AskUserQuestion`, `Task` (subagentes)
- **Playwright MCP** — Usado por skills de scraping (instagram-scraper, instagram-comments-scraper, image-creator, image-fetcher, carrossel-twitter) para navegacao web, screenshots e interacao com DOM

Infraestrutura:
- **yt-dlp** — Download de videos/legendas do YouTube e Instagram (`pip install yt-dlp`)
- **ffmpeg** — Extracao de audio de videos para transcricao (`apt install ffmpeg`)
- **OpenAI Whisper** — Transcricao de audio de reels/videos (`pip install openai-whisper`, modelo `medium`)
- **Gemini API** — Geracao de fotos para slides de carrossel (chamado via `skills/carrossel-twitter/scripts/generate_slide.py`)
- **Python 3** — Scripts de geracao de imagens (`python3` deve estar no PATH)

## Configuracao

**Ambiente:**
- `APIFY_TOKEN` — Token da API Apify para web scraping (configurado via `.mcp.json`)
- `INSTAGRAM_ACCESS_TOKEN` — Token da Graph API do Instagram para publicacao (configurado em `.env`)
- `INSTAGRAM_USER_ID` — ID do usuario Instagram Business (configurado em `.env`)
- `GEMINI_API_KEY` — Chave da API Gemini para geracao de imagens (usado pelo script `generate_slide.py`)
- Arquivo `.env` presente — contem configuracao de ambiente (nao lido por seguranca)

**Model Tiers (`config.yaml`):**
- `chief: powerful` — Agentes orquestradores usam modelo mais forte (Opus)
- `writer: powerful` — Copywriters e estrategistas usam modelo forte
- `researcher: fast` — Agentes de pesquisa usam modelo rapido (Haiku)
- `analyst: fast` — Agentes de analise de dados usam modelo rapido
- `visual: fast` — Agentes de design/visual usam modelo rapido

**Instalacao:**
- `npx upsquads` — Installer interativo que copia arquivos para `~/.claude/`
- `npx upsquads --all` — Instalar todas as squads sem interacao
- `npx upsquads --uninstall` — Remover tudo de `~/.claude/`

**Destinos de instalacao (em `~/.claude/`):**
- `~/.claude/agents/` — Agentes .md com frontmatter (prefixo `sq-` para squads, `upsquads-` para orquestrador)
- `~/.claude/upsquads/squads/` — Dados das squads (tasks, workflows, config, data)
- `~/.claude/upsquads/lib/` — CLI tools (`squad-tools.cjs`)
- `~/.claude/upsquads/workflows/` — Workflows de roteamento
- `~/.claude/commands/` — Comando `/upsq`
- `~/.claude/skills/` — Skills compartilhadas (9 skills)

## Requisitos de Plataforma

**Desenvolvimento:**
- Node.js >= 16.7.0
- Python 3 (para scripts de geracao de imagens)
- Claude Code instalado com Playwright MCP configurado
- `yt-dlp`, `ffmpeg`, `whisper` no PATH (para skills de scraping/transcricao)
- Acesso a internet (APIs externas: Instagram, Gemini, Apify, catbox.moe)

**Producao/Distribuicao:**
- Publicado como pacote npm (`npx upsquads`)
- Instala-se em `~/.claude/` do usuario
- Nao ha servidor, banco de dados ou deploy — e uma CLI tool que estende o Claude Code
- Licenca: MIT
