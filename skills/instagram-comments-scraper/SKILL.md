---
name: instagram-comments-scraper
description: "Scrape comentarios de posts do Instagram. Use quando o usuario pedir para extrair, coletar ou scrape comentarios de um perfil do Instagram, analisar engajamento de posts, ou capturar feedback/reacoes de seguidores. Recebe um perfil e quantidade de posts, navega em cada post, expande e extrai todos os comentarios de primeiro nivel, e salva em arquivo .md na pasta 00-inbox/. Tambem use quando o usuario mencionar 'comentarios do instagram', 'reactions de seguidores', 'feedback dos posts', ou qualquer variacao de coleta de comentarios de perfis Instagram."
---

# Instagram Comments Scraper

Skill para extrair comentarios de primeiro nivel de posts de um perfil do Instagram.

**Entradas do usuario:**
- URL ou @username do perfil
- Quantidade de posts para processar (default: 10)

**Saida:** arquivo `.md` em `/home/vault/00-inbox/` com todos os comentarios estruturados.

**IMPORTANTE:** O Instagram exige login para acessar comentarios — nao funciona sem autenticacao.

## Prerequisitos

Nenhuma dependencia externa alem do Playwright (ja disponivel via MCP).

**Limitacoes tecnicas do `browser_run_code`:**
- `require('fs')` NAO funciona — nao e possivel salvar arquivos diretamente do browser
- `page.accessibility.snapshot()` NAO existe — usar a abordagem DOM descrita abaixo
- Resultados devem ser retornados como JSON no `return` e salvos via Bash/Write

## Pipeline (4 Fases)

### Fase 1: Setup + Login + Coleta de Links

#### 1a. Criar diretorio temporario
```bash
mkdir -p /tmp/instagram-comments-{username}
```

#### 1b. Login no Instagram via Playwright

1. `browser_resize` 1440x900
2. `browser_navigate` para `https://www.instagram.com/`
3. Verificar se ja esta logado (presenca de Home/Reels/Messages no snapshot)
4. Se nao logado:
   - Pedir credenciais via `AskUserQuestion`
   - `browser_fill_form` username + password
   - `browser_click` "Log In"
   - Tratar 2FA se necessario (pedir codigo ao usuario)
   - Dispensar dialogos: "Save login info?" → "Not now", "Turn on Notifications" → "Not Now"

#### 1c. Identificar o usuario logado

Anotar o username logado a partir do snapshot (link do perfil na sidebar). Esse username sera usado para filtrar profile pictures na extracao de comentarios.

#### 1d. Navegar ao perfil e extrair metadados

1. `browser_navigate` para `https://www.instagram.com/{username}/`
2. `browser_wait_for` 4s + `browser_snapshot`
3. Extrair: nome, bio, seguidores, seguindo, total posts
4. Se privado ou nao encontrado → informar usuario e abortar

#### 1e. Coletar links dos posts via scroll

O scroll precisa ser agressivo para coletar muitos posts. O Instagram carrega ~12 posts por vez e precisa de scrolls grandes com delays suficientes para o lazy loading funcionar.

```javascript
async (page) => {
  const TARGET = {quantidade_de_posts};
  let allLinks = new Set();
  // Coletar links iniciais ja visiveis
  const initial = await page.evaluate(() => {
    const els = document.querySelectorAll('a[href*="/p/"], a[href*="/reel/"]');
    return [...new Set([...els].map(a => a.href))];
  });
  initial.filter(l => l.includes('/{username}/')).forEach(l => allLinks.add(l));

  let noNewCount = 0;
  // noNewCount=8 para dar tempo suficiente ao lazy loading
  for (let i = 0; i < 300 && allLinks.size < TARGET && noNewCount < 8; i++) {
    // Scroll agressivo: 5000px por vez
    await page.evaluate(() => window.scrollBy(0, 5000));
    // Delay de 1200ms para o Instagram carregar novos posts
    await page.waitForTimeout(1200);

    const links = await page.evaluate(() => {
      const els = document.querySelectorAll('a[href*="/p/"], a[href*="/reel/"]');
      return [...new Set([...els].map(a => a.href))];
    });
    const prevSize = allLinks.size;
    // IMPORTANTE: filtrar apenas links do perfil alvo (ignorar sugestoes)
    links.filter(l => l.includes('/{username}/')).forEach(l => allLinks.add(l));
    if (allLinks.size === prevSize) noNewCount++;
    else noNewCount = 0;
  }
  return { total: allLinks.size, links: [...allLinks].slice(0, TARGET) };
}
```

**Parametros criticos:**
- Scroll de **5000px** (nao 3000) — mais rapido e confiavel
- Delay de **1200ms** (nao 800) — da tempo pro lazy loading
- Threshold de **8 tentativas** sem novos links (nao 3-5) — evita parar cedo
- **Filtrar por username** — o grid mostra sugestoes de outros perfis

### Fase 2: Extrair Comentarios de Cada Post

