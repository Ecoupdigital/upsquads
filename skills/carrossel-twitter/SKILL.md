---
name: carrossel-twitter
description: "Create carousel posts (up to 6 slides) for Instagram/Twitter in the style of @jonathanrenan.ia. Accepts multiple input sources: news article URLs, YouTube video URLs (transcribes automatically), Instagram post/carousel URLs, tweet URLs, or raw text. Generates final PNG images: photo via Gemini API + text via HTML/CSS + Playwright screenshot. Use when user asks to create a carousel, carrossel, thread visual, or slide deck for social media."
user-invocable: true
---

# Carrossel Twitter - Social Media Carousel Generator

Generates carousel slides as final PNG images (1080x1350). Text pixel-perfect via HTML/CSS, photo via Gemini API, Playwright screenshots the result.

## Input Sources (aceita qualquer um)

### 1. YouTube Video URL
```
User: "crie um carrossel com esse video: https://youtube.com/watch?v=..."
```
**Workflow:**
1. Usar skill youtube-transcript: `yt-dlp --write-auto-sub --skip-download` para baixar legendas
2. Converter VTT para texto limpo (deduplicar linhas)
3. Resumir o conteúdo do vídeo em 6-8 pontos-chave
4. Gerar slides com os pontos-chave

### 2. News Article URL
```
User: "crie um carrossel com essa notícia: https://site.com/artigo"
```
**Workflow:**
1. Usar WebFetch para extrair o conteúdo completo do artigo
2. Identificar título, fatos-chave, números e quotes
3. Dividir em 6-8 slides
4. Gerar slides

### 3. Instagram Post/Carousel URL
```
User: "crie um carrossel baseado nesse post: https://instagram.com/p/..."
```
**Workflow:**
1. Usar Playwright para navegar até o post
2. Capturar snapshot do conteúdo (texto da legenda + screenshots dos slides)
3. Extrair o conteúdo e adaptar
4. Gerar slides no estilo twitter

### 4. Tweet/X URL
```
User: "crie um carrossel com esse tweet: https://x.com/user/status/..."
```
**Workflow:**
1. Usar fxtwitter API: `curl -s "https://api.fxtwitter.com/user/status/ID"`
2. Extrair texto, artigo se houver
3. Adaptar conteúdo para slides
4. Gerar slides

### 5. Texto direto
```
User: "crie um carrossel sobre [tema]" ou cola o texto
```
**Workflow:**
1. Usar o texto fornecido diretamente
2. Dividir em slides
3. Gerar

## Script

```bash
S="$HOME/.claude/skills/carrossel-twitter/scripts/generate_slide.py"

python3 "$S" \
  --text "Texto com <b>bold</b>.<br><br>Segundo parágrafo." \
  --photo-prompt "dark workspace with monitors, no text" \
  --output ./slide-1.png
```

## Parameters

| Flag | Description |
|------|-------------|
| `-t`, `--text` | Text (HTML: `<b>` bold, `<br>` quebra) |
| `-p`, `--photo-prompt` | Prompt da foto (sem texto na foto) |
| `-o`, `--output` | Output PNG |
| `-a`, `--avatar` | Avatar custom |
| `-m`, `--model` | Modelo Gemini (default: flash v1, barato) |

## Layout fixo (1080x1350)
- Avatar 68px + Jonathan Renan 26px + @jonathanrenan.ia 20px
- Texto auto-resize (18-52px) pra preencher espaço
- Foto 16:9 no fundo com border-radius 16px
- Padding: 99/89/89/89px

## Busca de Imagens de Referência

Antes de gerar as fotos, buscar imagens reais do tema na internet para usar como `--ref`:

```bash
REF_SCRIPT="$HOME/.claude/skills/gemini/scripts/search_references.py"

# Buscar 2-3 referências do tema
python3 "$REF_SCRIPT" "Anthropic Claude Code" --output /tmp/refs --count 3

# Usar como --ref na geração (no generate_slide.py, adicionar manualmente)
```

O script usa DuckDuckGo Image Search, baixa imagens reais (logos, screenshots, fotos) e salva em pasta. Usar essas imagens como referência no prompt da foto para resultados mais fiéis ao tema real.

**Quando usar:** sempre que o tema envolver marcas, produtos, apps ou ferramentas específicas (TikTok, Claude, Instagram, etc.)

## Workflow de Geração
1. Extrair conteúdo da fonte (YouTube/artigo/Instagram/tweet/texto)
2. Buscar imagens de referência do tema (`search_references.py`)
3. Resumir e dividir em 6-8 slides (hook, conteúdo, CTA)
4. Gerar todos os slides em paralelo (passando refs quando relevante)
5. Salvar em `06-conteúdo/carrosseis/TEMA/`

## Regras de Conteúdo
- Texto em português BR, tom direto
- Use `<b>` para bold em números e palavras de impacto
- Use `<br><br>` para quebras de parágrafo
- Máximo ~6-8 frases por slide
- Último slide sempre CTA: "Salva esse post. Segue @jonathanrenan.ia"
- Adaptar o conteúdo original para a voz do Jonathan (direto, prático, sem enrolação)

## Custo
~R$0.12/slide | 6 slides = ~R$0.72
