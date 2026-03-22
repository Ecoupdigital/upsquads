---
task: analyzeAudienceComments()
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
    default: 30

Saida:
  - campo: audience_report
    tipo: file
    destino: Filesystem
    persistido: true

Checklist:
  - "[ ] Comentarios extraidos via skill instagram-comments-scraper"
  - "[ ] Linguagem da audiencia mapeada"
  - "[ ] Objecoes e desejos identificados"
  - "[ ] Swipe file de linguagem entregue"

Skills:
  - instagram-comments-scraper
---

# Task: Analisar Comentarios da Audiencia

Extrai comentarios de posts de um perfil Instagram e analisa a linguagem, objecoes, desejos e padroes da audiencia para informar copy.

## Por que isso importa

A melhor copy usa as EXATAS palavras que a audiencia usa. Comentarios sao ouro:
- Revelam objecoes reais ("mas e se...", "eu tentei e...")
- Mostram desejos ("queria muito...", "como faz pra...")
- Expoe a linguagem natural do publico
- Identificam perguntas frequentes

## Workflow

### 1. Extrair comentarios
Usar a skill `instagram-comments-scraper`:
- Login via Playwright
- Navegar aos posts do perfil
- Expandir e extrair comentarios de primeiro nivel
- Salvar estruturado com username, texto e likes

### 2. Categorizar comentarios
Agrupar por tipo:
- **Perguntas** → duvidas, curiosidades, pedidos de ajuda
- **Objecoes** → resistencias, "mas...", ceticismo
- **Desejos** → "queria...", "preciso de...", aspiracoes
- **Elogios** → o que mais agrada, validacao
- **Historias** → experiencias pessoais, relatos
- **Pedidos** → sugestoes de conteudo, demandas

### 3. Extrair linguagem
Para cada categoria, identificar:
- Frases exatas mais frequentes
- Palavras-chave repetidas
- Tom emocional predominante
- Nivel de sofisticacao da audiencia

### 4. Gerar swipe file de linguagem
Entregar:
- **Top 20 frases** da audiencia (copiar/colar pra usar em copy)
- **Top 10 objecoes** com sugestao de como abordar
- **Top 10 desejos** com sugestao de como usar em headlines
- **Perguntas frequentes** que viram ideias de conteudo
- **Palavras proibidas** (termos que a audiencia nao usa)

### 5. Recomendacoes de copy
- Headlines que usam a linguagem exata da audiencia
- Angulos de abordagem baseados nas objecoes
- CTAs que respondem aos desejos identificados
- Ideias de conteudo baseadas nas perguntas