Processar em lotes de **10 posts** por chamada `browser_run_code`. Cada lote leva ~40-60 segundos.

**CRITICO — Abordagem de extracao que funciona (testada em Marco 2026):**

O Instagram obfusca completamente o DOM com classes randomicas. Seletores CSS tradicionais (como `span[dir="auto"]`, `a[href^="/"]`, `time[datetime]` + parent traversal) NAO funcionam para extrair comentarios de forma confiavel.

A unica abordagem que funciona consistentemente:

1. Encontrar `img[alt*="profile picture"]` — cada comentario tem a foto do autor
2. Subir **exatamente 6 niveis** no DOM (`parentElement` x6)
3. Pegar o `nextElementSibling` desse elemento — contem todo o texto do comentario
4. Parsear o `innerText` desse sibling para extrair username, texto e likes

```javascript
async (page) => {
  const urls = ["url1", "url2", ...]; // lote de 10 posts
  const results = [];

  for (const url of urls) {
    try {
      await page.goto(url, {waitUntil: 'domcontentloaded', timeout: 15000});
      await page.waitForTimeout(2500);

      // Data do post
      const date = await page.evaluate(() => {
        const t = document.querySelector('time[datetime]');
        return t ? t.getAttribute('datetime') : null;
      });

      // Verificar se tem comentarios
      const noComments = await page.evaluate(() =>
        document.body.innerText.includes('No comments yet')
      );
      if (noComments) { results.push({url, date, comments: []}); continue; }

      // Expandir "View all N comments" (ate 5 tentativas)
      for (let i = 0; i < 5; i++) {
        const clicked = await page.evaluate(() => {
          const els = [...document.querySelectorAll('span, button')];
          for (const el of els) {
            if (/View all \d+ comment/i.test(el.textContent)) {
              el.click(); return true;
            }
          }
          return false;
        });
        if (clicked) await page.waitForTimeout(2000);
        else break;
      }

      // EXTRAIR COMENTARIOS — abordagem profile picture
      const comments = await page.evaluate(() => {
        const r = [];
        const imgs = document.querySelectorAll('img[alt*="profile picture"]');

        for (const img of imgs) {
          const alt = img.alt;
          // Filtrar: pular o perfil alvo e o usuario logado
          if (alt.includes('{username}')) continue;
          if (alt.includes('{logged_in_user}')) continue;

          const username = alt.replace("'s profile picture", '').trim();

          // Subir 6 niveis no DOM
          let el = img;
          for (let i = 0; i < 6; i++) {
            el = el.parentElement;
            if (!el) break;
          }
          if (!el) continue;

          // O proximo sibling contem o texto do comentario
          const nextSib = el.nextElementSibling;
          if (!nextSib) continue;

          const sibText = nextSib.innerText || '';
          if (!sibText.trim()) continue;

          // Parsear linhas do texto
          const lines = sibText.split('\n').map(l => l.trim()).filter(l => l.length > 0);
          let commentText = '', likes = 0;

          for (const line of lines) {
            if (line === username) continue;
            if (/^\d+[hmdws]$/.test(line)) continue;
            if (/^(Reply|Like|See translation|Verified)$/i.test(line)) continue;
            const m = line.match(/^(\d+) likes?$/);
            if (m) { likes = parseInt(m[1]); continue; }
            if (!commentText && line.length > 1) commentText = line;
          }

          if (commentText) r.push({username, text: commentText, likes});
        }

        // Deduplicar
        const seen = new Set();
        return r.filter(c => {
          const key = c.username + c.text.substring(0, 30);
          if (seen.has(key)) return false;
          seen.add(key);
          return true;
        });
      });

      results.push({url, date, comments});
    } catch(e) {
      results.push({url, date: null, comments: [], error: e.message});
    }
  }
  return results;
}
```

**Por que 6 niveis?** A estrutura do DOM do Instagram em Marco 2026 coloca a `<img>` de profile picture dentro de: `A > DIV > SPAN > DIV > DIV > DIV`. O 6o parent e o container que tem como sibling o bloco de texto do comentario. Se o Instagram mudar essa estrutura, ajustar esse numero.

**Salvando resultados entre lotes:** Como `require('fs')` nao funciona em `browser_run_code`, salvar cada lote via `Bash` ou `Write` tool apos receber o retorno JSON da funcao.

### Fase 3: Compilar Arquivo .md

Usar Python para compilar o arquivo final a partir dos JSONs parciais:

