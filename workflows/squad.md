# Workflow: Squad Management & Routing

<step id="parse-arguments">
## 1. Parse Arguments

Analise `$ARGUMENTS` para determinar o modo de operacao.

**Ordem de prioridade para classificacao:**

1. Se vazio ou `consultar` → **Orquestrador** (sem contexto)
2. Se comeca com `listar` → **Listagem**
3. Se comeca com `instalar <nome>` → **Instalacao**
4. Se comeca com `remover <nome>` → **Remocao**
5. Se e EXATAMENTE o nome de uma squad conhecida (ex: `copy-squad`, `hormozi-squad`) → **Info**
6. Se e EXATAMENTE `<nome-squad> <task>` (ex: `hormozi-squad criar-oferta`) → **Execucao de Task**
7. **QUALQUER OUTRA COISA** (texto livre, perguntas, pedidos) → **Orquestrador com contexto**

**IMPORTANTE:** O caso 7 e o mais comum. Se o usuario digitou `/upsq quero criar uma oferta irresistivel` ou `/upsq preciso de copy para meu email`, isso NAO e um nome de squad — e uma pergunta que deve ir para o orquestrador com esse texto como contexto inicial.

Squads conhecidas: advisory-board, brand-squad, c-level-squad, copy-squad, cybersecurity, data-squad, design-squad, hormozi-squad, movement, storytelling, traffic-masters
</step>

<step id="mode-orchestrator" condition="modo == orquestrador (com ou sem contexto)">
## 2A. Modo Orquestrador

Spawne o agente orquestrador. Se `$ARGUMENTS` contiver texto livre (pergunta/pedido do usuario), passe como contexto inicial para que o orquestrador ja comece direcionando sem precisar perguntar do zero.

```
Task(
  subagent_type="upsquads-orquestrador",
  prompt="
    <objective>
    Diagnosticar a necessidade do usuario e direciona-lo para a squad especializada mais adequada.
    Siga o protocolo de diagnostico.

    IMPORTANTE:
    - Se o usuario ja descreveu o que precisa no contexto abaixo, NAO repita a pergunta inicial. Analise o pedido, identifique a squad, e va direto para as perguntas de refinamento ou handoff.
    - Se o contexto esta vazio, siga o diagnostico completo desde a pergunta 1.
    - Se ja da pra identificar a squad com confianca, pule direto pro handoff (verificar instalacao + spawnar chief).
    </objective>

    <user_context>
    $ARGUMENTS
    </user_context>

    <files_to_read>
    - $HOME/.claude/upsquads/squads/registry.yaml
    </files_to_read>
  ",
  description="Orquestrador de Squads"
)
```

Apos o orquestrador completar, apresente o resultado ao usuario.
</step>

<step id="mode-list" condition="modo == listar">
## 2B. Modo Listagem

Execute:
```bash
SQUADS=$(node "$HOME/.claude/upsquads/lib/squad-tools.cjs" list)
```

Apresente os resultados em formato visual:

```
╭─ Squads Disponiveis ─────────────────────────────────╮
│                                                        │
│  <nome>    [INSTALADA|---]  <N> agentes                │
│  <descricao curta>                                     │
│  ...                                                   │
│                                                        │
│  Comandos:                                             │
│  /upsq instalar <nome>  — Instalar squad               │
│  /upsq <nome>           — Ver detalhes                 │
│  /upsq <nome> <task>    — Executar task                │
│  /upsq                  — Consultar orquestrador       │
╰────────────────────────────────────────────────────────╯
```

Use `[INSTALADA]` em verde para squads instaladas e `[---]` para nao instaladas.
</step>

<step id="mode-install" condition="modo == instalar">
## 2C. Modo Instalacao

1. Execute:
```bash
RESULT=$(node "$HOME/.claude/upsquads/lib/squad-tools.cjs" install "<nome>")
```

2. Parse o resultado JSON.

3. Se `status == "already_installed"`:
   - Informe: "A squad <nome> ja esta instalada."

4. Se `status == "installed"`:
   - Mostre os agentes instalados
   - Informe como usar: `/upsq <nome>` ou `/upsq <nome> <task>`

5. Se erro:
   - Mostre a mensagem de erro
   - Liste squads disponiveis com `/upsq listar`
</step>

<step id="mode-remove" condition="modo == remover">
## 2D. Modo Remocao

1. Execute:
```bash
RESULT=$(node "$HOME/.claude/upsquads/lib/squad-tools.cjs" remove "<nome>")
```

2. Parse o resultado JSON.

3. Se `status == "not_installed"`:
   - Informe: "A squad <nome> nao esta instalada."

4. Se `status == "removed"`:
   - Informe quantos agentes foram removidos
</step>

<step id="mode-info" condition="modo == info (nome-squad exato sem task)">
## 2E. Modo Info

1. Execute:
```bash
INFO=$(node "$HOME/.claude/upsquads/lib/squad-tools.cjs" info "<nome>")
```

2. Apresente em formato visual:

```
╭─ <Nome da Squad> ───────────────────────────────────╮
│                                                       │
│  Status: [INSTALADA|NAO INSTALADA]                    │
│  Agentes: <N>                                         │
│  <descricao>                                          │
│                                                       │
│  Agentes:                                             │
│  • <agent-1> (orchestrator)                           │
│  • <agent-2>                                          │
│  • ...                                                │
│                                                       │
│  Tasks:                                               │
│  • <task-1>                                           │
│  • <task-2>                                           │
│  • ...                                                │
│                                                       │
│  Uso:                                                 │
│  /upsq <nome> <task>                                  │
│  @sq-<nome>-<chief>  (invocar chief direto)           │
╰───────────────────────────────────────────────────────╯
```

3. Se a squad NAO esta instalada, sugira: `/upsq instalar <nome>`
</step>

<step id="mode-execute" condition="modo == executar task">
## 2F. Modo Execucao de Task

1. Verifique se a squad esta instalada:
```bash
INSTALLED=$(node "$HOME/.claude/upsquads/lib/squad-tools.cjs" installed)
```

2. Se NAO esta instalada:
   - Pergunte ao usuario se quer instalar
   - Se sim, instale: `node "$HOME/.claude/upsquads/lib/squad-tools.cjs" install "<nome>"`

3. Obtenha info da squad:
```bash
INFO=$(node "$HOME/.claude/upsquads/lib/squad-tools.cjs" info "<nome>")
```

4. Identifique o chief da squad (primeiro agente com "chief" ou "chair" no nome).

5. Leia o arquivo da task solicitada:
```bash
# Task files are in ~/.claude/upsquads/squads/<squad>/tasks/<task>.md
```

6. Spawne o chief com a task como contexto:

```
Task(
  subagent_type="sq-<squad>-<chief>",
  prompt="
    <objective>
    Executar a task '<task-name>' da squad <squad-name>.
    </objective>

    <task_definition>
    [Conteudo completo do arquivo da task .md]
    </task_definition>

    <user_context>
    $ARGUMENTS
    </user_context>

    <files_to_read>
    - .plano/PROJECT.md (se existir — contexto do projeto)
    - .plano/STATE.md (se existir — estado atual)
    - ./CLAUDE.md (se existir — instrucoes do projeto)
    </files_to_read>
  ",
  description="<squad-name>: <task-name>"
)
```

7. Apresente o resultado ao usuario.
</step>
