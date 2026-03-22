---
task: createCarouselVisual()
responsavel: "@design-chief"
responsavel_type: Agent
atomic_layer: Task
elicit: true

Entrada:
  - campo: style
    tipo: enum
    origem: User Input
    obrigatorio: true
    descricao: "twitter (estilo tweet) ou noticia (estilo editorial)"
  - campo: copy_slides
    tipo: string[]
    origem: Agent Output
    obrigatorio: true
    descricao: "Copy de cada slide (vem do copy-squad ou do usuario)"
  - campo: handle
    tipo: string
    origem: User Input
    obrigatorio: false
    default: "@jonathanrenan.ia"

Saida:
  - campo: slide_pngs
    tipo: file[]
    destino: Filesystem
    persistido: true

Checklist:
  - "[ ] Estilo visual definido (twitter ou noticia)"
  - "[ ] Imagens de referencia buscadas"
  - "[ ] PNGs gerados via skill correspondente"
  - "[ ] Qualidade visual revisada"

Skills:
  - carrossel-twitter
  - carrossel-estilo-noticia
---

# Task: Gerar Visual de Carrossel

Gera os PNGs finais de um carrossel de Instagram dado a copy dos slides.

Essa task e usada quando:
- O usuario ja tem a copy pronta e quer apenas o visual
- O copy-squad ja gerou a copy e precisa do visual
- O usuario quer um layout diferente do padrao

## Estilos disponiveis

### Estilo Twitter
Layout: avatar + nome + handle + texto grande + foto inferior
```bash
S="$HOME/.claude/skills/carrossel-twitter/scripts/generate_slide.py"
python3 "$S" --text "Texto <b>bold</b>" --photo-prompt "tema" --output slide.png
```

### Estilo Noticia
Layout: foto dramatica + gradiente + titulo uppercase + body
```bash
S="$HOME/.claude/skills/carrossel-estilo-noticia/scripts/generate_slide.py"
python3 "$S" --title "TITULO" --body "Texto." --photo-prompt "tema" --output slide.png
```

## Workflow

### 1. Definir estilo
Se o usuario nao especificou:
- Conteudo educativo/pessoal → **twitter**
- Noticias/eventos/dados → **noticia**

### 2. Buscar imagens de referencia
Quando o tema envolver marcas, produtos ou ferramentas:
```bash
REF_SCRIPT="$HOME/.claude/skills/gemini/scripts/search_references.py"
python3 "$REF_SCRIPT" "tema" --output /tmp/refs --count 3
```

### 3. Gerar cada slide
- Criar photo-prompts relevantes para cada slide
- Gerar todos os PNGs
- Verificar qualidade visual

### 4. Revisar
- Verificar legibilidade do texto
- Verificar consistencia visual entre slides
- Ajustar se necessario
