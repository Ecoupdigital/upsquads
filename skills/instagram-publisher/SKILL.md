---
name: instagram-publisher
description: "Publica carrosseis no Instagram via Graph API. Upload de imagens para catbox.moe, criacao de containers e publicacao automatica. Suporta 2-10 imagens por post. Use quando o usuario quiser publicar um carrossel pronto no Instagram."
---

# Instagram Publisher

Publica carrosseis do Instagram a partir de imagens locais via Graph API.

## Quando usar

Use quando tiver imagens prontas (PNGs/JPEGs) e quiser publicar direto no Instagram sem sair da IDE.

## Pre-requisitos

Variaveis de ambiente necessarias no `.env`:
```
INSTAGRAM_ACCESS_TOKEN=seu_token_aqui
INSTAGRAM_USER_ID=seu_user_id_aqui
```

### Como obter o token

1. Conta Instagram Business conectada a uma Pagina do Facebook
2. App criado em developers.facebook.com (tipo: Empresa)
3. Graph API Explorer → gerar token com permissoes:
   - `instagram_content_publish`
   - `instagram_basic`
   - `pages_read_engagement`
4. Converter para token de longa duracao (60 dias):
   ```
   GET https://graph.facebook.com/oauth/access_token
     ?grant_type=fb_exchange_token
     &client_id={APP_ID}
     &client_secret={APP_SECRET}
     &fb_exchange_token={TOKEN_CURTO}
   ```

### Como obter o User ID

1. GET `/me/accounts` → pegar `id` da Pagina
2. GET `/{page-id}?fields=instagram_business_account` → pegar `id`

## Workflow

1. Listar JPEGs/PNGs na pasta de output
2. Confirmar ordem das imagens com o usuario
3. Extrair caption do conteudo
4. Executar script de publicacao:

```bash
node --env-file=.env ~/.claude/skills/instagram-publisher/scripts/publish.js \
  --images "slide-01.jpg,slide-02.jpg,slide-03.jpg" \
  --caption "Texto da legenda aqui"
```

Adicionar `--dry-run` para testar sem publicar.

## O script faz

1. Upload das imagens para catbox.moe (hosting temporario publico)
2. Cria child containers no Instagram para cada imagem
3. Aguarda processamento de cada container
4. Cria container do carrossel
5. Publica o carrossel
6. Retorna URL do post publicado

## Limitacoes

- Imagens: JPEG/PNG, 2-10 por carrossel
- Caption: max 2200 caracteres
- Requer conta Instagram Business (nao Personal/Creator)
- Rate limit: 25 posts publicados via API por 24 horas
- Token expira em 60 dias — renovar periodicamente
