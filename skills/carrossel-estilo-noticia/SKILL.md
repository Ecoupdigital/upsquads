---
name: carrossel-estilo-noticia
description: "Create news-style carousel posts for Instagram with dramatic image + gradient + title + body text. Accepts multiple input sources: news article URLs, YouTube video URLs (transcribes automatically), Instagram post/carousel URLs, tweet URLs, or raw text. Use when user asks for carrossel estilo noticia, news carousel, carrossel editorial, carrossel jornalistico, or wants dramatic/impactful carousel with dark background and large titles."
user-invocable: true
---

# Carrossel Estilo Notícia

Generates news-style carousel slides (1080x1350): dramatic photo top half with gradient → large uppercase title → body text → footer. Accepts YouTube, articles, Instagram, tweets, or text.

## Input Sources (aceita qualquer um)

### 1. YouTube Video URL
```
User: "crie um carrossel notícia com esse video: https://youtube.com/watch?v=..."
```
**Workflow:**
1. Baixar legendas: `yt-dlp --write-auto-sub --skip-download`
2. Se não tiver legendas, tentar `--write-sub`
3. Converter VTT para texto limpo (deduplicar)
4. Resumir em 6-8 pontos-chave para slides
5. Para cada slide: título impactante em CAIXA ALTA + body explicativo

### 2. News Article URL
```
User: "crie um carrossel notícia com essa matéria: https://site.com/artigo"
```
**Workflow:**
1. WebFetch para extrair conteúdo completo
2. Identificar título, fatos, números, quotes
3. Dividir em slides com títulos de manchete

### 3. Instagram Post/Carousel URL
```
User: "crie no estilo notícia baseado nesse post: https://instagram.com/p/..."
```
**Workflow:**
1. Playwright: navegar, capturar snapshot + screenshots dos slides
2. Extrair texto da legenda e conteúdo visual
3. Adaptar para estilo notícia

### 4. Tweet/X URL
```
User: "crie carrossel notícia com esse tweet: https://x.com/user/status/..."
```
**Workflow:**
1. fxtwitter API: `curl -s "https://api.fxtwitter.com/user/status/ID"`
2. Extrair texto e artigo se houver
3. Adaptar para slides estilo notícia

### 5. Texto direto
```
User: "crie um carrossel notícia sobre [tema]"
```

## Script

```bash
S="$HOME/.claude/skills/carrossel-estilo-noticia/scripts/generate_slide.py"

python3 "$S" \
  --title "TÍTULO GRANDE" \
  --body "Texto explicativo." \
  --photo-prompt "dramatic scene, no text" \
  --output ./slide-1.png
```

## Parameters

| Flag | Description |
|------|-------------|
| `-t`, `--title` | Título grande uppercase |
| `-b`, `--body` | Texto corpo explicativo |
| `-p`, `--photo-prompt` | Prompt da foto de fundo |
| `-o`, `--output` | Output PNG |
| `-c`, `--title-color` | Cor do título (default: #ffffff) |
| `-s`, `--sources` | Créditos/fontes |
| `--cta` | Texto rodapé (default: ARRASTA PRO LADO >>>) |
| `--handle` | Handle (default: @jonathanrenan.ia) |
| `-m`, `--model` | Modelo Gemini |

## Layout (1080x1350, fundo preto)
- Imagem 50% superior com gradiente escurecendo
- Título auto-resize (53-106px), bold 900, uppercase
- Body auto-resize (ratio 0.42 do título, min 24px)
- Sources 19px cinza
- Footer: CTA + handle 16px

## Busca de Imagens de Referência

Antes de gerar as fotos, buscar imagens reais do tema para usar como `--ref`:

```bash
REF_SCRIPT="$HOME/.claude/skills/gemini/scripts/search_references.py"
python3 "$REF_SCRIPT" "TikTok app logo" --output /tmp/refs --count 3
```

Usa DuckDuckGo Image Search — baixa logos, screenshots e fotos reais do tema. Passar como referência no prompt da foto para resultados mais fiéis.

**Quando usar:** sempre que o tema envolver marcas, produtos, apps ou ferramentas específicas.

## Estrutura dos Slides
1. **Capa**: só título grande + sources (sem body)
2. **Conteúdo** (3-6 slides): título + body explicativo
3. **Destaque**: título com cor diferente (`-c "#ff3333"` vermelho, `"#FFD700"` dourado)
4. **CTA** (último): título + body + `--cta "SALVE PARA DEPOIS"`

## Regras de Conteúdo
- Títulos SEMPRE em caixa alta, estilo manchete de jornal
- Body em tom informativo mas acessível
- Adaptar conteúdo original para linguagem direta
- Números e dados em destaque
- Último slide sempre CTA

## Custo
~R$0.12/slide | 5 slides = ~R$0.60
