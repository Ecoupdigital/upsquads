---
name: instagram-scraper
description: "Scrape e transcreva perfis do Instagram. Use quando o usuario enviar uma URL de perfil do Instagram, pedir para extrair posts, transcrever videos/reels, analisar tom de comunicacao, ou capturar conteudo de um perfil. Suporta imagens, carrosseis e videos com transcricao de audio via Whisper e transcricao visual de slides/imagens."
---

# Instagram Profile Scraper

Skill para extrair e transcrever conteudo completo de perfis do Instagram:
- **Transcricao de audio** de videos/reels via Whisper
- **Transcricao visual** de cada slide de carrossel e imagem via Claude vision
- **Analise de tom e comunicacao** consolidada

**IMPORTANTE:** O Instagram exige login para acessar qualquer perfil — nao funciona sem autenticacao.

## Prerequisitos

Verificar ferramentas:
```bash
which yt-dlp && which ffmpeg && which whisper
```

Se faltar: `pip install --break-system-packages yt-dlp openai-whisper && apt install -y ffmpeg`

Whisper model: `medium` (portugues/ingles). Primeira execucao baixa ~1.4GB.

## Pipeline Otimizado (5 Fases)

O fluxo e dividido em 5 fases para maxima velocidade:

### Fase 1: Setup + Login + Coleta de Links (~2 min)

#### 1a. Criar diretorios
```bash
mkdir -p /home/vault/00-inbox/instagram-{username}
mkdir -p /tmp/instagram-{username}/{images,audio,videos}
```

**IMPORTANTE:** Apenas o `.md` final fica em `/home/vault/00-inbox/`. Todo resto vai em `/tmp/`.

#### 1b. Login no Instagram via Playwright

1. `browser_resize` 1440x900
2. `browser_navigate` para `https://www.instagram.com/`
3. Verificar se ja esta logado (presenca de Home/Reels/Messages no snapshot)
4. Se nao logado:
   - Navegar para `https://www.instagram.com/`
   - Pedir credenciais via `AskUserQuestion`
   - `browser_fill_form` username + password
   - `browser_click` "Log In"
   - Tratar 2FA se necessario (WhatsApp/email code)
   - Dispensar dialogos: "Save login info?" → "Not now", "Turn on Notifications" → "Not Now"

#### 1c. Exportar cookies para yt-dlp

Usar `browser_run_code` (NAO `browser_evaluate` — cookies httpOnly nao sao acessiveis via JS da pagina):

```javascript
async (page) => {
  const cookies = await page.context().cookies();
  return cookies
    .filter(c => c.domain.includes('instagram'))
    .map(c => `${c.domain}\tTRUE\t${c.path}\t${c.secure ? 'TRUE' : 'FALSE'}\t${Math.floor(c.expires)}\t${c.name}\t${c.value}`)
    .join('\n');
}
```

Salvar em `/tmp/instagram_cookies.txt` com header `# Netscape HTTP Cookie File`.

#### 1d. Navegar ao perfil e extrair metadados

1. `browser_navigate` para `https://www.instagram.com/{username}/`
2. `browser_wait_for` 3s + `browser_snapshot`
3. Extrair: nome, bio, seguidores, seguindo, total posts
4. Se privado ou nao encontrado → abortar

#### 1e. Coletar links dos posts via scroll rapido

Usar `browser_run_code` para scroll automatico rapido:

```javascript
async (page) => {
  let allLinks = new Set();
  let noNewCount = 0;
  for (let i = 0; i < 50 && allLinks.size < TARGET && noNewCount < 3; i++) {
    const links = await page.evaluate(() => {
      const els = document.querySelectorAll('a[href*="/p/"], a[href*="/reel/"]');
      return [...new Set([...els].map(a => a.href))];
    });
    const prevSize = allLinks.size;
    links.forEach(l => allLinks.add(l));
    if (allLinks.size === prevSize) noNewCount++;
    else noNewCount = 0;
    await page.evaluate(() => window.scrollBy(0, 3000));
    await page.waitForTimeout(800);
  }
  return { total: allLinks.size, links: [...allLinks] };
}
```

**800ms de delay e suficiente** — nao precisa de 2-4s. Filtrar apenas links do username alvo (ignorar posts de outros perfis que aparecem como sugestao).

### Fase 2: Screenshots em Batch (~3 min para 50 posts)

Usar `browser_run_code` para navegar e screenshotar todos os slides de multiplos posts de uma vez. Processar em lotes de ~10 posts por chamada:

