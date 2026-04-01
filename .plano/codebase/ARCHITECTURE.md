# Arquitetura

**Data da Analise:** 2026-04-01

## Visao Geral do Padrao

**Geral:** Multi-Agent Orchestration System (sistema de orquestracao multi-agente para Claude Code)

**Caracteristicas Chave:**
- Nao e uma aplicacao web/API — e um sistema de agentes AI que se instala no `~/.claude/` e opera dentro do Claude Code
- Arquitetura de squads: cada squad e um time autonomo com chief (orquestrador), agentes especialistas, tasks, workflows, checklists e dados
- Roteamento hierarquico em 3 niveis: comando `/upsq` -> orquestrador global -> chief da squad -> agente especialista
- Skills compartilhadas: ferramentas reutilizaveis que qualquer agente de qualquer squad pode invocar
- Instalacao sob demanda: squads sao instaladas/removidas individualmente via CLI Node.js

## Camadas

**Camada 1 — Entry Point (Comando):**
- Proposito: Ponto de entrada do usuario via slash command `/upsq`
- Localizacao: `commands/upsq.md`
- Contem: Definicao do comando com frontmatter YAML (name, description, allowed-tools, argument-hint)
- Depende de: `workflows/squad.md` (referenciado via `@~/.claude/upsquads/workflows/squad.md`)
- Usado por: Usuario final no Claude Code

**Camada 2 — Workflow de Roteamento:**
- Proposito: Parsear argumentos do comando e determinar modo de operacao (orquestrador, listar, instalar, remover, info, executar task)
- Localizacao: `workflows/squad.md`
- Contem: Logica de roteamento em 6 modos com condicoes, comandos bash para `squad-tools.cjs`, e templates de `Task()` para spawnar agentes
- Depende de: `lib/squad-tools.cjs` (CLI), `agents/upsquads-orquestrador.md` (agente orquestrador)
- Usado por: `commands/upsq.md`

**Camada 3 — Orquestrador Global:**
- Proposito: Diagnosticar necessidade do usuario e rotear para a squad correta
- Localizacao: `agents/upsquads-orquestrador.md`
- Contem: Protocolo de diagnostico em 3 passos (identificar dominio, perguntas de refinamento, handoff), registry completo de 11 squads com sinais de roteamento, logica de combinacao de squads
- Depende de: `squads/registry.yaml` (indice de squads), `lib/squad-tools.cjs` (verificar/instalar squads)
- Usado por: `workflows/squad.md` (modo orquestrador)

**Camada 4 — Squad Chiefs (Orquestradores de Squad):**
- Proposito: Receber demanda do orquestrador global e rotear para o agente especialista correto dentro da squad
- Localizacao: `squads/{squad-id}/agents/{chief-name}.md` (ex: `squads/copy-squad/agents/copy-chief.md`)
- Contem: Logica de roteamento intra-squad (awareness routing, medium routing), catalogo de especialistas, regras de colaboracao e escalacao
- Depende de: `squads/{squad-id}/config/config.yaml` (configuracao da squad), `squads/{squad-id}/data/routing-catalog.yaml` (mapeamento keywords->agentes)
- Usado por: Orquestrador global via `Task(subagent_type="sq-{squad}-{chief}")`

**Camada 5 — Agentes Especialistas:**
- Proposito: Executar tarefas especificas de copywriting, estrategia, design, etc. com persona e expertise real
- Localizacao: `squads/{squad-id}/agents/{agent-name}.md`
- Contem: Persona completa (arquetipo, tom, estilo, frameworks), principios core, instrucoes de execucao
- Depende de: `squads/{squad-id}/tasks/*.md` (definicoes de tasks), `skills/` (ferramentas compartilhadas)
- Usado por: Chiefs via `Task(subagent_type="sq-{squad}-{agent}")`

