---
task: analyzeCompetitorCreatives()
responsavel: "@traffic-chief"
responsavel_type: Agent
atomic_layer: Task
elicit: true

Entrada:
  - campo: profile_url
    tipo: string
    origem: User Input
    obrigatorio: true
    descricao: "URL ou @username do perfil Instagram do concorrente"
  - campo: posts_count
    tipo: number
    origem: User Input
    obrigatorio: false
    default: 30

Saida:
  - campo: creative_analysis
    tipo: file
    destino: Filesystem
    persistido: true

Checklist:
  - "[ ] Criativos do concorrente extraidos via instagram-scraper"
  - "[ ] Padroes visuais e de copy identificados"
  - "[ ] Angulos de anuncio mapeados"
  - "[ ] Swipe file de criativos entregue"

Skills:
  - instagram-scraper
  - instagram-comments-scraper
---

# Task: Analisar Criativos de Concorrente

Extrai e analisa os criativos (posts/ads) de um concorrente no Instagram para identificar padroes e oportunidades.

## Workflow

### 1. Coletar criativos
Usar skill `instagram-scraper` para extrair:
- Screenshots de cada post/slide
- Transcricao visual do texto nas imagens
- Transcricao de audio dos reels
- Tipo de formato (carrossel, reel, imagem)

### 2. Coletar engajamento
Usar skill `instagram-comments-scraper` para entender:
- Quais criativos geram mais comentarios
- Reacao da audiencia (positiva, negativa, perguntas)
- Objecoes que aparecem nos comentarios

### 3. Analisar padroes de criativos
**Visual:**
- Estilo de imagem predominante (fotos, graficos, screenshots)
- Paleta de cores recorrente
- Uso de texto sobre imagem
- Formatos de carrossel (quantos slides, estrutura)

**Copy:**
- Headlines/hooks usados
- Estrutura do conteudo (problema → solucao, lista, historia)
- CTAs mais frequentes
- Tom de voz

**Angulos de anuncio:**
- Quais dores abordam
- Quais beneficios prometem
- Quais provas sociais usam
- Quais gatilhos mentais aplicam

### 4. Swipe file
Entregar:
- Top 10 criativos do concorrente (por engajamento)
- Angulos que funcionam (replicar adaptando)
- Angulos que nao funcionam (evitar)
- Gaps: temas que o concorrente NAO aborda (oportunidades)
- Templates de criativos baseados nos padroes