```javascript
async (page) => {
  const posts = [{id: "p01", url: "..."}, ...];
  const results = [];
  for (const post of posts) {
    await page.goto(post.url, {waitUntil: 'domcontentloaded'});
    await page.waitForTimeout(2000);
    let slideNum = 1;
    await page.screenshot({path: `/tmp/instagram-{username}/images/${post.id}-s${String(slideNum).padStart(2,'0')}.png`, type: 'png'});
    let hasNext = true;
    while (hasNext && slideNum < 15) {
      try {
        const nextBtn = page.getByLabel('Next');
        if (await nextBtn.isVisible({timeout: 1000})) {
          await nextBtn.click();
          await page.waitForTimeout(800);
          slideNum++;
          await page.screenshot({path: `...`, type: 'png'});
        } else { hasNext = false; }
      } catch { hasNext = false; }
    }
    results.push({id: post.id, slides: slideNum});
  }
  return results;
}
```

### Fase 3: Download + Transcricao de Audio em Background

Rodar em background (`run_in_background: true`) enquanto a Fase 4 processa visual:

```bash
# Batch: download, extract audio, transcribe ALL reels
for reel in ...; do
  yt-dlp --cookies /tmp/instagram_cookies.txt --no-check-certificates --quiet -o "video.mp4" "$url"
  ffmpeg -y -i video.mp4 -vn -acodec pcm_s16le -ar 16000 -ac 1 audio.wav
  whisper audio.wav --model medium --language pt --output_format txt --output_dir ...
done
```

### Fase 4: Transcricao Visual com Agentes Paralelos (~5 min para 50 posts)

**CRITICO: A transcricao visual e OBRIGATORIA.** O conteudo real dos posts esta nas IMAGENS (texto sobre fundo, infograficos, dados educativos), nao na legenda.

Lancar agentes em paralelo para ler screenshots via `Read` (Claude vision). **Manter batches equilibrados de ~50-60 slides por agente** (nao sobrecarregar um agente com mais que isso).

Cada agente:
1. Le cada screenshot com `Read`
2. Transcreve TODO o texto visivel + descreve o visual brevemente
3. Salva em arquivo `/tmp/instagram-{username}/transcriptions-batchN.txt`

Formato de saida por slide:
```
POST_ID|SLIDE_NUM|TEXT: {todo texto visivel}|VISUAL: {descricao breve}
```

### Fase 5: Compilacao do .md via Python + Limpeza (~10 seg)

**NAO usar agente para compilar o .md** — e muito lento. Usar Python para parsear os arquivos de transcricao e gerar o .md:

```python
# Ler todos os batch files de transcricao visual
# Ler todos os .txt de transcricao de audio
# Montar o .md com template
# Escrever o arquivo final
```

O script Python:
1. Le transcricoes visuais de `/tmp/instagram-{username}/transcriptions-batch*.txt`
2. Le transcricoes de audio de `/tmp/instagram-{username}/audio/reel-*.txt`
3. Gera o .md consolidado em `/home/vault/00-inbox/instagram-{username}/{username}-posts.md`
4. Limpa temp: `rm -rf /tmp/instagram-{username}/ /tmp/instagram_cookies.txt`

## Formato do Arquivo de Saida

```markdown
---
source: instagram
username: "{username}"
display_name: "{nome}"
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

## Post N — YYYY-MM-DD

**Tipo**: Video/Reel | Carrossel (N slides) | Imagem
**URL**: https://www.instagram.com/frankcosta/{type}/{code}/

### Conteudo Visual

#### Slide 1
**Texto**: {todo texto visivel na imagem}
**Visual**: {descricao breve do layout/visual}

#### Slide 2
**Texto**: {texto}
**Visual**: {descricao}

(etc)

### Transcricao do Audio (apenas reels)
> {transcricao completa do Whisper}

---

# Analise Geral de Comunicacao

## Tom predominante
## Padroes de linguagem
## Estilo de conteudo
## Estrutura recorrente dos carrosseis
```

## Tratamento de erros

| Situacao | Acao |
|----------|------|
| Perfil privado/nao encontrado | Informar e abortar |
| Login necessario | Fluxo de login interativo |
| 2FA | Pedir codigo ao usuario |
| Dialogos pos-login | "Not Now" |
| yt-dlp falha | Registrar e continuar |
| ffmpeg/Whisper falha | Registrar e continuar |
| Post nao carrega | Pular e continuar |
| Rate limit | Pausar 60s, retry 1x |
| Agente travado | Parar e relancer com batch menor |
| Screenshots limpos antes de transcrever | Re-tirar screenshots antes de relancer agentes |

## Limitacoes

1. **Login obrigatorio** — Instagram bloqueia tudo sem autenticacao
2. **2FA pode ser necessario** — usuario precisa acesso ao WhatsApp/email
3. **yt-dlp precisa estar atualizado** — `pip install -U yt-dlp`
4. **Tempo**: ~10-15 min para 50 posts com transcricao visual completa
5. **Whisper**: musica de fundo pode comprometer transcricao
6. **Screenshots, nao originais** — capturas do viewport
7. **Apenas grid posts** — sem stories/highlights
8. **Risco da conta** — uso excessivo pode gerar restricao temporaria
