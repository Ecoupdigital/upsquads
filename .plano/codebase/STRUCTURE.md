# Estrutura do Codebase

**Data da Analise:** 2026-04-01

## Layout de Diretorios

```
up-squads/
├── agents/                              # Agente orquestrador global
│   └── upsquads-orquestrador.md         # Diagnostica e roteia para squad correta
├── bin/                                 # Installer executavel via npx
│   └── install.js                       # Onboarding interativo + copia arquivos para ~/.claude/
├── commands/                            # Slash commands para Claude Code
│   └── upsq.md                          # Comando /upsq — entry point do usuario
├── lib/                                 # Utilitarios CLI
│   └── squad-tools.cjs                  # list, info, install, remove, installed
├── skills/                              # 9 skills compartilhadas (ferramentas dos agentes)
│   ├── apify/SKILL.md                   # Web scraping via Apify Actors
│   ├── carrossel-estilo-noticia/        # Carrosseis estilo manchete jornalistica
│   │   ├── SKILL.md
│   │   └── scripts/
│   ├── carrossel-twitter/               # Carrosseis estilo tweet (PNG via Gemini + HTML/CSS)
│   │   ├── SKILL.md
│   │   ├── fonts/
│   │   └── scripts/
│   ├── image-creator/SKILL.md           # Renderiza HTML/CSS em PNG via Playwright
│   ├── image-fetcher/SKILL.md           # Busca logos, screenshots e assets visuais
│   ├── instagram-comments-scraper/      # Extrai comentarios de posts Instagram
│   │   ├── SKILL.md
│   │   └── references/
│   ├── instagram-publisher/             # Publica carrosseis no Instagram via Graph API
│   │   ├── SKILL.md
│   │   └── scripts/
│   ├── instagram-scraper/               # Extrai e transcreve posts de perfis Instagram
│   │   ├── SKILL.md
│   │   └── references/
│   └── youtube-transcript/SKILL.md      # Baixa transcricoes de videos YouTube
├── squads/                              # 11 squads de agentes especializados
│   ├── registry.yaml                    # Indice central de todas as squads
│   ├── advisory-board/                  # 11 agentes — conselho estrategico
│   ├── brand-squad/                     # 15 agentes — branding e posicionamento
│   ├── c-level-squad/                   # 6 agentes — gestao executiva (CEO, COO, CMO...)
│   ├── copy-squad/                      # 23 agentes — copywriting e direct response
│   ├── cybersecurity/                   # 15 agentes — pentest, red/blue team, AppSec
│   ├── data-squad/                      # 7 agentes — analytics, growth, retencao
│   ├── design-squad/                    # 8 agentes — design systems, UX, UI
│   ├── hormozi-squad/                   # 16 agentes — ofertas, leads, pricing, scaling
│   ├── movement/                        # 7 agentes — movimentos e comunidades
│   ├── storytelling/                    # 12 agentes — narrativa, pitch, apresentacoes
│   └── traffic-masters/                 # 16 agentes — Facebook, Google, YouTube Ads
├── workflows/                           # Workflows globais
│   └── squad.md                         # Workflow de roteamento do comando /upsq
├── config.yaml                          # Configuracao de model tiers (powerful/fast)
├── package.json                         # Manifesto npm (npx upsquads)
└── README.md                            # Documentacao do projeto
```

## Estrutura Padrao de Squad

Todas as 11 squads seguem exatamente a mesma estrutura:

```
squads/{squad-id}/
├── agents/                 # Agentes da squad (1 chief + N especialistas)
│   ├── {chief-name}.md     # Orquestrador da squad (tier 0)
│   └── {agent-name}.md     # Especialistas (tier 1+)
├── tasks/                  # Tasks executaveis
│   ├── diagnose.md         # Diagnostico inicial (presente em quase todas)
│   ├── review.md           # Revisao de output (presente em quase todas)
│   └── {task-name}.md      # Tasks especificas do dominio
├── workflows/              # Workflows multi-fase (YAML)
│   └── wf-{nome}.yaml      # Orquestracao de agentes com fases e checkpoints
├── config/                 # Configuracao da squad
│   └── config.yaml         # Tiers, agentes, handoffs, routing matrix
├── data/                   # Dados de referencia
│   └── {nome}.yaml         # Frameworks, catalogo de roteamento, etc.
├── checklists/             # Checklists de qualidade
│   └── {nome}.md           # Validacao de output antes da entrega
├── squad.yaml              # Metadados da squad (name, version, tags, components)
└── README.md               # Documentacao da squad
```

## Propositos dos Diretorios

