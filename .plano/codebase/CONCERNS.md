# Preocupacoes do Codebase

**Data da Analise:** 2026-04-01

## Divida Tecnica

**Nomes de Chiefs Inconsistentes no Orquestrador (BUG CRITICO):**
- Problema: O orquestrador em `agents/upsquads-orquestrador.md` referencia nomes de chiefs que nao correspondem aos nomes reais gerados pelo instalador. O instalador gera nomes no formato `sq-{squad-id}-{agent-filename}`, mas o orquestrador omite o squad-id em 3 squads.
- Arquivos: `agents/upsquads-orquestrador.md` (linhas com `**Chief:**`)
- Impacto: **Handoff falha silenciosamente** para 3 squads — hormozi-squad, copy-squad e brand-squad. O orquestrador tenta spawnar `sq-hormozi-chief` mas o agente instalado se chama `sq-hormozi-squad-hormozi-chief`. Idem para `sq-copy-chief` (deveria ser `sq-copy-squad-copy-chief`) e `sq-brand-chief` (deveria ser `sq-brand-squad-brand-chief`).
- Abordagem de correcao: Corrigir os 3 nomes no orquestrador para usar o formato completo: `sq-hormozi-squad-hormozi-chief`, `sq-copy-squad-copy-chief`, `sq-brand-squad-brand-chief`. As outras 8 squads ja estao corretas.

**Duplicacao de Codigo entre install.js e squad-tools.cjs:**
- Problema: Tres funcoes criticas estao duplicadas quase identicamente nos dois arquivos: `loadRegistry`/`loadRegistryFromSource` (parser de YAML), `extractAgentDescription`, e `buildFrontmatter`.
- Arquivos: `bin/install.js` (linhas 48-95), `lib/squad-tools.cjs` (linhas 56-122)
- Impacto: Qualquer correcao no parser YAML ou na geracao de frontmatter precisa ser feita em dois lugares. Se divergirem, squads instaladas via `npx upsquads` e via `squad-tools.cjs install` terao comportamentos diferentes.
- Abordagem de correcao: Extrair as funcoes compartilhadas para um modulo comum em `lib/shared.cjs` e importar em ambos os arquivos.

**Parser YAML Artesanal Fragil:**
- Problema: O parser de `registry.yaml` e feito manualmente com split/startsWith em vez de usar uma biblioteca YAML. So suporta campos flat de primeiro nivel por squad.
- Arquivos: `bin/install.js` (linhas 54-73), `lib/squad-tools.cjs` (linhas 60-81)
- Impacto: Campos com valores multilinea, listas aninhadas ou caracteres especiais (dois pontos, aspas) quebram o parser silenciosamente. A registry atual funciona porque e simples, mas qualquer extensao futura (ex: adicionar campo `dependencies` como lista) vai falhar.
- Abordagem de correcao: Usar `js-yaml` como dependencia ou manter o parser artesanal mas adicionar testes de regressao para formatos suportados.

**Dependencia Externa Nao Incluida no Repo (Gemini Skill):**
- Problema: Os scripts de carrossel (`carrossel-twitter` e `carrossel-estilo-noticia`) referenciam `~/.claude/skills/gemini/scripts/generate_image.py` que nao existe neste repositorio.
- Arquivos: `skills/carrossel-twitter/scripts/generate_slide.py` (linha 29), `skills/carrossel-estilo-noticia/scripts/generate_slide.py` (linha 47)
- Impacto: Qualquer usuario que instalar UPSquads e tentar usar as skills de carrossel vai receber um FileNotFoundError ao gerar imagens. A skill `gemini` e uma dependencia implcita nao documentada.
- Abordagem de correcao: Incluir a skill `gemini` no repositorio ou documentar a dependencia explicitamente no SKILL.md de cada carrossel com instrucoes de instalacao.

**Caminhos Hardcoded para /home/vault/:**
- Problema: Multiplos arquivos de skill referenciam caminhos absolutos especificos da maquina do desenvolvedor (`/home/vault/00-inbox/`, `/home/vault/06-conteudo/`).
- Arquivos:
  - `skills/carrossel-twitter/scripts/generate_slide.py` (linha 30): `DEFAULT_AVATAR = "/home/vault/06-conteudo/Referencias Jonathan/avatar_instagram.jpg"`
  - `skills/carrossel-twitter/scripts/compose_html.py` (linha 23): idem
  - `skills/carrossel-twitter/scripts/compose_card.py` (linha 20): idem
  - `skills/instagram-scraper/SKILL.md` (linhas 34, 176): `/home/vault/00-inbox/`
  - `skills/instagram-comments-scraper/SKILL.md` (linhas 14, 272): `/home/vault/00-inbox/`
