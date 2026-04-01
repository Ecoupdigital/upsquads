# Integracoes Externas

**Data da Analise:** 2026-04-01

## APIs e Servicos Externos

**Geracao de Imagens:**
- **Google Gemini API** — Geracao de fotos para slides de carrossel
  - SDK/Cliente: Script Python customizado em `skills/carrossel-twitter/scripts/generate_slide.py`
  - Auth: `GEMINI_API_KEY` (variavel de ambiente)
  - Modelo default: Gemini Flash v1 (barato, ~R$0.12/slide)
  - Uso: Gera a foto de fundo dos slides, combinada com texto HTML/CSS renderizado via Playwright

**Instagram Graph API:**
- **Publicacao de carrosseis** — Upload e publicacao automatica no Instagram
  - SDK/Cliente: Script Node.js em `skills/instagram-publisher/scripts/publish.js`
  - Auth: `INSTAGRAM_ACCESS_TOKEN` + `INSTAGRAM_USER_ID` (variaveis de ambiente)
  - API base: `https://graph.facebook.com/v21.0`
  - Operacoes: `createChildContainer`, `createCarouselContainer`, `publishMedia`, `getPermalink`
  - Requer conta Instagram Business conectada a Pagina do Facebook
  - Token expira em 60 dias — renovacao manual via Graph API Explorer
  - Rate limit: 25 posts/24h via API

**Instagram Web (Scraping via Playwright):**
- **Scraping de perfis** — Extracao de posts, imagens e metadata
  - Implementacao: `skills/instagram-scraper/SKILL.md` (pipeline de 5 fases)
  - Auth: Login interativo via Playwright (credenciais pedidas ao usuario)
  - Exporta cookies para yt-dlp em formato Netscape
  - Extrai: nome, bio, seguidores, posts, screenshots de slides, transcricao visual via Claude vision
- **Scraping de comentarios** — Extracao de comentarios de primeiro nivel
  - Implementacao: `skills/instagram-comments-scraper/SKILL.md` (pipeline de 4 fases)
  - Auth: Mesmo login Playwright
  - Tecnica: Navegacao DOM via `img[alt*="profile picture"]` + 6 niveis de parent traversal
  - Limitacao: ~40-50 comentarios por expansao "View all"

**Apify:**
- **Web scraping robusto** — Scrapers pre-prontos para Instagram, YouTube, Twitter, TikTok, Google
  - SDK/Cliente: MCP server `@apify/actors-mcp-server` (configurado em `.mcp.json`)
  - Auth: `APIFY_TOKEN` (variavel de ambiente)
  - Actors populares: `apify/instagram-scraper`, `apify/youtube-scraper`, `apify/twitter-scraper`, `apify/tiktok-scraper`, `apify/google-search-scraper`
  - Uso: Alternativa mais confiavel ao scraping manual via Playwright
  - Skill: `skills/apify/SKILL.md`

**YouTube (via yt-dlp):**
- **Download de transcricoes** — Legendas manuais e auto-geradas
  - SDK/Cliente: CLI `yt-dlp` (instalado via pip)
  - Auth: Nenhuma (acesso publico) ou cookies do Instagram para videos restritos
  - Formatos: VTT (com timestamps), TXT (texto limpo deduplicado)
  - Fallback: Whisper para videos sem legendas
  - Skill: `skills/youtube-transcript/SKILL.md`

**Twitter/X (via fxtwitter):**
- **Extracao de tweets** — Acesso a conteudo de tweets sem autenticacao
  - SDK/Cliente: API publica `https://api.fxtwitter.com/user/status/ID`
  - Auth: Nenhuma
  - Uso: Extrair texto de tweets para geracao de carrosseis (`skills/carrossel-twitter/SKILL.md`)

**catbox.moe:**
- **Hosting temporario de imagens** — Upload de imagens para URLs publicas
  - SDK/Cliente: HTTP POST direto (`skills/instagram-publisher/scripts/publish.js` funcao `uploadToCatbox`)
  - Auth: Nenhuma (anonimo)
  - Endpoint: `https://catbox.moe/user/api.php`
  - Uso: Intermediario para publicacao no Instagram (Graph API requer URLs publicas)

