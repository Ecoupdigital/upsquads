# Instagram Comment Extraction — Abordagem Validada

> Atualizado em: 2026-03-21. Testada com 100 posts de @lfpro.oficial (912 comentarios extraidos com sucesso).

## Abordagem que FUNCIONA: Profile Picture DOM Traversal

O Instagram obfusca classes CSS e muda a estrutura frequentemente. A unica ancora estavel sao os atributos `alt` das imagens de profile picture, que seguem o padrao `"{username}'s profile picture"`.

### Algoritmo

```javascript
// 1. Encontrar todas as profile pictures
const imgs = document.querySelectorAll('img[alt*="profile picture"]');

// 2. Para cada imagem (excluindo perfil alvo e usuario logado):
for (const img of imgs) {
  const alt = img.alt;
  if (alt.includes('PERFIL_ALVO') || alt.includes('USUARIO_LOGADO')) continue;
  const username = alt.replace("'s profile picture", '').trim();

  // 3. Subir 6 niveis no DOM
  let el = img;
  for (let i = 0; i < 6; i++) { el = el.parentElement; if (!el) break; }
  if (!el) continue;

  // 4. O nextElementSibling contem o texto do comentario
  const nextSib = el.nextElementSibling;
  if (!nextSib) continue;
  const sibText = nextSib.innerText || '';

  // 5. Parsear linhas (filtrar username, timestamps, botoes)
  // ...
}
```

### Estrutura DOM (Marco 2026)

```
<div>                          ← 6o parent (container do comentario)
  <div>                        ← 5o parent
    <div>                      ← 4o parent
      <span>                   ← 3o parent
        <div>                  ← 2o parent
          <a role="link">      ← 1o parent (link da profile picture)
            <img alt="username's profile picture">  ← ANCORA
          </a>
        </div>
      </span>
    </div>
  </div>
  <div>                        ← nextElementSibling — CONTEM O COMENTARIO
    <div>
      <div>
        <a>username</a>        ← username do comentario
        <a><time>3h</time></a> ← timestamp
      </div>
      <div>Texto do comentario aqui</div>  ← texto real
    </div>
    <div>
      <button>1 like</button>
      <button>Reply</button>
    </div>
  </div>
</div>
```

### Parseamento do innerText

O `innerText` do sibling vem como linhas separadas por `\n`. Filtrar:
- Linha igual ao username → pular
- Linha tipo `3h`, `2d`, `1w` → timestamp, pular
- Linha tipo `Reply`, `Like`, `See translation`, `Verified` → botao, pular
- Linha tipo `N likes` / `N like` → extrair contagem de likes
- Primeira linha restante com mais de 1 char → texto do comentario

## Expandir Comentarios

```javascript
// Clicar "View all N comments" (ate 5 tentativas)
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
```

## Deteccao de Posts sem Comentarios

```javascript
const noComments = await page.evaluate(() =>
  document.body.innerText.includes('No comments yet')
);
```

## Abordagens que NAO funcionam

1. **`page.accessibility.snapshot()`** — NAO existe em `browser_run_code`
2. **Seletores CSS com classes** — Instagram usa classes randomicas tipo `x1lliihq x1plvlek`
3. **`querySelector('a[href^="/"]')` para usernames** — pega links de navegacao, hashtags, perfis sugeridos
4. **`time[datetime]` + parent traversal** — o parent chain e inconsistente e pega timestamps do post
5. **`span[dir="auto"]`** — pega textos de toda a pagina, nao so comentarios
6. **`require('fs')` em browser_run_code** — contexto e browser, nao Node.js