**Camada 6 — Tasks:**
- Proposito: Definir inputs, outputs, checklist e processo para cada tipo de tarefa executavel
- Localizacao: `squads/{squad-id}/tasks/{task-name}.md`
- Contem: Frontmatter YAML com schema de entrada/saida, checklist de validacao, e corpo markdown com instrucoes detalhadas
- Depende de: Nada (sao definicoes declarativas)
- Usado por: Agentes especialistas e chiefs

**Camada 7 — Skills (Ferramentas Compartilhadas):**
- Proposito: Capacidades tecnicas reutilizaveis (scraping, geracao de imagem, publicacao)
- Localizacao: `skills/{skill-name}/SKILL.md` (+ `scripts/` e `references/` opcionais)
- Contem: Instrucoes passo-a-passo para o agente executar via bash/playwright
- Depende de: Ferramentas externas (yt-dlp, ffmpeg, whisper, Playwright, Gemini API, Instagram Graph API, Apify)
- Usado por: Qualquer agente de qualquer squad

**Camada 8 — CLI de Gerenciamento:**
- Proposito: Instalar, remover e listar squads programaticamente
- Localizacao: `lib/squad-tools.cjs` (runtime), `bin/install.js` (installer npx)
- Contem: Logica Node.js para copiar agentes para `~/.claude/agents/`, gerar frontmatter YAML, gerenciar markers `.installed`
- Depende de: `squads/registry.yaml` (indice), filesystem `~/.claude/`
- Usado por: `workflows/squad.md` (via bash), `npx upsquads` (instalacao inicial)

## Fluxo de Dados

**Fluxo Principal — Usuario pede algo:**

1. Usuario digita `/upsq quero criar uma oferta irresistivel`
2. `commands/upsq.md` delega para `workflows/squad.md` com `$ARGUMENTS`
3. `workflows/squad.md` classifica como "texto livre" -> modo orquestrador com contexto
4. Spawna `upsquads-orquestrador` via `Task()` passando contexto do usuario
5. Orquestrador analisa sinais de roteamento, identifica `hormozi-squad`
6. Orquestrador verifica instalacao via `node squad-tools.cjs installed`
7. Se nao instalada, instala via `node squad-tools.cjs install hormozi-squad`
8. Orquestrador faz handoff via `Task(subagent_type="sq-hormozi-squad-hormozi-chief")` com contexto
9. Chief da hormozi-squad roteia para `hormozi-offers` (agente de ofertas)
10. Agente executa task `create-offer.md` usando frameworks de Hormozi

**Fluxo de Instalacao — npx upsquads:**

1. `bin/install.js` copia base para `~/.claude/upsquads/` (squads data, lib, workflows)
2. Copia orquestrador para `~/.claude/agents/upsquads-orquestrador.md`
3. Copia comando para `~/.claude/commands/upsq.md`
4. Copia skills para `~/.claude/skills/`
5. Onboarding interativo mostra cada squad e pergunta se quer instalar
6. Para cada squad aceita: copia agentes para `~/.claude/agents/sq-{squad}-{agent}.md` com frontmatter gerado
7. Cria marker `.installed` no diretorio da squad

**Fluxo de Execucao de Task Direta:**

1. Usuario digita `/upsq copy-squad write-headline`
2. Workflow verifica instalacao, le task `squads/copy-squad/tasks/write-headline.md`
3. Spawna chief `sq-copy-squad-copy-chief` com task definition no prompt
4. Chief analisa task e delega para `eugene-schwartz` (responsavel padrao)
5. Agente executa seguindo instrucoes da task e checklist

**Gerenciamento de Estado:**
- Nao ha estado persistente entre execucoes alem dos markers `.installed`
- Contexto e passado inteiramente via prompts de `Task()`
- Cada execucao de agente e stateless — todo contexto necessario esta no prompt

## Abstracoes Chave

**Squad:**
- Proposito: Unidade autonoma de agentes especializados em um dominio
- Exemplos: `squads/copy-squad/`, `squads/hormozi-squad/`, `squads/traffic-masters/`
- Padrao: Estrutura padronizada com 7 subdiretorios (agents, tasks, workflows, config, data, checklists) + `squad.yaml` + `README.md`
- Todas as 11 squads seguem exatamente a mesma estrutura

