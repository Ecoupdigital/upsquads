# Template de Saída — Instagram Scraper

## Estrutura de diretórios

```
00-inbox/instagram-{username}/
├── {username}-posts.md          # Arquivo principal consolidado
├── images/                      # Screenshots dos posts
│   ├── post-001.png
│   ├── post-002-slide-1.png
│   └── ...
├── videos/                      # Vídeos baixados
│   ├── post-003.mp4
│   └── ...
└── audio/                       # Áudio extraído + transcrições
    ├── post-003.wav
    ├── post-003.txt             # Transcrição Whisper
    └── ...
```

## Formato do arquivo .md

```markdown
---
source: instagram
username: "{username}"
display_name: "{display_name}"
bio: "{bio}"
followers: {n}
following: {n}
posts_scraped: {n}
scraped_at: "YYYY-MM-DD HH:MM"
---

# Instagram: @{username}

**Bio**: {bio}
**Seguidores**: {n} | **Seguindo**: {n} | **Posts**: {n}

---

## Post 1 — YYYY-MM-DD

**Tipo**: Imagem | Carrossel (N slides) | Video/Reel
**Likes**: {n}
**URL**: https://www.instagram.com/p/{shortcode}/

### Legenda
{texto completo da legenda}

### Conteudo Visual
{Descricao detalhada da imagem/thumbnail por Claude}

### Transcricao do Audio
> {Transcricao completa do Whisper — apenas para videos}

### Analise de Tom
{Analise de Claude sobre tom, estilo, energia — apenas para videos}

#### Slide 2
{transcricao visual do slide 2 — apenas para carrosseis}

---

## Post 2 — YYYY-MM-DD
...

---

# Analise Geral de Comunicacao

## Tom predominante
{analise consolidada de todas as transcricoes de audio}

## Padroes de linguagem
{palavras/frases recorrentes, vocabulario, estilo de fala}

## Estilo de conteudo
{distribuicao de tipos de post, temas recorrentes, frequencia}
```

## Regras de formatacao

- Frontmatter YAML valido para Obsidian
- Sem wikilinks `[[]]` no conteudo gerado (evitar links quebrados)
- Usar `>` blockquote para transcricoes de audio
- Numeracao sequencial: Post 1, Post 2, etc (ordem cronologica reversa — mais recente primeiro)
- Datas em formato ISO: YYYY-MM-DD
- Secoes de audio/tom so aparecem em posts de video/reel
- Secoes de slides so aparecem em carrosseis
