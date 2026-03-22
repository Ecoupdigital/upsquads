---
name: image-fetcher
description: "Busca e captura assets visuais de multiplas fontes: busca de imagens na web, screenshots de sites via Playwright, e arquivos do usuario. Use quando precisar de imagens de referencia, logos, screenshots de produtos ou qualquer asset visual."
---

# Image Fetcher

Obtem assets visuais de multiplas fontes para uso em conteudo.

## Quando usar

Use quando precisar de imagens para compor conteudo:
- Buscar logo de uma marca/produto
- Capturar screenshot de um site/app
- Baixar imagens de referencia para carrosseis
- Organizar assets visuais

## Modos de aquisicao

### 1. Busca de imagens na web
Usar `web_search` para encontrar imagens por keyword. Avaliar resultados e baixar.

### 2. Screenshot de sites
Usar Playwright MCP:
1. `browser_navigate` para a URL
2. `browser_resize` para dimensoes do alvo
3. `browser_wait_for` se necessario
4. `browser_take_screenshot` para salvar

### 3. Assets do usuario
Organizar arquivos fornecidos pelo usuario na pasta de referencia.

## Viewport presets para screenshots

| Formato | Dimensoes |
|---------|-----------|
| Instagram Post | 1080 x 1080 |
| Instagram Carrossel | 1080 x 1350 |
| Story/Reel | 1080 x 1920 |
| Generico | 1280 x 720 |

## Boas praticas

- Preferir screenshots a busca web para paginas de produtos (imagens da web podem estar desatualizadas)
- Nomear descritivamente: `gemini-benchmark-chart.png` nao `image1.png`
- Verificar cache antes de buscar novamente
- Timeout max: 30s por screenshot