**DuckDuckGo Image Search:**
- **Busca de imagens de referencia** — Logos, screenshots e fotos reais de temas
  - SDK/Cliente: Script Python `skills/gemini/scripts/search_references.py` (externo ao repo, em `~/.claude/skills/gemini/`)
  - Auth: Nenhuma
  - Uso: Buscar imagens reais de marcas/produtos para usar como referencia na geracao de fotos Gemini

## Armazenamento de Dados

**Bancos de Dados:**
- Nenhum. O projeto nao usa banco de dados.

**Armazenamento de Arquivos:**
- Sistema de arquivos local apenas
- Instalacao: `~/.claude/` (agentes, skills, commands, workflows)
- Temp: `/tmp/instagram-{username}/` (scraping intermediario, limpo apos uso)
- Output permanente: `/home/vault/00-inbox/` (arquivos .md de scraping)
- Marcadores: `.installed` (arquivo timestamp em cada squad instalada)

**Cache:**
- Nenhum sistema de cache formal
- Cookies do Instagram salvos em `/tmp/instagram_cookies.txt` (temporario, por sessao)

## Autenticacao e Identidade

**Provedor de Auth:**
- Nao aplicavel (CLI tool, sem usuarios)

**Autenticacao de servicos externos:**
- Instagram Graph API: Token de longa duracao (60 dias) via Facebook Developer App
- Instagram Web: Login interativo via Playwright (credenciais do usuario, 2FA suportado)
- Gemini API: API key direta
- Apify: API token via MCP server
- YouTube/Twitter/catbox: Sem autenticacao

## Monitoramento e Observabilidade

**Rastreamento de Erros:**
- Nenhum servico externo. Erros sao logados no console (`console.error`, `console.log`).

**Logs:**
- Console output apenas. Sem arquivo de log persistente.
- Skills de scraping tem tabelas de tratamento de erros documentadas nos respectivos `SKILL.md`.

## CI/CD e Deploy

**Hospedagem:**
- npm registry (pacote `upsquads`, instalado via `npx upsquads`)

**Pipeline CI:**
- Nao detectado. Sem GitHub Actions, sem CI configurado.

**Versionamento:**
- `package.json` version: `0.1.0`
- Arquivo `VERSION` criado em `~/.claude/upsquads/` durante instalacao

## Webhooks e Callbacks

**Entrada:**
- Nenhum. O projeto nao expoe endpoints HTTP.

**Saida:**
- Nenhum. Comunicacao com APIs e unidirecional (request/response).

## MCP Servers Utilizados

**Playwright MCP:**
- Ferramentas: `browser_navigate`, `browser_resize`, `browser_snapshot`, `browser_take_screenshot`, `browser_click`, `browser_fill_form`, `browser_wait_for`, `browser_run_code`, `browser_evaluate`
- Uso: Scraping de Instagram, renderizacao de HTML em PNG, captura de screenshots
- Configuracao: Deve estar no `.mcp.json` do usuario

**Apify MCP:**
- Ferramentas: `call-actor`, `fetch-actor-details`
- Uso: Web scraping robusto como alternativa ao Playwright manual
- Configuracao: `@apify/actors-mcp-server` em `.mcp.json` com `APIFY_TOKEN`

## Claude Code Integration

**Ferramentas nativas utilizadas pelos agentes:**
- `Read` — Leitura de arquivos e vision (transcricao visual de screenshots)
- `Write` — Criacao de arquivos de output
- `Bash` — Execucao de scripts Python/Node.js, yt-dlp, ffmpeg, whisper
- `Glob` — Busca de arquivos por padrao
- `Grep` — Busca de conteudo em arquivos
- `WebFetch` — Download de conteudo de URLs (artigos, paginas)
- `WebSearch` — Busca na web
- `AskUserQuestion` — Interacao com usuario (credenciais, confirmacoes)
- `Task` — Delegacao para subagentes (handoff entre orquestrador e chiefs)

**Padrao de delegacao (multi-agente):**
1. Comando `/upsq` → Workflow `workflows/squad.md`
2. Workflow spawna `upsquads-orquestrador` via `Task()`
3. Orquestrador diagnostica e spawna chief da squad via `Task(subagent_type="sq-<squad>-<chief>")`
4. Chief roteia para agente especialista via `Task()`
5. Agente executa task usando skills (Bash para scripts, Playwright MCP para browser)