**`agents/` (raiz):**
- Proposito: Agente orquestrador global que nao pertence a nenhuma squad
- Contem: Apenas `upsquads-orquestrador.md`
- Arquivos chave: `upsquads-orquestrador.md` (13.6k, contem registry completo de 11 squads com sinais de roteamento)

**`bin/`:**
- Proposito: Installer executavel via `npx upsquads`
- Contem: `install.js` (14k, Node.js puro sem dependencias externas)
- Arquivos chave: `install.js` — onboarding interativo, copia arquivos para `~/.claude/`, gera frontmatter para agentes

**`commands/`:**
- Proposito: Slash commands registrados no Claude Code
- Contem: `upsq.md` — definicao do comando `/upsq` com modos de uso
- Arquivos chave: `upsq.md` — referencia `@~/.claude/upsquads/workflows/squad.md`

**`lib/`:**
- Proposito: CLI utilitario para gerenciamento de squads (usado programaticamente pelos workflows)
- Contem: `squad-tools.cjs` (8.4k, CommonJS para compatibilidade com Node 16+)
- Arquivos chave: `squad-tools.cjs` — 5 comandos: list, info, install, remove, installed

**`skills/`:**
- Proposito: Ferramentas tecnicas compartilhadas que qualquer agente pode invocar
- Contem: 9 skills, cada uma com `SKILL.md` e opcionalmente `scripts/`, `fonts/`, `references/`
- Arquivos chave: Cada `SKILL.md` contem frontmatter (name, description) + instrucoes passo-a-passo

**`squads/`:**
- Proposito: Diretorio central com todas as 11 squads e o registry
- Contem: 11 subdiretorios de squad + `registry.yaml`
- Arquivos chave: `registry.yaml` — indice usado pelo CLI e orquestrador para listar/buscar squads

**`squads/{squad-id}/agents/`:**
- Proposito: Definicoes de agentes com persona, expertise e instrucoes
- Contem: Arquivos `.md` (~150-250 linhas cada) com persona completa
- O chief tem `chief` ou `chair` no nome do arquivo

**`squads/{squad-id}/tasks/`:**
- Proposito: Definicoes de tarefas executaveis com schema de I/O
- Contem: Arquivos `.md` com frontmatter YAML (Entrada, Saida, Checklist) + instrucoes

**`squads/{squad-id}/workflows/`:**
- Proposito: Orquestracoes multi-fase de agentes com dependencias
- Contem: Arquivos `.yaml` com phases, conditions, outputs e completion_criteria

**`squads/{squad-id}/config/`:**
- Proposito: Configuracao detalhada da squad (tiers, handoffs, routing)
- Contem: `config.yaml` com definicao completa de agentes, tiers e regras de roteamento

**`squads/{squad-id}/data/`:**
- Proposito: Dados de referencia usados por agentes (frameworks, catalogo de roteamento)
- Contem: Arquivos `.yaml` com frameworks, keywords, mapeamentos

**`squads/{squad-id}/checklists/`:**
- Proposito: Checklists de validacao de qualidade do output
- Contem: Arquivos `.md` com itens marcaveis `[ ]`, itens CRITICAL bloqueiam entrega

**`workflows/` (raiz):**
- Proposito: Workflows globais nao atrelados a nenhuma squad especifica
- Contem: `squad.md` — workflow de roteamento do comando `/upsq`

## Localizacoes Chave

**Entry Points:**
- `commands/upsq.md`: Comando `/upsq` — unico entry point do usuario
- `bin/install.js`: Installer `npx upsquads` — instalacao inicial
- `lib/squad-tools.cjs`: CLI programatico — usado por workflows via bash

**Configuracao:**
- `config.yaml`: Model tiers globais (chief=powerful, researcher=fast, etc.)
- `squads/registry.yaml`: Indice central de todas as squads (id, name, agents, description, tags)
- `squads/{squad-id}/config/config.yaml`: Configuracao completa por squad
- `squads/{squad-id}/squad.yaml`: Metadados da squad (name, version, tags, components)
- `package.json`: Manifesto npm (name: upsquads, version: 0.1.0, engines: node>=16.7.0)

**Logica Core:**
- `agents/upsquads-orquestrador.md`: Orquestrador global — diagnostico e roteamento
- `workflows/squad.md`: Workflow de roteamento do comando (6 modos)
- `lib/squad-tools.cjs`: Logica de instalacao/remocao de squads
- `bin/install.js`: Logica de onboarding e copia de arquivos

**Dados de Dominio:**
- `squads/{squad-id}/data/`: Frameworks, catalogo de roteamento, dados de referencia
- `squads/{squad-id}/checklists/`: Criterios de qualidade

