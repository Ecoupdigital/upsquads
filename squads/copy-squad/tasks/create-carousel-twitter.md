---
task: createCarouselTwitter()
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
  - campo: slides
    tipo: number
    origem: User Input
    obrigatorio: false
    default: 7

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
  - "[ ] Fonte do conteudo extraida (URL processada ou texto recebido)"
  - "[ ] Copy de cada slide escrita (hook, conteudo, CTA)"
  - "[ ] PNGs gerados via skill carrossel-twitter"
  - "[ ] Caption com hashtags gerada"

Skills:
  - carrossel-twitter
  - youtube-transcript
---

# Task: Criar Carrossel Estilo Twitter

Cria carrossel de Instagram no estilo tweet/thread com PNGs finais prontos para upload.

## Fontes aceitas

O usuario pode fornecer qualquer uma dessas fontes:
- **YouTube URL** → transcrever video (skill youtube-transcript) e resumir
- **Artigo/noticia URL** → WebFetch e extrair conteudo
- **Instagram post URL** → Playwright e extrair conteudo
- **Tweet/X URL** → fxtwitter API e extrair
- **Texto livre** → usar diretamente

## Workflow

### 1. Extrair conteudo da fonte
Dependendo do tipo de fonte, usar a skill ou ferramenta apropriada:
- YouTube: usar skill `youtube-transcript` (yt-dlp + VTT cleanup)
- Artigo: usar `WebFetch` para extrair texto
- Instagram: usar Playwright para snapshot + screenshot
- Tweet: usar `curl -s "https://api.fxtwitter.com/user/status/ID"`
- Texto: usar diretamente

### 2. Rotear para copywriter
O copy-chief deve rotear para o copywriter mais adequado ao tom:
- **Dan Koe** → conteudo educativo, autoridade, personal branding
- **Ben Settle** → provocativo, polarizante, email-style
- **Gary Halbert** → storytelling pessoal, emocional
- **Russell Brunson** → vendas, funil, CTA forte
- **Frank Kern** → casual, descontraido
- **David Ogilvy** → informativo, dados, credibilidade

### 3. Escrever copy dos slides
O copywriter deve entregar:
- **Slide 1**: Hook — frase que para o scroll (max 3 linhas)
- **Slides 2-N**: 1 ideia por slide, frases curtas, palavras-chave em **negrito**
- **Ultimo slide**: CTA — salvar, compartilhar, seguir

Regras:
- Frases curtas, tom conversacional brasileiro
- Use `<b>` para bold e `<br><br>` para quebras (formato HTML do script)
- Max 6-8 frases por slide
- Numeros e dados concretos sempre que possivel

### 4. Gerar PNGs
Usar a skill `carrossel-twitter` para gerar cada slide:

```bash
S="$HOME/.claude/skills/carrossel-twitter/scripts/generate_slide.py"

python3 "$S" \
  --text "Texto com <b>bold</b>.<br><br>Segundo paragrafo." \
  --photo-prompt "dark workspace with monitors, no text" \
  --output ./slide-1.png
```

- Buscar imagens de referencia quando o tema envolver marcas/produtos
- Gerar todos os slides
- Salvar em pasta organizada

### 5. Gerar caption
3 opcoes de legenda com hashtags relevantes.

## Entrega final
- PNGs prontos para upload
- Copy de cada slide em texto
- 3 opcoes de caption com hashtags