```python
import json, glob
from datetime import datetime

username = "{username}"
all_posts = []

# Ler todos os batch files
for f in sorted(glob.glob(f'/tmp/instagram-comments-{username}/batch*.json')):
    all_posts.extend(json.load(open(f)))

total_comments = sum(len(p['comments']) for p in all_posts)

md = []
md.append("---")
md.append(f'source: instagram-comments')
md.append(f'username: "{username}"')
md.append(f'display_name: "{display_name}"')
md.append(f'followers: {followers}')
md.append(f'following: {following}')
md.append(f'posts_scraped: {len(all_posts)}')
md.append(f'total_comments: {total_comments}')
md.append(f'scraped_at: "{datetime.now().strftime("%Y-%m-%d %H:%M")}"')
md.append("---\n")

md.append(f"# Comentarios -- @{username}\n")
md.append(f"**Posts analisados**: {len(all_posts)}")
md.append(f"**Total de comentarios**: {total_comments}")
md.append(f'**Coletado em**: {datetime.now().strftime("%Y-%m-%d %H:%M")}\n')
md.append("---\n")

for i, post in enumerate(all_posts, 1):
    date_str = post['date'][:10] if post.get('date') else 'desconhecida'
    md.append(f"## Post {i} -- {date_str}\n")
    md.append(f"**URL**: {post['url']}")
    md.append(f"**Comentarios**: {len(post['comments'])}\n")

    if not post['comments']:
        md.append("_(Sem comentarios)_\n")
    else:
        for c in post['comments']:
            likes_str = f" ({c['likes']} likes)" if c.get('likes') else ""
            md.append(f"- **@{c['username']}**{likes_str}: {c['text']}")
        md.append("")

    md.append("---\n")

with open(f"/home/vault/00-inbox/instagram-comments-{username}.md", "w") as f:
    f.write("\n".join(md))
```

### Fase 4: Limpeza

```bash
rm -rf /tmp/instagram-comments-{username}/
```

## Formato do Arquivo de Saida

```markdown
---
source: instagram-comments
username: "{username}"
display_name: "{nome}"
followers: {n}
following: {n}
posts_scraped: {n}
total_comments: {n}
scraped_at: "YYYY-MM-DD HH:MM"
---

# Comentarios -- @{username}

**Posts analisados**: {n}
**Total de comentarios**: {n}
**Coletado em**: YYYY-MM-DD HH:MM

---

## Post 1 -- YYYY-MM-DD

**URL**: https://www.instagram.com/p/{shortcode}/
**Comentarios**: {n}

- **@usuario1** (5 likes): Texto do comentario aqui
- **@usuario2**: Outro comentario de primeiro nivel
- **@usuario3** (12 likes): Mais um comentario

---
```

## Tratamento de Erros

| Situacao | Acao |
|----------|------|
| Perfil privado/nao encontrado | Informar e abortar |
| Login necessario | Fluxo de login interativo |
| 2FA | Pedir codigo ao usuario |
| Dialogos pos-login | "Not Now" |
| Post nao carrega | Pular e continuar |
| Comentarios desativados | Registrar no .md e continuar |
| Rate limit | Pausar 30s, retry 1x |
| Poucos posts disponiveis | Coletar o que houver e informar |

## Performance e Tempos Reais (testado Mar 2026)

- **Coleta de links**: ~30s para 100 posts (scroll agressivo)
- **Extracao por lote**: ~40-60s para 10 posts
- **Total para 100 posts**: ~8-12 minutos
- Processar posts **sequencialmente** — Playwright compartilha uma unica instancia do browser, paralelizar agentes causa conflitos de navegacao
- Lotes de **10 posts** por `browser_run_code` sao o sweet spot — menos que isso e lento demais, mais que isso pode dar timeout

## Armadilhas Conhecidas

1. **Seletores CSS do Instagram NAO funcionam** — classes sao randomicas e mudam entre sessoes. Nunca tentar extrair comentarios via `querySelector` com classes CSS.
2. **`page.accessibility.snapshot()` NAO existe** em `browser_run_code` — nao confundir com `browser_snapshot` (que e uma tool MCP separada).
3. **`require('fs')` NAO funciona** em `browser_run_code` — o contexto e de browser, nao Node.js.
4. **Scroll de 3000px com delay de 800ms e insuficiente** para coletar 100+ posts. Usar 5000px e 1200ms.
5. **Filtrar links por username** — o grid de posts mostra sugestoes de outros perfis misturadas.
6. **Filtrar o usuario logado** — o alt da profile picture contem o username logado, que precisa ser excluido dos comentarios.
7. **Verificar "No comments yet"** via `document.body.innerText.includes('No comments yet')` antes de tentar extrair — evita processamento desnecessario.

## Limitacoes

1. **Login obrigatorio** — Instagram bloqueia tudo sem autenticacao
2. **2FA pode ser necessario** — usuario precisa acesso ao WhatsApp/email
3. **Comentarios paginados** — posts muito populares podem ter centenas de comentarios; a expansao "View all" carrega no maximo ~40-50 por vez
4. **Apenas grid posts** — sem stories/highlights
5. **Risco da conta** — uso excessivo pode gerar restricao temporaria
6. **Estrutura DOM pode mudar** — o truque dos "6 niveis" depende da estrutura atual do Instagram (Mar 2026). Se parar de funcionar, re-debugar com a abordagem descrita na Fase 2.