## Onde Adicionar Novo Codigo

**Nova Squad:**
1. Criar diretorio `squads/{squad-id}/` seguindo a estrutura padrao (agents, tasks, workflows, config, data, checklists, squad.yaml, README.md)
2. Adicionar entrada no `squads/registry.yaml` com id, name, agents, description, tags, dominio
3. Adicionar squad no registro de roteamento do `agents/upsquads-orquestrador.md` (secao `<squads_registry>`)
4. Criar chief em `squads/{squad-id}/agents/{chief-name}.md` com logica de roteamento intra-squad
5. Criar agentes especialistas em `squads/{squad-id}/agents/`
6. Criar tasks em `squads/{squad-id}/tasks/`
7. Opcional: criar workflows em `squads/{squad-id}/workflows/`, config em `config/config.yaml`, data e checklists

**Novo Agente em Squad Existente:**
1. Criar arquivo `squads/{squad-id}/agents/{agent-name}.md` com persona completa
2. Atualizar `squads/{squad-id}/config/config.yaml` — adicionar agente no tier correto e nos handoffs
3. Atualizar `squads/{squad-id}/data/routing-catalog.yaml` se existir — adicionar keywords de roteamento
4. Atualizar contagem de agentes no `squads/registry.yaml`
5. Atualizar chief da squad se necessario (adicionar agente na routing matrix)

**Nova Task em Squad Existente:**
1. Criar arquivo `squads/{squad-id}/tasks/{task-name}.md` com frontmatter YAML (Entrada, Saida, Checklist) + instrucoes
2. Referenciar a task no chief da squad para que saiba quando usa-la
3. Opcional: adicionar no README da squad

**Nova Skill:**
1. Criar diretorio `skills/{skill-name}/`
2. Criar `skills/{skill-name}/SKILL.md` com frontmatter (name, description) + instrucoes passo-a-passo
3. Opcional: adicionar `scripts/` para scripts auxiliares, `references/` para exemplos
4. Skills sao automaticamente copiadas para `~/.claude/skills/` na instalacao

**Novo Workflow:**
- Global: criar em `workflows/{nome}.md`
- Por squad: criar em `squads/{squad-id}/workflows/wf-{nome}.yaml`
- Seguir padrao: phases com agent, task, depends_on, condition, outputs, checkpoint

## Convencoes de Nomeacao

**Diretorios de Squad:** kebab-case (ex: `copy-squad`, `traffic-masters`, `c-level-squad`)

**Arquivos de Agente:** kebab-case sem prefixo (ex: `gary-halbert.md`, `copy-chief.md`, `hormozi-offers.md`)

**Nome instalado do agente:** `sq-{squad-id}-{agent-name}` (ex: `sq-copy-squad-gary-halbert`, `sq-hormozi-squad-hormozi-chief`)

**Arquivos de Task:** kebab-case descritivo (ex: `write-headline.md`, `create-offer.md`, `analyze-instagram-profile.md`)

**Arquivos de Workflow:** prefixo `wf-` + kebab-case (ex: `wf-copy-review-cycle.yaml`, `wf-full-copy-project.yaml`)

**Arquivos de Skill:** Diretorio kebab-case + `SKILL.md` maiusculo (ex: `skills/instagram-scraper/SKILL.md`)

**Arquivos de Config:** Sempre `config.yaml` dentro de `config/`

**Arquivos de Dados:** kebab-case descritivo em `data/` (ex: `routing-catalog.yaml`, `copy-frameworks.yaml`)

## Destino de Instalacao

Apos `npx upsquads`, os arquivos ficam em:

```
~/.claude/
├── agents/
│   ├── upsquads-orquestrador.md          # Orquestrador global
│   ├── sq-copy-squad-copy-chief.md       # Chief (com frontmatter gerado)
│   ├── sq-copy-squad-gary-halbert.md     # Especialista (com frontmatter gerado)
│   └── ...                                # Todos agentes das squads instaladas
├── commands/
│   └── upsq.md                            # Comando /upsq
├── skills/
│   ├── instagram-scraper/SKILL.md         # Skills copiadas integralmente
│   └── ...
└── upsquads/
    ├── squads/                            # Dados completos de todas as squads
    │   ├── registry.yaml
    │   ├── copy-squad/
    │   │   ├── .installed                 # Marker de instalacao
    │   │   └── ...
    │   └── ...
    ├── lib/
    │   └── squad-tools.cjs                # CLI utilitario
    ├── workflows/
    │   └── squad.md                       # Workflow de roteamento
    └── VERSION                            # Versao instalada
```
