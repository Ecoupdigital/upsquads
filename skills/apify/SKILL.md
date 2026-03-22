---
name: apify
description: "Web scraping e automacao via Apify. Extraia dados de qualquer site com scrapers pre-prontos (Actors). Instagram, YouTube, Twitter, TikTok, Google e mais. Use quando precisar de scraping robusto sem depender de Playwright manual."
---

# Apify Web Scraper

Plataforma de web scraping e automacao. Scrapers pre-prontos (Actors) para qualquer site.

## Quando usar

Use Apify quando precisar de scraping robusto:
- Extrair posts/perfis de Instagram, YouTube, Twitter, TikTok
- Buscar no Google em escala
- Coletar dados estruturados de qualquer site
- Alternativa mais confiavel ao scraping manual via Playwright

## Pre-requisitos

1. Conta Apify (apify.com)
2. Token de API: Apify Console → Settings → API tokens
3. Variavel de ambiente: `APIFY_TOKEN`
4. MCP server configurado em `.mcp.json`:

```json
{
  "mcpServers": {
    "apify": {
      "command": "npx",
      "args": ["-y", "@apify/actors-mcp-server@latest"],
      "env": {
        "APIFY_TOKEN": "${APIFY_TOKEN}"
      }
    }
  }
}
```

## Actors populares

| Actor | O que faz |
|-------|-----------|
| `apify/instagram-scraper` | Posts, perfis, hashtags do Instagram |
| `apify/youtube-scraper` | Videos, canais, comentarios do YouTube |
| `apify/twitter-scraper` | Tweets, perfis, trending do Twitter/X |
| `apify/tiktok-scraper` | Videos, perfis do TikTok |
| `apify/google-search-scraper` | Resultados de busca do Google |
| `apify/web-scraper` | Scraping generico de qualquer site |

## Boas praticas

- Comece com o Actor mais simples que resolve o problema
- Use `maxItems` para limitar resultados e custo
- Verifique pricing do Actor antes de rodar (alguns cobram por resultado)
- Parse os resultados e extraia apenas os campos necessarios

## Operacoes disponiveis

- **Run Actor** — Executar qualquer Actor com parametros customizados
- **Web Scraping** — Extrair dados estruturados de sites
- **Social Media Scraping** — Perfis, posts e engajamento de Instagram, YouTube, Twitter/X, TikTok
- **Search Scraping** — Buscas no Google/Bing em escala
- **Data Export** — Receber datasets em JSON
