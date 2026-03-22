---
task: analyzeInstagramProfile()
responsavel: "@copy-chief"
responsavel_type: Agent
atomic_layer: Task
elicit: true

Entrada:
  - campo: profile_url
    tipo: string
    origem: User Input
    obrigatorio: true
    descricao: "URL ou @username do perfil Instagram"
  - campo: posts_count
    tipo: number
    origem: User Input
    obrigatorio: false
    default: 20

Saida:
  - campo: analysis_report
    tipo: file
    destino: Filesystem
    persistido: true

Checklist:
  - "[ ] Perfil scrapeado via skill instagram-scraper"
  - "[ ] Tom de comunicacao analisado"
  - "[ ] Padroes de copy identificados"
  - "[ ] Relatorio com recomendacoes entregue"

Skills:
  - instagram-scraper
---

# Task: Analisar Perfil Instagram (Copy)

Extrai e analisa o conteudo de um perfil Instagram focando em copy, tom de comunicacao e padroes de linguagem.

## Workflow

### 1. Scrape do perfil
Usar a skill `instagram-scraper` para extrair posts do perfil:
- Login via Playwright
- Coletar links dos posts
- Screenshots de cada slide
- Transcricao visual (texto nas imagens)
- Transcricao de audio (reels)

### 2. Analise de copy
O copy-chief deve direcionar para os agentes relevantes analisarem:

**Tom e voz:**
- Formal vs informal
- Tecnico vs acessivel
- Provocativo vs educativo
- Emocional vs racional

**Padroes de copy:**
- Estrutura recorrente dos carrosseis (hook → conteudo → CTA)
- Formulas de headline usadas
- Tamanho medio dos textos
- Uso de emojis, bold, maiusculas
- Frequencia de CTAs e tipos

**Palavras e expressoes:**
- Vocabulario mais frequente
- Expressoes de marca
- Ganchos que se repetem
- Padroes de abertura e fechamento

### 3. Analise de engajamento (se disponivel)
- Quais tipos de post geram mais interacao
- Temas que parecem performar melhor
- Formatos mais usados (carrossel vs reel vs imagem)

### 4. Relatorio
Entregar relatorio consolidado com:
- Resumo do perfil (bio, seguidores, frequencia)
- Analise de tom e voz
- Padroes de copy identificados
- Top 5 posts (pela qualidade do copy)
- Recomendacoes para replicar o estilo
- Template de copy baseado nos padroes encontrados