**Agent (arquivo .md):**
- Proposito: Definicao completa de persona AI com expertise, tom, frameworks e instrucoes
- Exemplos: `squads/copy-squad/agents/gary-halbert.md`, `squads/hormozi-squad/agents/hormozi-offers.md`
- Padrao: Arquivo markdown com YAML frontmatter (gerado na instalacao) + definicao de persona + instrucoes de execucao
- Media de ~200 linhas por agente

**Task (arquivo .md):**
- Proposito: Definicao declarativa de tarefa executavel com schema de I/O
- Exemplos: `squads/copy-squad/tasks/write-headline.md`, `squads/hormozi-squad/tasks/create-offer.md`
- Padrao: Frontmatter YAML com campos Entrada/Saida/Checklist + corpo markdown com instrucoes

**Skill (diretorio com SKILL.md):**
- Proposito: Capacidade tecnica reutilizavel que agentes invocam
- Exemplos: `skills/instagram-scraper/SKILL.md`, `skills/carrossel-twitter/SKILL.md`
- Padrao: Frontmatter YAML (name, description) + instrucoes detalhadas com comandos bash

**Workflow (arquivo .yaml):**
- Proposito: Orquestracao multi-fase de agentes com dependencias e checkpoints
- Exemplos: `squads/copy-squad/workflows/wf-copy-review-cycle.yaml`, `squads/copy-squad/workflows/wf-full-copy-project.yaml`
- Padrao: Definicao YAML com phases, agents, conditions, outputs e completion_criteria

**Config (arquivo .yaml):**
- Proposito: Configuracao da squad com tiers de agentes, handoffs e cross-cutting concerns
- Exemplos: `squads/copy-squad/config/config.yaml`
- Padrao: Definicao completa de squad com tiers, agentes, routing matrix, handoffs e settings

## Pontos de Entrada

**Comando `/upsq` (usuario):**
- Localizacao: `commands/upsq.md`
- Gatilhos: Usuario digita `/upsq` com ou sem argumentos no Claude Code
- Responsabilidades: Delegar para workflow de roteamento

**`npx upsquads` (instalacao):**
- Localizacao: `bin/install.js`
- Gatilhos: Usuario executa `npx upsquads` no terminal
- Responsabilidades: Copiar arquivos para `~/.claude/`, onboarding interativo, instalar squads selecionadas

**`node squad-tools.cjs` (CLI programatico):**
- Localizacao: `lib/squad-tools.cjs`
- Gatilhos: Chamado por workflows e orquestrador via bash
- Responsabilidades: list, info, install, remove, installed

## Tratamento de Erros

**Estrategia:** Defensiva e orientada ao usuario
- Squads nao encontradas: CLI retorna lista de squads disponiveis
- Squad nao instalada ao executar task: workflow pergunta ao usuario se quer instalar
- Frontmatter ausente em agentes: installer gera frontmatter automaticamente
- Registry nao encontrado: CLI retorna erro com instrucao de instalacao

## Preocupacoes Transversais

**Logging:** Nao ha logging estruturado — output e via console.log no CLI e via resposta do agente no Claude Code

**Validacao:** Tasks definem checklist de validacao no frontmatter YAML. Checklists em `squads/{squad}/checklists/` validam qualidade de output.

**Autenticacao:** Nao aplicavel (sistema local). Skills que acessam APIs externas (Instagram, Apify, Gemini) requerem credenciais configuradas no ambiente.

**Model Tiers:** `config.yaml` na raiz define tiers de modelo (powerful=opus, fast=haiku) por tipo de agente (chief, writer, researcher, analyst, visual). Chiefs e writers usam modelo powerful; researchers, analysts e visual usam fast.

**Qualidade de Output:** Ciclo de revisao definido em workflows (ex: `wf-copy-review-cycle.yaml`) — especialista escreve, chief critica, especialista revisa, max 3 iteracoes com threshold de score 60%.