- Impacto: Para qualquer usuario que nao seja o desenvolvedor original, os scripts de carrossel falham com avatar nao encontrado e as instrucoes de scraping apontam para diretorios inexistentes.
- Abordagem de correcao: Substituir caminhos hardcoded por variaveis de ambiente ou paths relativos ao projeto. Para o avatar, aceitar `--avatar` como parametro obrigatorio ou usar um fallback generico incluso no repo.

**Diretorio references/ Duplicado no instagram-scraper:**
- Problema: Existe um diretorio `references/references/` aninhado dentro de `skills/instagram-scraper/references/` contendo copias quase identicas dos mesmos arquivos.
- Arquivos: `skills/instagram-scraper/references/references/output-template.md`, `skills/instagram-scraper/references/references/instagram-selectors.md`
- Impacto: Confusao sobre qual versao e a canonica. O `output-template.md` interno tem tamanho diferente (2187 vs 2398 bytes), indicando versoes divergentes.
- Abordagem de correcao: Remover o diretorio aninhado `references/references/` apos verificar qual versao e a mais atual.

## Consideracoes de Seguranca

**Upload de Imagens para Servico Publico Nao-Autenticado (catbox.moe):**
- Risco: O instagram-publisher faz upload de todas as imagens para catbox.moe antes de publicar no Instagram. Essas imagens ficam permanentemente acessiveis em URLs publicas sem autenticacao.
- Arquivos: `skills/instagram-publisher/scripts/publish.js` (linhas 28-42)
- Mitigacao atual: Nenhuma. As URLs sao geradas e nunca removidas.
- Abordagem de correcao: Considerar alternativas como o proprio upload temporario do Instagram ou um servico de hosting com TTL. No minimo, documentar que as imagens ficam publicas permanentemente e avisar o usuario antes do upload.

**Skills de Scraping Solicitam Credenciais de Login:**
- Risco: As skills `instagram-scraper` e `instagram-comments-scraper` instruem o agente a pedir username e password do Instagram ao usuario via `AskUserQuestion` e preencher formularios de login.
- Arquivos: `skills/instagram-scraper/SKILL.md` (Fase 1b), `skills/instagram-comments-scraper/SKILL.md` (Fase 1b)
- Mitigacao atual: Credenciais sao usadas apenas na sessao do Playwright e nao sao salvas em disco.
- Abordagem de correcao: Documentar o fluxo de seguranca claramente. Considerar alternativa via cookies de sessao pre-existentes ou login manual pelo usuario antes de invocar a skill.

**Ausencia de .gitignore:**
- Risco: Nenhum `.gitignore` no repositorio. Se algum desenvolvedor criar um `.env` local ou gerar arquivos temporarios, eles podem ser commitados acidentalmente.
- Arquivos: Raiz do repositorio (arquivo ausente)
- Mitigacao atual: Nenhuma.
- Abordagem de correcao: Criar `.gitignore` com: `.env*`, `node_modules/`, `.installed`, `/tmp/`, `*.log`, `.plano/`.

## Gargalos de Performance

**Instalacao Copia 62k+ Linhas de Arquivos:**
- Problema: O instalador copia recursivamente todos os 325 arquivos do repo para `~/.claude/upsquads/`, incluindo READMEs, checklists, data files e workflows de todas as squads, mesmo as que o usuario nao instalou.
- Arquivos: `bin/install.js` (funcao `installBase`, linhas 156-211)
- Causa: `installBase()` copia a pasta `squads/` inteira incondicionalmente. Apenas os agents sao instalados seletivamente via `installSquadAgents()`.
- Abordagem de correcao: Copiar apenas os metadados (registry.yaml, squad.yaml) na instalacao base e copiar data/workflows/tasks apenas das squads que o usuario instalar.

**Context Window Bloat nos Agentes:**
- Problema: Os agentes maiores (charlie-munger.md com 590 linhas, ray-dalio.md com 586 linhas) consomem uma porcao significativa do context window quando spawnados, reduzindo espaco para a tarefa real.
- Arquivos: `squads/advisory-board/agents/charlie-munger.md`, `squads/advisory-board/agents/ray-dalio.md`, `squads/movement/agents/analista-de-impacto.md` (350 linhas)
- Causa: Definicoes de agente extremamente detalhadas com exemplos extensos e frameworks completos inline.
- Abordagem de correcao: Mover frameworks e exemplos extensos para arquivos `data/` separados que o agente carrega sob demanda via `Read`, mantendo o arquivo do agente com no maximo ~150-200 linhas de instrucoes core.

