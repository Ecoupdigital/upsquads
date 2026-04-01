# Convencoes de Codigo

**Data da Analise:** 2026-04-01

## Visao Geral

UPSquads e um projeto predominantemente baseado em **conteudo Markdown e YAML**, com uma camada fina de JavaScript (Node.js CommonJS) para instalacao e gerenciamento de squads. Nao e uma aplicacao web tradicional -- e um sistema de agentes AI instalavel via `npx`.

## Linguagens e Formatos

**Markdown (.md):** ~95% do codebase. Usado para agentes, tasks, workflows, skills, checklists e comandos.
**YAML (.yaml):** Configuracao de squads, registros, workflows estruturados, catalogs de roteamento.
**JavaScript (.js/.cjs):** Apenas 2 arquivos: `bin/install.js` e `lib/squad-tools.cjs`. Logica de instalacao e CLI.
**Python (.py):** Scripts auxiliares em skills (geracao de slides de carrossel).

## Padroes de Nomeacao

### Arquivos

**Agentes:** `kebab-case.md` usando nome da persona (ex: `gary-halbert.md`, `copy-chief.md`, `board-chair.md`)
- Chiefs/orquestradores: `<role>-chief.md` ou `<role>-chair.md`
- Especialistas: `<nome-pessoa>.md` ou `<funcao>.md`

**Tasks:** `kebab-case.md` com verbo no inicio (ex: `create-carousel-twitter.md`, `audit-brand.md`, `diagnose.md`)

**Workflows:** Prefixo `wf-` + `kebab-case.yaml` (ex: `wf-full-copy-project.yaml`, `wf-offer-creation.yaml`)

**Data/Catalogs:** `kebab-case.yaml` com sufixo descritivo (ex: `routing-catalog.yaml`, `copy-frameworks.yaml`, `platform-benchmarks.yaml`)

**Checklists:** `kebab-case.md` (ex: `output-quality.md`)

**Config:** `config.yaml` (sempre este nome, dentro de cada squad)

**Skills:** `SKILL.md` (maiusculo, arquivo principal de cada skill)

**Scripts:** `kebab-case.py` ou `kebab-case.js` dentro de `scripts/` da skill

### Diretorios

**Squads:** `kebab-case` (ex: `copy-squad`, `hormozi-squad`, `traffic-masters`, `advisory-board`)
**Skills:** `kebab-case` (ex: `carrossel-twitter`, `instagram-publisher`, `image-creator`)

### Variaveis e Funcoes (JavaScript)

**Funcoes:** `camelCase` (ex: `copyDirRecursive`, `loadRegistryFromSource`, `buildFrontmatter`, `installSquadAgents`)
**Variaveis:** `camelCase` (ex: `squadId`, `agentFiles`, `finalContent`, `isChief`)
**Constantes de caminho:** `camelCase` (ex: `packageRoot`, `claudeDir`, `upsquadsDir`)
**Constantes de cor (ANSI):** `camelCase` curto (ex: `green`, `cyan`, `bold`, `reset`)

### Variaveis e Funcoes (Python)

**Funcoes:** `snake_case` (ex: `img_to_b64`, `generate_photo`)
**Variaveis:** `snake_case` (ex: `output_path`, `skill_dir`)
**Constantes:** `UPPER_SNAKE_CASE` (ex: `SKILL_DIR`, `GEMINI_SCRIPT`, `DEFAULT_AVATAR`, `DEFAULT_MODEL`)

### Identificadores YAML

**Chaves:** `snake_case` em config de squads (ex: `entry_agent`, `display_name`, `primary_agent`)
**IDs de squad:** `kebab-case` (ex: `copy-squad`, `hormozi-squad`)
**IDs de agente:** `kebab-case` (ex: `gary-halbert`, `copy-chief`)
**IDs de workflow:** Prefixo `wf-` + `kebab-case` (ex: `wf-full-copy-project`)

## Estilo de Codigo JavaScript

### Modulo e Imports

**`lib/squad-tools.cjs` e `bin/install.js`:** Usam CommonJS (`require`/`module.exports`).
```javascript
const fs = require('fs');
const path = require('path');
const readline = require('readline');
```

