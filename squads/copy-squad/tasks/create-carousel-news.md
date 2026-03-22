---
task: createCarouselNews()
responsavel: "@copy-chief"
responsavel_type: Agent
atomic_layer: Task
elicit: true

Entrada:
  - campo: source
    tipo: string
    origem: User Input
    obrigatorio: true
    descricao: "URL (YouTube, artigo, Instagram, tweet) ou texto/tema livre"
  - campo: handle
    tipo: string
    origem: User Input
    obrigatorio: false
    default: "@jonathanrenan.ia"

Saida:
  - campo: carousel_slides
    tipo: file[]
    destino: Filesystem
    persistido: true
  - campo: caption
    tipo: string
    destino: Console
    persistido: false

Checklist:
  - "[ ] Fonte do conteudo extraida"
  - "[ ] Copy estilo manchete jornalistica escrita"
  - "[ ] PNGs gerados via skill carrossel-estilo-noticia"
  - "[ ] Caption com hashtags gerada"

Skills:
  - carrossel-estilo-noticia
  - youtube-transcript
---

# Task: Criar Carrossel Estilo Noticia

Cria carrossel de Instagram estilo editorial/jornalistico: foto dramatica + gradiente + titulo grande uppercase + body texto.

## Fontes aceitas

Mesmas fontes do carrossel twitter: YouTube URL, artigo, Instagram, tweet ou texto livre.

## Workflow

### 1. Extrair conteudo da fonte
Mesma logica do carrossel twitter.

### 2. Rotear para copywriter
O copy-chief deve rotear para copywriters com estilo editorial:
- **Claude Hopkins** → dados, cientifico, factual
- **David Ogilvy** → informativo, credibilidade, headlines longas
- **Eugene Schwartz** → awareness levels, manchetes poderosas
- **Dan Koe** → educativo, autoridade

### 3. Escrever copy dos slides
Estilo MANCHETE DE JORNAL:
- **Slide 1 (Capa)**: Titulo grande uppercase + fontes (sem body)
- **Slides 2-6 (Conteudo)**: Titulo manchete uppercase + body informativo
- **Slide destaque**: Titulo com cor diferente (vermelho ou dourado)
- **Ultimo slide (CTA)**: Titulo + body + "SALVE PARA DEPOIS"

Regras:
- Titulos SEMPRE em caixa alta, estilo manchete
- Body em tom informativo mas acessivel
- Numeros e dados em destaque
- Adaptar conteudo para linguagem direta

### 4. Gerar PNGs
Usar a skill `carrossel-estilo-noticia`:

```bash
S="$HOME/.claude/skills/carrossel-estilo-noticia/scripts/generate_slide.py"

# Slide capa (sem body)
python3 "$S" \
  --title "TITULO GRANDE" \
  --photo-prompt "dramatic scene, no text" \
  --sources "Fonte: site.com" \
  --output ./slide-1.png

# Slide conteudo
python3 "$S" \
  --title "TITULO MANCHETE" \
  --body "Texto explicativo do conteudo." \
  --photo-prompt "relevant dramatic image" \
  --output ./slide-2.png

# Slide destaque (cor diferente)
python3 "$S" \
  --title "DESTAQUE IMPORTANTE" \
  --body "Texto." \
  --title-color "#ff3333" \
  --photo-prompt "dramatic image" \
  --output ./slide-5.png

# Slide CTA
python3 "$S" \
  --title "QUER SABER MAIS?" \
  --body "Segue @jonathanrenan.ia" \
  --cta "SALVE PARA DEPOIS" \
  --output ./slide-7.png
```

- Buscar imagens de referencia do tema
- Gerar todos os slides
- Salvar em pasta organizada

### 5. Gerar caption
3 opcoes de legenda com hashtags relevantes.

## Entrega final
- PNGs prontos para upload (1080x1350, fundo preto, foto + gradiente)
- Copy de cada slide
- 3 opcoes de caption com hashtags
