# Padroes de Teste

**Data da Analise:** 2026-04-01

## Framework de Teste

**Runner:** Nao detectado
**Config:** Nao detectado

Nao existe framework de teste configurado neste projeto. Nao ha `jest.config.*`, `vitest.config.*`, `mocha`, `.nycrc`, nem qualquer outro arquivo de configuracao de testes.

**Comandos:**
Nenhum script de teste em `package.json`. Nao ha `"test"` ou `"test:*"` definidos.

## Organizacao dos Arquivos de Teste

**Localizacao:** Nao ha arquivos de teste no codebase.
**Nomeacao:** Nenhum arquivo `*.test.*`, `*.spec.*`, ou diretorio `__tests__/` encontrado.

## Cobertura de Teste

**Status:** Zero cobertura. Nenhum teste automatizado existe.

## Ausencia de Testes — Contexto

Este e um projeto de **conteudo estruturado** (agentes AI em Markdown/YAML) com uma camada fina de JavaScript para instalacao. O codigo JavaScript total soma ~650 linhas em 3 arquivos:

- `bin/install.js` (~390 linhas) - Installer com onboarding interativo
- `lib/squad-tools.cjs` (~256 linhas) - CLI de gerenciamento de squads
- `skills/instagram-publisher/scripts/publish.js` (~162 linhas) - Publisher Instagram

Scripts Python auxiliares em skills (~60 linhas cada):
- `skills/carrossel-twitter/scripts/generate_slide.py`
- `skills/carrossel-twitter/scripts/compose_html.py`
- `skills/carrossel-twitter/scripts/compose_card.py`
- `skills/carrossel-estilo-noticia/scripts/generate_slide.py`

## Validacao Existente (Nao-Automatizada)

### Checklists de Qualidade

Cada squad possui um `checklists/output-quality.md` que funciona como validacao manual de output dos agentes. Exemplo em `squads/copy-squad/checklists/output-quality.md`:

```markdown
## PASS/FAIL Criteria

**PASS:** All CRITICAL items [x] and fewer than 3 non-critical failures.
**REVISE:** All CRITICAL items [x] but 3+ non-critical failures.
**FAIL:** Any CRITICAL item unchecked.
```

Estes checklists sao referenciados por tasks de review (ex: `tasks/review.md`) e executados pelo chief agent da squad durante o workflow.

### Validacao de Input em Runtime

O `publish.js` faz validacao de inputs no inicio do `main()`:

```javascript
if (!images.length) throw new Error('--images is required');
if (!caption) throw new Error('--caption is required');
if (images.length < 2 || images.length > 10) {
  throw new Error(`Instagram carousels require 2-10 images (got ${images.length})`);
}
if (caption.length > 2200) {
  throw new Error(`Caption exceeds Instagram's 2200-character limit`);
}
```

O `squad-tools.cjs` valida existencia de registros e argumentos:

```javascript
if (!squadId) error('squad name required: squad install <name>');
const squad = squads.find(s => s.id === squadId);
if (!squad) error(`Squad not found: ${squadId}\nAvailable: ${squads.map(s => s.id).join(', ')}`);
```

## Tipos de Teste que Seriam Relevantes

Se testes forem adicionados ao projeto, as areas prioritarias seriam:

### Unitarios (Alta Prioridade)

**Funcoes de parsing YAML manual:**
- `loadRegistryFromSource()` em `bin/install.js`
- `loadRegistry()` em `lib/squad-tools.cjs`
- Estas funcoes parseiam YAML manualmente e sao frageis. Qualquer mudanca no formato de `registry.yaml` pode quebra-las silenciosamente.
- Arquivos: `bin/install.js`, `lib/squad-tools.cjs`

**Funcoes de build de frontmatter:**
- `buildFrontmatter()` - gera YAML frontmatter para agentes instalados
- `extractAgentDescription()` - extrai descricao de conteudo markdown
- Duplicadas entre `bin/install.js` e `lib/squad-tools.cjs`
- Arquivos: `bin/install.js`, `lib/squad-tools.cjs`

**Funcoes de parsing de argumentos:**
- `parseArgs()` em `skills/instagram-publisher/scripts/publish.js`
- Arquivo: `skills/instagram-publisher/scripts/publish.js`

### Integracao (Media Prioridade)

**Fluxo de instalacao de squad:**
- `installSquadAgents()` - copia agents, gera frontmatter, cria marker
- `cmdInstall()` / `cmdRemove()` - ciclo completo de install/uninstall
- Verificar que agents sao copiados corretamente para `~/.claude/agents/`

**Fluxo CLI:**
- `cmdList()`, `cmdInfo()`, `cmdInstalled()` - comandos de leitura
- Verificar output JSON no modo `--raw`

### E2E (Baixa Prioridade)

**Nao aplicavel** para a maioria do codebase (conteudo Markdown). O unico candidato seria o fluxo completo de `npx upsquads` mas requer interacao terminal.

## Recomendacao de Setup (Se Implementar)

**Runner sugerido:** Vitest ou Node.js built-in test runner (`node --test`)
- Zero deps externas e um principio do projeto, entao `node --test` (Node 18+) seria mais alinhado.

**Localizacao sugerida:** Co-localizado com o arquivo testado:
- `bin/install.test.js`
- `lib/squad-tools.test.cjs`
- `skills/instagram-publisher/scripts/publish.test.js`

**Estrutura sugerida:**
```javascript
const { describe, it } = require('node:test');
const assert = require('node:assert');

describe('loadRegistry', () => {
  it('parses registry.yaml correctly', () => {
    // ...
  });
});
```