**`skills/instagram-publisher/scripts/publish.js`:** Usa ESM (`import`/`export`).
```javascript
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
```

**Regra:** Codigo de instalacao/CLI usa CommonJS. Scripts de skills podem usar ESM.

### Funcoes

- Funcoes sao declaradas com `function` (nao arrow functions no escopo de modulo).
- Arrow functions usadas apenas em callbacks curtos (`.map()`, `.filter()`, `.forEach()`).
- Funcoes `async` usadas quando ha operacoes assinc ronas (ex: `onboarding()`, `main()`).

```javascript
// Padrao: function declaration
function copyDirRecursive(src, dest) {
  fs.mkdirSync(dest, { recursive: true });
  // ...
}

// Callback curto: arrow
const files = fs.readdirSync(agentsDir).filter(f => f.endsWith('.md'));
```

### Tratamento de Erros

**JavaScript (CLI tools):**
- Funcao `error(msg)` centralizada que faz `console.error` + `process.exit(1)`.
- Suporta modo `--raw` (output JSON) vs modo humano.
- `main().catch()` no entry point para erros nao capturados.

```javascript
function error(msg) {
  if (raw) {
    console.log(JSON.stringify({ error: msg }));
  } else {
    console.error(`Error: ${msg}`);
  }
  process.exit(1);
}
```

**JavaScript (publish.js):**
- Throw `new Error()` com mensagens descritivas incluindo status HTTP.
- Validacao de inputs no inicio de `main()` com throws.

```javascript
if (!res.ok) throw new Error(`createChildContainer failed [${res.status}]: ${await res.text()}`);
```

**Python (scripts):**
- `subprocess.run()` com `capture_output=True` e verificacao de `returncode`.
- Print de erros em `sys.stderr`.

### Output e CLI

- Modo `--raw`: output em JSON (para consumo por agentes).
- Modo normal: output formatado com cores ANSI para terminal.
- Cores definidas como constantes simples no topo do arquivo.

```javascript
const green = '\x1b[32m';
const cyan = '\x1b[36m';
const reset = '\x1b[0m';
```

## Estrutura de Agentes (.md)

### Formato de Agente de Squad

Agentes de squad NAO possuem frontmatter YAML proprio. O frontmatter e gerado automaticamente pelo installer (`buildFrontmatter()`).

**Padrao de conteudo de agente:**

```markdown
# Nome do Agente

> ACTIVATION-NOTICE: Descricao curta do que o agente faz (max ~120 chars)

## COMPLETE AGENT DEFINITION

```yaml
agent:
  name: "Nome"
  id: agent-id
  title: "Titulo — Subtitulo"
  icon: "emoji"
  tier: 0|1a|1b|1c|1d
  squad: squad-id
  whenToUse: "Quando ativar este agente"

persona_profile:
  archetype: Tipo
  communication:
    tone: tom1, tom2, tom3
    style: "Descricao do estilo"
    greeting: "Frase de abertura"

persona:
  role: "Papel"
  identity: "Identidade"
  style: "Estilo"
  focus: "Foco"

core_principles:
  - "Principio 1"
  - "Principio 2"
```

### Frontmatter Gerado (agents instalados)

O installer gera automaticamente:
```yaml
---
name: sq-{squad-id}-{agent-name}
description: "Extraido do ACTIVATION-NOTICE"
tools: Read, Write, Bash, Glob, Grep, WebFetch, WebSearch, AskUserQuestion
color: blue|yellow  # blue para chiefs, yellow para especialistas
---
```

### Hierarquia de Tiers

- **Tier 0:** Chief/Orquestrador (1 por squad). Roteia, nao executa.
- **Tier 1a-1d:** Especialistas organizados por sub-grupo tematico.

## Estrutura de Tasks (.md)

Tasks usam frontmatter YAML estruturado:

```yaml
---
task: nomeDoMetodo()
responsavel: "@agent-id"
responsavel_type: Agent
atomic_layer: Task
elicit: true

Entrada:
  - campo: nome_do_campo
    tipo: string|number|file[]
    origem: User Input
    obrigatorio: true|false
    default: "valor"

