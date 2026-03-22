---
name: upsq
description: Gerenciar e usar squads (times de agentes especializados por dominio)
argument-hint: "[instalar|remover|listar|<squad-name>] [<task>]"
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
  - Task
  - AskUserQuestion
---
<objective>
Gerenciar e usar squads — times de agentes AI especializados por dominio (negocio, copy, branding, trafego, etc.).

**Modos de uso:**
- `/upsq` — Ativa o orquestrador que faz perguntas e direciona para a squad certa
- `/upsq listar` — Lista squads disponiveis e status de instalacao
- `/upsq instalar <nome>` — Instala uma squad (agentes ficam disponiveis)
- `/upsq remover <nome>` — Remove uma squad instalada
- `/upsq <nome>` — Mostra detalhes da squad (agentes, tasks, workflows)
- `/upsq <nome> <task>` — Executa uma task especifica de uma squad
</objective>

<execution_context>
@~/.claude/upsquads/workflows/squad.md
</execution_context>

<context>
$ARGUMENTS

Squads sao times de agentes AI especializados por dominio. Cada squad tem um chief (orquestrador) que roteia para especialistas.
</context>

<process>
Execute the squad workflow from @~/.claude/upsquads/workflows/squad.md end-to-end.
Parse $ARGUMENTS to determine the mode (orchestrator, list, install, remove, info, execute task).
</process>
