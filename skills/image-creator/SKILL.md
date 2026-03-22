---
name: image-creator
description: "Renderiza HTML/CSS em imagens PNG via Playwright. Motor generico — qualquer formato visual e definido pelo template HTML. Use para gerar carrosseis, posts, thumbnails, infograficos ou qualquer imagem a partir de HTML/CSS."
---

# Image Creator

Renderiza HTML/CSS em imagens prontas para producao via Playwright. Motor generico — qualquer formato visual e definido pelo template HTML.

## Quando usar

Use quando precisar gerar imagens a partir de HTML/CSS:
- Carrosseis de Instagram
- Posts para redes sociais
- Thumbnails
- Infograficos
- Qualquer imagem pixel-perfect definida por HTML

## Workflow

### 1. Gerar HTML
Escreva um HTML completo e autocontido com CSS inline. O HTML E o design.

### 2. Salvar HTML
Salvar em pasta de output (ex: `output/slides/slide-01.html`)

### 3. Iniciar servidor HTTP
```bash
python3 -m http.server 8765 --directory "OUTPUT_DIR" &
for i in $(seq 1 30); do curl -s http://localhost:8765 > /dev/null 2>&1 && break || sleep 0.1; done
```

### 4. Renderizar via Playwright
- `browser_navigate` para `http://localhost:8765/slide-01.html`
- `browser_resize` para dimensoes do viewport
- `browser_take_screenshot` para salvar como PNG

### 5. Verificar qualidade
Ler o screenshot para confirmar. Re-renderizar se necessario.

### 6. Parar servidor
```bash
pkill -f "http.server 8765" 2>/dev/null || true
```

## Viewport Presets (largura x altura)

| Plataforma | Dimensoes |
|------------|-----------|
| Instagram Post | 1080 x 1080 |
| Instagram Carrossel | 1080 x 1350 |
| Instagram Story/Reel | 1080 x 1920 |
| Facebook Post | 1200 x 630 |
| Twitter/X Post | 1200 x 675 |
| LinkedIn Post | 1200 x 627 |
| YouTube Thumbnail | 1280 x 720 |

## Template HTML — Estrutura minima

```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { width: 1080px; height: 1350px; overflow: hidden; }
    /* seu design aqui */
  </style>
</head>
<body>
  <!-- seu conteudo -->
</body>
</html>
```

## Regras de Tipografia (tamanhos minimos)

| Tipo de texto | Instagram Post/Carrossel | Story/Reel | LinkedIn/Facebook | YouTube |
|---------------|------------------------|------------|-------------------|---------|
| Hero/Display | 58px | 56px | 40px | 60px |
| Heading | 43px | 42px | 32px | 36px |
| Body/Bullets | 34px | 32px | 24px | 36px |
| Caption/Footer | 24px | 20px | 20px | 32px |

**Regra universal:** Nenhum texto legivel pode ter menos de 20px.
**Font weight:** Body 500+, caption 500+ (400 apenas com contraste 4.5:1).

## Batch Rendering (Carrosseis)

1. Gerar um HTML por slide
2. Iniciar servidor HTTP UMA vez
3. Renderizar cada slide sequencialmente
4. Nomear: slide-01.png, slide-02.png, etc.
5. Parar servidor ao final

## Boas praticas

- Sempre verificar a primeira imagem antes de renderizar em batch
- Usar CSS Grid/Flexbox para layout
- Sem animacoes (screenshot estatico)
- Para cantos arredondados: `border-radius` + `overflow: hidden`
- Usar Google Fonts via `@import` ou web-safe fonts
- Manter HTML + PNG juntos para re-renderizacao facil