Saida:
  - campo: nome_saida
    tipo: string|file[]
    destino: Filesystem|Console
    persistido: true|false

Checklist:
  - "[ ] Item de verificacao"

Skills:
  - skill-name
---
```

## Estrutura de Skills (SKILL.md)

Skills usam frontmatter simples:

```yaml
---
name: skill-name
description: "Descricao longa da skill"
user-invocable: true|false
---
```

Corpo do SKILL.md: documentacao completa com exemplos de uso, workflows, parametros e outputs.

## Estrutura de Workflows (.yaml)

```yaml
workflow:
  id: wf-nome
  name: "Nome Legivel"
  version: "1.0.0"
  description: |
    Descricao multilinea
  trigger: "*trigger-pattern"
  entry_agent: agent-id
  type: sequential
  sequence:
    - agent: agent-id
      action: nome-acao
      creates: nome-output

phases:
  - id: phase_N
    name: "Nome da Fase"
    agent: agent-id
    task: task-file.md
    outputs:
      - nome: "tipo"
    checkpoint:
      gate: "Condicao de passagem"
      veto: "Condicao de bloqueio"
```

## Estrutura de Config de Squad (config.yaml)

```yaml
squad:
  name: squad-id
  display_name: "Nome Visivel"
  version: "1.0.0"
  domain: "Descricao do dominio"
  entry_agent: chief-id

tiers:
  tier_0:
    name: "Orchestration"
    agents: [chief-id]

agents:
  agent-id:
    file: agents/agent.md
    tier: 0|1a|1b
    icon: "emoji"
    focus: "Foco curto"

handoffs:
  agent-id:
    routes_to: [lista-de-agentes]
    collaborates_with: [lista]
    escalates_to: [lista]

cross_cutting:
  quality_standards:
    min_score: 7.0
```

## Organizacao de Imports (JavaScript)

**Ordem:**
1. Modulos nativos do Node.js (`fs`, `path`, `readline`, `os`)
2. Nao ha dependencias externas (zero deps no package.json)

## Convencoes de Documentacao

- Documentacao em **portugues brasileiro** para conteudo voltado ao usuario.
- Documentacao interna de agentes em **ingles** (ACTIVATION-NOTICE, persona definitions, frameworks).
- Comentarios em codigo JavaScript: **ingles** com JSDoc-style no topo do arquivo.
- README.md: **portugues brasileiro**.

## Idioma dos Agentes

- Agentes sao definidos em **ingles** (persona, frameworks, core principles).
- O orquestrador (`upsquads-orquestrador.md`) e comandos (`upsq.md`) sao em **portugues brasileiro**.
- Workflows top-level (`squad.md`) em **portugues brasileiro**.
- Workflows de squad (`wf-*.yaml`) em **ingles**.

## Padrao de Parsing YAML Manual

O codebase NAO usa biblioteca YAML. O parsing de `registry.yaml` e feito manualmente linha por linha tanto em `bin/install.js` quanto em `lib/squad-tools.cjs`:

```javascript
for (const line of content.split('\n')) {
  const trimmed = line.trim();
  if (trimmed.startsWith('- id:')) {
    current = { id: trimmed.replace('- id:', '').trim() };
  } else if (current && trimmed.startsWith('name:')) {
    current.name = trimmed.replace('name:', '').trim().replace(/^["']|["']$/g, '');
  }
  // ...
}
```

**Regra:** Manter zero dependencias externas. Parsing manual e intencional.

## Padrao de Deteccao de Chiefs

Chiefs/orquestradores sao identificados por padrao de nome:
```javascript
const isChief = agentName.includes('chief') || agentName.includes('chair') || agentName.includes('orchestr');
```

Use `chief`, `chair` ou `orchestr` no nome do arquivo de agentes orquestradores.

## Padrao de Markers de Instalacao

Squads instaladas recebem um arquivo `.installed` no diretorio da squad:
```javascript
const markerPath = path.join(getSquadsDir(), squadId, '.installed');
fs.writeFileSync(markerPath, new Date().toISOString(), 'utf8');
```