## Areas Frageis

**Scraping do Instagram Depende de Estrutura DOM Especifica:**
- Arquivos: `skills/instagram-comments-scraper/SKILL.md` (Fase 2)
- Por que fragil: A extracao de comentarios depende de subir exatamente 6 niveis no DOM a partir de `img[alt*="profile picture"]`. Qualquer mudanca no HTML do Instagram quebra a extracao silenciosamente (retorna array vazio em vez de erro).
- Cobertura de testes: Zero. Nao ha testes automatizados para nenhuma skill.
- Abordagem de correcao: Documentar a data do ultimo teste funcional (Mar 2026) e adicionar validacao no script que detecte quando a estrutura DOM mudou (ex: verificar se o parent na profundidade 6 tem o sibling esperado).

**Uninstall Nao Remove Skills:**
- Arquivos: `bin/install.js` (funcao `uninstall`, linhas 343-376)
- Por que fragil: O comando `--uninstall` remove agents e o diretorio `upsquads/`, mas NAO remove os skills copiados para `~/.claude/skills/`. Skills como `instagram-publisher`, `carrossel-twitter` etc. permanecem orfaos.
- Cobertura de testes: Zero.
- Abordagem de correcao: Adicionar remocao dos skills na funcao `uninstall()`, com logica para so remover skills que foram instalados pelo UPSquads (manter um manifesto de skills instalados).

**Referencia a "Synkra AIOS" nos squad.yaml:**
- Arquivos: Todos os `squads/*/squad.yaml` (campo `author`)
- Por que fragil: Os squad.yaml referenciam `author: "Synkra AIOS"` e `aios.minVersion: "4.0.0"`, que parece ser uma plataforma original de onde os squads foram adaptados. O UPSquads nao implementa nenhuma verificacao de `aios.minVersion`. Se o formato desses YAMLs for consumido no futuro, esses campos remanescentes podem causar confusao.
- Abordagem de correcao: Atualizar `author` para o autor real do UPSquads e remover o bloco `aios` ou substituir por um bloco `upsquads.minVersion`.

## Lacunas de Cobertura de Teste

**Zero Testes Automatizados:**
- O que nao e testado: Todo o codebase. Nao existe nenhum arquivo de teste, nenhum framework de teste configurado, nenhum script de teste no `package.json`.
- Arquivos: `package.json` (sem campo `scripts.test`), nenhum arquivo `*.test.*` ou `*.spec.*` no repositorio
- Risco: Qualquer mudanca no parser YAML, no instalador, na geracao de frontmatter ou no squad-tools pode quebrar funcionalidades sem deteccao. O bug dos nomes de chiefs no orquestrador e um exemplo direto — teria sido detectado por um teste simples.
- Prioridade: **Alta** — pelo menos o instalador (`bin/install.js`) e o squad-tools (`lib/squad-tools.cjs`) deveriam ter testes unitarios cobrindo: parsing de registry, geracao de nomes de agentes, install/uninstall, e consistencia entre orquestrador e nomes gerados.

**Nenhuma Validacao de Integridade:**
- O que nao e testado: Consistencia entre registry.yaml, orquestrador, e arquivos reais de squad (contagem de agentes, nomes de chiefs, existencia de tasks referenciadas).
- Arquivos: `squads/registry.yaml`, `agents/upsquads-orquestrador.md`, `squads/*/agents/`
- Risco: Adicionar uma nova squad ou renomear um agent pode introduzir inconsistencias que so serao descobertas pelo usuario ao tentar usar.
- Prioridade: **Alta** — um script de CI que valide a consistencia entre registry, orquestrador e filesystem evitaria bugs como o dos nomes de chiefs.

**Skills Sem Validacao de Pre-requisitos:**
- O que nao e testado: As skills de scraping e carrossel listam pre-requisitos (yt-dlp, ffmpeg, whisper, Playwright MCP, Gemini skill) mas nao ha validacao automatica. O usuario so descobre que falta algo quando o script falha.
- Arquivos: `skills/instagram-scraper/SKILL.md`, `skills/carrossel-twitter/SKILL.md`, `skills/carrossel-estilo-noticia/SKILL.md`
- Risco: Experiencia ruim para novos usuarios que tentam usar skills sem ter as dependencias instaladas.
- Prioridade: **Media** — um pre-check automatico nas skills mais complexas melhoraria a experiencia.
