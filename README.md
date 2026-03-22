# UPSquads

Squads de agentes AI especializados para Claude Code. Times prontos de copywriters, estrategistas, designers, growth hackers e mais — direto na sua IDE.

## O que e

UPSquads instala **times de agentes AI especializados** no seu Claude Code. Cada squad tem agentes com personalidades, frameworks e expertise reais:

- A **Copy Squad** tem 22 copywriters lendarios — Gary Halbert, Eugene Schwartz, David Ogilvy, Dan Koe e mais
- A **Hormozi Squad** aplica os frameworks de Alex Hormozi — Grand Slam Offers, Value Equation, CLOSER
- A **Design Squad** tem Brad Frost (Atomic Design), Dan Mall e especialistas em UX/UI
- A **Traffic Masters** tem 16 especialistas em Facebook Ads, Google Ads, YouTube Ads

Nao sao agentes genericos. Sao **personas com expertise real** que colaboram via um chief (orquestrador).

## Instalacao

```bash
npx upsquads
```

O onboarding interativo mostra cada squad e pergunta quais voce quer instalar.

```bash
# Instalar todas as squads de uma vez
npx upsquads --all

# Remover
npx upsquads --uninstall
```

## Squads disponiveis

| Squad | Agentes | Dominio |
|-------|---------|---------|
| **Copy Squad** | 23 | Copywriting — headlines, VSLs, emails, landing pages, carrosseis |
| **Hormozi Squad** | 16 | Crescimento — ofertas, leads, pricing, vendas, scaling |
| **Brand Squad** | 15 | Branding — posicionamento, identidade, naming, arquitetura |
| **Traffic Masters** | 16 | Trafego pago — Facebook, Google, YouTube Ads, scaling |
| **Cybersecurity** | 15 | Seguranca — pentest, red team, AppSec, incident response |
| **Storytelling** | 12 | Narrativa — pitches, apresentacoes, manifestos |
| **Advisory Board** | 11 | Conselho estrategico — Ray Dalio, Naval Ravikant, Peter Thiel |
| **Design Squad** | 8 | Design — design systems, UX, UI, componentes |
| **Data Squad** | 7 | Dados — analytics, growth, retencao, CLV |
| **Movement** | 7 | Movimentos — comunidades, identidade coletiva, impacto |
| **C-Level Squad** | 6 | Gestao executiva — CEO, COO, CMO, CTO, CAIO |

**Total: 11 squads, 136 agentes**

## Como usar

### Orquestrador inteligente

```
/upsq
```

O orquestrador faz perguntas para entender sua necessidade e direciona para a squad certa. Se a squad nao estiver instalada, oferece instalar.

### Com contexto direto

```
/upsq quero criar uma oferta irresistivel
/upsq preciso de copy para um carrossel sobre IA
/upsq analisar o perfil @frankcosta no instagram
/upsq meu CPA esta muito alto, preciso otimizar
```

O orquestrador identifica a squad pelo contexto e pula direto pro handoff.

### Gerenciar squads

```
/upsq listar                      # Ver todas as squads
/upsq instalar copy-squad         # Instalar uma squad
/upsq remover hormozi-squad       # Remover uma squad
/upsq copy-squad                  # Ver detalhes da squad
/upsq copy-squad create-carousel-twitter   # Executar task especifica
```

## Skills incluidas

UPSquads vem com 9 skills que os agentes usam como ferramentas:

| Skill | O que faz |
|-------|-----------|
| **carrossel-twitter** | Gera carrosseis estilo tweet (PNG via Gemini + HTML/CSS) |
| **carrossel-estilo-noticia** | Carrosseis estilo manchete jornalistica (foto + gradiente + titulo) |
| **image-creator** | Renderiza qualquer HTML/CSS em PNG via Playwright |
| **image-fetcher** | Busca logos, screenshots e assets visuais da web |
| **instagram-publisher** | Publica carrosseis direto no Instagram via Graph API |
| **instagram-scraper** | Extrai e transcreve posts de perfis Instagram |
| **instagram-comments-scraper** | Extrai comentarios de posts para analise de audiencia |
| **youtube-transcript** | Baixa transcricoes de videos do YouTube |
| **apify** | Web scraping robusto via Apify Actors (Instagram, YouTube, Twitter, TikTok) |

## Exemplos

### Criar carrossel a partir de uma noticia

```
/upsq quero criar um carrossel sobre essa noticia: https://blog.google/...
```

O orquestrador direciona para a **Copy Squad**, que:
1. Extrai o conteudo da URL
2. Roteia para o copywriter mais adequado (Dan Koe para educativo, Ben Settle para provocativo)
3. Gera a copy dos 7 slides
4. Usa a skill `carrossel-twitter` para gerar os PNGs
5. Opcionalmente publica via `instagram-publisher`

### Analisar concorrente

```
/upsq analisar os criativos do @concorrente no instagram
```

Direciona para **Traffic Masters**, que:
1. Usa `instagram-scraper` para extrair posts
2. Usa `instagram-comments-scraper` para engajamento
3. Analisa padroes visuais e de copy
4. Entrega swipe file de criativos + recomendacoes

### Criar oferta irresistivel

```
/upsq quero criar uma oferta para meu curso de IA
```

Direciona para **Hormozi Squad**, que:
1. Aplica o framework Grand Slam Offers
2. Define Value Equation (Dream Outcome, Likelihood, Time, Effort)
3. Cria stack de valor com bonus
4. Define pricing e garantia

## Standalone vs com UP

UPSquads funciona de forma **100% independente**. Nao precisa do UP instalado.

Se voce tambem usa o [UP](https://github.com/Ecoupdigital/up-cc), eles coexistem perfeitamente — `/upsq` para squads, `/up:*` para spec-driven development.

## Estrutura do projeto

```
upsquads/
├── bin/install.js          # Installer com onboarding interativo
├── lib/squad-tools.cjs     # CLI: list, info, install, remove
├── squads/                 # 11 squads com agentes, tasks e workflows
│   ├── registry.yaml       # Indice de squads
│   ├── copy-squad/
│   │   ├── agents/         # 23 agentes .md
│   │   └── tasks/          # Tasks executaveis
│   ├── hormozi-squad/
│   └── ...
├── skills/                 # 9 skills (ferramentas dos agentes)
├── agents/                 # Orquestrador
├── commands/               # /upsq command
├── workflows/              # Workflow de roteamento
└── config.yaml             # Model tiers (powerful/fast)
```

## Licenca

MIT
