---
task: analyzeInstagramEngagement()
responsavel: "@data-chief"
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
    default: 50

Saida:
  - campo: engagement_report
    tipo: file
    destino: Filesystem
    persistido: true

Checklist:
  - "[ ] Perfil scrapeado via skill instagram-scraper"
  - "[ ] Comentarios extraidos via skill instagram-comments-scraper"
  - "[ ] Metricas de engajamento calculadas"
  - "[ ] Padroes identificados e relatorio entregue"

Skills:
  - instagram-scraper
  - instagram-comments-scraper
---

# Task: Analisar Engajamento Instagram

Analisa engajamento de um perfil Instagram usando dados reais (posts + comentarios).

## Workflow

### 1. Coletar dados
- Usar skill `instagram-scraper` para extrair posts (tipo, formato, conteudo visual)
- Usar skill `instagram-comments-scraper` para extrair comentarios e contagem

### 2. Metricas por post
Para cada post calcular:
- Quantidade de comentarios
- Comentarios com mais likes (alta relevancia)
- Tipo de conteudo (carrossel, reel, imagem)
- Tema principal

### 3. Analise de padroes
- **Formato que mais engaja**: carrossel vs reel vs imagem
- **Temas que mais engajam**: quais assuntos geram mais comentarios
- **Horarios** (se timestamps disponiveis)
- **Comprimento do conteudo**: posts longos vs curtos
- **Tipos de CTA**: quais geram mais acao

### 4. Analise de sentimento dos comentarios
- Proporcao positivo/negativo/neutro
- Temas dos comentarios negativos (objecoes)
- Temas dos comentarios positivos (validacao)
- Perguntas frequentes (oportunidades)

### 5. Relatorio
- Dashboard de metricas consolidadas
- Top 10 posts por engajamento
- Bottom 10 posts (o que nao funciona)
- Padroes de conteudo que funciona vs nao funciona
- Recomendacoes data-driven para otimizar
